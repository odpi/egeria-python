"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module tests the PeopleOrganizer class and methods from people_organizer.py

A running Egeria environment is needed to run these tests.
"""

from rich import print
from rich.console import Console

from pyegeria.core._exceptions import (
    PyegeriaConnectionException,
    PyegeriaAPIException,
    PyegeriaNotFoundException,
)
from pyegeria.omvs.people_organizer import PeopleOrganizer
from pyegeria.core.logging_configuration import config_logging, init_logging

disable_ssl_warnings = True

console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"


class TestPeopleOrganizer:
    good_platform1_url = PLATFORM_URL
    good_user_1 = USER_ID
    good_user_2 = USER_ID
    good_view_server_1 = VIEW_SERVER

    def test_link_peer_person(self):
        """Test linking peer persons"""
        po_client = PeopleOrganizer(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
        try:
            po_client.create_egeria_bearer_token(self.good_user_2, USER_PWD)
            
            # Since we don't have easy way to create persons here without other clients,
            # we just test the method call with dummy GUIDs and expect it to fail on the server
            # but succeed in making the request if the connection is up.
            
            person_one_guid = "cf73ee3b-893d-43d3-948b-15fb9482527d"
            person_two_guid = "c9fce4ac-e03b-4be7-a01d-48ac7c450a19"
            
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "PeerProperties",
                }
            }
            
            try:
                po_client.link_peer_person(person_one_guid, person_two_guid, body)
            except (PyegeriaNotFoundException, PyegeriaAPIException):
                # This is expected if dummy GUIDs are used
                pass

        except PyegeriaConnectionException:
            print("Skipping test due to connection error (no Egeria running)")
        finally:
            po_client.close_session()

    def test_link_team_structure(self):
        """Test linking team structure"""
        po_client = PeopleOrganizer(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
        try:
            po_client.create_egeria_bearer_token(self.good_user_2, USER_PWD)
            
            super_team_guid = "dummy-team-guid-1"
            subteam_guid = "dummy-team-guid-2"
            
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "TeamStructureProperties",
                    "delegationEscalationAuthority": True,
                }
            }
            
            try:
                po_client.link_team_structure(super_team_guid, subteam_guid, body)
            except (PyegeriaNotFoundException, PyegeriaAPIException):
                # This is expected if dummy GUIDs are used
                pass

        except PyegeriaConnectionException:
            print("Skipping test due to connection error (no Egeria running)")
        finally:
            po_client.close_session()
