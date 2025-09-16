"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the core Project Manager class and methods
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""

import json
import time
from pydantic import ValidationError
from pyegeria.reference_data import ReferenceDataManager

from pyegeria._exceptions_new import PyegeriaException, print_basic_exception, print_exception_table, \
    print_validation_error, PyegeriaAPIException

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)



disable_ssl_warnings = True


class TestReferenceDataManager:
    good_platform1_url = "https://127.0.0.1:9443"

    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    good_user_3 = "peterprofile"
    bad_user_1 = "eviledna"
    bad_user_2 = ""
    good_integ_1 = "fluffy_integration"
    good_server_1 = "qs-metadata-store"
    good_server_2 = "laz_kv"
    good_server_3 = "active-metadata-store"
    good_server_4 = "integration-daemon"
    good_server_5 = "fluffy_kv"
    good_server_6 = "cocoVIew1"
    good_engine_host_1 = "governDL01"
    good_view_server_1 = "view-server"
    good_view_server_2 = "qs-view-server"
    bad_server_1 = "coco"
    bad_server_2 = ""



    def test_find_vv_definitions(self):
        try:
            p_client = ReferenceDataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            search_string = "*"

            response = p_client.find_valid_value_definitions(
                search_string, output_format="DICT", output_format_set="Valid-Value-Def"
            )
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Found {len(response)} valid value definitions  {type(response)}\n\n")
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            PyegeriaException
        ) as e:
            print_basic_exception()
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
        finally:
            p_client.close_session()

    def test_get_vv_def_by_name(self):
        try:
            p_client = ReferenceDataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            # project_name = "Teddy Bear Drop Foot Clinical Trial IT Setup"
            name = "mpp"
            response = p_client.get_valid_value_definitions_by_name(name)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nResponse is: " + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            p_client.close_session()


    def test_get_vv_def_by_guid(self):
        try:
            p_client = ReferenceDataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            guid = "8fbc6e7f-ac2f-47b6-8a31-f42ea92868ae"

            response = p_client.get_valid_value_definition_by_guid(guid, output_format="DICT", output_format_set="Valid-Value-Def")
            duration = time.perf_counter() - start_time
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"Type of response is {type(response)}")

            if isinstance(response, list| dict):
                print("dict:\n\n")
                print(json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}\n\n")
                print(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            PyegeriaException, PyegeriaAPIException,
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            p_client.close_session()



    def test_create_valid_value_definition(self):
        try:
            p_client = ReferenceDataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties":{
                    "class": "ValidValueDefinitionProperties",
                    "displayName": "Colors",
                    "qualifiedName": f"ValidValueDef::Colors",
                    "description": "List of colors"

                    }
                }
            response = p_client.create_valid_value_definition(body)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            PyegeriaException,
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
        finally:
            p_client.close_session()

    def test_create_valid_value_def_from_template(self):
        try:
            p_client = ReferenceDataManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            anchor_guid = None
            parent_guid = "97bbfe07-6696-4550-bf8b-6b577d25bef0"
            parent_relationship_type_name = "CollectionMembership"
            parent_at_end1 = True
            display_name = "Meow"
            description = "Meow"
            project_type = "Meow"
            is_own_anchor = False
            project_ordering = "NAME"
            order_property_name = None
            body = {
                "class": "TemplateRequestBody",
                "parentGUID": parent_guid,
                "parentRelationshipTypeName": parent_relationship_type_name,
                "parentAtEnd1": True,
                "templateGUID": "c7368217-d013-43cb-9af1-b58e3a491e77",
                "replacementProperties": {
                    "class": "ElementProperties",
                    "propertyValueMap": {
                        "qualifiedName": {
                            "class": "PrimitiveTypePropertyValue",
                            "typeName": "string",
                            "primitiveTypeCategory": "OM_PRIMITIVE_TYPE_STRING",
                            "primitiveValue": f"templated-{display_name}-{time.asctime()}",
                        },
                        "name": {
                            "class": "PrimitiveTypePropertyValue",
                            "typeName": "string",
                            "primitiveTypeCategory": "OM_PRIMITIVE_TYPE_STRING",
                            "primitiveValue": display_name,
                        },
                        "description": {
                            "class": "PrimitiveTypePropertyValue",
                            "typeName": "string",
                            "primitiveTypeCategory": "OM_PRIMITIVE_TYPE_STRING",
                            "primitiveValue": description,
                        },
                    },
                },
            }

            response = p_client.create_valid_value_definition_from_template(body)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            p_client.close_session()

    def test_update_valid_value_def(self):
        try:
            p_client = ReferenceDataManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            guid = "7ab4f441-83e2-4e3f-8b63-2ed3946a5dd7"

            response = p_client.update_valid_value_definition("fill in")
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            p_client.close_session()

    def test_delete_valid_value_definition(self):
        try:
            p_client = ReferenceDataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            guid = "90213557-be19-421c-990d-78a76c30e0f5"

            response = p_client.delete_valid_value_definition(guid)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            print(f"Valid Value GUID: {guid} was deleted")
            assert True

        except (
            PyegeriaException
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        finally:
            p_client.close_session()

