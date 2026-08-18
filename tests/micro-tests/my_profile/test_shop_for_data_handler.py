"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Unit tests for shop_for_data_handler module.
"""

from unittest.mock import MagicMock, AsyncMock, patch
import pytest

from shop_for_data_handler import ShopForDataMixin
from ShopForDataScreen import ShopForDataScreen
from SearchForTermScreen import SearchForTermScreen
from SelectionOverviewScreen import SelectionOverviewScreen
from CreateSubscriptionRequestScreen import CreateSubscriptionRequestScreen
from StatusScreen import StatusScreen
from pyegeria import PyegeriaException


class DummyShopApp(ShopForDataMixin):
    """Test harness implementing ShopForDataMixin."""

    def __init__(self):
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
        res = await app.handle_shop_for_data_option()
        assert res == 420
        assert app.exit_code == 420

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

    @patch("shop_for_data_handler.ProductManager")
    def test_overview_callback_subscribe_success(self, mock_pm_cls):
        app = DummyShopApp()
        mock_pm = MagicMock()
        mock_pm.create_egeria_bearer_token.return_value = "token"
        mock_pm_cls.return_value = mock_pm

        app.overview_callback([211, "Item1", "Tree1"])
        mock_pm.create_digital_subscription.assert_called_once_with("Item1")

    @patch("shop_for_data_handler.ProductManager")
    def test_overview_callback_subscribe_failure(self, mock_pm_cls):
        app = DummyShopApp()
        mock_pm = MagicMock()
        mock_pm.create_egeria_bearer_token.return_value = "token"
        mock_pm.create_digital_subscription.side_effect = PyegeriaException("Subscription failed")
        mock_pm_cls.return_value = mock_pm

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
