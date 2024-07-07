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
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
    ValidMetadataManager
)

# from pyegeria.admin_services import FullServerConfig

disable_ssl_warnings = True


class TestValidMetadataOMVs:
    good_platform1_url = "https://127.0.0.1:9443"
    good_platform2_url = "https://oak.local:9443"
    bad_platform1_url = "https://localhost:9443"

    # good_platform1_url = "https://127.0.0.1:30080"
    # good_platform2_url = "https://127.0.0.1:30081"
    # bad_platform1_url = "https://localhost:9443"

    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    good_user_3 = "peterprofile"
    bad_user_1 = "eviledna"
    bad_user_2 = ""
    good_integ_1 = "fluffy_integration"
    good_server_1 = "simple-metadata-store"
    good_server_2 = "laz_kv"
    good_server_3 = "active-metadata-store"
    good_server_4 = "integration-daemon"
    good_server_5 = "fluffy_kv"
    good_server_6 = "cocoVIew1"
    good_engine_host_1 = "governDL01"
    good_view_server_1 = "view-server"
    good_view_server_2 = "fluffy_view"
    bad_server_1 = "coco"
    bad_server_2 = ""

    def test_setup_valid_metadata_value(self):
        try:
            m_client = ValidMetadataManager(self.good_view_server_1, self.good_platform1_url,
                                            user_id=self.good_user_2)
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            type_name = "Project"
            property_name = "projectHealth"
            body = {
                "displayName": "Abandoned",
                "description": "Who cares?",
                "preferredValue": "Abandoned",
                "dataType": "string",
                "isCaseSensitive": False,
                "isDeprecated": False,
                "additionalProperties": {
                    "colour": "black"
                }
            }

            response = m_client.setup_valid_metadata_value(property_name, type_name, body)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()


    def test_get_all_entity_types(self):
        try:
            m_client = ValidMetadataManager(self.good_view_server_1, self.good_platform1_url,
                                            user_id=self.good_user_2)
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            response = m_client.get_all_entity_types()
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_all_entity_defs(self):
        try:
            m_client = ValidMetadataManager(self.good_view_server_1, self.good_platform1_url,
                                            user_id=self.good_user_2)
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            response = m_client.get_all_entity_defs()
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_all_relationship_defs(self):
        try:
            m_client = ValidMetadataManager(self.good_view_server_1, self.good_platform1_url,
                                            user_id=self.good_user_2)
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            response = m_client.get_all_relationship_defs()
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_all_classification_defs(self):
        try:
            m_client = ValidMetadataManager(self.good_view_server_1, self.good_platform1_url,
                                            user_id=self.good_user_2)
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            response = m_client.get_all_classification_defs()
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_valid_metadata_values(self):
        try:
            m_client = ValidMetadataManager(self.good_view_server_1, self.good_platform1_url,
                                            user_id=self.good_user_2)
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            type_name = "Project"
            property_name = "projectHealth"
            # type_name = None
            # property_name = "stewardTypeName"

            response = m_client.get_valid_metadata_values(property_name, type_name)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_valid_metadata_value(self):
        try:
            m_client = ValidMetadataManager(self.good_view_server_1, self.good_platform1_url,
                                            user_id=self.good_user_2)
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            type_name = "Project"
            property_name = "projectHealth"
            preferred_value = "At Risk"

            response = m_client.get_valid_metadata_value(property_name, type_name, preferred_value)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_valid_relationship_types(self):
        try:
            m_client = ValidMetadataManager(self.good_view_server_1, self.good_platform1_url,
                                            user_id=self.good_user_2)
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            entity_type = "AssetOwner"

            response = m_client.get_valid_relationship_types(entity_type)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_valid_classification_types(self):
        try:
            m_client = ValidMetadataManager(self.good_view_server_1, self.good_platform1_url,
                                            user_id=self.good_user_2)
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            entity_type = "AssetOwner"

            response = m_client.get_valid_classification_types(entity_type)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_typedef_by_name(self):
        try:
            m_client = ValidMetadataManager(self.good_view_server_1, self.good_platform1_url,
                                            user_id=self.good_user_2)
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            entity_type = "AssetOwner"

            response = m_client.get_typedef_by_name(entity_type)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()
