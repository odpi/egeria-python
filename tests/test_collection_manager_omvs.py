"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module tests the CollectionManager class and methods

A running Egeria environment is needed to run these tests.

"""

import json
import time

from rich import print, print_json
from rich.console import Console

from pyegeria import (CollectionManager, InvalidParameterException, PropertyServerException, UserNotAuthorizedException,
                      print_exception_response, )

disable_ssl_warnings = True

console = Console(width=250)


class TestCollectionManager:
    good_platform1_url = "https://127.0.0.1:9443"

    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    good_user_3 = "peterprofile"
    bad_user_1 = "eviledna"
    bad_user_2 = ""
    good_server_1 = "simple-metadata-store"
    good_server_2 = "qs-view-server"
    good_server_3 = "active-metadata-store"
    good_engine_host_1 = "governDL01"
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            c_client.close_session()

    def test_find_collections(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            search_string = "*"

            response = c_client.find_collections(search_string, output_format="DICT", output_format_set="Collections")
            duration = time.perf_counter() - start_time

            print(f"\n\tNumber elements {len(response)} & Duration was {duration:.2f} seconds")
            if type(response) is list:
                print(f"Found {len(response)} collections {type(response)}\n\n")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                console.print(response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            c_client.close_session()

    def test_find_collections_w_body(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            # classification_name = "DataSharingAgreement"
            # classification_name = "ConnectorTypeDirectory"
            classification_name = None
            out_struct = {
                    "heading": "General Agreement Information",
                    "description": "Attributes generic to all Agreements.",
                    "aliases": [],
                    "formats": {"columns": [
                        {'name': 'Name', 'key': 'display_name'},
                        {'name': 'Qualified Name', 'key': 'qualified_name', 'format': True},
                        {'name': 'Super Category', 'key': 'category'},
                        {'name': 'My Description', 'key': 'description', 'format': True},
                        {'name': "Classifications", 'key': 'classifications'},
                        {'name': 'Members', 'key': 'members', 'format': True},
                        {'name': 'CreatedBy Meow', 'key': 'created_by'},
                        ],
                        "formats": ["ALL"]
                        },
                    "annotations": {"wikilinks": ["[[Agreements]]", "[[Egeria]]"]}
                }
            body = {
                "class": "FilterRequestBody",
                "asOfTime": None,
                "effectiveTime": None,
                "forLineage": False,
                "forDuplicateProcessing": False,
                "limitResultsByStatus": [],
                "sequencingOrder": "PROPERTY_ASCENDING",
                "sequencingProperty": "qualifiedName",
                "filter": None
                }

            response = c_client.find_collections_w_body(body,classification_name , output_format="DICT", output_format_set=out_struct)
            duration = time.perf_counter() - start_time

            print(f"\n\tNumber elements {len(response)} & Duration was {duration:.2f} seconds")
            if type(response) is list:
                print(f"Found {len(response)} collections {type(response)}\n\n")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                console.print(response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            c_client.close_session()

    def test_get_collection_by_name(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_name = "Dans Artifacts"

            response = c_client.get_collections_by_name(collection_name, output_format="DICT")
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            c_client.close_session()

    def test_get_collections_by_type(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_type = "*"
            classification_name = "DataSpec"

            response = c_client.get_collections_by_type(collection_type, classification_name, output_format="LIST")
            duration = time.perf_counter() - start_time

            print(f"\n\tNumber elements was {len(response)} & Duration was {duration:.2f} seconds")
            if type(response) is list:
                print_json(json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print_json("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            c_client.close_session()

    def test_get_collection_by_guid(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "21293d82-a394-46d8-9466-1c954f604c29"

            response = c_client.get_collection_by_guid(collection_guid, output_format="DICT")
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            c_client.close_session()

    def test_get_collection_graph(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )
            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "21293d82-a394-46d8-9466-1c954f604c29"

            response = c_client.get_collection_graph(collection_guid, output_format="REPORT")
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            c_client.close_session()

    def test_create_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            anchor_guid = None
            parent_guid = "f3e4de0e-320a-4b17-8581-b9613fa6cbbb"
            parent_relationship_type_name = "CollectionMembership"
            parent_at_end1 = True
            display_name = "Elecraft Radio collection"
            description = "Another collection of my Elecraft radios"
            collection_type = "Hobby Collection"
            is_own_anchor = True

            response = c_client.create_collection(display_name, description, is_own_anchor, None, None, None,
                parent_relationship_type_name, parent_at_end1, collection_type, None, )
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_create_collection_w_body(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            classification_name = "Set"
            body = {
                "class": "NewElementRequestBody", "anchorGUID": None, "isOwnAnchor": True,
                "parentGUID": "11311b9a-58f9-4d8e-94cd-616b809c5f66",
                "parentRelationshipTypeName": "CollectionMembership", "parentAtEnd1": True, "collectionProperties": {
                    "class": "CollectionFolderProperties", "name": "A radio collection",
                    "qualifiedName": f"{classification_name}-My Radios-{time.asctime()}",
                    "description": "A collection of my radios", "collectionType": "Hobby Collection"
                    },
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"
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

            response = c_client.create_root_collection(display_name, description, qualified_name, is_own_anchor,
                anchor_guid, parent_guid, parent_relationship_type_name)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
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

            additional_props = {
                "user": " dan", "location": "laz"
                }
            response = c_client.create_folder_collection(display_name, description, is_own_anchor)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_create_data_spec_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            anchor_guid = None
            parent_guid = None
            parent_relationship_type_name = "CollectionMembership"
            # parent_relationship_type_name = None
            parent_at_end1 = None
            # parent_at_end1 = None
            display_name = "MooClinical Trial Test Data Spec"
            description = "Test- Clinical Trials Specification"
            collection_type = "Test Data Specification"
            is_own_anchor = True

            anchor_scope_guid = None
            qualified_name = c_client.__create_qualified_name__("DataSpec", display_name)

            response = c_client.create_data_spec_collection(display_name, description, is_own_anchor,
                collection_type=collection_type)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

            def test_create_data_spec_collection(self):
                try:
                    c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                        user_id=self.good_user_2, )

                    token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
                    start_time = time.perf_counter()
                    anchor_guid = None
                    parent_guid = None
                    parent_relationship_type_name = "CollectionMembership"
                    # parent_relationship_type_name = None
                    parent_at_end1 = True
                    # parent_at_end1 = None
                    display_name = "Clinical Trial Data Spec"
                    description = "Clinical Trials Specification"
                    collection_type = "Data Specificationn"
                    is_own_anchor = True
                    anchor_scope_guid = None
                    qualified_name = c_client.__create_qualified_name__("DataSpec", display_name)

                    response = c_client.create_data_spec_collection(display_name, description, qualified_name,
                        is_own_anchor, anchor_guid, parent_guid, parent_relationship_type_name, parent_at_end1,
                        collection_type, anchor_scope_guid)
                    duration = time.perf_counter() - start_time
                    # resp_str = json.loads(response)
                    print(f"\n\tDuration was {duration} seconds\n")
                    if type(response) is dict:
                        print_json(json.dumps(response, indent=4))
                    elif type(response) is str:
                        print("\n\nGUID is: " + response)
                    assert True

                except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
                    print_exception_response(e)
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
            display_name = "Clinical Test"
            description = "Testing Clinical Trials Specification"
            collection_type = "Data Dictionary"
            is_own_anchor = True
            anchor_scope_guid = None
            qualified_name = c_client.__create_qualified_name__("DataDict", display_name)

            response = c_client.create_data_dictionary_collection(display_name, description, qualified_name,
                is_own_anchor, anchor_guid, parent_guid)

            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

            def test_create_data_spec_collection(self):
                try:
                    c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                        user_id=self.good_user_2, )

                    token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
                    start_time = time.perf_counter()
                    anchor_guid = None
                    parent_guid = None
                    parent_relationship_type_name = "CollectionMembership"
                    # parent_relationship_type_name = None
                    parent_at_end1 = True
                    # parent_at_end1 = None
                    display_name = "Clinical Trial Data Spec"
                    description = "Clinical Trials Specification"
                    collection_type = "Data Specificationn"
                    is_own_anchor = True

                    anchor_scope_guid = None
                    qualified_name = c_client.__create_qualified_name__("DataSpec", display_name)

                    response = c_client.create_data_spec_collection(display_name, description, qualified_name,
                        is_own_anchor, anchor_guid, parent_guid, parent_relationship_type_name, parent_at_end1,
                        collection_type, anchor_scope_guid)
                    duration = time.perf_counter() - start_time
                    # resp_str = json.loads(response)
                    print(f"\n\tDuration was {duration} seconds\n")
                    if type(response) is dict:
                        print_json(json.dumps(response, indent=4))
                    elif type(response) is str:
                        print("\n\nGUID is: " + response)
                    assert True

                except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
                    print_exception_response(e)
                    assert False, "Invalid request"
                finally:
                    c_client.close_session()

    def test_create_name_space_collection(self):
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
            display_name = "Austria"
            description = "A namespace collection"
            collection_type = "Namespaces"
            is_own_anchor = True
            anchor_scope_guid = None
            qualified_name = c_client.__create_qualified_name__("DataDict", display_name)

            response = c_client.create_name_space_collection(display_name, description, qualified_name, is_own_anchor,
                anchor_guid, parent_guid, collection_type=collection_type)

            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

            def test_create_data_spec_collection(self):
                try:
                    c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                        user_id=self.good_user_2, )

                    token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
                    start_time = time.perf_counter()
                    anchor_guid = None
                    parent_guid = None
                    parent_relationship_type_name = "CollectionMembership"
                    # parent_relationship_type_name = None
                    parent_at_end1 = True
                    # parent_at_end1 = None
                    display_name = "Clinical Trial Data Spec"
                    description = "Clinical Trials Specification"
                    collection_type = "Data Specificationn"
                    is_own_anchor = True
                    anchor_scope_guid = None
                    qualified_name = c_client.__create_qualified_name__("DataSpec", display_name)

                    response = c_client.create_data_spec_collection(display_name, description, qualified_name,
                        is_own_anchor, anchor_guid, parent_guid, parent_relationship_type_name, parent_at_end1,
                        collection_type, anchor_scope_guid,

                        )
                    duration = time.perf_counter() - start_time
                    # resp_str = json.loads(response)
                    print(f"\n\tDuration was {duration} seconds\n")
                    if type(response) is dict:
                        print_json(json.dumps(response, indent=4))
                    elif type(response) is str:
                        print("\n\nGUID is: " + response)
                    assert True

                except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
                    print_exception_response(e)
                    assert False, "Invalid request"
                finally:
                    c_client.close_session()

    def test_create_context_event_collection(self):
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
            display_name = "Audits"
            description = "Testing context events"
            collection_type = "Audit"
            is_own_anchor = True
            anchor_scope_guid = None
            qualified_name = c_client.__create_qualified_name__("DataDict", display_name)

            response = c_client.create_context_event_collection(display_name, description, qualified_name,
                is_own_anchor, anchor_guid, parent_guid, None, True, collection_type, anchor_scope_guid, )

            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

            def test_create_data_spec_collection(self):
                try:
                    c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                        user_id=self.good_user_2, )

                    token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
                    start_time = time.perf_counter()
                    anchor_guid = None
                    parent_guid = None
                    parent_relationship_type_name = "CollectionMembership"
                    # parent_relationship_type_name = None
                    parent_at_end1 = True
                    # parent_at_end1 = None
                    display_name = "Clinical Trial Data Spec"
                    description = "Clinical Trials Specification"
                    collection_type = "Data Specificationn"
                    is_own_anchor = True
                    anchor_scope_guid = None
                    qualified_name = c_client.__create_qualified_name__("DataSpec", display_name)

                    response = c_client.create_data_spec_collection(display_name, description, qualified_name,
                        is_own_anchor, anchor_guid, parent_guid, parent_relationship_type_name, parent_at_end1,
                        collection_type, anchor_scope_guid, )
                    duration = time.perf_counter() - start_time
                    # resp_str = json.loads(response)
                    print(f"\n\tDuration was {duration} seconds\n")
                    if type(response) is dict:
                        print_json(json.dumps(response, indent=4))
                    elif type(response) is str:
                        print("\n\nGUID is: " + response)
                    assert True

                except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
                    print_exception_response(e)
                    assert False, "Invalid request"
                finally:
                    c_client.close_session()

    def test_create_event_set_collection(self):
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
            display_name = "Events collection"
            description = "Testing  events"
            collection_type = "Events"
            is_own_anchor = True
            anchor_scope_guid = None
            qualified_name = c_client.__create_qualified_name__("DataDict", display_name)

            response = c_client.create_event_set_collection(display_name, description, qualified_name, is_own_anchor,
                anchor_guid, parent_guid, parent_relationship_type_name, parent_at_end1, collection_type,
                anchor_scope_guid, )

            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

            def test_create_data_spec_collection(self):
                try:
                    c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                        user_id=self.good_user_2, )

                    token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
                    start_time = time.perf_counter()
                    anchor_guid = None
                    parent_guid = None
                    parent_relationship_type_name = "CollectionMembership"
                    # parent_relationship_type_name = None
                    parent_at_end1 = True
                    # parent_at_end1 = None
                    display_name = "Clinical Trial Data Spec"
                    description = "Clinical Trials Specification"
                    collection_type = "Data Specificationn"
                    is_own_anchor = True
                    anchor_scope_guid = None
                    qualified_name = c_client.__create_qualified_name__("DataSpec", display_name)

                    response = c_client.create_data_spec_collection(display_name, description, qualified_name,
                        is_own_anchor, anchor_guid, parent_guid, parent_relationship_type_name, parent_at_end1,
                        collection_type, anchor_scope_guid, )
                    duration = time.perf_counter() - start_time
                    # resp_str = json.loads(response)
                    print(f"\n\tDuration was {duration} seconds\n")
                    if type(response) is dict:
                        print_json(json.dumps(response, indent=4))
                    elif type(response) is str:
                        print("\n\nGUID is: " + response)
                    assert True

                except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
                    print_exception_response(e)
                    assert False, "Invalid request"
                finally:
                    c_client.close_session()

    def test_create_naming_standard_ruleset_collection(self):
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
            display_name = "ruleset1"
            description = "a first ruleset"
            collection_type = "hoyle"
            is_own_anchor = True
            anchor_scope_guid = None
            qualified_name = c_client.__create_qualified_name__("DataDict", display_name)

            response = c_client.create_naming_standard_ruleset_collection(display_name, description, qualified_name,
                is_own_anchor, anchor_guid, parent_guid, None, True, collection_type, anchor_scope_guid, )

            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

            def test_create_data_spec_collection(self):
                try:
                    c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url,
                        user_id=self.good_user_2, )

                    token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
                    start_time = time.perf_counter()
                    anchor_guid = None
                    parent_guid = None
                    parent_relationship_type_name = "CollectionMembership"
                    # parent_relationship_type_name = None
                    parent_at_end1 = True
                    # parent_at_end1 = None
                    display_name = "Clinical Trial Data Spec"
                    description = "Clinical Trials Specification"
                    collection_type = "Data Specificationn"
                    is_own_anchor = True
                    anchor_scope_guid = None
                    qualified_name = c_client.__create_qualified_name__("DataSpec", display_name)

                    response = c_client.create_data_spec_collection(anchor_guid, parent_guid, qualified_name,
                        is_own_anchor, anchor_guid, parent_guid, parent_relationship_type_name, parent_at_end1,
                        collection_type, anchor_scope_guid, )
                    duration = time.perf_counter() - start_time
                    # resp_str = json.loads(response)
                    print(f"\n\tDuration was {duration} seconds\n")
                    if type(response) is dict:
                        print_json(json.dumps(response, indent=4))
                    elif type(response) is str:
                        print("\n\nGUID is: " + response)
                    assert True

                except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
                    print_exception_response(e)
                    assert False, "Invalid request"
                finally:
                    c_client.close_session()

    def test_create_collection_from_template(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

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

            body = {
                "class": "TemplateRequestBody", "parentGUID": parent_guid,
                "parentRelationshipTypeName": parent_relationship_type_name, "parentAtEnd1": True,
                "templateGUID": "c7368217-d013-43cb-9af1-b58e3a491e77", "replacementProperties": {
                    "class": "ElementProperties", "propertyValueMap": {
                        "qualifiedName": {
                            "class": "PrimitiveTypePropertyValue", "typeName": "string",
                            "primitiveTypeCategory": "OM_PRIMITIVE_TYPE_STRING",
                            "primitiveValue": f"templated-{display_name}-{time.asctime()}",
                            }, "name": {
                            "class": "PrimitiveTypePropertyValue", "typeName": "string",
                            "primitiveTypeCategory": "OM_PRIMITIVE_TYPE_STRING", "primitiveValue": display_name,
                            }, "description": {
                            "class": "PrimitiveTypePropertyValue", "typeName": "string",
                            "primitiveTypeCategory": "OM_PRIMITIVE_TYPE_STRING", "primitiveValue": description,
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_create_digital_product(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            parent_guid = "5d4fec06-f033-4743-bc50-06e7fd2eef10"
            parent_relationship_type_name = "CollectionMembership"
            display_name = "Sentinel1 Raw Data"
            description = "Raw Sentinel 1 data"
            collection_type = "Data Product Marketplace"

            body = {
                "class": "NewElementRequestBody", "isOwnAnchor": True, "parentGUID": parent_guid,
                "parentRelationshipTypeName": parent_relationship_type_name, "parentAtEnd1": True, "properties": {
                    "class": "DigitalProductProperties",
                    "qualifiedName": f"DigitalProduct::{collection_type}::{display_name}",
                    "userDefinedStatus": "ACTIVE", "name": "Land Use Classifications", "productType": "Periodic Delta",
                    "identifier": "sent1", "productName": "My sentinel 1", "serviceLife": "While budgets last",
                    "description": description, "introductionDate": "2023-12-31", "maturity": "Nacent",
                    "currentVersion": "V.5", "nextVersionDate": "2025-08-01", "withdrawDate": "2030-01-01",
                    "additionalProperties": {
                        "thought_id": "a guid", "license": "cc-by-sa",
                        }, "initialStatus": "DRAFT", "forLineage": False, "forDuplicateProcessing": False
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_get_collection_members(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = 'd4adc047-9005-471f-b2a1-e86201961e0b'

            response = c_client.get_collection_members(collection_guid=collection_guid, output_format="DICT")
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tNumber of elements returned was {len(response)} & Duration was {duration:.2f} seconds\n")
            if type(response) is list:
                print_json(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nResult is: " + response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_delete_collection(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            collection_guid = "e9b42536-a898-4141-9d41-1df73ea009ae"
            response = c_client.delete_collection(collection_guid, cascade=True)
            duration = time.perf_counter() - start_time
            print("\n\nCollection deleted successfully")
            print(f"\n\tDuration was {duration} seconds")

            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_delete_collection_type(self):
        try:
            c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2, )

            token = c_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            # collection_type = "Digital Product"
            # collection_type = "Product Catalog"
            # collection_type = "Digital Product Marketplace"
            # collection_type = "Data Spec Collection"
            # collection_type = "Medical Data"
            # collection_type = "Data Product Marketplace"
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
                    except (InvalidParameterException) as e:
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
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
            #         "description": description,  #         "collectionType": collection_type,  #
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
            # products"  # parent_relationship_type_name = "CollectionMembership"  # collection_type = "Digital
            # Product Marketplace"  #  # folder5 = c_client.create_folder_collection(  #     None,
            #     parent_guid,  #     parent_relationship_type_name,  #     True,  #     display_name,
            #     description,  #     collection_type,  #     True,  #     "DATE_CREATED",  #     None,
            # )  # # Create a DigitalProduct for Level-1B  # parent_guid = folder5  # display_name = "Sentinel 2 -
            # Level 1B"  # description = "Level 1B of Sentinel 2"  #  # body_6 = {  #     "class":
            # "NewDigitalProductRequestBody",  #     "anchor_guid": parent_guid,  #     "isOwnAnchor": False,
            #     "parentGUID": parent_guid,  #     "parentRelationshipTypeName": parent_relationship_type_name,
            #     "parentAtEnd1": True,  #     "collectionProperties": {  #         "class": "CollectionProperties",
            #         "qualifiedName": f"{classification_name}-{display_name}-{time.asctime()}",  #         "name":
            #         display_name,  #         "description": description,  #         "collectionType":
            #         collection_type,  #         "collectionOrdering": "DATE_CREATED",  #     },
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
            #         "collectionType": collection_type,  #         "collectionOrdering": "DATE_CREATED",  #     },
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
            #         "description": description,  #         "collectionType": collection_type,  #
            #         "collectionOrdering": "DATE_CREATED",  #     },  #     "digitalProductProperties": {  #
            #         "class": "DigitalProductProperties",  #         "productStatus": "ACTIVE",  #
            #         "productName": "Sentinel 2 - Level 1B",  #         "productType": "Geospatial Data Assets",
            #         "description": description,  #         "introductionDate": "2024-01-01",  #         "maturity":
            #         "Mature",  #         "serviceLife": "3 years",  #         "currentVersion": "V1.5",
            #         "nextVersion": "2024-06-01",  #         "withdrawDate": "2030-01-01",  #
            #         "additionalProperties": {  #             "thought_id": "a guid",  #             "license":
            #         "cc-by-sa",  #         },  #     },  # }  # folder8 = c_client.create_digital_product(body_8)
            # print(f"\n\n created a collection with guid {folder8}")  # assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()
