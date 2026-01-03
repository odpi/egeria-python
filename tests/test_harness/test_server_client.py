import json
import types
from json import JSONDecodeError

import pytest
import os

from pydantic import ValidationError

from pyegeria._server_client import ServerClient
from pyegeria.config import settings
from pyegeria.external_links import ExternalReferences
from pyegeria.logging_configuration import config_logging

from pyegeria._exceptions import PyegeriaException, print_exception_response, print_basic_exception, \
    print_validation_error, PyegeriaAPIException

EGERIA_USER = os.environ.get("EGERIA_USER", "peterprofile")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")


app_config = settings.Environment
config_logging()
view_server: str = app_config.egeria_view_server
view_url: str = app_config.egeria_view_server_url
user: str = EGERIA_USER
user_pass: str = EGERIA_USER_PASSWORD

def test_add_archive_file():
    server_display_name = "qs-metadata-server"

    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()
        archive_file = "content-packs/CocoComboArchive.omarchive"
        response = client.add_archive_file(archive_file, display_name = "qs-metadata-store")
        print(response)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
        assert False

def test_get_guid_for_name():
    name = "PostgreSQL Server"


    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()

        response = client.get_guid_for_name(name)
        print(f"\n\nGUID is {response}\n\n")
        assert True
    except (PyegeriaException, PyegeriaAPIException) as e:
        print_basic_exception(e)
        assert False


def test_add_search_keyword():
    keyword = "Sentinel"
    element_guid = "a3442fd4-7e23-4778-b139-9739172fdcd7"

    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()

        response = client.add_search_keyword_to_element(element_guid, keyword)
        print(response)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
        assert False

def test_find_search_keyword() :
    keyword = "*"
    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()
        response = client.find_search_keywords(keyword, output_format="DICT", report_spec = "Search-Keywords")
        if isinstance(response, dict | list):
            print(json.dumps(response, indent = 2))
        else:
            print(response)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
        assert False


def test_remove_search_keyword() :
    keyword_guid = "49cedf27-3aa3-4522-b4b9-7764bac99a3d"
    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()
        client.remove_search_keyword(keyword_guid)

        assert True
    except (PyegeriaException, JSONDecodeError) as e:
        print_basic_exception(e)
        assert False

def test_get_user_guid() :
    user_id = "peterprofile"
    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()
        response = client.get_elements_by_property_value(user_id,['userId', 'displayName','fullName'],None)
        if isinstance(response, dict | list):
            print(json.dumps(response, indent = 2))
        else:
            print(response)
        assert True
    except (PyegeriaException, JSONDecodeError) as e:
        print_basic_exception(e)
        assert False

def test_create_note_log():
    element_guid = "1a16188a-9cba-4c86-835b-e223e97d22bb" # Milvus
    element_qn = "SolutionComponent::Milvus::V1.0"
    note_log_display_name = "Milvus-NoteLog"
    journal_entry_display_name = "test-journal-entry"
    journal_entry_description = "First Journal Entry"

    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()
        response = client.create_note_log(element_qn = element_qn,
                                            note_log_display_name=note_log_display_name,
                                            journal_entry_description=journal_entry_description,)
        print("\n\n" + response)
        assert True
    except (PyegeriaException, JSONDecodeError) as e:
        print_basic_exception(e)
        assert False

def test_add_journal_entry():
    element_guid = "1a16188a-9cba-4c86-835b-e223e97d22bb" # Milvus
    element_qn = "SolutionComponent::Milvus"
    note_log_display_name = "Milvus-NoteLog"
    journal_entry_display_name = "test-journal-entry"
    journal_entry_description = "First Journal Entry"

    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()
        response = client.add_journal_entry(element_qn=element_qn, note_log_display_name=note_log_display_name,
                                            journal_entry_display_name=journal_entry_display_name,
                                            note_entry=journal_entry_description)
        print("\n\n" + response)
        assert True
    except (PyegeriaException, JSONDecodeError) as e:
        print_basic_exception(e)
        assert False

def test_find_note_logs():
    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()
        search_string = "*"
        output_format = "JSON"
        report_spec = "Referenceables"
        response = client.find_note_logs(search_string, output_format = output_format, report_spec=report_spec)
        if isinstance(response, dict | list):
            print(json.dumps(response, indent = 2))
        else:
            print(response)
    except (PyegeriaException, JSONDecodeError) as e:
        print_basic_exception(e)
        assert False

def test_remove_note_log() :
    note_log_guid = "5bcc6c62-b9aa-4f56-9d86-4c2bd63eb7f8"
    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()
        client.remove_note_log(note_log_guid)

        assert True
    except (PyegeriaException, JSONDecodeError) as e:
        print_basic_exception(e)
        assert False

def test_remove_note() :
    note_guid = "14067611-c5d6-4dd9-aa0a-52b8d0516610"
    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()
        client.remove_note(note_guid)

        assert True
    except (PyegeriaException, JSONDecodeError) as e:
        print_basic_exception(e)
        assert False

def test_find_notes():
    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()
        search_string = "Note::71a2d327-115b-4700-aac8"
        output_format = "JSON"
        report_spec = "Journal-Entry-DrE"
        response = client.find_notes(search_string, output_format = output_format, report_spec=report_spec)
        if isinstance(response, dict | list):
            print(json.dumps(response, indent = 2))
        else:
            print(response)
    except (PyegeriaException, JSONDecodeError) as e:
        print_basic_exception(e)
        assert False
    except ValidationError as e:
        print_validation_error(e)
        assert False

def test_get_notes_for_note_log():
    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()
        note_log_guid = "5c01cab6-3e57-4f74-b2b2-2438cf36415b"
        output_format = "JSON"
        report_spec = "Referenceables"
        response = client.get_notes_for_note_log(note_log_guid, output_format = output_format, report_spec = report_spec)
        if isinstance(response, dict | list):
            print(json.dumps(response, indent = 2))
        else:
            print(response)
    except (PyegeriaException, JSONDecodeError) as e:
        print_basic_exception(e)
        assert False

def test_add_comment():
    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()
        associated_guid = "ec80a761-2472-4c2a-a088-872c68b4961d"
        comment = "a new comment"
        comment_type = "STANDARD_COMMENT"
        body = {
            "class": "NewAttachmentRequestBody",
            "properties": {
                "class": "CommentProperties",
                "qualifiedName": client.make_feedback_qn("Comment", associated_guid),
                "description": comment,
                "commentType": comment_type
            }
        }
        response = client.add_comment_to_element(associated_guid, body=body)
        if isinstance(response, dict | list):
            print(json.dumps(response, indent = 2))
        else:
            print(response)
    except (PyegeriaException, JSONDecodeError) as e:
        print_basic_exception(e)
        assert False

def test_remove_comment_from_element():
    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()
        guid = "5c0a9924-b72a-4f0d-aac2-44e5cc7a05f6"

        response = client.remove_comment_from_element(comment_guid = guid, cascade_delete=True)
        if isinstance(response, dict | list):
            print(json.dumps(response, indent = 2))
        else:
            print(response)
    except (PyegeriaException, JSONDecodeError) as e:
        print_basic_exception(e)
        assert False

def test_get_comment_by_guid():
    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()
        guid = '11c2d9aa-8128-43c3-a06d-7231f148ecc6'

        response = client.get_comment_by_guid(guid)
        if isinstance(response, dict | list):
            print(json.dumps(response, indent = 2))
        else:
            print(response)
    except (PyegeriaException, JSONDecodeError) as e:
        print_basic_exception(e)
        assert False

def test_find_comments():
    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()
        search_string = "*"

        response = client.find_comments(search_string, output_format = "DICT", report_spec = "Journal-Entry-DrE")
        if isinstance(response, dict | list):
            print(json.dumps(response, indent = 2))
        if isinstance(response, dict | list):
            print(json.dumps(response, indent = 2))
        else:
            print(response)
    except (PyegeriaException, JSONDecodeError) as e:
        print_basic_exception(e)
        assert False


def test_create_informal_tag():
    tag = "GeoSpatial"
    description = "Tag for GeoSpatial"

    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()

        response = client.create_informal_tag(tag, description)
        if isinstance(response, dict | list):
            print(response)
        else:
            print(response)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
        assert False

def test_find_informal_tags() :
    search_string = "*"
    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()
        response = client.find_tags(search_string, output_format="DICT", report_spec = "Informal-Tags-DrE")
        if isinstance(response, dict | list):
            print(json.dumps(response, indent = 2))
        else:
            print(response)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
        assert False


def test_delete_tag() :
    keyword_guid = "cd87a519-4dab-4bc4-b4e0-e939082820e8"
    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()
        client.delete_tag(keyword_guid)

        assert True
    except (PyegeriaException, JSONDecodeError) as e:
        print_basic_exception(e)
        assert False

def test_get_tag_by_guid() :
    guid = "d465235f-0dfa-435f-82b7-e50becde2b25"
    try:
        client = ServerClient(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()
        response = client.get_tag_by_guid(guid, output_format = "DICT", report_spec = "Informal-Tags-DrE")
        if isinstance(response, dict | list):
            print(json.dumps(response, indent = 2))
        assert True
    except (PyegeriaException, JSONDecodeError) as e:
        print_basic_exception(e)
        assert False
