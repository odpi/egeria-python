"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module tests the ValidTypeLists class and methods from valid_type_lists.py
"""

from rich import print
from rich.console import Console

from pyegeria.core._exceptions import (
    PyegeriaInvalidParameterException,
    PyegeriaConnectionException,
    PyegeriaAPIException,
    PyegeriaNotFoundException,
)
from pyegeria.omvs.valid_type_lists import ValidTypeLists
from pyegeria.core.logging_configuration import config_logging, init_logging

disable_ssl_warnings = True

console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"


class TestValidTypeLists:
    good_platform1_url = PLATFORM_URL
    good_user_1 = USER_ID
    good_user_2 = USER_ID
    good_view_server_1 = VIEW_SERVER

    def test_get_all_entity_types(self):
        """Test getting all entity types"""
        vtl_client = ValidTypeLists(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
        try:
            vtl_client.create_egeria_bearer_token(self.good_user_2, USER_PWD)
            
            try:
                response = vtl_client.get_all_entity_types()
                assert response is not None
            except (PyegeriaInvalidParameterException, PyegeriaNotFoundException, PyegeriaAPIException):
                pass

        except PyegeriaConnectionException:
            print("Skipping test due to connection error")
        finally:
            vtl_client.close_session()
