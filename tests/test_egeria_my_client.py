"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the core OMAG config class and methods
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""

import json
import time

from rich import print, print_json

from pyegeria import (
    EgeriaMy,
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

disable_ssl_warnings = True

notelog_for_testing = {
    "class": "NoteLogProperties",
    "qualifiedName": "test-note-log",
    "name": "Test Note Log",
    "description": "This is a note log for testing purposes",
    "additionalProperties": {"skyColor": "blue", "bestNoteLogEver": "this one"},
}

note_for_testing = {
    "class": "NoteProperties",
    "qualifiedName": "ready for testing",
    "title": "Ready for Testing",
    "text": "This element has been reviewed and is ready for further testing",
    "additionalProperties": {"status": "Testing Ready", "isCritical?": "No"},
}

term_guid = "d8ecbed1-b521-4feb-80f5-6224338e5ec2"


class TestEgeriaMy:
    good_platform1_url = "https://127.0.0.1:9443"

    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    good_user_3 = "peterprofile"
    bad_user_1 = "eviledna"
    bad_user_2 = ""
    good_server_1 = "simple-metadata-store"
    good_server_2 = "laz_kv"
    good_server_3 = "active-metadata-store"
    good_engine_host_1 = "governDL01"
    good_view_server_1 = "view-server"

    def test_get_my_profile(self):
        try:
            m_client = EgeriaMy(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")

            response = m_client.get_my_profile()

            id_list = []
            if type(response) is dict:
                print_json(data=response)
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            m_client.close_session()

    def test_find_notes(self):
        m_client = EgeriaMy(
            self.good_view_server_1,
            self.good_platform1_url,
            user_id=self.good_user_2,
        )

        token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")

        note_log_response = m_client.create_note_log(
            term_guid, body=notelog_for_testing
        )
        response = m_client.create_note(
            note_log_response["guid"], body=note_for_testing
        )
        response = m_client.find_notes({"filter": ""})
        assert "class" in response[0]
        assert "qualifiedName" in response[0]
        assert "guid" in response[0]
        m_client.remove_note_log(note_log_response["guid"])
