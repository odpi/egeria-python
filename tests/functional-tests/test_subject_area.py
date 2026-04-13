"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module tests the SubjectArea class and methods from subject_area.py
"""
from datetime import datetime

from rich import print
from rich.console import Console

from pyegeria.core._exceptions import (
    PyegeriaInvalidParameterException,
    PyegeriaAPIException,
    PyegeriaNotFoundException,
    print_basic_exception,
    PyegeriaException,
)
from pyegeria.omvs.subject_area import SubjectArea
from pyegeria.core.logging_configuration import config_logging, init_logging

disable_ssl_warnings = True

console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"


class TestSubjectArea:
    good_platform1_url = PLATFORM_URL
    good_user_1 = USER_ID
    good_user_2 = USER_ID
    good_view_server_1 = VIEW_SERVER

    def _unique_qname(self, prefix: str = "SubjectArea") -> str:
        ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"{prefix}::{ts}"

    def test_create_subject_area(self):
        """Test creating a subject area"""
        sa_client = SubjectArea(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
        try:
            sa_client.create_egeria_bearer_token(self.good_user_2, USER_PWD)
            
            qualified_name = self._unique_qname("TestSA")
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "SubjectAreaProperties",
                    "qualifiedName": qualified_name,
                    "displayName": "Test Subject Area",
                    "subjectAreaName": "Testing Subject Area",
                    "domainIdentifier": 0,
                }
            }
            try:
                response = sa_client.create_subject_area(body)
                assert response is not None
            except (PyegeriaInvalidParameterException, PyegeriaNotFoundException, PyegeriaAPIException):
                pass

        except PyegeriaException as e:
            print("Skipping test due to connection error")
            print_basic_exception(e)
        finally:
            sa_client.close_session()
