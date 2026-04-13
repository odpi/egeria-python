"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module tests the ActionAuthor class and methods from action_author.py
"""

from rich import print
from rich.console import Console

from pyegeria.core._exceptions import (
    PyegeriaInvalidParameterException,
    PyegeriaConnectionException,
    PyegeriaAPIException,
    PyegeriaNotFoundException,
)
from pyegeria.omvs.action_author import ActionAuthor
from pyegeria.core.logging_configuration import config_logging, init_logging

disable_ssl_warnings = True

console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"


class TestActionAuthor:
    good_platform1_url = PLATFORM_URL
    good_user_1 = USER_ID
    good_user_2 = USER_ID
    good_view_server_1 = VIEW_SERVER

    def test_link_governance_action_executor(self):
        """Test linking governance action executor"""
        aa_client = ActionAuthor(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
        try:
            aa_client.create_egeria_bearer_token(self.good_user_2, USER_PWD)
            
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "GovernanceActionExecutorProperties",
                    "requestType": "TestRequest",
                }
            }
            try:
                aa_client.link_governance_action_executor("type_guid", "engine_guid", body)
            except (PyegeriaInvalidParameterException, PyegeriaNotFoundException, PyegeriaAPIException):
                pass

        except PyegeriaConnectionException:
            print("Skipping test due to connection error")
        finally:
            aa_client.close_session()
