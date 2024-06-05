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
    CollectionManager
)

disable_ssl_warnings = True


class TestCollectionManager:
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


    def test_get_linked_collections(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            parent_guid = "a277414f-d714-452d-a805-d42bd20956dc"

            response = c_client.get_linked_collections(parent_guid)
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

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            c_client.close_session()

    def test_get_classified_collections(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            # parent_guid = "0fa16a37-5c61-44c1-85a0-e415c3cecb82"
            # classification = "RootCollection"
            classification = "Folder"
            response = c_client.get_classified_collections(classification)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"response type is: {type(response)}")
            if type(response) is tuple:
                t = response[0]
                count = len(t)
                print(f"Found {count} collections {type(t)}\n\n")
                print_json(json.dumps(response, indent=4))
            elif type(response) is list:
                count = len(response)
                print(f"Found {count} collections\n\n")
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            c_client.close_session()

    def test_find_collections(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            search_string = "Digital Products Root"

            response = c_client.find_collections(search_string, None, True, ignore_case=False)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Found {len(response)} collections {type(response)}\n\n")
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
            c_client.close_session()

    def test_get_collection_by_name(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_name = "Scope 2 Emissions"

            response = c_client.get_collections_by_name(collection_name)
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

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            c_client.close_session()

    def test_get_collections_by_type(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_type = "Sustainability Collection"

            response = c_client.get_collections_by_type(collection_type)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Type was list - found {len(response)} elements\n")
                print_json(json.dumps(response, indent=4))
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
            c_client.close_session()

    def test_get_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "59b4d6b2-110c-488d-88d9-2975ed51506c"

            response = c_client.get_collection(collection_guid)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"Type of response is {type(response)}")

            if type(response) is dict:
                print("dict:\n\n")
                print_json(json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}\n\n")
                print_json(json.dumps(response, indent=4))
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
            c_client.close_session()

    def test_create_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            anchor_guid = None
            parent_guid = "11311b9a-58f9-4d8e-94cd-616b809c5f66"
            parent_relationship_type_name = "CollectionMembership"
            parent_at_end1 = True
            display_name = "Elecraft Radio collection"
            description = "Another collection of my Elecraft radios"
            collection_type = "Hobby Collection"
            is_own_anchor = True
            collection_ordering = None
            order_property_name = None

            response = c_client.create_collection("Set", anchor_guid, parent_guid,
                                                  parent_relationship_type_name, parent_at_end1,
                                                  display_name, description, collection_type,
                                                  is_own_anchor, collection_ordering, order_property_name)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
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
            c_client.close_session()

    def test_create_collection_w_body(self):

        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            classification_name = "Set"
            body = {
                "anchorGUID": None,
                "isOwnAnchor": True,
                "parentGUID": "11311b9a-58f9-4d8e-94cd-616b809c5f66",
                "parentRelationshipTypeName": "CollectionMembership",
                "parentAtEnd1": True,
                "collectionProperties": {
                    "class": "CollectionProperties",
                    "name": "A radio collection",
                    "qualifiedName": f"{classification_name}-My Radios-{time.asctime()}",
                    "description": "A collection of my radios",
                    "collectionType": "Hobby Collection",
                    "collectionOrdering": "NAME",
                    "orderPropertyName": None,
                }
            }
            response = c_client.create_collection_w_body(classification_name, body)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
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
            c_client.close_session()

    def test_create_root_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            anchor_guid = None
            parent_guid = None
            parent_relationship_type_name = None
            parent_at_end1 = False
            display_name = "Clinical Trials Data"
            description = "This is the root catalog for clinical trials data"
            collection_type = "Medical Data"
            is_own_anchor = True

            response = c_client.create_root_collection(anchor_guid, parent_guid,
                                                       parent_relationship_type_name, parent_at_end1,
                                                       display_name, description, collection_type,
                                                       is_own_anchor)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
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
            c_client.close_session()

    def test_create_folder_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            anchor_guid = None
            parent_guid = "766a0395-004a-4448-88ea-27527f1ed820"
            parent_relationship_type_name = "CollectionMembership"
            parent_at_end1 = True
            display_name = "Oak Dene Clinical Trials Data"
            description = "This folder contains Oak Denedata and collections of clinical data"
            collection_type = "Medical Data"
            is_own_anchor = True
            collection_ordering = "DATE_CREATED"
            order_property_name = None

            response = c_client.create_folder_collection(anchor_guid, parent_guid,
                                                         parent_relationship_type_name, parent_at_end1,
                                                         display_name, description, collection_type,
                                                         is_own_anchor, collection_ordering, order_property_name)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
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
            c_client.close_session()

    def test_create_data_spec_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            anchor_guid = None
            parent_guid = "11311b9a-58f9-4d8e-94cd-616b809c5f66"
            parent_relationship_type_name = "CollectionMembership"
            parent_at_end1 = True
            display_name = "First Data Specification Collection"
            description = "First collection of data specs"
            collection_type = "Data Spec Collection"
            is_own_anchor = True
            collection_ordering = "NAME"
            order_property_name = None

            response = c_client.create_data_spec_collection(anchor_guid, parent_guid,
                                                            parent_relationship_type_name, parent_at_end1,
                                                            display_name, description, collection_type,
                                                            is_own_anchor, collection_ordering, order_property_name)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
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
            c_client.close_session()

    def test_create_collection_from_template(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            anchor_guid = None
            parent_guid = "97bbfe07-6696-4550-bf8b-6b577d25bef0"
            parent_relationship_type_name = "CollectionMembership"
            parent_at_end1 = True
            display_name = "Meow"
            description = "Meow"
            collection_type = "Meow"
            is_own_anchor = False
            collection_ordering = "NAME"
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
                            "primitiveValue": f"templated-{display_name}-{time.asctime()}"
                        },
                        "name": {
                            "class": "PrimitiveTypePropertyValue",
                            "typeName": "string",
                            "primitiveTypeCategory": "OM_PRIMITIVE_TYPE_STRING",
                            "primitiveValue": display_name
                        },
                        "description": {
                            "class": "PrimitiveTypePropertyValue",
                            "typeName": "string",
                            "primitiveTypeCategory": "OM_PRIMITIVE_TYPE_STRING",
                            "primitiveValue": description
                        }
                    }
                }
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

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_create_digital_product(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            parent_guid = "a133a7a3-197a-4bf3-837a-780867c25c2b"
            parent_relationship_type_name = "CollectionMembership"
            display_name = "Land Use Classification"
            description = "Land use classification assets"
            collection_type = "Data Product Marketplace"
            classification_name = "Data Product Marketplace"
            body = {
                "class": "NewDigitalProductRequestBody",
                "isOwnAnchor": True,
                "parentGUID": parent_guid,
                "parentRelationshipTypeName": parent_relationship_type_name,
                "parentAtEnd1": True,
                "collectionProperties": {
                    "class": "CollectionProperties",
                    "qualifiedName": f"{classification_name}-{display_name}-{time.asctime()}",
                    "name": display_name,
                    "description": description,
                    "collectionType": collection_type,
                    "collectionOrdering": "DATE_CREATED",
                },
                "digitalProductProperties": {
                    "class": "DigitalProductProperties",
                    "productStatus": "ACTIVE",
                    "productName": "Land Use Classifications",
                    "productType": "Geospatial Data Assets",
                    "description": "Land use classification assets",
                    "introductionDate": "2023-12-31",
                    "maturity": "Nacent",
                    "serviceLife": "3 years",
                    "currentVersion": "V.5",
                    "nextVersionDate": "2024-06-01",
                    "withdrawDate": "2030-01-01",
                    "additionalProperties": {
                        "thought_id": "a guid",
                        "license": "cc-by-sa",
                    }
                }
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

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_update_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "79f43cb7-0e1b-4785-9bf4-7f8b4bb6d4f1"
            new_desc = " A somewhat general collection of product catalogs"
            response = c_client.update_collection(collection_guid, description=new_desc)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
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
            c_client.close_session()

    def test_get_collection_members(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "fbcfdb5a-5d32-4f1e-b85b-0f67ff43275e"

            response = c_client.get_collection_members(collection_guid)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is list:
                print_json(json.dumps(response, indent=4))
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
            c_client.close_session()

    def test_attach_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "fbcfdb5a-5d32-4f1e-b85b-0f67ff43275e"
            element_guid = "5c8e1430-8944-466e-90ba-245e861d1285"

            c_client.attach_collection(collection_guid, element_guid,
                                       "Clinical Data Storage",
                                       "Clinical data storage for OAK Dene", None,
                                       watch_resources=True, make_anchor=False)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")

            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_detach_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)

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

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_delete_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "d46fb553-60f5-4558-8ee8-e36fe2ed6560"
            response = c_client.delete_collection(collection_guid)
            duration = time.perf_counter() - start_time
            print("\n\nCollection deleted successfully")
            print(f"\n\tDuration was {duration} seconds")

            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_delete_collection_type(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_type = "Digital Product"
            # collection_type = "Product Catalog"
            # collection_type = "Digital Product Marketplace"
            # collection_type = "Data Spec Collection"
            # collection_type = "Medical Data"
            # collection_type = "Data Product Marketplace"
            collection_type = "Digital Products Root"

            response = c_client.get_collections_by_type(collection_type)
            if type(response) is list:
                count = len(response)
                print(f"\n\nAbout to delete {count} collections")
                print_json(json.dumps(response, indent=4))
                for member in response:
                    member_guid = member['elementHeader']["guid"]
                    member_name = member["properties"]["name"]
                    print(f"\n about to delete member {member_name} of count members")
                    c_client.delete_collection(member_guid)
                duration = time.perf_counter() - start_time
                # resp_str = json.loads(response)
                print(f"\n\tDuration was {duration} seconds\n")
                response = c_client.get_collections_by_type(collection_type)

            elif type(response) is str:
                print("No members found")
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_add_to_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "fbcfdb5a-5d32-4f1e-b85b-0f67ff43275e"
            element_guid = "5c8e1430-8944-466e-90ba-245e861d1285"
            body = {
                "class": "CollectionMembershipProperties",
                "membershipRationale": "test purposes",

                "expression": "just testing",
                "confidence": 50,
                "status": "PROPOSED",
                "userDefinedStatus": "Maybe",
                "steward": "peterprofile",
                "stewardTypeName": "a type name?",
                "stewardPropertyName": "a property name?",
                "source": "clinical data",
                "notes": "just an experiment"
            }

            c_client.add_to_collection(collection_guid, element_guid,
                                       body)

            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")

            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_get_member_list(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # name = "Root Sustainability Collection"
            name = "Digital Products Root"
            # name = "Land Use Classification"

            response = c_client.get_member_list(name)

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

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_update_collection_membership(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "fbcfdb5a-5d32-4f1e-b85b-0f67ff43275e"
            element_guid = "5c8e1430-8944-466e-90ba-245e861d1285"
            name = "Root Sustainability Collection"

            body = {
                "class": "CollectionMembershipProperties",
                "membershipRationale": "xxx",
                "expression": "convenience",
                "confidence": 100,
                "status": "PROPOSED",
                "userDefinedStatus": "Validation required",
                "source": "archive",
                "notes": "arbitrary notes"
            }
            c_client.update_collection_membership(collection_guid, element_guid, body,
                                                             replace_all_props=False)

            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds\n")
            # print(f"Member List is: {response}")
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_sample_setup(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            # Create a Data Products Root collection
            anchor_guid = None
            parent_guid = None
            parent_relationship_type_name = None
            parent_at_end1 = False
            display_name = "Digital Products Root"
            description = "This is the root catalog for digital products"
            collection_type = "Digital Products Root"
            is_own_anchor = True

            response = c_client.create_root_collection(anchor_guid, parent_guid,
                                                       parent_relationship_type_name, parent_at_end1,
                                                       display_name, description, collection_type,
                                                       is_own_anchor)

            # Create first folder for Agriculture Insights
            parent_guid = response
            parent_relationship_type_name = "CollectionMembership"
            display_name = "Agriculture Insights Collection"
            description = "A folder for agricultural insights data product collections"
            collection_type = "Digital Product Marketplace"

            folder1 = c_client.create_folder_collection(None, parent_guid,
                                                        parent_relationship_type_name,
                                                        True, display_name, description,
                                                        collection_type, True, "DATE_CREATED",
                                                        None
                                                        )
            print(f"\n\n created a folder with guid {folder1}")
            # create second folder for Earth Observations
            display_name = "Earth Observation Data Collection"
            description = "A folder for Earth Observation data product collections"

            folder2 = c_client.create_folder_collection(None, parent_guid,
                                                        parent_relationship_type_name,
                                                        True, display_name, description,
                                                        collection_type, True, "DATE_CREATED",
                                                        None
                                                        )
            print(f"\n\n created a folder with guid {folder2}")

            # create a digital product, child of folder 1, for Land Use products
            parent_guid = folder1
            parent_relationship_type_name = "CollectionMembership"
            display_name = "Land Use Classification"
            description = "Land use classification assets"
            collection_type = "Digital Product"
            classification_name = "Digital Product"
            body_3 = {
                "class": "NewDigitalProductRequestBody",
                "isOwnAnchor": True,
                "parentGUID": parent_guid,
                "parentRelationshipTypeName": parent_relationship_type_name,
                "parentAtEnd1": True,
                "collectionProperties": {
                    "class": "CollectionProperties",
                    "qualifiedName": f"{classification_name}-{display_name}-{time.asctime()}",
                    "name": display_name,
                    "description": description,
                    "collectionType": collection_type,
                    "collectionOrdering": "DATE_CREATED",
                },
                "digitalProductProperties": {
                    "class": "DigitalProductProperties",
                    "productStatus": "ACTIVE",
                    "productName": "Land Use Classifications",
                    "productType": "Geospatial Data Assets",
                    "description": "Land use classification assets",
                    "introductionDate": "2023-12-01",
                    "maturity": "Nacent",
                    "serviceLife": "3 years",
                    "currentVersion": "V.5",
                    "nextVersionDate": "2024-12-01",
                    "withdrawDate": "2030-01-01",
                    "additionalProperties": {
                        "thought_id": "a guid",
                        "license": "cc-by-sa",
                    }
                }
            }
            folder3 = c_client.create_digital_product(body_3)
            print(f"\n\n created a collection with guid {folder3}")

            # create a fourth collection, a digital product, child of folder 2, for Landsat 8
            parent_guid = folder2
            display_name = "Landsat 8"
            description = "Landsat 8 data products"

            body_4 = {
                "class": "NewDigitalProductRequestBody",
                "isOwnAnchor": True,
                "parentGUID": parent_guid,
                "parentRelationshipTypeName": parent_relationship_type_name,
                "parentAtEnd1": True,
                "collectionProperties": {
                    "class": "CollectionProperties",
                    "qualifiedName": f"{classification_name}-{display_name}-{time.asctime()}",
                    "name": display_name,
                    "description": description,
                    "collectionType": collection_type,
                    "collectionOrdering": "DATE_CREATED",
                },
                "digitalProductProperties": {
                    "class": "DigitalProductProperties",
                    "productStatus": "ACTIVE",
                    "productName": "Landsat 8 Imagery",
                    "productType": "Geospatial Data Assets",
                    "description": description,
                    "introductionDate": "2024-01-01",
                    "maturity": "Mature",
                    "serviceLife": "3 years",
                    "currentVersion": "V1.5",
                    "nextVersion": "2024-06-01",
                    "withdrawDate": "2030-01-01",
                    "additionalProperties": {
                        "thought_id": "a guid",
                        "license": "cc-by-sa",
                    }
                }
            }
            folder4 = c_client.create_digital_product(body_4)
            print(f"\n\n created a collection with guid {folder4}")

            # Now create a 5th collection for sentinel 2 data
            parent_guid = folder2
            display_name = "Sentinel 2"
            description = "Sentinel 2 products"
            parent_relationship_type_name = "CollectionMembership"
            collection_type = "Digital Product Marketplace"

            folder5 = c_client.create_folder_collection(None, parent_guid,
                                                        parent_relationship_type_name,
                                                        True, display_name, description,
                                                        collection_type, True, "DATE_CREATED",
                                                        None
                                                        )
            # Create a DigitalProduct for Level-1B
            parent_guid = folder5
            display_name = "Sentinel 2 - Level 1B"
            description = "Level 1B of Sentinel 2"

            body_6 = {
                "class": "NewDigitalProductRequestBody",
                "anchor_guid": parent_guid,
                "isOwnAnchor": False,
                "parentGUID": parent_guid,
                "parentRelationshipTypeName": parent_relationship_type_name,
                "parentAtEnd1": True,
                "collectionProperties": {
                    "class": "CollectionProperties",
                    "qualifiedName": f"{classification_name}-{display_name}-{time.asctime()}",
                    "name": display_name,
                    "description": description,
                    "collectionType": collection_type,
                    "collectionOrdering": "DATE_CREATED",
                },
                "digitalProductProperties": {
                    "class": "DigitalProductProperties",
                    "productStatus": "ACTIVE",
                    "productName": "Sentinel 2 - Level 1B",
                    "productType": "Geospatial Data Assets",
                    "description": description,
                    "introductionDate": "2024-01-01",
                    "maturity": "Mature",
                    "serviceLife": "3 years",
                    "currentVersion": "V1.5",
                    "nextVersion": "2024-06-01",
                    "withdrawDate": "2030-01-01",
                    "additionalProperties": {
                        "thought_id": "a guid",
                        "license": "cc-by-sa",
                    }
                }
            }
            folder6 = c_client.create_digital_product(body_6)
            print(f"\n\n created a collection with guid {folder6}")

            # now lets create a digital product for - Level - 1c
            parent_guid = folder5
            display_name = "Sentinel 2 - Level 1C"
            description = "Level 1C of Sentinel 2"
            body_7 = {
                "class": "NewDigitalProductRequestBody",
                "anchor_guid": parent_guid,
                "isOwnAnchor": False,
                "parentGUID": parent_guid,
                "parentRelationshipTypeName": parent_relationship_type_name,
                "parentAtEnd1": True,
                "collectionProperties": {
                    "class": "CollectionProperties",
                    "qualifiedName": f"{classification_name}-{display_name}-{time.asctime()}",
                    "name": display_name,
                    "description": description,
                    "collectionType": collection_type,
                    "collectionOrdering": "DATE_CREATED",
                },
                "digitalProductProperties": {
                    "class": "DigitalProductProperties",
                    "productStatus": "ACTIVE",
                    "productName": "Sentinel 2 - Level 1B",
                    "productType": "Geospatial Data Assets",
                    "description": description,
                    "introductionDate": "2024-01-01",
                    "maturity": "Mature",
                    "serviceLife": "3 years",
                    "currentVersion": "V1.5",
                    "nextVersion": "2024-06-01",
                    "withdrawDate": "2030-01-01",
                    "additionalProperties": {
                        "thought_id": "a guid",
                        "license": "cc-by-sa",
                    }
                }
            }
            folder7 = c_client.create_digital_product(body_7)
            print(f"\n\n created a collection with guid {folder7}")
            assert True

            # now lets create a digital product for - Level - 2A
            parent_guid = folder5
            display_name = "Sentinel 2 - Level 2A"
            description = "Level 2A of Sentinel 2"
            body_8 = {
                "class": "NewDigitalProductRequestBody",
                "anchor_guid": parent_guid,
                "isOwnAnchor": False,
                "parentGUID": parent_guid,
                "parentRelationshipTypeName": parent_relationship_type_name,
                "parentAtEnd1": True,
                "collectionProperties": {
                    "class": "CollectionProperties",
                    "qualifiedName": f"{classification_name}-{display_name}-{time.asctime()}",
                    "name": display_name,
                    "description": description,
                    "collectionType": collection_type,
                    "collectionOrdering": "DATE_CREATED",
                },
                "digitalProductProperties": {
                    "class": "DigitalProductProperties",
                    "productStatus": "ACTIVE",
                    "productName": "Sentinel 2 - Level 1B",
                    "productType": "Geospatial Data Assets",
                    "description": description,
                    "introductionDate": "2024-01-01",
                    "maturity": "Mature",
                    "serviceLife": "3 years",
                    "currentVersion": "V1.5",
                    "nextVersion": "2024-06-01",
                    "withdrawDate": "2030-01-01",
                    "additionalProperties": {
                        "thought_id": "a guid",
                        "license": "cc-by-sa",
                    }
                }
            }
            folder8 = c_client.create_digital_product(body_8)
            print(f"\n\n created a collection with guid {folder8}")
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_delete_all_collections(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            search_string = "*"

            response = c_client.find_collections(search_string, None, True, ignore_case=False)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Found {len(response)} collections {type(response)}\n\n")
                for collection in response:
                    c_client.delete_collection(collection['elementHeader']["guid"])
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
            c_client.close_session()
