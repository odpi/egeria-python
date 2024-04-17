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
from pyegeria.glossary_omvs import GlossaryBrowser

# from pyegeria.admin_services import FullServerConfig

disable_ssl_warnings = True


class TestCollectionManager:
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

    def test_get_linked_collections(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                     user_id=self.good_user_2)
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            parent_guid = "11311b9a-58f9-4d8e-94cd-616b809c5f66"

            response = c_client.get_linked_collections(parent_guid)
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
            search_string = "*"

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
            collection_name = "OpenMetadataJDBCConnectorCategory_09450b83-20ff-4a8b-a8fb-f9b527bbcba6"

            response = c_client.get_collections_by_name(collection_name)
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
            c_client.close_session()

    def test_get_collections_by_type(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                     user_id=self.good_user_2)
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_type = "Data Spec Collection"

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
            collection_guid = "cc830f0a-bb17-4459-8293-6c3fa2372b1f"

            response = c_client.get_collection(collection_guid)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"Type of response is {type(response)}")

            if type(response) is dict:
                print("dict:\n\n" )
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

            response = c_client.create_collection("Set",anchor_guid, parent_guid,
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
            response = c_client.create_collection_w_body(classification_name, body )
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
            display_name = "Product Catalog Collection"
            description = "This is the root collection for our product catalog"
            collection_type = "Product Catalog"
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
            parent_guid = "11311b9a-58f9-4d8e-94cd-616b809c5f66"
            parent_relationship_type_name = "CollectionMembership"
            parent_at_end1 = True
            display_name = "Dans Data Product Collection"
            description = "Dan's collection of data products collection"
            collection_type = "Data Product Folder"
            is_own_anchor = True
            collection_ordering = "NAME"
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
            parent_guid = "11311b9a-58f9-4d8e-94cd-616b809c5f66"
            parent_relationship_type_name = "CollectionMembership"
            parent_at_end1 = True
            display_name = "First Data Specification Collection"
            description = "First collection of data specs"
            collection_type = "Data Spec Collection"
            is_own_anchor = True
            collection_ordering = "NAME"
            order_property_name = None
            body = {
                # need to work this out
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
            parent_relationship_type_name = "DigitalServiceProduct"
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
                    "introductionDate": "12/31/23",
                    "maturity": "Nacent",
                    "serviceLife": "3 years",
                    "currentVersion": "V.5",
                    "nextVersion": "V.6",
                    "withdrawDate": "1/1/30",
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
            collection_guid = "08711623-711e-48f2-ba16-0cdf69b8f6f1"
            collection_type = "Radios"

            response = c_client.update_collection(collection_guid, collection_type = collection_type)
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
            collection_guid = "533a0346-b047-485a-82ea-05db671ab485"

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

    def test_delete_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "7886bb39-d600-42e0-992c-8792b8a696f8"
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
            collection_type = "Data Spec Collection"

            response = c_client.get_collections_by_type(collection_type)
            for member in response:
                c_client.delete_collection(member['elementHeader']["guid"])
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            response = c_client.get_collections_by_type(collection_type)
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

    def test_sample_setup(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2)

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # Create first folder for Agriculture Insights
            parent_guid = "97bbfe07-6696-4550-bf8b-6b577d25bef0"
            parent_relationship_type_name = "ResourceList"
            display_name = "Agriculture Insights Collection"
            description = "A folder for agricultural insights data product collections"
            collection_type = "Data Product Marketplace"

            folder1 = c_client.create_folder_collection(None, parent_guid,
                                                        parent_relationship_type_name,
                                                        True, display_name, description,
                                                        collection_type,True, "DATE_CREATED",
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
            parent_guid = folder2
            parent_relationship_type_name = "DigitalServiceProduct"
            display_name = "Land Use Classification"
            description = "Land use classification assets"
            collection_type = "Data Product Marketplace"
            classification_name = "Data Product Marketplace"
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
                        "introductionDate": "12/31/23",
                        "maturity": "Nacent",
                        "serviceLife": "3 years",
                        "currentVersion": "V.5",
                        "nextVersion": "V.6",
                        "withdrawDate": "1/1/30",
                        "additionalProperties": {
                            "thought_id": "a guid",
                            "license": "cc-by-sa",
                        }
                    }
            }


            folder3 = c_client.create_digital_product(body_3)
            print(f"\n\n created a collection with guid {folder3}")
            # create a fourth folder, child of folder 2, for Landsat 8
            parent_guid = folder3
            parent_relationship_type_name = "DigitalServiceProduct"
            display_name = "Landsat 8"
            description = "Landsat 8 data products"
            collection_type = "Data Product Marketplace"
            parent_relationship_type_name = "DigitalServiceProduct"
            classification_name = "Data Product Marketplace"

            body_4 = {
                {
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
                        "introductionDate": "12/31/23",
                        "maturity": "Mature",
                        "serviceLife": "3 years",
                        "currentVersion": "V1.5",
                        "nextVersion": "V1.6",
                        "withdrawDate": "1/1/30",
                        "additionalProperties": {
                            "thought_id": "a guid",
                            "license": "cc-by-sa",
                        }
                    }
                }
            }

            folder4 = c_client.create_digital_product(body_3)
            print(f"\n\n created a collection with guid {folder4}")

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

