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
from rich.console import Console
from pyegeria import (
    ValidMetadataManager,
    print_basic_exception,
    PyegeriaException,
)

# from pyegeria.admin_services import FullServerConfig

disable_ssl_warnings = True
console = Console(width = 300)

class TestValidMetadataOMVs:
    good_platform1_url = "https://127.0.0.1:9443"
    # good_platform2_url = "https://oak.local:9443"
    # bad_platform1_url = "https://localhost:9443"



    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    good_user_3 = "peterprofile"
    bad_user_1 = "eviledna"
    bad_user_2 = ""
    good_integ_1 = "fluffy_integration"
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

    def test_setup_valid_metadata_value(self):
        try:
            m_client = ValidMetadataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
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
                "additionalProperties": {"colour": "black"},
            }

            response = m_client.setup_valid_metadata_value(
                property_name, type_name, body
            )
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, (list, dict)):
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_setup_valid_metadata_map_name(self):
        try:
            m_client = ValidMetadataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            type_name = "Project"
            property_name = "additionalProperties"
            body = {
                "displayName": "Expected Duration",
                "description": "How long is this project expected to take?",
                "preferredValue": "expectedDuration",
                "dataType": "string",
                "isCaseSensitive": False,

            }

            response = m_client.setup_valid_metadata_map_name(
                property_name, type_name, body
            )
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, (list, dict)):
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_setup_valid_metadata_map_value(self):
        try:
            m_client = ValidMetadataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            type_name = "Project"
            property_name = "additionalProperties"
            map_name = "expectedDuration"
            body = {
                "displayName": "Two Months",
                "description": "The project is expted to last 2 months.",
                "preferredValue": "Two Months",
                "dataType": "string",
                "isCaseSensitive": False,

            }

            response = m_client.setup_valid_metadata_map_value(
                property_name, map_name, type_name, body
            )
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, (list, dict)):
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_valid_metadata_value(self):
        try:
            m_client = ValidMetadataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            type_name = "Project"
            property_name = "projectHealth"
            preferred_value = "Abandoned"

            response = m_client.get_valid_metadata_value(
                property_name, type_name, preferred_value, output_format="LIST", report_spec='Valid-Values' )
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, (list, dict)):
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_valid_metadata_values(self):
        try:
            m_client = ValidMetadataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            type_name = "Project"
            property_name = "projectHealth"
            # type_name = None
            # property_name = "stewardTypeName"

            response = m_client.get_valid_metadata_values(property_name, type_name, output_format="LIST", report_spec='Valid-Values')
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, list | dict):
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nOutput is: " + response)
            assert True

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_valid_metadata_map_values(self):
        try:
            m_client = ValidMetadataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            type_name = "Project"
            property_name = "additionalProperties"
            preferred_value = "1 month"
            map_name = "expectedDuration"
            # type_name = None
            # property_name = "stewardTypeName"

            response = m_client.get_valid_metadata_map_value(property_name, type_name, preferred_value, map_name,
                                                             output_format="DICT", report_spec='Valid-Values')
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, list | dict):
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nOutput is: " + response)
            assert True

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()


    def test_get_all_valid_metadata_values(self):
        try:
            m_client = ValidMetadataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            type_name = "Project"
            property_name = "purposes"
            preferred_value = "1 month"
            map_name = "expectedDuration"
            # type_name = None
            # property_name = "stewardTypeName"

            response = m_client.get_valid_metadata_values(property_name, type_name,
                                                             output_format="DICT", report_spec='Valid-Values')
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, list | dict):
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                console.print("\n\nOutput is: " + response)
            assert True

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()


    def test_validate_metadata_value(self):
        try:
            m_client = ValidMetadataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            type_name = "Project"
            property_name = "purposes"
            actual_value = "marketing"


            response = m_client.validate_metadata_value(property_name, type_name, actual_value = actual_value)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, list | dict):
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nOutput is: " + response)
            else:
                print(response)
            assert True

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_set_consistent_metadata_values(self):
        try:
            m_client = ValidMetadataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            property_name1 = "category"
            property_name2 = "purposes"
            type_name1 = None
            type_name2 = "Project"
            map_name1 = None
            map_name2 = None
            preferred_value1 = "clinical-trial"
            preferred_value2 = "product-verification"


            response = m_client.set_consistent_metadata_values(property_name1, type_name1, map_name1, preferred_value1,
                                                               property_name2, type_name2, map_name2, preferred_value2)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, list | dict):
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nOutput is: " + response)
            else:
                print(response)
            assert True

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_consistent_metadata_values(self):
        try:
            m_client = ValidMetadataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # property_name = "category"
            # type_name = "Project"
            # map_name = None
            # preferred_value = "clinical-trial"
            property_name = 'fileType'
            type_name = 'CSVFile'
            map_name = None
            preferred_value = None
            response = m_client.get_consistent_metadata_values(property_name='fileType',
                                                           type_name='CSVFile',
                                                           map_name=None,
                                                           preferred_value="CSV File")

            # response = m_client.get_consistent_metadata_values(property_name, type_name, map_name, preferred_value)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, list | dict):
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nOutput is: " + response)
            else:
                print(response)
            assert True

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()


    def test_find_spec_property(self):
        try:
            m_client = ValidMetadataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            search_string = "port"

            response = m_client.find_specification_property(search_string)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds for {len(response)} elements")
            if isinstance(response, list | dict):
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nOutput is: " + response)
            else:
                print(response)
            assert True

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

## Entities, TypeDefs etc.

    def test_get_all_entity_types(self):
        try:
            m_client = ValidMetadataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            response = m_client.get_all_entity_types(output_format="JSON", report_spec="Referenceable")
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, (list, dict)):
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            PyegeriaException
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_all_entity_defs(self):
        try:
            m_client = ValidMetadataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            response = m_client.get_all_entity_defs()
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, (list, dict)):
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_all_relationship_defs(self):
        try:
            m_client = ValidMetadataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            response = m_client.get_all_relationship_defs()
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, (list, dict)):
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_all_classification_defs(self):
        try:
            m_client = ValidMetadataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            response = m_client.get_all_classification_defs(output_format="LIST", report_spec="TypeDef")
            duration = time.perf_counter() - start_time
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, (list, dict)):
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                console.print("\n\nGUID is: " + response)
            assert True

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_sub_types(self):
        try:
            m_client = ValidMetadataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            type_name = "Collection"
            response = m_client.get_sub_types(type_name, output_format="MERMAID",report_spec="Common-Mermaid")
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, (list, dict)):
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()




    def test_get_valid_relationship_types(self):
        try:
            m_client = ValidMetadataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            entity_type = "AssetOwner"

            response = m_client.get_valid_relationship_types(entity_type, output_format="DICT",report_spec="Referenceable")
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, list | dict):
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            PyegeriaException
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_valid_classification_types(self):
        try:
            m_client = ValidMetadataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            entity_type = "Asset"

            response = m_client.get_valid_classification_types(entity_type)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, list | dict):
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_typedef_by_name(self):
        try:
            m_client = ValidMetadataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")

            start_time = time.perf_counter()
            entity_type = "Project"

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

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_specification_property_types(self):
        try:
            m_client = ValidMetadataManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")

            start_time = time.perf_counter()

            response = m_client.get_specification_property_types()
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

        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()
