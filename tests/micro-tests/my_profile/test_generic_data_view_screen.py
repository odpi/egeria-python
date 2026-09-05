"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Unit tests for GenericDataViewScreen and its data sampling functionality in My Profile App.
"""

from unittest.mock import MagicMock, AsyncMock, patch
import pytest
from textual.app import App
from textual.widgets import DataTable

from GenericDataViewScreen import GenericDataViewScreen, DataViewScreen
from shop_for_data_handler import ShopForDataMixin
from ShopForDataScreen import ShopForDataScreen


class GenericDataViewTestApp(App):
    """Host app for testing GenericDataViewScreen."""

    def __init__(self, screen_factory):
        super().__init__()
        self.screen_factory = screen_factory
        self.target_screen = None
        self.dismissed_result = None

    async def on_mount(self):
        self.target_screen = self.screen_factory()

        def _cb(result):
            self.dismissed_result = result

        await self.push_screen(self.target_screen, callback=_cb)


class TestGenericDataViewParsing:
    """Tests for parsing dict and list-of-dicts sample data into (Key, Value) pairs (max 10 rows)."""

    def test_parse_dict_data_under_10_rows(self):
        data = {
            "Host": "localhost",
            "Port": 8080,
            "Environment": "Production",
            "Status": "Active",
        }
        rows = GenericDataViewScreen.parse_sample_data(data, max_rows=10)
        assert len(rows) == 4
        assert rows[0] == ("Host", "localhost")
        assert rows[1] == ("Port", "8080")
        assert rows[2] == ("Environment", "Production")
        assert rows[3] == ("Status", "Active")

    def test_parse_dict_data_capped_at_10_rows(self):
        data = {f"Key_{i}": f"Value_{i}" for i in range(25)}
        rows = GenericDataViewScreen.parse_sample_data(data, max_rows=10)
        assert len(rows) == 10
        assert rows[0] == ("Key_0", "Value_0")
        assert rows[9] == ("Key_9", "Value_9")

    def test_parse_dict_wrapping_list(self):
        data = {
            "kind": "table",
            "data": [
                {"Key": f"K_{i}", "Value": f"V_{i}"} for i in range(15)
            ],
        }
        rows = GenericDataViewScreen.parse_sample_data(data, max_rows=10)
        assert len(rows) == 10
        assert rows[0] == ("K_0", "V_0")
        assert rows[9] == ("K_9", "V_9")

    def test_parse_list_of_single_key_dicts(self):
        data = [{"col_a": "val_1"}, {"col_b": "val_2"}, {"col_c": "val_3"}]
        rows = GenericDataViewScreen.parse_sample_data(data, max_rows=10)
        assert len(rows) == 3
        assert rows[0] == ("col_a", "val_1")
        assert rows[1] == ("col_b", "val_2")
        assert rows[2] == ("col_c", "val_3")

    def test_parse_list_of_explicit_key_value_dicts(self):
        data = [
            {"Key": "Customer ID", "Value": "1001"},
            {"Key": "Customer Name", "Value": "Alice"},
            {"Key": "Region", "Value": "EMEA"},
        ]
        rows = GenericDataViewScreen.parse_sample_data(data, max_rows=10)
        assert len(rows) == 3
        assert rows[0] == ("Customer ID", "1001")
        assert rows[1] == ("Customer Name", "Alice")
        assert rows[2] == ("Region", "EMEA")

    def test_parse_list_of_multikey_records_with_name_candidate(self):
        data = [
            {"Display Name": f"Record_{i}", "Type": "Integer", "Nullable": False}
            for i in range(15)
        ]
        rows = GenericDataViewScreen.parse_sample_data(data, max_rows=10)
        assert len(rows) == 10
        assert rows[0][0] == "Record_0"
        assert "Type: Integer" in rows[0][1]
        assert "Nullable: False" in rows[0][1]
        assert rows[9][0] == "Record_9"

    def test_parse_list_of_multikey_records_without_name_candidate(self):
        data = [
            {"col1": f"val1_{i}", "col2": f"val2_{i}"}
            for i in range(12)
        ]
        rows = GenericDataViewScreen.parse_sample_data(data, max_rows=10)
        assert len(rows) == 10
        assert rows[0][0] == "Row 1"
        assert "col1: val1_0" in rows[0][1]
        assert "col2: val2_0" in rows[0][1]

    def test_parse_empty_data(self):
        assert GenericDataViewScreen.parse_sample_data(None) == []
        assert GenericDataViewScreen.parse_sample_data([]) == []
        assert GenericDataViewScreen.parse_sample_data({}) == []

    def test_parse_string_data(self):
        rows = GenericDataViewScreen.parse_sample_data("Some sample text", max_rows=10)
        assert len(rows) == 1
        assert rows[0] == ("Sample Data", "Some sample text")


class TestGenericDataViewScreenUI:
    """UI lifecycle and interaction tests for GenericDataViewScreen."""

    @pytest.mark.asyncio
    async def test_screen_mount_with_dict_data(self):
        sample = {"Attribute 1": "Value 1", "Attribute 2": "Value 2"}
        app = GenericDataViewTestApp(
            lambda: GenericDataViewScreen(
                sample_data=sample,
                data_element_name="Test Product",
                data_element_qualified_name="DP::TestProduct",
            )
        )
        async with app.run_test() as pilot:
            table = app.target_screen.query_one("#generic_data_view_table", DataTable)
            assert table.row_count == 2
            # Verify columns
            cols = [col.label.plain for col in table.columns.values()]
            assert "Key" in cols
            assert "Value" in cols

    @pytest.mark.asyncio
    async def test_screen_mount_with_list_data(self):
        sample = [
            {"Display Name": f"Element_{i}", "Detail": f"Detail_{i}"}
            for i in range(15)
        ]
        app = GenericDataViewTestApp(
            lambda: GenericDataViewScreen(
                sample_data=sample,
                data_element_name="Test Dataset",
                data_element_qualified_name="DS::TestDataset",
            )
        )
        async with app.run_test() as pilot:
            table = app.target_screen.query_one("#generic_data_view_table", DataTable)
            assert table.row_count == 10

    @pytest.mark.asyncio
    async def test_screen_mount_with_empty_data(self):
        app = GenericDataViewTestApp(
            lambda: GenericDataViewScreen(
                sample_data=None,
                data_element_name="Empty Dataset",
            )
        )
        async with app.run_test() as pilot:
            table = app.target_screen.query_one("#generic_data_view_table", DataTable)
            assert table.row_count == 1
            row_vals = table.get_row_at(0)
            assert row_vals[0] == "No data"

    @pytest.mark.asyncio
    async def test_screen_action_back(self):
        app = GenericDataViewTestApp(
            lambda: GenericDataViewScreen(
                sample_data={"K": "V"},
                data_element_name="Test Element",
            )
        )
        async with app.run_test() as pilot:
            app.target_screen.action_back()
            await pilot.pause()
            assert app.dismissed_result == 200

    @pytest.mark.asyncio
    async def test_screen_action_quit(self):
        app = GenericDataViewTestApp(
            lambda: GenericDataViewScreen(
                sample_data={"K": "V"},
                data_element_name="Test Element",
            )
        )
        async with app.run_test() as pilot:
            app.target_screen.action_quit()
            await pilot.pause()
            assert app.dismissed_result == 210

    @pytest.mark.asyncio
    async def test_screen_action_subscribe(self):
        app = GenericDataViewTestApp(
            lambda: GenericDataViewScreen(
                sample_data={"K": "V"},
                data_element_name="Test Product",
                data_element_qualified_name="DP::TestProduct::123",
            )
        )
        async with app.run_test() as pilot:
            app.target_screen.action_subscribe()
            await pilot.pause()
            assert isinstance(app.dismissed_result, list)
            assert app.dismissed_result[0] == 211
            assert app.dismissed_result[1] == "Test Product"
            assert app.dismissed_result[2] == "DP::TestProduct::123"


class DummyShopForDataApp(ShopForDataMixin):
    """Test harness for shop_for_data_handler sampling actions."""

    def __init__(self):
        self.pushed_screens = []
        self.log_messages = []
        self.shown_main_screen = False
        self.user_name = "garygeeke"
        self.user_password = "secret"
        self.view_server = "qs-view-server"
        self.platform_url = "https://127.0.0.1:9443"
        self.widgets = {}

    def log(self, msg, *args, **kwargs):
        self.log_messages.append(str(msg))

    def _show_main_screen(self):
        self.shown_main_screen = True

    def push_screen(self, screen, callback=None):
        self.pushed_screens.append((screen, callback))
        async def _noop():
            pass
        return _noop()

    def query_one(self, selector, *args, **kwargs):
        if selector in self.widgets:
            return self.widgets[selector]
        mock_widget = MagicMock()
        return mock_widget

    def notify(self, msg, *args, **kwargs):
        self.log_messages.append(f"Notify: {msg}")


class TestShopForDataSamplingIntegration:
    """Integration tests for launching GenericDataViewScreen from shop_for_data_handler."""

    @pytest.mark.asyncio
    async def test_request_to_sample_data_source_launches_screen(self):
        app = DummyShopForDataApp()
        mock_table = MagicMock()
        mock_table.get_row.return_value = ["Product 1", "Product Description", "DP::Product1"]
        mock_table.row_count = 1
        app.widgets["#digital_product_catalog_table"] = mock_table

        await app.request_to_sample_data_source("row1", 0, "digital_product_catalog_table")

        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, GenericDataViewScreen)
        assert screen.data_element_name == "Product 1"
        assert screen.data_element_qualified_name == "DP::Product1"
        assert cb == app.generic_data_view_callback

    @pytest.mark.asyncio
    async def test_request_to_sample_data_source_with_passed_row_values(self):
        app = DummyShopForDataApp()
        row_values = ["Direct Product", "Direct Desc", "DP::Direct::1"]
        await app.request_to_sample_data_source("row1", 0, "digital_product_catalog_table", row_values=row_values)

        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, GenericDataViewScreen)
        assert screen.data_element_name == "Direct Product"
        assert screen.data_element_qualified_name == "DP::Direct::1"
        assert cb == app.generic_data_view_callback

    def test_parse_tabular_data_set_report(self):
        sample_report = {
            "tabularDataSetReport": {
                "recordCount": 2,
                "tableName": "TestTable",
                "columnDescriptions": [
                    {"columnName": "ID"},
                    {"columnName": "Value"},
                    {"columnName": "Description"},
                ],
                "dataRecords": {
                    "0": ["REC-1", "Val-1", "Desc-1"],
                    "1": ["REC-2", "Val-2", "Desc-2"],
                },
            }
        }
        rows = GenericDataViewScreen.parse_sample_data(sample_report, max_rows=10)
        assert len(rows) == 2
        assert rows[0][0] == "REC-1"
        assert "Value: Val-1" in rows[0][1]
        assert "Description: Desc-1" in rows[0][1]
        assert rows[1][0] == "REC-2"
        assert "Value: Val-2" in rows[1][1]

    @pytest.mark.asyncio
    @patch("shop_for_data_handler.ProductManager")
    async def test_generic_data_view_callback_subscribe(self, mock_pm_cls):
        mock_pm = MagicMock()
        mock_pm_cls.return_value = mock_pm

        app = DummyShopForDataApp()
        await app.generic_data_view_callback([211, "Product 1", "DP::Product1"])

        mock_pm.create_digital_subscription.assert_called_once_with("DP::Product1")

    @pytest.mark.asyncio
    async def test_generic_data_view_callback_quit(self):
        app = DummyShopForDataApp()
        await app.generic_data_view_callback(210)
        assert app.shown_main_screen is True

    @pytest.mark.asyncio
    @patch("shop_for_data_handler.Egeria")
    async def test_request_to_sample_data_source_with_egeria_tabular_data(self, mock_egeria_cls):
        mock_egeria = MagicMock()
        mock_egeria_cls.return_value = mock_egeria
        mock_egeria.find_tabular_data_sets.return_value = [{"GUID": "guid-123"}]
        mock_egeria.get_tabular_data_set.return_value = {
            "tabularDataSetReport": {
                "recordCount": 1,
                "tableName": "SampleTabular",
                "columnDescriptions": [{"columnName": "Col1"}, {"columnName": "Col2"}],
                "dataRecords": {"0": ["V1", "V2"]},
            }
        }

        app = DummyShopForDataApp()
        row_values = ["Tabular Prod", "Tabular Desc", "DP::Tabular::1"]
        await app.request_to_sample_data_source("row1", 0, "digital_product_catalog_table", row_values=row_values)

        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, GenericDataViewScreen)
        assert screen.sample_data["tabularDataSetReport"]["tableName"] == "SampleTabular"

    @pytest.mark.asyncio
    async def test_request_to_sample_data_source_placeholder_notifies(self):
        app = DummyShopForDataApp()
        app.handle_shop_for_data_option = AsyncMock()
        row_values = ["No digital product catalogs found", "No data returned from Egeria", ""]
        await app.request_to_sample_data_source("row1", 0, "digital_product_catalog_table", row_values=row_values)

        assert len(app.pushed_screens) == 0
        assert any("No data element selected" in msg for msg in app.log_messages)
        app.handle_shop_for_data_option.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_shop_for_data_screen_action_sample_data_source(self):
        mock_table = DataTable(id="digital_product_catalog_table")
        screen = ShopForDataScreen(digital_product_catalog_table=mock_table)
        screen.dismiss = MagicMock()
        screen.data_table_highlighted = "digital_product_catalog_table"
        screen.row_highlighted = "r1"
        screen.cursor_row_highlighted = 0

        screen.action_sample_data_source()
        screen.dismiss.assert_called_once()
        args = screen.dismiss.call_args[0][0]
        assert args[0] == 212
        assert args[1] == "r1"
        assert args[2] == 0
        assert args[3] == "digital_product_catalog_table"
