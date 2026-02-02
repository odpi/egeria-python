"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module is for testing the FeedbackManager class and methods.
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
from pyegeria.omvs.feedback_manager import FeedbackManager

disable_ssl_warnings = True


class TestFeedbackManager:
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
    test_element_guid = "49bc1002-1b0a-4194-9305-3607c713726d"

    def test_add_like_to_element(self):
        """Test adding a like to an element"""
        try:
            f_client = FeedbackManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = f_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            
            # Use a known element GUID from your test environment
            # This should be replaced with an actual test element
            # test_element_guid = "test-element-guid-123"
            
            start_time = time.perf_counter()
            response = f_client.add_like_to_element(
                self.test_element_guid,
                is_public=True,
                body={}
            )
            duration = time.perf_counter() - start_time
            
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\tResponse was: {json.dumps(response, indent=2)}")
            
            assert True, "Like added successfully"

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
        except Exception as e:
            print_basic_exception(e)
            assert False, "Unexpected exception"
        finally:
            f_client.close_session()

    def test_add_rating_to_element(self):
        """Test adding a rating to an element"""
        try:
            f_client = FeedbackManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = f_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            
            # test_element_guid = "test-element-guid-123"
            
            # Rating body with star rating and review
            rating_body = {
                "starRating": 5,
                "review": "Excellent element!"
            }
            
            start_time = time.perf_counter()
            response = f_client.add_rating_to_element(
                self.test_element_guid,
                is_public=True,
                body=rating_body
            )
            duration = time.perf_counter() - start_time
            
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\tResponse was: {json.dumps(response, indent=2)}")
            
            assert True, "Rating added successfully"

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
        except Exception as e:
            print_basic_exception(e)
            assert False, "Unexpected exception"
        finally:
            f_client.close_session()

    def test_get_attached_likes(self):
        """Test retrieving likes attached to an element"""
        try:
            f_client = FeedbackManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = f_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            
            test_element_guid = "test-element-guid-123"
            
            start_time = time.perf_counter()
            response = f_client.get_attached_likes(
                test_element_guid,
                start_from=0,
                page_size=50
            )
            duration = time.perf_counter() - start_time
            
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\tResponse was: {json.dumps(response, indent=2)}")
            
            assert True, "Likes retrieved successfully"

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
        except Exception as e:
            print_basic_exception(e)
            assert False, "Unexpected exception"
        finally:
            f_client.close_session()

    def test_get_attached_ratings(self):
        """Test retrieving ratings attached to an element"""
        try:
            f_client = FeedbackManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = f_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            
            test_element_guid = "test-element-guid-123"
            
            start_time = time.perf_counter()
            response = f_client.get_attached_ratings(
                test_element_guid,
                start_from=0,
                page_size=50
            )
            duration = time.perf_counter() - start_time
            
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\tResponse was: {json.dumps(response, indent=2)}")
            
            assert True, "Ratings retrieved successfully"

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
        except Exception as e:
            print_basic_exception(e)
            assert False, "Unexpected exception"
        finally:
            f_client.close_session()

    def test_remove_like_from_element(self):
        """Test removing a like from an element"""
        try:
            f_client = FeedbackManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = f_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            
            test_element_guid = "test-element-guid-123"
            
            start_time = time.perf_counter()
            response = f_client.remove_like_from_element(
                test_element_guid,
                body={}
            )
            duration = time.perf_counter() - start_time
            
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\tResponse was: {json.dumps(response, indent=2)}")
            
            assert True, "Like removed successfully"

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
        except Exception as e:
            print_basic_exception(e)
            assert False, "Unexpected exception"
        finally:
            f_client.close_session()

    def test_remove_rating_from_element(self):
        """Test removing a rating from an element"""
        try:
            f_client = FeedbackManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = f_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            
            test_element_guid = "test-element-guid-123"
            
            start_time = time.perf_counter()
            response = f_client.remove_rating_from_element(
                test_element_guid,
                body={}
            )
            duration = time.perf_counter() - start_time
            
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\tResponse was: {json.dumps(response, indent=2)}")
            
            assert True, "Rating removed successfully"

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
        except Exception as e:
            print_basic_exception(e)
            assert False, "Unexpected exception"
        finally:
            f_client.close_session()


if __name__ == "__main__":
    print("Running FeedbackManager unit tests...")