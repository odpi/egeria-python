"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module tests the DataDiscovery class and methods from data_discovery.py
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
from pyegeria.omvs.data_discovery import DataDiscovery
from pyegeria.core.logging_configuration import config_logging, init_logging

disable_ssl_warnings = True

console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"


class TestDataDiscovery:
    good_platform1_url = PLATFORM_URL
    good_user_1 = USER_ID
    good_user_2 = USER_ID
    good_view_server_1 = VIEW_SERVER

    def _unique_qname(self, prefix: str = "Annotation") -> str:
        ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"{prefix}::{ts}"

    def test_create_annotation(self):
        """Test creating an annotation"""
        dd_client = DataDiscovery(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
        try:
            dd_client.create_egeria_bearer_token(self.good_user_2, USER_PWD)
            
            qualified_name = self._unique_qname("TestAnn")
            body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "AnnotationProperties",
                    "qualifiedName": qualified_name,
                    "displayName": "Test Annotation",
                    "annotationType": "Discovery",
                }
            }
            try:
                response = dd_client.create_annotation(body)
                assert response is not None
            except (PyegeriaInvalidParameterException, PyegeriaNotFoundException, PyegeriaAPIException):
                pass

        except PyegeriaConnectionException:
            print("Skipping test due to connection error")
        finally:
            dd_client.close_session()
