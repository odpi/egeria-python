"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module tests the JacquardDataSets class and methods from jacquard_data_sets.py
"""
import json

from rich import print
from rich.console import Console

from pyegeria.core._exceptions import (
    PyegeriaInvalidParameterException,
    PyegeriaConnectionException,
    PyegeriaAPIException,
    PyegeriaNotFoundException,
)
from examples.jacquard_data_sets import JacquardDataSets
from pyegeria.core.logging_configuration import config_logging, init_logging

disable_ssl_warnings = True

console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"


class TestJacquardDataSets:
    good_platform1_url = PLATFORM_URL
    good_user_1 = USER_ID
    good_user_2 = USER_ID
    good_view_server_1 = VIEW_SERVER

    def test_find_tabular_data_sets(self):
        """Test finding tabular data sets"""
        jds_client = JacquardDataSets(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
        try:
            jds_client.create_egeria_bearer_token(self.good_user_2, USER_PWD)
            
            try:
                response = jds_client.find_tabular_data_sets(search_string="*")
                print(f"\nFound {len(response)} tabular data sets")
                # print(json.dumps(response, indent=2))
                assert response is not None
            except (PyegeriaInvalidParameterException, PyegeriaNotFoundException, PyegeriaAPIException):
                pass

        except PyegeriaConnectionException:
            print("Skipping test due to connection error")
        finally:
            jds_client.close_session()
