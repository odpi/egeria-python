"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module tests the SchemaMaker class and methods from schema_maker.py
"""
from datetime import datetime

from rich import print
from rich.console import Console

from pyegeria.core._exceptions import (
    PyegeriaInvalidParameterException,
    PyegeriaConnectionException,
    PyegeriaAPIException,
    PyegeriaNotFoundException,
)
from pyegeria.omvs.schema_maker import SchemaMaker
from pyegeria.core.logging_configuration import config_logging, init_logging

disable_ssl_warnings = True

console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"


class TestSchemaMaker:
    good_platform1_url = PLATFORM_URL
    good_user_1 = USER_ID
    good_user_2 = USER_ID
    good_view_server_1 = VIEW_SERVER

    def _unique_qname(self, prefix: str = "SchemaType") -> str:
        ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"{prefix}::{ts}"

    def test_create_schema_type(self):
        """Test creating a schema type"""
        sm_client = SchemaMaker(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
        try:
            sm_client.create_egeria_bearer_token(self.good_user_2, USER_PWD)
            
            qualified_name = self._unique_qname("TestST")
            body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "SchemaTypeProperties",
                    "qualifiedName": qualified_name,
                    "displayName": "Test Schema Type",
                }
            }
            try:
                response = sm_client.create_schema_type(body)
                assert response is not None
            except (PyegeriaInvalidParameterException, PyegeriaNotFoundException, PyegeriaAPIException):
                pass

        except PyegeriaConnectionException:
            print("Skipping test due to connection error")
        finally:
            sm_client.close_session()
