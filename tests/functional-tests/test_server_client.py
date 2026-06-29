"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module is for testing the ServerClient class feedback methods (likes and ratings).
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.
"""

import json
import time
from datetime import datetime

from pydantic import ValidationError

from pyegeria import (
    PyegeriaException,
    print_exception_table,
    print_validation_error,
    print_basic_exception,
)
from pyegeria.core._exceptions import (
    PyegeriaInvalidParameterException,
    PyegeriaAPIException,
    PyegeriaUnauthorizedException,
)
from pyegeria.core._server_client import ServerClient
from pyegeria.omvs.my_profile import MyProfile

disable_ssl_warnings = True


class TestServerClientFeedback:
    """Test class for ServerClient feedback methods (likes and ratings)"""
    
    good_platform1_url = "https://localhost:9443"
    good_platform2_url = "https://oak.local:9443"
    bad_platform1_url = "https://localhost:9443"

    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    good_user_3 = "peterprofile"
    bad_user_1 = "eviledna"
    bad_user_2 = ""
    good_user_2_pwd = "secret"
    good_server_1 = "simple-metadata-store"
    good_server_2 = "qs-view-server"
    good_server_3 = "active-metadata-store"
    good_server_4 = "integration-daemon"
    good_server_5 = "fluffy_kv"
    good_server_6 = "cocoVIew1"
    good_engine_host_1 = "governDL01"
    good_view_server_1 = "view-server"
    good_view_server_2 = "qs-view-server"
    bad_server_1 = "coco"
    bad_server_2 = ""
    test_element_guid = "71e67a50-ced4-40ed-b25e-98142a009604"

    def test_add_like_to_element(self):
        """Test adding a like to an element"""
        s_client = None
        try:
            s_client = ServerClient(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )
            # Use a known element GUID from your test environment
            start_time = time.perf_counter()
            response = s_client.add_like_to_element(
                self.test_element_guid,
                body={}
            )
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\tResponse was: {json.dumps(response, indent=2)}")
            assert response is not None, "Like not added"
        except PyegeriaInvalidParameterException as e:
            print_exception_table(e)
            assert False, "Invalid parameter exception"
        except PyegeriaAPIException as e:
            print_exception_table(e)
            assert False, "API exception"
        except PyegeriaUnauthorizedException as e:
            print_exception_table(e)
            assert False, "Unauthorized exception"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Validation error"
        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Unexpected Pyegeria exception"
        except Exception as e:
            print(e)
            assert False, "Unexpected exception"
        finally:
            if s_client:
                s_client.close_session()

    def test_add_rating_to_element(self):
        """Test adding a rating to an element"""
        s_client = None
        try:
            s_client = ServerClient(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )
            rating_body = {
                "starRating": 5,
                "review": "Excellent element!"
            }
            start_time = time.perf_counter()
            response = s_client.add_rating_to_element(
                self.test_element_guid,
                body=rating_body
            )
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\tResponse was: {json.dumps(response, indent=2)}")
            assert response is not None, "Rating not added"
        except PyegeriaInvalidParameterException as e:
            print_exception_table(e)
            assert False, "Invalid parameter exception"
        except PyegeriaAPIException as e:
            print_exception_table(e)
            assert False, "API exception"
        except PyegeriaUnauthorizedException as e:
            print_exception_table(e)
            assert False, "Unauthorized exception"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Validation error"
        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Unexpected Pyegeria exception"
        except Exception as e:
            print(e)
            assert False, "Unexpected exception"
        finally:
            if s_client:
                s_client.close_session()

    def test_get_attached_likes(self):
        """Test retrieving likes attached to an element"""
        s_client = None
        try:
            s_client = ServerClient(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )
            start_time = time.perf_counter()
            response = s_client.get_attached_likes(
                self.test_element_guid,
                start_from=0,
                page_size=50
            )
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\tResponse was: {json.dumps(response, indent=2)}")
            assert response is not None, "Likes not retrieved"
        except PyegeriaInvalidParameterException as e:
            print_exception_table(e)
            assert False, "Invalid parameter exception"
        except PyegeriaAPIException as e:
            print_exception_table(e)
            assert False, "API exception"
        except PyegeriaUnauthorizedException as e:
            print_exception_table(e)
            assert False, "Unauthorized exception"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Validation error"
        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Unexpected Pyegeria exception"
        except Exception as e:
            print(e)
            assert False, "Unexpected exception"
        finally:
            if s_client:
                s_client.close_session()

    def test_get_attached_ratings(self):
        """Test retrieving ratings attached to an element"""
        s_client = None
        try:
            s_client = ServerClient(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )
            test_element_guid = "test-element-guid-123"
            start_time = time.perf_counter()
            response = s_client.get_attached_ratings(
                test_element_guid,
                start_from=0,
                page_size=50
            )
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\tResponse was: {json.dumps(response, indent=2)}")
            assert response is not None, "Ratings not retrieved"
        except PyegeriaInvalidParameterException as e:
            print_exception_table(e)
            assert False, "Invalid parameter exception"
        except PyegeriaAPIException as e:
            print_exception_table(e)
            assert False, "API exception"
        except PyegeriaUnauthorizedException as e:
            print_exception_table(e)
            assert False, "Unauthorized exception"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Validation error"
        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Unexpected Pyegeria exception"
        except Exception as e:
            print(e)
            assert False, "Unexpected exception"
        finally:
            if s_client:
                s_client.close_session()

    def test_remove_like_from_element(self):
        """Test removing a like from an element"""
        s_client = None
        try:
            s_client = ServerClient(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )
            start_time = time.perf_counter()
            response = s_client.remove_like_from_element(
                self.test_element_guid,
                body={}
            )
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\tResponse was: {json.dumps(response, indent=2)}")
            assert response is not None, "Like not removed"
        except PyegeriaInvalidParameterException as e:
            print_exception_table(e)
            assert False, "Invalid parameter exception"
        except PyegeriaAPIException as e:
            print_exception_table(e)
            assert False, "API exception"
        except PyegeriaUnauthorizedException as e:
            print_exception_table(e)
            assert False, "Unauthorized exception"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Validation error"
        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Unexpected Pyegeria exception"
        except Exception as e:
            print(e)
            assert False, "Unexpected exception"
        finally:
            if s_client:
                s_client.close_session()

    def test_remove_rating_from_element(self):
        """Test removing a rating from an element"""
        s_client = None
        try:
            s_client = ServerClient(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )
            test_element_guid = "test-element-guid-123"
            start_time = time.perf_counter()
            response = s_client.remove_rating_from_element(
                test_element_guid,
                body={}
            )
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\tResponse was: {json.dumps(response, indent=2)}")
            assert response is not None, "Rating not removed"
        except PyegeriaInvalidParameterException as e:
            print_exception_table(e)
            assert False, "Invalid parameter exception"
        except PyegeriaAPIException as e:
            print_exception_table(e)
            assert False, "API exception"
        except PyegeriaUnauthorizedException as e:
            print_exception_table(e)
            assert False, "Unauthorized exception"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Validation error"
        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Unexpected Pyegeria exception"
        except Exception as e:
            print(e)
            assert False, "Unexpected exception"
        finally:
            if s_client:
                s_client.close_session()

    def test_find_assets(self):
        from pyegeria.view.base_report_formats import select_report_spec
        report_spec_name = "Referenceable"
        output_format = "JSON"
        fmt = select_report_spec(report_spec_name, output_format)
        if not fmt:
            print(f"\nMissing report_spec: '{report_spec_name}' for output_format '{output_format}'. Run 'list_reports' to see available reports.")
            assert False, f"Missing report_spec: {report_spec_name}"
        action = fmt.get("action", {}) or {}
        if not action or not (action.get("function") or action.get("find_command")):
            print(f"\nMissing find command for report_spec: '{report_spec_name}'. Please define a find action in the report spec.")
            assert False, f"Missing find command for report_spec: {report_spec_name}"
        s_client = None
        try:
            s_client = ServerClient(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )
            start_time = time.perf_counter()
            search_string = "Sustainability"
            response = s_client.find_assets(
                search_string, output_format=output_format, report_spec=report_spec_name, page_size=10
            )
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, list):
                print(f"Found {len(response)} projects {type(response)}\n\n")
                print("\n\n" + json.dumps(response, indent=4))
            elif isinstance(response, str):
                print("\n\nGUID is: " + response)
            assert response is not None, "No assets found"
        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Validation error"
        except Exception as e:
            print(e)
            assert False, "Unexpected exception"
        finally:
            if s_client:
                s_client.close_session()

    def test_get_guid_for_name(self):
        """Test retrieving likes attached to an element"""
        s_client = None
        try:
            s_client = ServerClient(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )
            start_time = time.perf_counter()
            response = s_client.__get_guid__(display_name="My first comment", property_name="displayName")
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\tResponse was: {json.dumps(response, indent=2)}")
            assert response is not None, "GUID not retrieved"
        except PyegeriaInvalidParameterException as e:
            print_exception_table(e)
            assert False, "Invalid parameter exception"
        except PyegeriaAPIException as e:
            print_exception_table(e)
            assert False, "API exception"
        except PyegeriaUnauthorizedException as e:
            print_exception_table(e)
            assert False, "Unauthorized exception"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Validation error"
        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Unexpected Pyegeria exception"
        except Exception as e:
            print(e)
            assert False, "Unexpected exception"
        finally:
            if s_client:
                s_client.close_session()


class TestServerClientNoteLogs:
    """Test class for ServerClient NoteLog and Note methods"""

    good_platform1_url = "https://localhost:9443"
    good_view_server_2 = "qs-view-server"
    good_user_2 = "erinoverview"
    good_user_2_pwd = "secret"
    test_element_guid = "8bd082dc-b2a9-48c8-8dfb-31d32980662a"

    def test_notelog_lifecycle(self):
        """Test NoteLog lifecycle: create, update, find, get attached, remove"""
        s_client = None
        try:
            s_client = ServerClient(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )
            s_client.create_egeria_bearer_token()

            display_name = f"Test Note Log {int(time.time())}"

            # 1. Create NoteLog attached to an element (using convenience parameters)
            note_log_guid = s_client.create_note_log(
                self.test_element_guid,
                display_name=display_name,
                description="Functional test note log",
            )
            assert note_log_guid, "NoteLog was not created"
            print(f"\n\tCreated NoteLog GUID: {note_log_guid}")

            # 2. Update NoteLog (description supersedes nothing - merge update by default)
            s_client.update_note_log(
                note_log_guid,
                description="Updated functional test note log",
            )
            print("\n\tUpdated NoteLog")

            # 3. Find NoteLogs - returns dict (elements) or str ("no elements found")
            find_response = s_client.find_note_logs(display_name)
            assert find_response is not None, "find_note_logs returned None"
            print(f"\n\tfind_note_logs response: {json.dumps(find_response, indent=2)}")

            # 4. Get NoteLogs attached to the element
            attached_response = s_client.get_attached_note_logs(self.test_element_guid)
            assert attached_response is not None, "get_attached_note_logs returned None"
            print(f"\n\tget_attached_note_logs response: {json.dumps(attached_response, indent=2)}")

            # 5. Remove NoteLog
            s_client.remove_note_log(note_log_guid)
            print("\n\tRemoved NoteLog")

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Unexpected Pyegeria exception"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Validation error"
        finally:
            if s_client:
                s_client.close_session()

    def test_note_lifecycle(self):
        """Test Note lifecycle: create note log, create note, get note, list notes, remove"""
        s_client = None
        try:
            s_client = ServerClient(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )
            s_client.create_egeria_bearer_token()

            # Create a NoteLog first to hold the notes
            note_log_guid = s_client.create_note_log(
                self.test_element_guid,
                display_name=f"Test Note Log for Notes {int(time.time())}",
                description="Holds notes for the note lifecycle test",
            )
            assert note_log_guid, "NoteLog was not created"
            print(f"\n\tCreated NoteLog GUID: {note_log_guid}")

            # 1. Create a Note within the NoteLog
            note_guid = s_client.create_note(
                note_log_guid,
                display_name=f"Test Note {int(time.time())}",
                description="Functional test note content",
            )
            assert note_guid, "Note was not created"
            print(f"\n\tCreated Note GUID: {note_guid}")

            # 2. Retrieve the Note by GUID (notes are of type Notification)
            note = s_client.get_note_by_guid(note_guid, metadata_element_type_name="Notification")
            assert note is not None, "get_note_by_guid returned None"
            print(f"\n\tget_note_by_guid response: {json.dumps(note, indent=2)}")

            # 3. List the Notes attached to the NoteLog
            notes = s_client.get_notes_for_note_log(note_log_guid, metadata_element_type_name="Notification")
            assert notes is not None, "get_notes_for_note_log returned None"
            print(f"\n\tget_notes_for_note_log response: {json.dumps(notes, indent=2)}")

            # Cleanup - cascade delete removes the contained notes with the note log
            s_client.remove_note_log(note_log_guid, cascade_delete=True)
            print("\n\tRemoved NoteLog")

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Unexpected Pyegeria exception"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Validation error"
        finally:
            if s_client:
                s_client.close_session()


class TestServerClientJournal:
    """Test class for ServerClient Journal methods"""

    good_platform1_url = "https://laz.local:9443"
    good_view_server_2 = "qs-view-server"
    good_user_2 = "erinoverview"
    good_user_2_pwd = "secret"
    test_element_guid = "71e67a50-ced4-40ed-b25e-98142a009604"

    def test_add_journal_entry(self):
        """Test adding a journal entry"""
        s_client = None
        try:
            s_client = ServerClient(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            journal_qn = f"test-journal-{int(time.time())}"
            note_entry = "This is a test journal entry"

            journal_guid = s_client.add_journal_entry(
                note_log_qn=journal_qn,
                journal_entry_display_name="Test Journal Entry",
                note_entry=note_entry
            )
            assert journal_guid is not None
            print(f"\n\tCreated Journal Entry GUID: {journal_guid}")

        except Exception as e:
            print(f"Exception: {e}")
            assert False, f"Test failed with exception: {e}"
        finally:
            if s_client:
                s_client.close_session()


class TestMyProfileActivity:
    """Test class for MyProfile activity methods (Blog, Journal, Log)"""

    good_platform1_url = "https://laz.local:9443"
    good_view_server_2 = "qs-view-server"
    good_user_2 = "erinoverview"
    good_user_2_pwd = "secret"

    def test_activity_methods(self):
        """Test blog, journal, and log activity methods"""
        m_client = None
        try:
            m_client = MyProfile(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            activity_body = {
                "class": "NewAttachmentRequestBody",
                "properties": {
                    "class": "NotificationProperties",
                    "typeName": "Notification",
                    "qualifiedName": f"test-activity-{int(time.time())}",
                    "displayName": "Test Activity",
                    "description": "Functional test activity"
                }
            }

            # 1. Blog my activity
            blog_guid = m_client.blog_my_activity(body=activity_body)
            assert blog_guid is not None
            print(f"\n\tBlogged activity GUID: {blog_guid}")

            # 2. Journal my activity
            journal_guid = m_client.journal_my_activity(body=activity_body)
            assert journal_guid is not None
            print(f"\n\tJournaled activity GUID: {journal_guid}")

            # 3. Log my activity
            log_guid = m_client.log_my_activity(body=activity_body)
            assert log_guid is not None
            print(f"\n\tLogged activity GUID: {log_guid}")

        except Exception as e:
            print(f"Exception: {e}")
            assert False, f"Test failed with exception: {e}"
        finally:
            if m_client:
                m_client.close_session()


class TestServerClientSearchKeywords:
    """Test class for ServerClient Search Keyword methods"""

    good_platform1_url = "https://localhost:9443"
    good_view_server_2 = "qs-view-server"
    good_user_2 = "erinoverview"
    good_user_2_pwd = "secret"
    test_element_guid = "71e67a50-ced4-40ed-b25e-98142a009604"

    def test_add_search_keyword_to_element(self):
        """Test adding a search keyword to an element"""
        s_client = None
        try:
            s_client = ServerClient(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )
            keyword = f"test-keyword-{int(time.time())}"
            start_time = time.perf_counter()
            response = s_client.add_search_keyword_to_element(
                self.test_element_guid,
                keyword=keyword
            )
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\tResponse was: {response}")
            assert response is not None, "Search keyword not added"
        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Pyegeria exception"
        except Exception as e:
            print(e)
            assert False, f"Unexpected exception: {e}"
        finally:
            if s_client:
                s_client.close_session()

    def test_find_search_keywords(self):
        """Test finding search keywords and printing formatted results"""
        from pyegeria.view.base_report_formats import select_report_spec
        report_spec_name = "Search-Keywords"
        output_formats = ["JSON"]

        s_client = None
        try:
            s_client = ServerClient(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )
            s_client.create_egeria_bearer_token()

            # Verify report spec exists
            # for out_fmt in output_formats:
            #     fmt = select_report_spec(report_spec_name, out_fmt)
            #     if not fmt:
            #         print(f"\nMissing report_spec: '{report_spec_name}' for output_format '{out_fmt}'.")
            #         assert False, f"Missing report_spec: {report_spec_name}"

            search_string = "*"
            for out_fmt in output_formats:
                print(f"\n\t--- Testing find_search_keywords with output_format='{out_fmt}' ---")
                start_time = time.perf_counter()
                response = s_client.find_search_keywords(
                    search_string, output_format=out_fmt, report_spec=report_spec_name, page_size=10
                )
                s_client.create_egeria_bearer_token()
                duration = time.perf_counter() - start_time
                print(f"\n\tDuration was {duration} seconds")

                if out_fmt == "JSON":
                    print(f"\n\tResponse (JSON):\n{json.dumps(response, indent=4)}")
                else:
                    print(f"\n\tResponse ({out_fmt}):\n{response}")

                assert response is not None, f"No search keywords found for format {out_fmt}"

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Pyegeria exception"
        except Exception as e:
            print(e)
            assert False, f"Unexpected exception: {e}"
        finally:
            if s_client:
                s_client.close_session()

    def test_get_search_keyword_by_keyword(self):
        """Test retrieving search keyword by its name"""
        s_client = None
        try:
            s_client = ServerClient(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )
            keyword = "Sustainability"
            start_time = time.perf_counter()
            response = s_client.get_search_keyword_by_keyword(keyword)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\tResponse was: {json.dumps(response, indent=2)}")
            assert response is not None, "Search keyword not retrieved"
        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Pyegeria exception"
        except Exception as e:
            print(e)
            assert False, f"Unexpected exception: {e}"
        finally:
            if s_client:
                s_client.close_session()

    def test_search_keyword_lifecycle(self):
        """Test search keyword lifecycle: add, find, remove"""
        s_client = None
        try:
            s_client = ServerClient(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )
            s_client.create_egeria_bearer_token()

            keyword = f"lifecycle-keyword-{int(time.time())}"

            # 1. Add
            print(f"\n\tAdding keyword '{keyword}'...")
            keyword_guid = s_client.add_search_keyword_to_element(
                self.test_element_guid,
                keyword=keyword
            )
            assert keyword_guid and keyword_guid != 'Search keyword was not created'
            print(f"\tCreated GUID: {keyword_guid}")

            # 2. Find (with formatting)
            print(f"\n\tFinding keyword '{keyword}' with LIST format...")
            response = s_client.find_search_keywords(
                keyword, output_format="LIST", report_spec="Search-Keywords"
            )
            print(f"\tFind Response:\n{response}")
            assert keyword in str(response)

            # 3. Remove
            print(f"\n\tRemoving keyword GUID: {keyword_guid}...")
            s_client.remove_search_keyword(keyword_guid)
            print("\tRemoved.")

        except Exception as e:
            print(e)
            assert False, f"Lifecycle failed: {e}"
        finally:
            if s_client:
                s_client.close_session()


if __name__ == "__main__":
    print("Running ServerClient feedback unit tests...")
