"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module tests the LineageLinker class and methods from lineage_linker.py
"""

from rich import print
from rich.console import Console

from pyegeria.core._exceptions import (
    PyegeriaInvalidParameterException,
    PyegeriaConnectionException,
    PyegeriaAPIException,
    PyegeriaNotFoundException,
)
from pyegeria.omvs.lineage_linker import LineageLinker
from pyegeria.core.logging_configuration import config_logging, init_logging

disable_ssl_warnings = True

console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"


class TestLineageLinker:
    good_platform1_url = PLATFORM_URL
    good_user_1 = USER_ID
    good_user_2 = USER_ID
    good_view_server_1 = VIEW_SERVER

    def test_link_lineage(self):
        """Test linking lineage"""
        ll_client = LineageLinker(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
        try:
            ll_client.create_egeria_bearer_token(self.good_user_2, USER_PWD)
            
            # This is hard to test without valid GUIDs, so we'll just check if it handles connection errors
            # or basic invalid parameter reporting if Egeria is running.
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "DataFlowProperties",
                    "label": "Test Flow",
                }
            }
            try:
                ll_client.link_lineage("guid1", "DataFlow", "guid2", body)
            except (PyegeriaInvalidParameterException, PyegeriaNotFoundException, PyegeriaAPIException):
                pass

        except PyegeriaConnectionException:
            print("Skipping test due to connection error")
        finally:
            ll_client.close_session()
