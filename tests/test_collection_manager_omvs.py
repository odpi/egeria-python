"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module tests the CollectionManager class and methods

A running Egeria environment is needed to run these tests.

"""

import json
import time
from datetime import datetime

from loguru import logger

from rich import print, print_json
from rich.console import Console
from pyegeria.collection_manager import CollectionManager, CollectionProperties
from pyegeria.collection_models import ClassificationProperties
# from pyegeria import EgeriaTech, CollectionManager
from pyegeria.load_config import get_app_config
from pyegeria.logging_configuration import config_logging
from pyegeria._exceptions_new import (
    PyegeriaInvalidParameterException, PyegeriaException, PyegeriaConnectionException, PyegeriaClientException,
    PyegeriaAPIException, PyegeriaUnknownException, PyegeriaNotFoundException,
    PyegeriaUnauthorizedException, print_exception_response, print_exception_table, print_basic_exception,
    print_validation_error
    )
from pydantic import ValidationError
from pyegeria.models import (SearchStringRequestBody, SequencingOrder, FilterRequestBody,
                             NewElementRequestBody, InitialClassifications)

from tests.test_feedback_manager_omvs import password

disable_ssl_warnings = True

console = Console(width=250)

from loguru import logger
app_settings = get_app_config()
config_logging()

class TestCollectionManager:
    good_platform1_url = "https://127.0.0.1:9443"

    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    # good_user_3 = "peterprofile"
    # bad_user_1 = "eviledna"
    # bad_user_2 = ""
    good_server_1 = "simple-metadata-store"
    good_server_2 = "qs-view-server"
    # good_server_3 = "active-metadata-store"
    # good_engine_host_1 = "governDL01"
    good_view_server_1 = "qs-view-server"


    def test_get_attached_collections(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            parent_guid = "f3e4de0e-320a-4b17-8581-b9613fa6cbbb"

            response = c_client.get_attached_collections(parent_guid, output_format="JSON")
            duration = time.perf_counter() - start_time
            print(f"response type is {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"

        finally:
            c_client.close_session()

    def test_find_collections(self):
        try:
            c_client = CollectionManager(self.good_server_2, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            search_string = "Radio"
            classification_name = "DataSpec"
            output_format = "DICT"
            output_format_set = "Collections"

            response = c_client.find_collections(search_string = search_string, classification_names = [classification_name],output_format=output_format, output_format_set=output_format_set)
            duration = time.perf_counter() - start_time
            if response:
                print(f"\nOutput Format: {output_format} and Output Format Set: {output_format_set}")
                print(f"\n\tNumber elements {len(response)} & Duration was {duration:.2f} seconds")
                if type(response) is list:
                    print(f"Found {len(response)} collections {type(response)}\n\n")
                    print_json("\n\n" + json.dumps(response, indent=4))
                elif type(response) is str:
                    console.print(response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)

        finally:
            c_client.close_session()

    def test_find_collections_w_body(self):

        try:
            c_client = CollectionManager(self.good_server_2, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            # classification_name = "DataSharingAgreement"
            # classification_name = "ConnectorTypeDirectory"
            classification_name = ["DataSpec", "DataDictionary"]
            out_struct = {
                    "heading": "General Agreement Information",
                    "description": "Attributes generic to all Agreements.",
                    "aliases": [],
                    "formats": [{"columns": [
                        {'name': 'Name', 'key': 'display_name'},
                        {'name': 'Qualified Name', 'key': 'qualified_name', 'format': True},
                        {'name': 'Super Category', 'key': 'category'},
                        {'name': 'My Description', 'key': 'description', 'format': True},
                        {'name': "Classifications", 'key': 'classifications'},
                        {'name': 'Members', 'key': 'members', 'format': True},
                        {'name': 'CreatedBy Meow', 'key': 'created_by'},
                        {'name': 'GUID', 'key': 'GUID'},
                        ],
                        "types": ["ALL"]
                        },
                        ],
                    "annotations": {"wikilinks": ["[[Agreements]]", "[[Egeria]]"]}
                }
            search_string = "*"
            body = {
                "class": "SearchStringRequestBody",
                "searchString": search_string,
                "ignoreCase": True,
                "asOfTime": None,
                "effectiveTime": None,
                "forLineage": False,
                "forDuplicateProcessing": False,
                "limitResultsByStatus": [],
                "sequencingOrder": "PROPERTY_ASCENDING",
                "sequencingProperty": "qualifiedName",
                }

            response = c_client.find_collections(body=body, output_format="DICT", output_format_set="Collections")
            duration = time.perf_counter() - start_time

            print(f"\n\tNumber elements {len(response)} & Duration was {duration:.2f} seconds")
            if type(response) is list:
                print(f"Found {len(response)} collections {type(response)}\n\n")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                console.print(response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_basic_exception(e)
            # assert False, "Invalid request"
        except (AttributeError, UnboundLocalError) as e:
            logger.error(e)
            # assert False
        finally:
            c_client.close_session()

    def test_find_collections_pyd(self):

        try:
            c_client = CollectionManager(self.good_server_2, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            # classification_name = "DataSharingAgreement"

            classification_name = "Folder"
            out_struct = {
                    "heading": "General Agreement Information",
                    "description": "Attributes generic to all Agreements.",
                    "aliases": [],
                    "formats": [{"columns": [
                        {'name': 'Name', 'key': 'display_name'},
                        {'name': 'Qualified Name', 'key': 'qualified_name', 'format': True},
                        {'name': 'Super Category', 'key': 'category'},
                        {'name': 'My Description', 'key': 'description', 'format': True},
                        {'name': "Classifications", 'key': 'classifications'},
                        {'name': 'Members', 'key': 'members', 'format': True},
                        {'name': 'CreatedBy Meow', 'key': 'created_by'},
                        {'name': 'GUID', 'key': 'GUID'},
                        ],
                        "types": ["ALL"]
                        },
                        ],
                    "annotations": {"wikilinks": ["[[Agreements]]", "[[Egeria]]"]}
                }
            search_string = None
            request_body = SearchStringRequestBody(
                class_ = "SearchStringRequestBody",
                search_string=search_string,
                ignore_case=True,
                as_of_time=None,
                sequencing_order=SequencingOrder.CREATION_DATE_OLDEST,
                include_only_classified_elements= [classification_name]

                )

            response = c_client.find_collections_w_body(request_body, output_format="DICT", output_format_set="Collections")
            duration = time.perf_counter() - start_time

            print(f"\n\tNumber elements {len(response)} & Duration was {duration:.2f} seconds")
            if type(response) is list:
                print(f"Found {len(response)} collections {type(response)}\n\n")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                console.print(response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_basic_exception(e)
            # assert False, "Invalid request"
        except (AttributeError, UnboundLocalError) as e:
            logger.error(e)
        except ValidationError as e:
            print(e)
            # assert False
        finally:
            c_client.close_session()


    def test_get_collection_by_name(self):
        try:
            c_client = CollectionManager(self.good_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_name = "Chemicals"

            response = c_client.get_collections_by_name(collection_name, output_format="DICT", output_format_set="Collections" )
            duration = time.perf_counter() - start_time
            print(f"Type is {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is list:
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)

        finally:
            c_client.close_session()

    def test_get_collection_by_name_pyd(self):
        try:
            c_client = CollectionManager(self.good_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_name = "Chemicals"
            filter_body = FilterRequestBody(
                class_ = "FilterRequestBody",
                filter = collection_name,
                include_only_classified_elements=None
                )
            response = c_client.get_collections_by_name(body=filter_body, output_format="DICT",
                                                        output_format_set="Collections")
            duration = time.perf_counter() - start_time
            print(f"Type is {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is list:
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaInvalidParameterException, PyegeriaConnectionException, PyegeriaAPIException,
                PyegeriaUnknownException,) as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            c_client.close_session()

    def test_get_collections_by_type(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            category = "Radios"
            classification_name = None

            response = c_client.get_collections_by_category(category, classification_name, output_format="DICT")
            duration = time.perf_counter() - start_time
            if response:
                print(f"\n\tNumber elements was {len(response)} & Duration was {duration:.2f} seconds")
                if type(response) is list:
                    print_json(json.dumps(response, indent=4))
                elif type(response) is tuple:
                    print(f"Type is {type(response)}")
                    print_json("\n\n" + json.dumps(response, indent=4))
                elif type(response) is str:
                    print("\n\nGUID is: " + response)
            assert True

        except PyegeriaException as e:
            print_basic_exception(e)
            # assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
        finally:
            c_client.close_session()

    def test_get_collection_by_guid(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "ed0507a0-c957-48ba-80af-2b39951ef315"
            element_type = "Agreement"
            response = c_client.get_collection_by_guid(collection_guid, element_type, output_format="DICT")
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"Type of response is {type(response)}")

            if isinstance(response, (dict, list)):
                print("dict:\n\n")
                print_json(json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}\n\n")
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaException, AssertionError) as e:
           # pass
            print_exception_table(e)
            # assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
        finally:
            if hasattr(self, 'c_client'):
                c_client.close_session()

    def test_get_collection_graph(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "a9e298b6-b8ce-4e2c-abd6-c73b3428f061"

            response = c_client.get_collection_graph(collection_guid, output_format="DICT")
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"Type of response is {type(response)}")

            if isinstance(response, (dict, list)):
                print("dict:\n\n")
                print_json(json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}\n\n")
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"

        finally:
            c_client.close_session()

    def test_get_collection_graph_w_body(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "d4adc047-9005-471f-b2a1-e86201961e0b"
            body = {
                "class": "ResultsRequestBody", "effectiveTime": None, "limitResultsByStatus": ["ACTIVE"],
                "asOfTime": None, "sequencingOrder": "CREATION_DATE_RECENT", "sequencingProperty": ""
                }

            response = c_client.get_collection_graph(collection_guid, output_format="MERMAID")
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"Type of response is {type(response)}")

            if isinstance(response, (dict, list)):
                print("dict:\n\n")
                # print_json(response[0])
                print_json(json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}\n\n")
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except PyegeriaException as e:
            print_exception_table(e)
            # assert False, "Invalid request"

        finally:
            c_client.close_session()

    def test_create_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            anchor_guid = None
            parent_guid = None
            parent_relationship_type_name = "CollectionMembership"
            parent_at_end1 = True
            display_name = "Ham Radio collection"
            description = "Another collection of my Elecraft radios"
            classification_name = "Folder"
            collection_type = "Hobby Collection"
            is_own_anchor = True

            response = c_client.create_collection(display_name, description,
                                                  collection_type, classification_name, None,
               )
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            # assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_create_collection_w_body(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            display_name = "Flex Radios"
            description = "Radios made by Flex Radio"
            classification_name = "Folder"
            q_name = c_client.__create_qualified_name__(classification_name, display_name, version_identifier="")
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "initialClassifications": {
                    classification_name : {
                      "class" :  "ClassificationProperties"
                    }
                  },
                "properties": {
                    "class": "CollectionProperties",
                    "displayName": display_name,
                    "qualifiedName": q_name,
                    "description": "A collection of my Flex radios",
                    "category": "Radios"
                    },
                }
            response = c_client.create_collection_w_body( body=body)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print(e)
        finally:
            c_client.close_session()


    def test_create_collection_w_body_param(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            display_name = "Kenwood Radios"
            description = "Radios made by Kenwood"
            classification_name = "Folder"

            response = c_client.create_collection_w_body(display_name, description, category="Radios",
                                                         classification_name =classification_name)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print(e)
        finally:
            c_client.close_session()

    def test_create_collection_w_pyd(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            q_name = c_client.__create_qualified_name__("Collection", "Yaesu Radios", version_identifier="")
            body = {
                "class": "NewElementRequestBody",
                "is_own_anchor": True,
                "initialClassifications": {
                    "folder" : {
                      "class" :  "ClassificationProperties"
                    }
                  },
                "properties": {
                    "class": "CollectionProperties",
                    "displayName": "Yaesu Radios",
                    "qualifiedName": q_name,
                    "description": "A collection of my Yaesu radios",
                    "category": "Radios"
                    },
            }
            validated_body = NewElementRequestBody.model_validate(body)
            response = c_client.create_collection_w_body(body=validated_body)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaClientException,  PyegeriaException, PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print(e)
        finally:
            c_client.close_session()

    def test_create_root_collection(self):
        try:
            c_client = CollectionManager('qs-view-server', self.good_platform1_url, user_id=self.good_user_2,
                user_pwd="secret", )

            # token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            token = c_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            anchor_guid = None
            parent_guid = None
            parent_relationship_type_name = None
            parent_at_end1 = None
            display_name = "Base Collection"
            description = "This is the root catalog Testing"
            collection_type = "Test Data"
            is_own_anchor = True
            qualified_name = None
            category = "Test Data"

            response = c_client.create_root_collection(display_name, description, category)

            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_create_folder_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            anchor_guid = None
            parent_guid = None
            parent_relationship_type_name = "CollectionMembership"
            parent_at_end1 = True
            display_name = "Dans Artifacts"
            description = ("This folder contains Dans artifacts")
            collection_type = "User Data"
            is_own_anchor = True


            response = c_client.create_folder_collection(display_name, description)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_create_data_spec_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            display_name = "My Clinical Trial Test Data Spec"
            description = "Test- Clinical Trials Specification"
            category = "Test Data Specification"
            is_own_anchor = True

            response = c_client.create_data_spec_collection(display_name, description,
                                category=category)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            # print_exception_table(e)
            print_basic_exception(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_create_data_spec_collection2(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            display_name = "Clinical Trial Data Spec2"
            description = "Clinical Trials Specification"
            collection_type = "Data Specification"

            response = c_client.create_data_spec_collection(display_name, description,
                collection_type)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_create_data_dictionary_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            anchor_guid = None
            parent_guid = None
            parent_relationship_type_name = "CollectionMembership"
            # parent_relationship_type_name = None
            parent_at_end1 = True
            # parent_at_end1 = None
            display_name = "My Other Dictionary"
            description = "My very own data dictionary"
            category = "Data Dictionary"

            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "DataDictionaryProperties",
                    "displayName": display_name,
                    "qualifiedName": "DataDict::My Other Dictionary",
                    "description": "My very own data dictionary",
                    category: "Data Dictionary",
                    }
                }

            response = c_client.create_data_dictionary_collection(display_name, description,
                                                                  category=category, body=body)

            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)

        finally:
            c_client.close_session()


    #
    # def test_create_name_space_collection(self):
    #     try:
    #         c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )
    #
    #         token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
    #         start_time = time.perf_counter()
    #         anchor_guid = None
    #         parent_guid = None
    #         parent_relationship_type_name = "CollectionMembership"
    #         # parent_relationship_type_name = None
    #         parent_at_end1 = True
    #         # parent_at_end1 = None
    #         display_name = "Austria"
    #         description = "A namespace collection"
    #         collection_type = "Namespaces"
    #         is_own_anchor = True
    #         anchor_scope_guid = None
    #         qualified_name = c_client.__create_qualified_name__("DataDict", display_name)
    #
    #         response = c_client.create_name_space_collection(display_name, description, qualified_name, is_own_anchor,
    #             anchor_guid, parent_guid, collection_type=collection_type)
    #
    #         duration = time.perf_counter() - start_time
    #         # resp_str = json.loads(response)
    #         print(f"\n\tDuration was {duration} seconds\n")
    #         if type(response) is dict:
    #             print_json(json.dumps(response, indent=4))
    #         elif type(response) is str:
    #             print("\n\nGUID is: " + response)
    #         assert True
    #
    #     except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
    #         print_exception_table(e)
    #         assert False, "Invalid request"
    #     finally:
    #         c_client.close_session()
    #
    #
    # def test_create_context_event_collection(self):
    #     try:
    #         c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )
    #
    #         token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
    #         start_time = time.perf_counter()
    #         anchor_guid = None
    #         parent_guid = None
    #         parent_relationship_type_name = "CollectionMembership"
    #         # parent_relationship_type_name = None
    #         parent_at_end1 = True
    #         # parent_at_end1 = None
    #         display_name = "Audits"
    #         description = "Testing context events"
    #         collection_type = "Audit"
    #         is_own_anchor = True
    #         anchor_scope_guid = None
    #         qualified_name = c_client.__create_qualified_name__("DataDict", display_name)
    #
    #         response = c_client.create_context_event_collection(display_name, description, qualified_name,
    #             is_own_anchor, anchor_guid, parent_guid, None, True, collection_type, anchor_scope_guid, )
    #
    #         duration = time.perf_counter() - start_time
    #         # resp_str = json.loads(response)
    #         print(f"\n\tDuration was {duration} seconds\n")
    #         if type(response) is dict:
    #             print_json(json.dumps(response, indent=4))
    #         elif type(response) is str:
    #             print("\n\nGUID is: " + response)
    #         assert True
    #
    #     except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
    #         print_exception_table(e)
    #         assert False, "Invalid request"
    #     finally:
    #         c_client.close_session()
    #
    # def test_create_event_set_collection(self):
    #     try:
    #         c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )
    #
    #         token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
    #         start_time = time.perf_counter()
    #         anchor_guid = None
    #         parent_guid = None
    #         parent_relationship_type_name = "CollectionMembership"
    #         # parent_relationship_type_name = None
    #         parent_at_end1 = True
    #         # parent_at_end1 = None
    #         display_name = "Events collection"
    #         description = "Testing  events"
    #         collection_type = "Events"
    #         is_own_anchor = True
    #         anchor_scope_guid = None
    #         qualified_name = c_client.__create_qualified_name__("DataDict", display_name)
    #
    #         response = c_client.create_event_set_collection(display_name, description, qualified_name, is_own_anchor,
    #             anchor_guid, parent_guid, parent_relationship_type_name, parent_at_end1, collection_type,
    #             anchor_scope_guid, )
    #
    #         duration = time.perf_counter() - start_time
    #         # resp_str = json.loads(response)
    #         print(f"\n\tDuration was {duration} seconds\n")
    #         if type(response) is dict:
    #             print_json(json.dumps(response, indent=4))
    #         elif type(response) is str:
    #             print("\n\nGUID is: " + response)
    #         assert True
    #
    #     except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
    #         print_exception_table(e)
    #         assert False, "Invalid request"
    #     finally:
    #         c_client.close_session()
    #
    #
    #
    # def test_create_naming_standard_ruleset_collection(self):
    #     try:
    #         c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )
    #
    #         token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
    #         start_time = time.perf_counter()
    #         anchor_guid = None
    #         parent_guid = None
    #         parent_relationship_type_name = "CollectionMembership"
    #         # parent_relationship_type_name = None
    #         parent_at_end1 = True
    #         # parent_at_end1 = None
    #         display_name = "ruleset1"
    #         description = "a first ruleset"
    #         collection_type = "hoyle"
    #         is_own_anchor = True
    #         anchor_scope_guid = None
    #         qualified_name = c_client.__create_qualified_name__("DataDict", display_name)
    #
    #         response = c_client.create_naming_standard_ruleset_collection(display_name, description, qualified_name,
    #             is_own_anchor, anchor_guid, parent_guid, None, True, collection_type, anchor_scope_guid, )
    #
    #         duration = time.perf_counter() - start_time
    #         # resp_str = json.loads(response)
    #         print(f"\n\tDuration was {duration} seconds\n")
    #         if type(response) is dict:
    #             print_json(json.dumps(response, indent=4))
    #         elif type(response) is str:
    #             print("\n\nGUID is: " + response)
    #         assert True
    #
    #     except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
    #         print_exception_table(e)
    #         assert False, "Invalid request"
    #     finally:
    #         c_client.close_session()
    #

    def test_create_collection_from_template(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            anchor_guid = None
            parent_guid = None
            parent_relationship_type_name = "CollectionMembership"
            parent_at_end1 = True
            display_name = "Hobby Collections"
            description = "Meow"
            collection_type = "Meow"
            is_own_anchor = False

            body = {
                "class": "TemplateRequestBody",
                "templateGUID": "d4dca087-6494-460a-9a8f-e4c788b41638",
                "replacementProperties": {
                    "class": "ElementProperties",
                    "propertyValueMap": {
                        "qualifiedName": {
                            "class": "PrimitiveTypePropertyValue", "typeName": "string",
                            "primitiveTypeCategory": "OM_PRIMITIVE_TYPE_STRING",
                            "primitiveValue": f"templated-{display_name}",
                            },
                        "displayName": {
                            "class": "PrimitiveTypePropertyValue", "typeName": "string",
                            "primitiveTypeCategory": "OM_PRIMITIVE_TYPE_STRING", "primitiveValue": display_name,
                            },
                        },
                    },
                }

            response = c_client.create_collection_from_template(body)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            # print_exception_table(e)
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            # print(json.dumps(e.errors(), indent=2))
            print_validation_error(e)
        finally:
            c_client.close_session()

    def test_create_digital_product(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            parent_guid = "5d4fec06-f033-4743-bc50-06e7fd2eef10"
            parent_relationship_type_name = "CollectionMembership"
            display_name = "Sentinel2 Raw Data"
            description = "Raw Sentinel 1 data"
            collection_type = "Data Product Marketplace"

            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "DigitalProductProperties",
                    "qualifiedName": f"DigitalProduct::{collection_type}::{display_name}",
                    "displayName": "Land Use Classifications",
                    "productType": "Periodic Delta",
                    "identifier": "sent1",
                    "productName": "My sentinel 1",
                    "serviceLife": "While budgets last",
                    "description": description,
                    "introductionDate": "2023-12-31",
                    "maturity": "Nacent",
                    "currentVersion": "V.5",
                    "nextVersionDate": "2025-08-01",
                    "withdrawDate": "2030-01-01",
                    },
                }
            response = c_client.create_digital_product(body)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaAPIException,PyegeriaInvalidParameterException, PyegeriaUnauthorizedException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_update_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "c18a75c2-ce4f-461f-b710-43ef9cee60ab"
            new_desc = " Where audit events are kept"
            collection_type = "Audits"
            response = c_client.update_collection(collection_guid, collection_type=collection_type,
                                                  description=new_desc)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_get_collection_members(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = '4300c161-25e6-4d10-a47e-3df2b143e607'
            name = "Teddy Bear Drop Foot Data Fields"
            response = c_client.get_collection_members(collection_name = name, output_format="DICT")
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tNumber of elements returned was {len(response)} & Duration was {duration:.2f} seconds\n")
            if type(response) is list:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nResult is: " + response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_basic_exception(e)
            # assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_attach_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "fbcfdb5a-5d32-4f1e-b85b-0f67ff43275e"
            element_guid = "5c8e1430-8944-466e-90ba-245e861d1285"

            c_client.attach_collection(collection_guid, element_guid, "Clinical Data Storage",
                "Clinical data storage for OAK Dene", None, watch_resources=True, make_anchor=False, )
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")

            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_detach_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "d13a8a6e-e35c-4c6e-bb11-cf4f86faeac5"
            element_guid = "5974c163-d097-4f65-922b-e8ac8193197e"

            response = c_client.detach_collection(collection_guid, element_guid)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is list:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_delete_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "f1fb7aa3-5447-4e8b-88d2-b3b9511807b4"
            response = c_client.delete_collection(collection_guid, cascade=True)
            duration = time.perf_counter() - start_time
            print("\n\nCollection deleted successfully")
            print(f"\n\tDuration was {duration} seconds")

            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_delete_collection_type(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            # category = "Digital Product"
            # category = "Product Catalog"
            # category = "Digital Product Marketplace"
            # category = "Data Spec Collection"
            # category = "Medical Data"
            # category = "Data Product Marketplace"
            collection_type = "Test"

            response = c_client.get_collections_by_type(collection_type, '*')
            if type(response) is list:
                count = len(response)
                print(f"\n\nAbout to delete {count} collections")
                print_json(json.dumps(response, indent=4))
                for member in response:
                    try:
                        member_guid = member["elementHeader"]["guid"]
                        member_name = member["properties"]["name"]
                        print(f"\n about to delete member {member_name} of count members")
                        c_client.delete_collection(member_guid, cascade=True)
                    except (PyegeriaInvalidParameterException) as e:
                        print(e)
                        print("Continueing")
                        continue
                duration = time.perf_counter() - start_time
                # resp_str = json.loads(response)
                print(f"\n\tDuration was {duration} seconds\n")
                response = c_client.get_collections_by_type(collection_type, '*')

            elif type(response) is str:
                print("No members found")
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_add_to_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "dca6f6d0-ad6a-4c75-a8b3-b1ce465af02a"
            element_guid = "32b53e8e-7b2f-467b-a3a9-3f55852f4919"
            body = {
                "class": "RelationshipRequestBody", "properties": {
                    "class": "CollectionMembershipProperties", "membershipRationale": "test purposes",
                    "expression": "just testing", "confidence": 50, "status": "PROPOSED", "userDefinedStatus": "Maybe",
                    "steward": "peterprofile", "stewardTypeName": "a type name?",
                    "stewardPropertyName": "a property name?", "source": "clinical data", "notes": "just an experiment"
                    }
                }

            c_client.add_to_collection(collection_guid, element_guid, body)

            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")

            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_remove_from_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "dca6f6d0-ad6a-4c75-a8b3-b1ce465af02a"
            element_guid = "32b53e8e-7b2f-467b-a3a9-3f55852f4919"

            c_client.remove_from_collection(collection_guid, element_guid, None)

            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")

            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_get_member_list(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            guid = 'd4adc047-9005-471f-b2a1-e86201961e0b'
            # name = "Earth Observation Data Collection"
            # name = "Land Use Classification"
            name = "Sentinel 2"

            # response = c_client.get_member_list(collection_=name)
            response = c_client.get_member_list(collection_guid=guid)
            duration = time.perf_counter() - start_time
            if type(response) is list:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nResponse is: " + response)
            else:
                print("\n\nNo members found")
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            # print(f"Member List is: {response}")
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_update_collection_membership(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "fbcfdb5a-5d32-4f1e-b85b-0f67ff43275e"
            element_guid = "5c8e1430-8944-466e-90ba-245e861d1285"

            body = {
                "class": "CollectionMembershipProperties", "membershipRationale": "xxx", "expression": "convenience",
                "confidence": 100, "status": "PROPOSED", "userDefinedStatus": "Validation required",
                "source": "archive", "notes": "arbitrary notes",
                }
            c_client.update_collection_membership(collection_guid, element_guid, body, replace_all_props=False)

            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds\n")
            # print(f"Member List is: {response}")
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_sample_setup(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            # Create a Data Products Root collection
            anchor_guid = None
            parent_guid = None
            parent_relationship_type_name = None
            parent_at_end1 = False
            anchor_scope_guid = None
            display_name = "Digital Insights Root"
            description = "This is the root catalog for digital products"
            collection_type = "Test"
            is_own_anchor = True

            root = c_client.create_root_collection(display_name, description, is_own_anchor,
                collection_type=collection_type)

            # Create first folder for Agriculture Insights
            parent_guid = root
            parent_relationship_type_name = "CollectionMembership"
            display_name = "Agriculture Insights Collection"
            description = "A folder for agricultural insights data product collections"
            collection_type = "Digital Insights Marketplace"

            folder1 = c_client.create_folder_collection(display_name, description, True, None, parent_guid,
                parent_relationship_type_name, True, collection_type, None, None, None, None, None)
            print(f"\n\n created a folder `{display_name}` with guid {folder1}")
            # create second folder for Earth Observations
            display_name = "Earth Observation Data Collection"
            description = "A folder for Earth Observation data product collections"
            parent_guid = root
            qualified_name = c_client.__create_qualified_name__("Folder", display_name)

            folder2 = c_client.create_folder_collection(display_name, description, qualified_name, True, None,
                parent_guid, parent_relationship_type_name, True, collection_type, None, None, None, None, )
            print(f"\n\n created a folder `{display_name}` with guid {folder2}")

            # create a digital product, child of folder 1, for Land Use products
            parent_guid = folder1
            parent_relationship_type_name = "CollectionMembership"
            display_name = "Land Use Classification"
            description = "Land use classification assets"
            collection_type = "Test"
            classification_name = "DataDictionary"
            body_3 = {
                "class": "NewElementRequestBody", "isOwnAnchor": True, "parentGUID": parent_guid,
                "parentRelationshipTypeName": parent_relationship_type_name, "parentAtEnd1": True, "properties": {
                    "class": "CollectionProperties", "qualifiedName": f"{classification_name}::{display_name}",
                    "name": display_name, "description": description, "collectionType": collection_type,
                    "collectionOrdering": "DATE_CREATED",
                    }
                }

            folder3 = c_client.create_collection_w_body(body_3, classification_name)
            print(f"\n\n created a collection `{display_name}` with guid {folder3}")

            # create a fourth collection, a digital product, child of folder 2, for Landsat 8  # parent_guid =
            # folder2  # display_name = "Landsat 8"  # description = "Landsat 8 data products"  #  # body_4 = {  #
            # "class": "NewDigitalProductRequestBody",  #     "isOwnAnchor": True,  #     "parentGUID": parent_guid,
            #     "parentRelationshipTypeName": parent_relationship_type_name,  #     "parentAtEnd1": True,
            #     "collectionProperties": {  #         "class": "CollectionProperties",  #         "qualifiedName":
            #     f"{classification_name}-{display_name}-{time.asctime()}",  #         "name": display_name,
            #         "description": description,  #         "collectionType": category,  #
            #         "collectionOrdering": "DATE_CREATED",  #     },  #     "digitalProductProperties": {  #
            #         "class": "DigitalProductProperties",  #         "productStatus": "ACTIVE",  #
            #         "productName": "Landsat 8 Imagery",  #         "productType": "Geospatial Data Assets",
            #         "description": description,  #         "introductionDate": "2024-01-01",  #         "maturity":
            #         "Mature",  #         "serviceLife": "3 years",  #         "currentVersion": "V1.5",
            #         "nextVersion": "2024-06-01",  #         "withdrawDate": "2030-01-01",  #
            #         "additionalProperties": {  #             "thought_id": "a guid",  #             "license":
            #         "cc-by-sa",  #         },  #     },  # }  # folder4 = c_client.create_digital_product(body_4)
            # print(f"\n\n created a collection with guid {folder4}")  #  # # Now create a 5th collection for
            # sentinel 2 data  # parent_guid = folder2  # display_name = "Sentinel 2"  # description = "Sentinel 2
            # products"  # parent_relationship_type_name = "CollectionMembership"  # category = "Digital
            # Product Marketplace"  #  # folder5 = c_client.create_folder_collection(  #     None,
            #     parent_guid,  #     parent_relationship_type_name,  #     True,  #     display_name,
            #     description,  #     category,  #     True,  #     "DATE_CREATED",  #     None,
            # )  # # Create a DigitalProduct for Level-1B  # parent_guid = folder5  # display_name = "Sentinel 2 -
            # Level 1B"  # description = "Level 1B of Sentinel 2"  #  # body_6 = {  #     "class":
            # "NewDigitalProductRequestBody",  #     "anchor_guid": parent_guid,  #     "isOwnAnchor": False,
            #     "parentGUID": parent_guid,  #     "parentRelationshipTypeName": parent_relationship_type_name,
            #     "parentAtEnd1": True,  #     "collectionProperties": {  #         "class": "CollectionProperties",
            #         "qualifiedName": f"{classification_name}-{display_name}-{time.asctime()}",  #         "name":
            #         display_name,  #         "description": description,  #         "collectionType":
            #         category,  #         "collectionOrdering": "DATE_CREATED",  #     },
            #     "digitalProductProperties": {  #         "class": "DigitalProductProperties",  #
            #     "productStatus": "ACTIVE",  #         "productName": "Sentinel 2 - Level 1B",  #
            #     "productType": "Geospatial Data Assets",  #         "description": description,  #
            #     "introductionDate": "2024-01-01",  #         "maturity": "Mature",  #         "serviceLife": "3
            #     years",  #         "currentVersion": "V1.5",  #         "nextVersion": "2024-06-01",
            #         "withdrawDate": "2030-01-01",  #         "additionalProperties": {  #             "thought_id":
            #         "a guid",  #             "license": "cc-by-sa",  #         },  #     },  # }  # folder6 =
            #         c_client.create_digital_product(body_6)  # print(f"\n\n created a collection with guid {
            #         folder6}")  #  # # now lets create a digital product for - Level - 1c  # parent_guid = folder5
            # display_name = "Sentinel 2 - Level 1C"  # description = "Level 1C of Sentinel 2"  # body_7 = {  #
            # "class": "NewDigitalProductRequestBody",  #     "anchor_guid": parent_guid,  #     "isOwnAnchor":
            # False,  #     "parentGUID": parent_guid,  #     "parentRelationshipTypeName":
            # parent_relationship_type_name,  #     "parentAtEnd1": True,  #     "collectionProperties": {  #
            # "class": "CollectionProperties",  #         "qualifiedName": f"{classification_name}-{display_name}-{
            # time.asctime()}",  #         "name": display_name,  #         "description": description,
            #         "collectionType": category,  #         "collectionOrdering": "DATE_CREATED",  #     },
            #     "digitalProductProperties": {  #         "class": "DigitalProductProperties",  #
            #     "productStatus": "ACTIVE",  #         "productName": "Sentinel 2 - Level 1B",  #
            #     "productType": "Geospatial Data Assets",  #         "description": description,  #
            #     "introductionDate": "2024-01-01",  #         "maturity": "Mature",  #         "serviceLife": "3
            #     years",  #         "currentVersion": "V1.5",  #         "nextVersion": "2024-06-01",
            #         "withdrawDate": "2030-01-01",  #         "additionalProperties": {  #             "thought_id":
            #         "a guid",  #             "license": "cc-by-sa",  #         },  #     },  # }  # folder7 =
            #         c_client.create_digital_product(body_7)  # print(f"\n\n created a collection with guid {
            #         folder7}")  # assert True  #  # # now lets create a digital product for - Level - 2A  #
            #         parent_guid = folder5  # display_name = "Sentinel 2 - Level 2A"  # description = "Level 2A of
            #         Sentinel 2"  # body_8 = {  #     "class": "NewDigitalProductRequestBody",  #     "anchor_guid":
            #         parent_guid,  #     "isOwnAnchor": False,  #     "parentGUID": parent_guid,
            #     "parentRelationshipTypeName": parent_relationship_type_name,  #     "parentAtEnd1": True,
            #     "collectionProperties": {  #         "class": "CollectionProperties",  #         "qualifiedName":
            #     f"{classification_name}-{display_name}-{time.asctime()}",  #         "name": display_name,
            #         "description": description,  #         "collectionType": category,  #
            #         "collectionOrdering": "DATE_CREATED",  #     },  #     "digitalProductProperties": {  #
            #         "class": "DigitalProductProperties",  #         "productStatus": "ACTIVE",  #
            #         "productName": "Sentinel 2 - Level 1B",  #         "productType": "Geospatial Data Assets",
            #         "description": description,  #         "introductionDate": "2024-01-01",  #         "maturity":
            #         "Mature",  #         "serviceLife": "3 years",  #         "currentVersion": "V1.5",
            #         "nextVersion": "2024-06-01",  #         "withdrawDate": "2030-01-01",  #
            #         "additionalProperties": {  #             "thought_id": "a guid",  #             "license":
            #         "cc-by-sa",  #         },  #     },  # }  # folder8 = c_client.create_digital_product(body_8)
            # print(f"\n\n created a collection with guid {folder8}")  # assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_delete_all_collections(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            search_string = "*"

            response = c_client.find_collections(search_string, None, True, False, ignore_case=False)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Found {len(response)} collections {type(response)}\n\n")
                for collection in response:
                    c_client.delete_collection(collection["elementHeader"]["guid"], cascade=True)
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"

        finally:
            c_client.close_session()

    #
    # Agreements
    #
    def test_create_agreement(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            anchor_guid = None
            parent_guid = None
            parent_relationship_type_name = "CollectionMembership"
            # parent_relationship_type_name = None
            parent_at_end1 = True
            # parent_at_end1 = None
            display_name = "No Biting"
            description = "Pets"
            identifier = "who me"
            collection_type = "Pets"
            is_own_anchor = True
            anchor_scope_guid = None
            qualified_name = c_client.__create_qualified_name__("Agreement", display_name)

            body = {
                "class": "NewElementRequestBody", "anchorGUID": anchor_guid, "isOwnAnchor": is_own_anchor,
                "parentGUID": parent_guid, "parentRelationshipTypeName": parent_relationship_type_name,
                "parentAtEnd1": parent_at_end1, "properties": {
                    "class": "AgreementProperties", "name": display_name, "qualifiedName": qualified_name,
                    "description": description, "identifier": identifier, "collectionType": collection_type
                    },
                }

            response = c_client.create_agreement(body)

            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_create_data_sharing_agreement(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            anchor_guid = None
            parent_guid = None
            parent_relationship_type_name = "CollectionMembership"
            # parent_relationship_type_name = None
            parent_at_end1 = True
            # parent_at_end1 = None
            display_name = "Fur balls per day"
            description = "Pets"
            identifier = "who me"
            collection_type = "Pets"
            is_own_anchor = True
            anchor_scope_guid = None
            qualified_name = c_client.__create_qualified_name__("Agreement", display_name)

            body = {
                "class": "NewElementRequestBody", "anchorGUID": anchor_guid, "isOwnAnchor": is_own_anchor,
                "parentGUID": parent_guid, "parentRelationshipTypeName": parent_relationship_type_name,
                "parentAtEnd1": parent_at_end1, "properties": {
                    "class": "AgreementProperties", "name": display_name, "qualifiedName": qualified_name,
                    "description": description, "identifier": identifier, "collectionType": collection_type
                    },
                }

            response = c_client.create_data_sharing_agreement(body)

            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()
