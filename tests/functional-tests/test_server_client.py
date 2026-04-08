"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module is for testing the ServerClient class feedback methods (likes and ratings).
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.
"""

import json
import time

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

disable_ssl_warnings = True


class TestServerClientFeedback:
    """Test class for ServerClient feedback methods (likes and ratings)"""
    
    good_platform1_url = "https://laz.local:9443"
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


if __name__ == "__main__":
    print("Running ServerClient feedback unit tests...")
