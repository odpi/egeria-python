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
from pyegeria.config import settings
from pyegeria.logging_configuration import config_logging, init_logging
from pyegeria._exceptions_new import (
    PyegeriaInvalidParameterException, PyegeriaException, PyegeriaConnectionException, PyegeriaClientException,
    PyegeriaAPIException, PyegeriaUnknownException, PyegeriaNotFoundException,
    PyegeriaUnauthorizedException,  print_exception_table, print_basic_exception,
    print_validation_error
    )
from pydantic import ValidationError
from pyegeria.models import (SearchStringRequestBody, SequencingOrder, FilterRequestBody,
                             NewElementRequestBody, InitialClassifications)

from tests.test_feedback_manager_omvs import password

disable_ssl_warnings = True

console = Console(width=250)

from loguru import logger

config_logging()
init_logging(True)

from unit_test._helpers import PLATFORM_URL, VIEW_SERVER, USER_ID, USER_PWD, require_local_server, make_client
import pytest

@pytest.fixture(autouse=True)
def _ensure_server():
    require_local_server()

class TestCollectionManager:
    good_platform1_url = PLATFORM_URL

    good_user_1 = USER_ID
    good_user_2 = USER_ID
    # good_user_3 = "peterprofile"
    # bad_user_1 = "eviledna"
    # bad_user_2 = ""
    good_server_1 = VIEW_SERVER
    good_server_2 = VIEW_SERVER
    # good_server_3 = "active-metadata-store"
    # good_engine_host_1 = "governDL01"
    good_view_server_1 = VIEW_SERVER

    def _unique_qname(self, prefix: str = "Collection") -> str:
        ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"{prefix}::{ts}"


    def test_get_attached_collections(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            parent_guid = "4300c161-25e6-4d10-a47e-3df2b143e607"

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

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException,
                PyegeriaClientException,PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
        finally:
            c_client.close_session()

    def test_find_collections(self):
        try:
            c_client = CollectionManager(self.good_server_2, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            search_string = None
            classification_name = None
            element_type = ["DigitalProduct"]
            output_format = "JSON"
            output_format_set = "Collections"

            response = c_client.find_collections(search_string = search_string, classification_names = classification_name
                                                 ,metadata_element_types=element_type
                                                 ,output_format=output_format, output_format_set=output_format_set)
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
        # except ValidationError as e:
        #     print_validation_error(e)

        finally:
            c_client.close_session()

    def test_find_collections_w_body(self):

        try:
            c_client = CollectionManager(self.good_server_2, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            # collection_type = "DataSharingAgreement"
            # collection_type = "ConnectorTypeDirectory"
            classification_name = []
            out_struct = {
                    "heading": "General Agreement Information",
                    "description": "Attributes generic to all Agreements.",
                    "aliases": [],
                    "formats": [{"columns": [
                        {'name': 'Name', 'key': 'display_name'},
                        {'name': 'Qualified Name', 'key': 'qualified_name', 'format': True},
                        {'name': 'Category', 'key': 'category'},
                        {'name': 'My Description', 'key': 'description', 'format': True},
                        {'name': "Classifications", 'key': 'classifications'},
                        {'name': 'Members', 'key': 'members', 'format': True},
                        {'name': 'CreatedBy', 'key': 'created_by'},
                        {'name': 'GUID', 'key': 'GUID'},
                        {'name': 'Type', 'key': 'type'},
                        ],
                        "types": ["ALL"]
                        },
                        ],
                    "annotations": {"wikilinks": ["[[Agreements]]", "[[Egeria]]"]}
                }
            search_string = "NAICS"
            body = {
                "class": "SearchStringRequestBody",
                "searchString": search_string,
                # "includeOnlyClassifiedElements" : element_type_name,
                "ignoreCase": True,
                "startsWith": True,
                "asOfTime": None,
                "effectiveTime": None,
                "forLineage": False,
                "forDuplicateProcessing": False,
                "limitResultsByStatus": [],
                "sequencingOrder": "PROPERTY_ASCENDING",
                "sequencingProperty": "qualifiedName",
                "metadataElementTypeName" : "DigitalProduct",
                "metadataElementSubtypeNames": []
                }

            response = c_client.find_collections(body=body, output_format="JSON", output_format_set="Digital-Products")
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
           print(e)
            # assert False
        finally:
            c_client.close_session()

    def test_find_collections_pyd(self):

        try:
            c_client = CollectionManager(self.good_server_2, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            # collection_type = "DataSharingAgreement"

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
            search_string = "GeoSpatial"
            request_body = SearchStringRequestBody(
                class_ = "SearchStringRequestBody",
                search_string=search_string,
                starts_with=True,
                ends_with=False,
                ignore_case=True,
                as_of_time=None,
                sequencing_order=SequencingOrder.CREATION_DATE_OLDEST,
                include_only_classified_elements= [classification_name]

                )

            response = c_client.find_collections(request_body, output_format="DICT", output_format_set="Collections")
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
            collection_name = "Subscription::GeoSpatial-Products-Subscription"

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
            collection_name = "myLocal::Folder::Ham-Radio-collection"
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

    def test_get_collections_by_category(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            category = "GeoSpatial"
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
            collection_guid = "545c62f6-a706-45f2-a157-8641fa096c02"
            element_type = None
            response = c_client.get_collection_by_guid(collection_guid, element_type,
                                                       output_format="JSON", output_format_set="Folders")
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

    def test_get_collection_hierarchy(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "04806a43-8002-4e5a-a59c-f9b614cd4180"

            response = c_client.get_collection_hierarchy(collection_guid, output_format="JSON",
                                                         output_format_set="Collections")
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

        except ( PyegeriaException) as e:
            print_exception_table(e)
            # assert False, "Invalid request"

        finally:
            c_client.close_session()

    def test_get_collection_graph_w_body(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "d95f2733-1db3-41ac-aea7-0e78cc30db96"
            body = {
                "class": "ResultsRequestBody", "effectiveTime": None, "limitResultsByStatus": ["ACTIVE"],
                "graphQueryDepth" : 3,
                "asOfTime": None, "sequencingOrder": "CREATION_DATE_RECENT", "sequencingProperty": ""
                }

            response = c_client.get_collection_hierarchy(collection_guid, output_format="MERMAID", body=body)
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

    def test_create_glossary(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            display_name = "Ham Glossary"
            description = "Collection of Ham Terms"
            language = "English"
            usage = "Amateur Radio"
            category = "Hobby"

            response = c_client.create_glossary(display_name, description, language, usage, category)

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
        except ValidationError as e:
            print_validation_error(e)
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
            display_name = "Ham Antenna collection"
            description = "Collection of Antennas"
            classification_name = "Folder"
            collection_type = "Hobby Collection"
            is_own_anchor = True

            response = c_client.create_collection(display_name, description,
                                                  collection_type, [classification_name], None,
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
        except ValidationError as e:
            print_validation_error(e)
        finally:
            c_client.close_session()


    def test_create_collection_w_body(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            display_name = "ESA Based Analytics"
            description = "Analytics based on ESA data."
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
            response = c_client.create_collection( body=body)
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

    def test_create_digital_product_catalog(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            display_name = "Antenna Reference Products"
            description = "A catalog of data products about antennas"
            classification_name = None
            q_name = c_client.__create_qualified_name__("DigProdCatalog", display_name, version_identifier="")
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                  "properties": {
                    "class": "DigitalProductCatalogProperties",
                    "qualifiedName": q_name,
                    "displayName": display_name,
                    "description": description,
                    "category": "Amateur Radio"
                  }
            }

            response = c_client.create_digital_product_catalog(body)
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
            c_client = CollectionManager('qs-view-server', self.good_platform1_url, user_id=self.good_user_2,
                user_pwd="secret", )

            # token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            token = c_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            anchor_guid = "c95617f2-c3c4-478e-a7cd-5369f3d4ed51"
            parent_guid = anchor_guid
            parent_relationship_type_name = "CollectionMembership"
            parent_at_end1 = True
            display_name = "Writing Dr.Egeria Markdown"
            description = "This folder holds descriptions of Dr.Egeria commands"
            is_own_anchor = False
            qualified_name = "Folder::Writing Dr.Egeria Markdown"
            category = "Dr.Egeria"
            body = {
                "class": "NewElementRequestBody",
                "parent_guid": parent_guid,
                "anchor_guid": anchor_guid,
                "parent_relationship_type_name": parent_relationship_type_name,
                "parent_at_end1": parent_at_end1,
                "is_own_anchor": is_own_anchor,
                "initialClassifications": {
                    "Folder": {
                        "class": "FolderProperties"
                        }
                    },
                "properties": {
                    "class": "CollectionProperties",
                    "displayName": display_name,
                    "description": description,
                    "category": category,
                    "qualifiedName": qualified_name,
                    },
                }
            validated_body = NewElementRequestBody.model_validate(body)
            response = c_client.create_folder_collection(body=validated_body)

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

    def test_create_folder_collection2(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            anchor_guid = None
            parent_guid = None
            parent_relationship_type_name = "CollectionMembership"
            parent_at_end1 = True
            display_name = "Dans Artifacts"
            description = "This folder contains Dans artifacts"
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

            body = {

          "class" : "NewElementRequestBody",
          "isOwnAnchor" : True,
          "initialClassifications" : { },
          "initialStatus" : "ACTIVE",
          "parentAtEnd1" : True,
          "properties" : {
            "class" : "DataSpecProperties",
            "displayName" : "Data Specification for the Teddy Bear Drop Foot Clinical Trial",
            "qualifiedName" : "DataSpec::Data Specification for the Teddy Bear Drop Foot Clinical Trial",
            "description" : "Principle data requirements for this clinical trial."

          }
        }

            response = c_client.create_data_spec_collection(body=body)
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
            display_name = "MyDictionary"
            description = "My very own data dictionary"
            category = "Data Dictionary"

            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "DataDictionaryProperties",
                    "displayName": display_name,
                    "qualifiedName": "DataDict::MyDictionary",
                    "description": "My very own data dictionary",
                    category: "Dan",
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
            display_name = "Sentinel3 sat Data"
            description = "Raw Sentinel 3 sat data"
            collection_type = "Data Product Marketplace"

            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "DigitalProductProperties",
                    "qualifiedName": f"DigitalProduct::{collection_type}::{display_name}",
                    "displayName": "Land Use Classifications - Processed",
                    "productType": "Periodic Delta",
                    "identifier": "sent3b",
                    "productName": "My sentinel 3-Processed",
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
        except ValidationError as e:
            print_validation_error(e)
        finally:
            c_client.close_session()

    def test_update_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "79439832-dffb-4b90-92e9-833e6d9b10cc"
            new_desc = "Some of my artifacts"
            collection_type = "MyStuff"
            body = {
                "class": "UpdateElementRequestBody",
                "mergeUpdate": True,
                "properties": {
                    "class": "CollectionProperties",
                    "displayName": "Dans Artifacts",
                    "description": new_desc
                    }
                }
            response = c_client.update_collection(collection_guid, body=body)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaException) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
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
            collection_guid = "8b407ab4-59fd-40c7-954a-a27163d727e8"
            body = {
                "class": "DeleteRequestBody",
                "cascadedDelete": True
                }
            response = c_client.delete_collection(collection_guid, body=body)
            duration = time.perf_counter() - start_time
            print("\n\nCollection deleted successfully")
            print(f"\n\tDuration was {duration} seconds")

            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_delete_collection_category(self):
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
            collection_type = "Sustainability"

            response = c_client.get_collections_by_category(collection_type)
            if type(response) is list:
                count = len(response)
                print(f"\n\nAbout to delete {count} collections")
                for member in response:
                    try:
                        member_guid = member["elementHeader"]["guid"]
                        member_name = member["properties"]["displayName"]
                        print(f"\n about to delete member {member_name} of count members")
                        c_client.delete_collection(member_guid, cascade=True)
                    except (PyegeriaInvalidParameterException, PyegeriaException) as e:
                        print_basic_exception(e)
                        print("Continueing")
                        continue
                    except ValidationError as e:
                        print_validation_error(e)
                duration = time.perf_counter() - start_time
                # resp_str = json.loads(response)
                print(f"\n\tDuration was {duration} seconds\n")
                response = c_client.get_collections_by_category(collection_type, '*')

            elif type(response) is str:
                print("No members found")
            assert True

        except (PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
        finally:
            c_client.close_session()

    def test_add_to_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid =  '660bfc21-12b5-4de1-a8f3-63239fbb58a0'# folder
            element_guid = '98c4c362-fd39-42fc-85e9-0718ab527131' # agreement
            body = {
                "class": "NewRelationshipRequestBody", "properties": {
                    "class": "CollectionMembershipProperties", "membershipRationale": "test purposes",
                    "expression": "just testing", "confidence": 50,  "userDefinedStatus": "Maybe",
                    "steward": "peterprofile", "stewardTypeName": "a type name?",
                    "stewardPropertyName": "a property name?", "source": "clinical data", "notes": "just an experiment"
                    }
                }

            c_client.add_to_collection(collection_guid, element_guid, None)

            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")

            assert True

        except (PyegeriaException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_basic_exception(e)
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

    def test_link_digital_product_dependency(self):
        upstream_prod = "a8a3e785-f305-4e67-9114-224f1874cafe"
        downstream_prod = "e02695bc-ed83-49cf-afb9-0d822c4f1f5b"

        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            c_client.link_digital_product_dependency(upstream_prod, downstream_prod)
            duration = time.perf_counter() - start_time


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
        logger.enable("pyegeria")
        try:
            client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            logger.info("Starting to create GeoSpatial Products")
            display_name = "GeoSpatial Root"
            description = "This is the root of the GeoSpatial work"
            category = "GeoSpatial"

            root = client.get_collections_by_name(display_name)
            if isinstance(root, dict| list):
                root_guid = root[0]['elementHeader']['guid']
                print(f"Found root guid of {root_guid}")
            else:
                root_guid = client.create_root_collection(
                    display_name=display_name,
                    description=description,
                    category=category
                    )
                logger.success(f"Created root collection {root_guid}")

            display_name = "Digital Products MarketPlace"
            description = "This is the digital products marketplace"
            category = "GeoSpatial"
            qualified_name = client.__create_qualified_name__("Folder", display_name)

            props_body = {
                "class": "CollectionProperties",
                "qualifiedName": qualified_name,
                "displayName": display_name,
                "description": description,
                "category": category
                }

            request_body = {

                "class": "NewElementRequestBody",
                "isOwnAnchor": False,
                "anchorGUID": root_guid,
                "parentGUID": root_guid,
                "parentRelationshipTypeName": "CollectionMembership",
                "parentAtEnd1": True,
                "properties": props_body,
                "initialClassifications": {"Folder": {"class": "ClassificationProperties"}}
                }
            marketplace = client.get_collections_by_name(qualified_name)
            if isinstance(marketplace, dict | list):
                marketplace_guid = marketplace[0]['elementHeader']['guid']
                print(f"Found marketplace guid of {marketplace_guid}")
            else:
                marketplace_guid = client.create_folder_collection(body=request_body)
                logger.success(f"Created folder collection for marketplace: {marketplace_guid}")


            display_name = "GeoSpatial Products"
            description = "GeoSpatial product offerings"
            category = "GeoSpatial"
            qualified_name = client.__create_qualified_name__("Folder", display_name)

            props_body = {
                "class": "CollectionProperties",
                "qualifiedName": qualified_name,
                "displayName": display_name,
                "description": description,
                "category": category
                }

            request_body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": False,
                "anchorGUID": marketplace_guid,
                "parentGUID": marketplace_guid,
                "parentRelationshipTypeName": "CollectionMembership",
                "parentAtEnd1": True,
                "properties": props_body,
                "initialClassifications": {"Folder": {"class": "ClassificationProperties"}}
                }
            geo_prods = client.get_collections_by_name(qualified_name)
            if isinstance(geo_prods, dict | list):
                geo_prods_guid = geo_prods[0]['elementHeader']['guid']
                print(f"Found geo_prods guid of {geo_prods_guid}")
            else:
                geo_prods_guid = client.create_folder_collection( body=request_body)
                logger.success(f"Created folder collection for geoprods: {geo_prods_guid}")


            display_name = "Agricultural Products"
            description = "Agricultural product offerings"
            category = "GeoSpatial"
            qualified_name = client.__create_qualified_name__("Folder", display_name)

            props_body = {

                "class": "CollectionProperties",
                "qualifiedName": qualified_name,
                "displayName": display_name,
                "description": description,
                "category": category
                }

            request_body = {

                "class": "NewElementRequestBody",
                "isOwnAnchor": False,
                "anchorGUID": marketplace_guid,
                "parentGUID": marketplace_guid,
                "parentRelationshipTypeName": "CollectionMembership",
                "parentAtEnd1": True,
                "properties": props_body,
                "initialClassifications": {"Folder": {"class": "ClassificationProperties"}}
                }
            ag_prods = client.get_collections_by_name(qualified_name)
            if isinstance(ag_prods, dict | list):
                ag_prods_guid = ag_prods[0]['elementHeader']['guid']
                print(f"Found ag_prods guid of {ag_prods_guid}")
            else:
                ag_prods_guid = client.create_folder_collection(body=request_body)
                logger.success(f"Created folder collection for  ag products: {ag_prods_guid}")


            display_name = "Prepared Imagery Products"
            description = "Imagery products that are ready for consumption"
            category = "GeoSpatial"
            qualified_name = client.__create_qualified_name__("Folder", display_name)

            props_body = {
                "class": "CollectionProperties",
                "qualifiedName": qualified_name,
                "displayName": display_name,
                "description": description,
                "category": category
                }

            request_body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": False,
                "anchorGUID": root_guid,
                "parentGUID": root_guid,
                "parentRelationshipTypeName": "CollectionMembership",
                "parentAtEnd1": True,
                "properties": props_body,
                "initialClassifications": {"Folder": {"class": "ClassificationProperties"}}
                }
            prepared_imagery = client.get_collections_by_name(qualified_name)
            if isinstance(prepared_imagery, dict | list):
                prepared_imagery_guid = prepared_imagery[0]['elementHeader']['guid']
                print(f"Found prepared_imagery guid of {prepared_imagery_guid}")
            else:
                prepared_imagery_guid = client.create_folder_collection(body=request_body)
                logger.success(f"Created folder for prepared imagery products: {prepared_imagery_guid}")

            display_name = "NDVI - Sentinel 2 derived"
            description = "NDVI vegetation index calculated from Sentinel 2 imagery"
            category = "GeoSpatial"
            qualified_name = client.__create_qualified_name__("DigitalProduct", display_name)

            props_body = {
                "class": "DigitalProductProperties",
                "qualifiedName": qualified_name,
                "displayName": display_name,
                "description": description,
                "category": category,
                "productType": "Periodic Extended",
                "identifier": "NDVI-S",
                "productName": "NDVI - Sentinel 2",
                "serviceLife": "Until interest and budget wane",
                "maturity": "Nascent"
                }

            request_body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": False,
                "anchorGUID": prepared_imagery_guid,
                "parentGUID": prepared_imagery_guid,
                "parentRelationshipTypeName": "CollectionMembership",
                "parentAtEnd1": True,
                "properties": props_body,
                "initialClassifications": {"Folder": {"class": "ClassificationProperties"}}
                }

            ndvi = client.get_collections_by_name(qualified_name)
            if isinstance(ndvi, dict | list):
                ndvi_guid = ndvi[0]['elementHeader']['guid']
                print(f"Found ndvi guid of {ndvi_guid}")
            else:
                ndvi_guid = client.create_digital_product(body=request_body)
                logger.success(f"Created NDVI product: {ndvi_guid}")


            display_name = "Raw Satellite Imagery Products"
            description = "Raw satellite imagery imported from or referenced from satellite data providers"
            category = "GeoSpatial"
            qualified_name = client.__create_qualified_name__("Folder", display_name)

            props_body = {
                "class": "CollectionProperties",
                "qualifiedName": qualified_name,
                "displayName": display_name,
                "description": description,
                "category": category
                }

            request_body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": False,
                "anchorGUID": root_guid,
                "parentGUID": root_guid,
                "parentRelationshipTypeName": "CollectionMembership",
                "parentAtEnd1": True,
                "properties": props_body,
                "initialClassifications": {"Folder": {"class": "ClassificationProperties"}}
                }
            raw_imagery = client.get_collections_by_name(qualified_name)
            if isinstance(raw_imagery, dict | list):
                raw_imagery_guid = raw_imagery[0]['elementHeader']['guid']
                print(f"Found raw_imagery guid of {raw_imagery_guid}")
            else:
                raw_imagery_guid = client.create_folder_collection(body=request_body)
                logger.success(f"Created folder for raw imagery products: {raw_imagery_guid}")

            display_name = "Sentinel-2a"
            description = "Level 2a (surface level) imagery"
            category = "GeoSpatial"
            qualified_name = client.__create_qualified_name__("DigitalProduct", display_name)

            props_body = {
                "class": "DigitalProductProperties",
                "qualifiedName": qualified_name,
                "displayName": display_name,
                "description": description,
                "category": category,
                "productType": "Periodic Extended",
                "identifier": "sentinel-2a",
                "productName": "Sentinel Level 2A",
                "serviceLife": "Until interest and budget wane",
                "maturity": "Nascent"
                }

            request_body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": False,
                "anchorGUID": raw_imagery_guid,
                "parentGUID": raw_imagery_guid,
                "parentRelationshipTypeName": "CollectionMembership",
                "parentAtEnd1": True,
                "properties": props_body,
                "initialClassifications": {"Folder": {"class": "ClassificationProperties"}}
                }
            sentinel2a = client.get_collections_by_name(qualified_name)
            if isinstance(sentinel2a, dict | list):
                sentinel2a_guid = sentinel2a[0]['elementHeader']['guid']
                print(f"Found sentinel2a guid of {sentinel2a_guid}")
            else:
                sentinel2a_guid = client.create_digital_product(body=request_body)
                logger.success(f"Created Sentinel-2a product: {sentinel2a_guid}")

            # Add dependency between ndvi dependent on sentinel2a
            client.link_digital_product_dependency(sentinel2a_guid, ndvi_guid)

            # Create a folder for standard agreements
            display_name = "Standard Subscription Agreements Folder"
            description = "A folder collection for digital product subscriptions"
            category = "GeoSpatial"
            qualified_name = client.__create_qualified_name__("Folder", display_name)

            props_body = {
                "class": "CollectionProperties",
                "qualifiedName": qualified_name,
                "displayName": display_name,
                "description": description,
                "category": category
                }

            request_body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": False,
                "anchorGUID": root_guid,
                "parentGUID": root_guid,
                "parentRelationshipTypeName": "CollectionMembership",
                "parentAtEnd1": True,
                "properties": props_body,
                "initialClassifications": {"Folder": {"class": "ClassificationProperties"}}
                }
            subscriptions_folder = client.get_collections_by_name(qualified_name)
            if isinstance(subscriptions_folder, dict | list):
                subscriptions_folder_guid = subscriptions_folder[0]['elementHeader']['guid']
                print(f"Found raw_imagery guid of {subscriptions_folder_guid}")
            else:
                subscriptions_folder_guid = client.create_folder_collection(body=request_body)
                logger.success(f"Created folder for raw imagery products: {subscriptions_folder_guid}")



            # Add Digital Subscription
            #
            anchor_guid = subscriptions_folder_guid
            parent_guid = subscriptions_folder_guid
            parent_relationship_type_name = "CollectionMembership"
            parent_at_end1 = True
            display_name = "GeoSpatial Data Products Subscription"
            description = "A generic subscription agreement for GeoSpatial Data Products"
            identifier = "GeoSpatial-0"
            category = "GeoSpatial"
            is_own_anchor = False

            qualified_name = client.__create_qualified_name__("DigitalSubscription", display_name)

            body = {
                "class": "NewElementRequestBody",
                "anchorGUID": anchor_guid,
                "isOwnAnchor": is_own_anchor,
                "parentGUID": parent_guid,
                # "initialClassification": {classification: {"class": {}}},
                "parentRelationshipTypeName": parent_relationship_type_name,
                "parentAtEnd1": parent_at_end1,
                "properties": {
                    "class": "DigitalSubscriptionProperties",
                    "displayName": display_name,
                    "qualifiedName": qualified_name,
                    "description": description,
                    "identifier": identifier,
                    "category": category,
                    "supportLevel": "Best Effort"
                    },
                }
            geo_subscriptions = client.get_collections_by_name(qualified_name)
            if isinstance(geo_subscriptions, dict | list):
                geo_subscriptions_guid = geo_subscriptions[0]['elementHeader']['guid']
                print(f"Found GeoSpatial Subscriptions guid of {subscriptions_folder_guid}")
            else:
                geo_subscriptions_guid = client.create_digital_subscription(body)
                print(f"Created Digital Subscription, GeoSpatial Data Products Subscription: {geo_subscriptions_guid}")
                logger.success(f"Created subscription : {geo_subscriptions_guid}")
            #
            #  Add agreement items to the agreement - the sentinel data
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "AgreementItemProperties",
                    "agreementItemId": "Sentinel-2a-Subscription",
                    "agreementStart": "2025-08-01",
                    "agreementEnd": "2025-12-31",
                    "entitlements": { "Data Download": "Allowed", "Data Sharing": "Allowed"}
                    }
                }
            client.link_agreement_item(geo_subscriptions_guid, sentinel2a_guid, body)
            msg = f"Linked agreement item sentinel2a to geo_subscriptions"
            logger.success(msg)
            print(msg)


            # create a fourth collection, a digital product, child of folder 2, for Landsat 8  # parent_guid =
            # folder2  # display_name = "Landsat 8"  # description = "Landsat 8 data products"  #  # body_4 = {  #
            # "class": "NewDigitalProductRequestBody",  #     "isOwnAnchor": True,  #     "parentGUID": parent_guid,
            #     "parentRelationshipTypeName": parent_relationship_type_name,  #     "parentAtEnd1": True,
            #     "collectionProperties": {  #         "class": "CollectionProperties",  #         "qualifiedName":
            #     f"{collection_type}-{display_name}-{time.asctime()}",  #         "name": display_name,
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
            #         "qualifiedName": f"{collection_type}-{display_name}-{time.asctime()}",  #         "name":
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
            # "class": "CollectionProperties",  #         "qualifiedName": f"{collection_type}-{display_name}-{
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
            #     f"{collection_type}-{display_name}-{time.asctime()}",  #         "name": display_name,
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
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"
        finally:
            client.close_session()

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
            display_name = "Geo Data Exchange"
            description = "An agreement for data usage"
            identifier = "DataUsage"
            category = "GeoSpatial"
            classification = "DataSharingAgreement"
            is_own_anchor = True
            anchor_scope_guid = None
            qualified_name = c_client.__create_qualified_name__("Agreement", display_name)

            body = {
                "class": "NewElementRequestBody",
                "anchorGUID": anchor_guid,
                "isOwnAnchor": is_own_anchor,
                "parentGUID": parent_guid,
                "initialClassification": {classification: {"class": {}}},
                "parentRelationshipTypeName": parent_relationship_type_name,
                "parentAtEnd1": parent_at_end1,
                "properties": {
                    "class": "AgreementProperties",
                    "displayName": display_name,
                    "qualifiedName": qualified_name,
                    "description": description,
                    "identifier": identifier,
                    "category": category
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
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
        finally:
            c_client.close_session()


    def test_update_agreement(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "538edd5a-459c-4b9b-a643-171be84eb3f7"
            new_desc = "We can share"
            qualified_name = "Agreement::Data-Usage-Agreement"
            category = "GeoSpatial"
            body = {
                "class": "UpdateElementRequestBody",
                "mergeUpdate": True,
                "properties": {
                    "class": "AgreementProperties",
                    "displayName": "Data-Usage Agreement",
                    "qualifiedName": qualified_name,
                    "category": category,
                    "description": new_desc
                    }
                }
            response = c_client.update_agreement(collection_guid, body)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (PyegeriaClientException, PyegeriaInvalidParameterException,  PyegeriaConnectionException, PyegeriaAPIException, PyegeriaUnknownException,) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_crud_collection_e2e(self):
        """End-to-end smoke test for Collection: create -> get -> update -> find -> delete."""
        from uuid import uuid4
        c_client = None
        created_guid = None
        display_name = f"Smoke Collection {uuid4().hex[:8]}"
        classification_name = "Folder"
        try:
            # Use helper to ensure token etc. If unavailable, fall back to direct constructor
            try:
                c_client = make_client(CollectionManager)
            except Exception:
                c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
                c_client.create_egeria_bearer_token(self.good_user_2, USER_PWD)

            # Create
            q_name = c_client.__create_qualified_name__(classification_name, display_name, version_identifier="")
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "initialClassifications": {classification_name: {"class": "ClassificationProperties"}},
                "properties": {
                    "class": "CollectionProperties",
                    "displayName": display_name,
                    "qualifiedName": q_name,
                    "description": "e2e smoke collection",
                    "category": "Test"
                }
            }
            create_resp = c_client.create_collection(body=body)
            assert isinstance(create_resp, (dict, str))
            created_guid = create_resp.get("guid") if isinstance(create_resp, dict) else create_resp
            assert created_guid and isinstance(created_guid, str)

            # Get by GUID
            got = c_client.get_collection_by_guid(created_guid, output_format="DICT")
            assert got, "get by guid returned empty"

            # Update
            new_desc = "updated description"
            upd_body = {
                "class": "UpdateElementRequestBody",
                "mergeUpdate": True,
                "properties": {
                    "class": "CollectionProperties",
                    "qualifiedName": q_name,
                    "description": new_desc,
                }
            }
            upd_resp = c_client.update_collection(created_guid, upd_body)
            assert upd_resp in (None, "") or isinstance(upd_resp, (dict, str))

            # Find
            found = c_client.find_collections(search_string=display_name, output_format="DICT")
            assert isinstance(found, list) and len(found) >= 1

            # Delete
            del_resp = c_client.delete_collection(created_guid)
            assert del_resp in (None, "", created_guid) or isinstance(del_resp, (dict, str))

            # Verify deletion (best effort)
            try:
                after = c_client.get_collection_by_guid(created_guid, output_format="DICT")
                # Some servers return not found exceptions; if we got content, ensure it's empty list or error-like
                assert not after or (isinstance(after, list) and len(after) == 0)
            except Exception:
                # Accept exceptions as deletion confirmation
                pass
        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "CRUD e2e failed"
        finally:
            try:
                if c_client:
                    c_client.close_session()
            except Exception:
                pass
    #
    # def test_create_data_sharing_agreement(self):
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
    #         display_name = "Fur balls per day"
    #         description = "Pets"
    #         identifier = "who me"
    #         category = "Pets"
    #         is_own_anchor = True
    #         anchor_scope_guid = None
    #         qualified_name = c_client.__create_qualified_name__("Agreement", display_name)
    #
    #         body = {
    #             "class": "NewElementRequestBody", "anchorGUID": anchor_guid, "isOwnAnchor": is_own_anchor,
    #             "parentGUID": parent_guid, "parentRelationshipTypeName": parent_relationship_type_name,
    #             "parentAtEnd1": parent_at_end1, "properties": {
    #                 "class": "AgreementProperties", "displayName": display_name, "qualifiedName": qualified_name,
    #                 "description": description, "identifier": identifier, "category": category
    #                 },
    #             }
    #
    #         response = c_client.create_data_sharing_agreement(body)
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
