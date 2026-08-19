"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Unit tests for tech_types_handler module.
"""

from unittest.mock import MagicMock, AsyncMock, patch
import pytest

from tech_types_handler import TechTypesMixin
from StatusScreen import StatusScreen
from TechnologyTypeScreens import (
    TechnologyTypesScreen,
    TechnologyTypeOptionsScreen,
    TechnologyTypeTemplatesScreen,
    TechnologyTypeProcessesScreen,
)
from pyegeria import PyegeriaException


class DummyTechTypesApp(TechTypesMixin):
    """Test harness implementing TechTypesMixin."""

    def __init__(self):
        self.pushed_screens = []
        self.exit_code = None
        self.shown_main_screen = False
        self.log_messages = []
        self.user_name = "garygeeke"
        self.user_password = "secret"
        self.karma_points = 150
        self.view_server = "qs-view-server"
        self.platform_url = "https://127.0.0.1:9443"
        self.tech_type_response = []
        self.tech_type_list = []
        self.tech_type_data = {}
        self.tech_type_templates = []
        self.tech_type_processes = []

    def log(self, msg, *args, **kwargs):
        self.log_messages.append(str(msg))

    def _show_main_screen(self):
        self.shown_main_screen = True

    def push_screen(self, screen, callback=None):
        self.pushed_screens.append((screen, callback))
        # Support await if called in async context
        async def _noop():
            pass
        return _noop()

    def exit(self, code):
        self.exit_code = code

    def status_callback(self, *args, **kwargs):
        pass


class TestTechTypesMixin:
    """Tests for TechTypesMixin methods."""

    @pytest.mark.asyncio
    @patch.object(TechTypesMixin, "fetch_technology_types", new_callable=AsyncMock)
    async def test_handle_technology_types_option_success(self, mock_fetch):
        app = DummyTechTypesApp()
        app.tech_type_response = [{"displayName": "Postgres"}]
        app.tech_type_list = [{"displayName": "Postgres"}]

        await app.handle_technology_types_option()

        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, TechnologyTypesScreen)
        assert cb == app.tech_type_callback

    @pytest.mark.asyncio
    @patch.object(TechTypesMixin, "fetch_technology_types", new_callable=AsyncMock)
    async def test_handle_technology_types_option_empty(self, mock_fetch):
        app = DummyTechTypesApp()
        app.tech_type_response = []

        await app.handle_technology_types_option()
        assert app.exit_code == 200

    @pytest.mark.asyncio
    @patch.object(TechTypesMixin, "fetch_technology_types", new_callable=AsyncMock)
    async def test_handle_technology_types_option_error(self, mock_fetch):
        app = DummyTechTypesApp()
        app.tech_type_response = "404"

        await app.handle_technology_types_option()
        assert app.exit_code == 404

    @pytest.mark.asyncio
    @patch("tech_types_handler.AutomatedCuration")
    async def test_tech_type_callback_valid_selection(self, mock_ac_cls, sample_tech_type_detail):
        app = DummyTechTypesApp()
        mock_ac = MagicMock()
        mock_ac.create_egeria_bearer_token.return_value = "token"
        mock_ac.get_tech_type_detail.return_value = sample_tech_type_detail
        mock_ac_cls.return_value = mock_ac

        res = await app.tech_type_callback("tech-type-guid-999")
        assert res == 200
        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, TechnologyTypeOptionsScreen)
        assert cb == app.tech_type_options_callback
        assert app.tech_type_name == "PostgreSQL Database"
        assert "specificationMermaidGraph" not in app.tech_type_data

    @pytest.mark.asyncio
    async def test_tech_type_callback_cancelled(self):
        app = DummyTechTypesApp()
        res = await app.tech_type_callback(None)
        assert res is None
        assert app.shown_main_screen is True

        app.shown_main_screen = False
        res = await app.tech_type_callback(400)
        assert res == 400
        assert app.shown_main_screen is True

    @pytest.mark.asyncio
    @patch("tech_types_handler.AutomatedCuration")
    async def test_tech_type_callback_exception(self, mock_ac_cls):
        app = DummyTechTypesApp()
        mock_ac = MagicMock()
        mock_ac.create_egeria_bearer_token.side_effect = PyegeriaException("Auth failed")
        mock_ac_cls.return_value = mock_ac

        await app.tech_type_callback("tech-type-guid-999")
        assert len(app.pushed_screens) == 2  # StatusScreen pushed on error, then TechnologyTypeOptionsScreen
        assert isinstance(app.pushed_screens[0][0], StatusScreen)

    @pytest.mark.asyncio
    async def test_tech_type_options_callback_template(self):
        app = DummyTechTypesApp()
        app.tech_type_name = "PostgreSQL"
        app.tech_type_description = "Database"
        app.tech_type_templates = [{"displayName": "Template1"}]

        res = await app.tech_type_options_callback(["template", "Template1"])
        assert res == 200
        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, TechnologyTypeTemplatesScreen)
        assert cb == app.tech_type_templates_callback

    @pytest.mark.asyncio
    async def test_tech_type_options_callback_process(self):
        app = DummyTechTypesApp()
        app.tech_type_name = "PostgreSQL"
        app.tech_type_description = "Database"
        app.tech_type_processes = [{"displayName": "Process1"}]

        res = await app.tech_type_options_callback(["process", "Process1"])
        assert res == 200
        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, TechnologyTypeProcessesScreen)
        assert cb == app.tech_type_processes_callback

    @pytest.mark.asyncio
    async def test_tech_type_options_callback_back_or_empty(self):
        app = DummyTechTypesApp()
        res = await app.tech_type_options_callback(None)
        assert res == 200
        assert app.shown_main_screen is True

        app.shown_main_screen = False
        res = await app.tech_type_options_callback("back")
        assert res == 200
        assert app.shown_main_screen is True

        app.shown_main_screen = False
        res = await app.tech_type_options_callback([])
        assert res == 200
        assert app.shown_main_screen is True

    def test_unpack_egeria_data_dict_with_data(self):
        app = DummyTechTypesApp()
        app.tech_type_data = {"data": [{"name": "item1"}]}
        assert app.unpack_egeria_data() == 200
        assert app.tech_type_list == [{"name": "item1"}]

    def test_unpack_egeria_data_direct_dict(self):
        app = DummyTechTypesApp()
        app.tech_type_data = {"name": "item1"}
        assert app.unpack_egeria_data() == 200
        assert app.tech_type_list == [{"name": "item1"}]

    def test_unpack_egeria_data_list(self):
        app = DummyTechTypesApp()
        app.tech_type_data = [{"data": [{"name": "item1"}]}]
        assert app.unpack_egeria_data() == 200
        assert app.tech_type_list == [{"name": "item1"}]

    def test_unpack_egeria_data_invalid(self):
        app = DummyTechTypesApp()
        app.tech_type_data = 12345
        assert app.unpack_egeria_data() == 417

    @patch("tech_types_handler.AutomatedCuration")
    def test_tech_type_templates_callback_success(self, mock_ac_cls):
        app = DummyTechTypesApp()
        app.autoc = MagicMock()
        mock_instance = MagicMock()
        mock_instance.initiate_gov_action_process.return_value = "new-proc-guid-999"
        mock_ac_cls.return_value = mock_instance

        input_result = [
            "input",
            {"database_name_placeholder_input": "mydb"},
            {
                "Catalog Template GUID": "templ-guid-1",
                "typeName": "Database",
            },
        ]
        app.tech_type_templates_callback(input_result)

        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, StatusScreen)
        assert "new-proc-guid-999" in screen.status_message

    def test_tech_type_templates_callback_invalid(self):
        app = DummyTechTypesApp()
        res = app.tech_type_templates_callback(400)
        assert res == 400

        res = app.tech_type_templates_callback(["invalid"])
        assert res == 418

    def test_tech_type_processes_callback_invalid(self):
        app = DummyTechTypesApp()
        res = app.tech_type_processes_callback(400)
        assert res == 400

        res = app.tech_type_processes_callback(["invalid"])
        assert res == 418
        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, StatusScreen)

    def test_tech_type_processes_callback_valid_input(self):
        app = DummyTechTypesApp()
        input_result = [
            "input",
            {"target_server_process_input": "srv1"},
            {
                "displayName": "Provision Server",
                "description": "Server provisioning process",
                "additionalProperties": {"templateGUID": "tmpl-1"},
            },
        ]
        app.tech_type_processes_callback(input_result)
        assert app.input_data == {"target_server_process_input": "srv1"}
        assert app.full_process["displayName"] == "Provision Server"
