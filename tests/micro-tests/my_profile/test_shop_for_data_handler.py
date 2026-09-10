"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Unit tests for shop_for_data_handler module.
"""

from unittest.mock import MagicMock, AsyncMock, patch
import pytest

from textual.app import App
from shop_for_data_handler import ShopForDataMixin
from ShopForDataScreen import ShopForDataScreen
from SearchForTermScreen import SearchForTermScreen
from SelectionOverviewScreen import SelectionOverviewScreen
from CreateSubscriptionRequestScreen import CreateSubscriptionRequestScreen
from StatusScreen import StatusScreen
from pyegeria import PyegeriaException


class DummyShopApp(App, ShopForDataMixin):
    """Test harness implementing ShopForDataMixin."""

    def __init__(self):
        super().__init__()
        self.pushed_screens = []
        self.exit_code = None
        self.shown_main_screen = False
        self.log_messages = []
        self.user_name = "garygeeke"
        self.user_password = "secret"
        self.view_server = "qs-view-server"
        self.platform_url = "https://127.0.0.1:9443"
        self.root_collection_table = MagicMock()
        self.collections = []
        self.selected_item = None
        self.selected_tree = None
        self.data_table_highlighted = "glossary_table"
        self.row_highlighted = "row1"
        self.cursor_row_highlighted = 0
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

    def exit(self, code=0, return_value=None):
        self.exit_code = code

    def status_callback(self, *args, **kwargs):
        pass

    def search_for_term_callback(self, *args, **kwargs):
        pass

    def notify(self, msg, *args, **kwargs):
        self.log_messages.append(f"Notify: {msg}")

    def query_one(self, selector, *args, **kwargs):
        if selector in self.widgets:
            return self.widgets[selector]
        mock_widget = MagicMock()
        return mock_widget


class TestShopForDataMixin:
    """Tests for ShopForDataMixin methods."""

    @pytest.mark.asyncio
    @patch("shop_for_data_handler.DataTable")
    @patch("shop_for_data_handler.exec_report_spec")
    async def test_handle_shop_for_data_option_success(self, mock_exec, mock_table_cls):
        mock_table = MagicMock()
        mock_table_cls.return_value = mock_table
        mock_exec.return_value = {
            "kind": "data",
            "data": [
                {
                    "Display Name": "Test Element",
                    "Description": "Test Desc",
                    "Qualified Name": "Test::QN",
                }
            ],
        }

        app = DummyShopApp()
        await app.handle_shop_for_data_option()

        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, ShopForDataScreen)
        assert cb == app.shop_for_data_callback

        # Test the underlying worker fetch methods directly
        await ShopForDataMixin.get_digital_product_data.__wrapped__(app)
        catalog_calls = [
            call for call in mock_exec.call_args_list
            if call.kwargs.get("format_set_name") == "Digital-Product-Catalog-MyE"
        ]
        assert len(catalog_calls) == 1
        assert catalog_calls[0].kwargs.get("params") == {
            "search_string": "*",
            "metadata_element_type": "DigitalProductCatalog",
            "_type": "DigitalProductCatalog",
            "graph_query_depth": 0,
        }

    @pytest.mark.asyncio
    @patch("shop_for_data_handler.DataTable")
    @patch("shop_for_data_handler.exec_report_spec")
    async def test_handle_shop_for_data_option_empty_data(self, mock_exec, mock_table_cls):
        mock_table = MagicMock()
        mock_table_cls.return_value = mock_table
        mock_exec.return_value = {"kind": "empty", "data": []}

        app = DummyShopApp()
        await app.handle_shop_for_data_option()

        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, ShopForDataScreen)

    @pytest.mark.asyncio
    @patch("shop_for_data_handler.DataTable")
    @patch("shop_for_data_handler.exec_report_spec")
    async def test_handle_shop_for_data_option_exception(self, mock_exec, mock_table_cls):
        mock_table = MagicMock()
        mock_table_cls.return_value = mock_table
        mock_exec.side_effect = PyegeriaException("Network Error")

        app = DummyShopApp()
        await app.handle_shop_for_data_option()
        res = await ShopForDataMixin.get_glossary_data.__wrapped__(app)
        assert res == ["No Data", "Returned by Egeria"]
        assert app.glossary_data == ["No Data", "Returned by Egeria"]

    @pytest.mark.asyncio
    async def test_shop_for_data_callback_exit_codes(self):
        app = DummyShopApp()
        res = await app.shop_for_data_callback(200)
        assert res == 200
        assert app.shown_main_screen is True

        app.shown_main_screen = False
        res = await app.shop_for_data_callback(210)
        assert res == 210
        assert app.shown_main_screen is True

    @pytest.mark.asyncio
    async def test_shop_for_data_callback_search_for_term(self):
        app = DummyShopApp()
        res = await app.shop_for_data_callback(201)
        assert res == 200
        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, SearchForTermScreen)

    @pytest.mark.asyncio
    async def test_shop_for_data_callback_sample_data_source(self):
        app = DummyShopApp()
        mock_table = MagicMock()
        mock_table.get_row.return_value = ["Item 1", "Desc 1", "QN 1"]
        app.widgets["#glossary_table"] = mock_table

        res = await app.shop_for_data_callback([212, "row1", 0, "glossary_table"])
        assert res == 200

    @pytest.mark.asyncio
    @patch("shop_for_data_handler.exec_report_spec")
    async def test_shop_for_data_callback_glossary_selection(self, mock_exec):
        mock_exec.return_value = {
            "kind": "data",
            "data": [
                {
                    "Display Name": "Term 1",
                    "Description": "Term 1 description",
                    "Qualified Name": "GlossaryTerm::T1",
                }
            ],
        }

        app = DummyShopApp()
        await app.shop_for_data_callback(["glossary", "Clinical Glossary", "Glossary::Clinical"])
        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, SelectionOverviewScreen)
        assert cb == app.overview_callback

    @pytest.mark.asyncio
    @patch("shop_for_data_handler.exec_report_spec")
    async def test_shop_for_data_callback_dictionary_selection(self, mock_exec):
        mock_exec.return_value = {
            "kind": "data",
            "data": [
                {
                    "Display Name": "Dict 1",
                    "Description": "Dict 1 desc",
                    "Qualified Name": "Dictionary::D1",
                }
            ],
        }

        app = DummyShopApp()
        await app.shop_for_data_callback(["dictionary", "DataDict", "Dict::QN"])
        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, SelectionOverviewScreen)

    @pytest.mark.asyncio
    @patch("shop_for_data_handler.exec_report_spec")
    async def test_shop_for_data_callback_domain_selection(self, mock_exec):
        mock_exec.return_value = {
            "kind": "data",
            "data": [
                {
                    "Display Name": "Domain 1",
                    "Description": "Domain 1 desc",
                    "Qualified Name": "Domain::Dom1",
                }
            ],
        }

        app = DummyShopApp()
        await app.shop_for_data_callback(["domain", "FinanceDomain", "Domain::Finance"])
        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, SelectionOverviewScreen)

    @pytest.mark.asyncio
    @patch("shop_for_data_handler.exec_report_spec")
    async def test_shop_for_data_callback_catalog_selection(self, mock_exec):
        mock_exec.return_value = {
            "kind": "data",
            "data": [
                {
                    "Display Name": "Cat 1",
                    "Description": "Cat 1 desc",
                    "Qualified Name": "Catalog::C1",
                }
            ],
        }

        app = DummyShopApp()
        await app.shop_for_data_callback(["catalog", "ProductCat", "Catalog::Prod"])
        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, SelectionOverviewScreen)

    @pytest.mark.asyncio
    async def test_shop_for_data_callback_collection_selection(self):
        app = DummyShopApp()
        app.collections = [{"Qualified Name": "Coll::Root", "Containing Members": "Folder1, Folder2"}]
        await app.shop_for_data_callback(["collection", "Coll::Root", "Root Collection"])
        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, SelectionOverviewScreen)

    def test_overview_callback_error_codes(self):
        for err_code in [410, 411, 412, 413, 414, 415]:
            app = DummyShopApp()
            app.overview_callback(err_code)
            if err_code in [410, 411, 412, 413]:
                assert len(app.pushed_screens) == 1
                assert isinstance(app.pushed_screens[0][0], StatusScreen)

    def test_overview_callback_subscribe_success(self):
        app = DummyShopApp()
        app.overview_callback([211, "Item1", "Tree1"])
        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, CreateSubscriptionRequestScreen)
        assert cb == app.create_subscription_callback

    def test_overview_callback_subscribe_failure(self):
        app = DummyShopApp()
        app.overview_callback([211, "Item1", "Tree1"])
        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, CreateSubscriptionRequestScreen)

    def test_create_subscription_callback_cancelled(self):
        app = DummyShopApp()
        app.create_subscription_callback(None)
        assert any("cancelled" in msg for msg in app.log_messages)

    def test_create_subscription_callback_success(self):
        app = DummyShopApp()
        app.create_subscription_callback("Sub-Result-123")
        assert any("Subscription created" in msg for msg in app.log_messages)

    def test_create_subscription_callback_dict_with_guid(self):
        app = DummyShopApp()
        app.selected_item = "fallback-guid"
        app.create_subscription_callback({
            "externalSourceGUID": "item-guid-123",
            "displayName": "Test Sub",
            "Status": "ACTIVE",
            "description": "Test Desc",
            "identifier": "TS1",
        })
        assert any("Subscription created" in msg for msg in app.log_messages)

    @pytest.mark.asyncio
    @patch("shop_for_data_handler.ProductManager")
    async def test_shop_for_data_callback_direct_subscribe(self, mock_pm_cls):
        app = DummyShopApp()
        res = await app.shop_for_data_callback([
            211,
            "row1",
            0,
            "digital_product_catalog_table",
            ["Prod Name", "Prod Desc", "Prod::QN", "guid-prod-123"],
        ])
        assert res == 211
        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, CreateSubscriptionRequestScreen)
        assert cb == app.create_subscription_callback
        assert app.selected_item == "guid-prod-123"

    @pytest.mark.asyncio
    @patch("shop_for_data_handler.ProductManager")
    async def test_request_to_subscribe_data_source_placeholder(self, mock_pm_cls):
        app = DummyShopApp()
        app.handle_shop_for_data_option = AsyncMock()
        await app.request_to_subscribe_data_source(
            "row1",
            0,
            "digital_product_catalog_table",
            row_values=["No digital product catalogs found", "No data returned from Egeria", "", ""],
        )
        assert any("No valid data element selected to subscribe" in msg for msg in app.log_messages)
        assert app.handle_shop_for_data_option.called

    @patch("shop_for_data_handler.ProductManager")
    def test_create_subscription_callback_creates_subscription_with_client(self, mock_pm_cls):
        mock_client = MagicMock()
        mock_pm_cls.return_value = mock_client
        mock_client.create_digital_subscription.return_value = "created-sub-guid"

        app = DummyShopApp()
        app.selected_item = "guid-prod-123"
        app.create_subscription_callback({
            "displayName": "My Sub",
            "description": "Sub Desc",
            "Status": "ACTIVE",
            "identifier": "MS-01",
            "externalSourceGUID": "guid-prod-123",
        })

        assert mock_client.create_digital_subscription.called
        call_args = mock_client.create_digital_subscription.call_args[0][0]
        assert call_args["class"] == "NewAgreementRequestBody"
        assert call_args["initialStatus"] == "ACTIVE"
        assert call_args["externalSourceGUID"] == "guid-prod-123"
        assert call_args["properties"]["displayName"] == "My Sub"
        assert any("Created digital subscription successfully" in msg for msg in app.log_messages)

    def test_on_worker_state_changed_product_group(self):
        app = DummyShopApp()
        mock_table = MagicMock()
        app.digital_product_catalog_table = mock_table

        mock_worker = MagicMock()
        mock_worker.group = "product_group"
        mock_worker.result = {
            "kind": "data",
            "data": [
                {
                    "Display Name": "Catalog 1",
                    "Description": "Desc 1",
                    "Qualified Name": "Cat::1",
                    "GUID": "g-1",
                }
            ],
        }

        mock_event = MagicMock()
        mock_event.worker = mock_worker
        from textual.worker import WorkerState
        mock_event.state = WorkerState.SUCCESS

        app.on_worker_state_changed(mock_event)
        mock_table.add_row.assert_called_once_with("Catalog 1", "Desc 1", "Cat::1", "g-1")
        assert mock_table.loading is False

    def test_on_worker_state_changed_without_active_dom_nodes(self):
        """Verify that when query_one fails, on_worker_state_changed handles it cleanly via instance tables."""
        app = DummyShopApp()
        mock_table = MagicMock()
        app.digital_product_catalog_table = mock_table
        # query_one raises Exception simulating missing DOM node on Screen(id='_default')
        app.query_one = MagicMock(side_effect=Exception("No nodes match"))

        mock_worker = MagicMock()
        mock_worker.group = "product_group"
        mock_worker.result = {
            "kind": "data",
            "data": [
                {
                    "Display Name": "Catalog 1",
                    "Description": "Desc 1",
                    "Qualified Name": "Cat::1",
                    "GUID": "g-1",
                }
            ],
        }

        mock_event = MagicMock()
        mock_event.worker = mock_worker
        from textual.worker import WorkerState
        mock_event.state = WorkerState.SUCCESS

        app.on_worker_state_changed(mock_event)
        mock_table.add_row.assert_called_once_with("Catalog 1", "Desc 1", "Cat::1", "g-1")
        assert mock_table.loading is False

    def test_on_worker_state_changed_product_group_list_error(self):
        """Verify that when worker returns a list (e.g. error list ['No Data', 'Returned by Egeria']), no AttributeError is raised."""
        app = DummyShopApp()
        mock_table = MagicMock()
        app.digital_product_catalog_table = mock_table

        mock_worker = MagicMock()
        mock_worker.group = "product_group"
        mock_worker.result = ["No Data", "Returned by Egeria"]

        mock_event = MagicMock()
        mock_event.worker = mock_worker
        from textual.worker import WorkerState
        mock_event.state = WorkerState.SUCCESS

        app.on_worker_state_changed(mock_event)
        mock_table.add_row.assert_called_once_with("No digital product catalogs found", "No data returned from Egeria", "", "")
        assert mock_table.loading is False

    def test_on_worker_state_changed_all_groups_raw_list(self):
        """Verify raw list of dicts works for all groups."""
        from textual.worker import WorkerState

        app = DummyShopApp()
        glossary_table = MagicMock()
        dict_table = MagicMock()
        domain_table = MagicMock()
        root_table = MagicMock()

        app.glossary_table = glossary_table
        app.data_dictionary_table = dict_table
        app.business_domain_table = domain_table
        app.root_collection_table = root_table

        # Glossary group
        worker = MagicMock(group="glossary_group", result=[{"Display Name": "G1", "Description": "D1", "Qualified Name": "Q1"}])
        app.on_worker_state_changed(MagicMock(worker=worker, state=WorkerState.SUCCESS))
        glossary_table.add_row.assert_called_once_with("G1", "D1", "Q1")

        # Dictionary group
        worker = MagicMock(group="dictionary_group", result=[{"Display Name": "Dic1", "Description": "D1", "Qualified Name": "Q1", "GUID": "g1"}])
        app.on_worker_state_changed(MagicMock(worker=worker, state=WorkerState.SUCCESS))
        dict_table.add_row.assert_called_once_with("Dic1", "D1", "Q1", "g1")

        # Domain group
        worker = MagicMock(group="domain_group", result=[{"Qualified Name": "Dom1", "Type Name": "T1", "GUID": "g1"}])
        app.on_worker_state_changed(MagicMock(worker=worker, state=WorkerState.SUCCESS))
        domain_table.add_row.assert_called_once_with("Dom1", "T1", "g1")

        # Root group
        worker = MagicMock(group="root_group", result=[{"Root Collection Name": "RC1", "Description": "Desc1", "GUID": "g1"}])
        app.on_worker_state_changed(MagicMock(worker=worker, state=WorkerState.SUCCESS))
        root_table.add_row.assert_called_once_with("RC1", "Desc1", "g1")
