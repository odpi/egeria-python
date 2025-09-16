"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the glossary manager class and methods
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""

import asyncio
import json
import time
from contextlib import nullcontext as does_not_raise

import pytest
from pydantic import ValidationError

from pyegeria import PyegeriaException, print_exception_table, print_validation_error, \
    PyegeriaInvalidParameterException, print_basic_exception
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria.glossary_manager import GlossaryManager, GlossaryTermProperties
from pyegeria.core_omag_server_config import CoreServerConfig
from pyegeria.models import NewElementRequestBody
from tests.test_classification_manager_omvs import relationship_type
from tests.test_feedback_manager_omvs import password

# from pyegeria.admin_services import FullServerConfig

disable_ssl_warnings = True


class TestGlossaryManager:
    good_platform1_url = "https://127.0.0.1:9443"
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

    def test_create_glossary(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = g_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            start_time = time.perf_counter()
            display_name = "test"
            description = "A glossary used for test"
            language = "English"
            usage = "for testing purposes only"
            response = g_client.create_glossary(
                display_name, description, language, usage
            )
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nNew glossary {display_name} created with GUID of {response}")
            assert True
        except (
                PyegeriaException
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
        finally:
            g_client.close_session()

    def test_update_glossary(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = g_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            glossary_guid = "b336de33-ae66-4db9-b669-85c146c4b053"
            start_time = time.perf_counter()
            body = {
                "class": "UpdateElementRequestBody",
                "properties": {
                    "class": "GlossaryProperties",
                    "displayName": "puddys-universe",
                    "qualified_name": "Glossary:puddys-universe",
                },
            }

            g_client.update_glossary(glossary_guid, body)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nUpdated glossary {glossary_guid}")
            assert True
        except (
                    PyegeriaException
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
        finally:
            g_client.close_session()

    def test_delete_glossary(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = g_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            start_time = time.perf_counter()
            glossary_guid = "46ec84bc-7264-4cf4-86bc-253cca63e115"
            g_client.delete_glossary(glossary_guid, cascade = True)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nDeleted glossary {glossary_guid}")
            assert True
        except (
                    PyegeriaException
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()



    def test_create_term(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = g_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            start_time = time.perf_counter()
            glossary_guid ="6222f556-9123-4bb2-ba60-d2fe2b1d7fe9"
            qualified_name = "GlossaryTerm:test-term"
            prop_body = GlossaryTermProperties(class_ = "GlossaryTermProperties",
                                               display_name = "test-term",
                                                description = "A test term",
                                                qualified_name = qualified_name,
                                               summary = "a quick summary",
                                               abbreviation = "dt2",
                                               examples="an example",
                                               usage="an usage example",
                                               )

            body = NewElementRequestBody(class_ = "NewElementRequestBody",
                                         parent_guid= glossary_guid,
                                        is_own_anchor= True,
                                        anchor_scope_guid= glossary_guid,
                                        parent_relationship_type_name = "CollectionMembership",
                                        parent_at_end_1 = True,
                                        properties = prop_body.model_dump(exclude_none=True),
                                         )

            response = g_client.create_glossary_term(body)

            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")

            assert True
        except (
                    PyegeriaException
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
        finally:
            g_client.close_session()

    def test_create_term_copy(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = g_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            start_time = time.perf_counter()
            glossary_guid ="9bf9e61a-bc4f-4e52-ac2a-c5c46eda950e"
            term_guid = "e6bfae8b-07ad-44be-a4a4-0a4310cb8964"

            response = g_client.create_term_copy(glossary_guid, term_guid, "new-test1")

            duration = time.perf_counter() - start_time
            print(f"Response is: {response}")
            print(f"\n\tDuration was {duration} seconds")

            assert True
        except (
                    PyegeriaException
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
        finally:
            g_client.close_session()




    def test_add_is_abstract_concept(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = g_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )


            start_time = time.perf_counter()
            category_guid = "6d848f56-0332-4c8f-a048-9209d912809b"
            term_guid =  "a6247ae4-0606-4aa9-94e1-4f0b0713cc58"
            g_client.add_is_abstract_concept(term_guid)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            assert True
        except  (PyegeriaException, PyegeriaInvalidParameterException) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
        finally:
            g_client.close_session()


    def test_find_glossaries(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            response = g_client.find_glossaries(
                "*",
                starts_with=False,
                ends_with=False,
                ignore_case=True,
                page_size=0,
                output_format="JSON"
            )
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                # print("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                print(f"Found {count} glossaries")

                print(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
                    PyegeriaException
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()

    def test_get_glossary_by_guid(self, server: str = good_view_server_2):
        try:
            server_name = server
            g_client = GlossaryManager(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            # glossary_guid = "f9b78b26-6025-43fa-9299-a905cc6d1575"  # This is the sustainability glossary
            # glossary_guid = (
            #     "ab84bad2-67f0-4ec8-b0e3-76e638ec9f63"  # This is CIM glossary
            # )
            glossary_guid = '8f829009-376e-42ae-9f5d-32433755ff92'
            response = g_client.get_glossary_by_guid(glossary_guid)
            print(f"type is {type(response)}")
            if type(response) is dict:
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\n" + response)
            assert True
        except (
                    PyegeriaException
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

    def test_get_glossaries_by_name(self, server: str = good_view_server_2):
        try:
            server_name = server
            g_client = GlossaryManager(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            glossary_name = "Egeria-Markdown"

            response = g_client.get_glossaries_by_name(glossary_name)
            print(f"type is {type(response)}")
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))

            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
                    PyegeriaException
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()




    # def test_get_terms_for_glossary(self, server: str = good_view_server_1):
    #     server_name = server
    #     try:
    #         g_client = GlossaryManager(
    #             server_name, self.good_platform1_url, user_id="erinoverview"
    #         )
    #
    #         token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
    #         # glossary_guid = "f9b78b26-6025-43fa-9299-a905cc6d1575"  # This is the sustainability glossary
    #         # glossary_guid = "706ba88d-d0bb-42da-82d9-385b13516b34" # Teddy Bear Drop Foot
    #         # glossary_guid = (
    #         #     "c13e22d5-756a-4b54-b784-14037ee3dfc4"  # larger sustainability glossary
    #         # )
    #         glossary_guid = "65b43594-b105-49da-a59e-269e1fdb2f76"
    #
    #         start_time = time.perf_counter()
    #         response = g_client.get_terms_for_glossary(
    #             glossary_guid
    #         )
    #         print(f"Duration is {time.perf_counter()-start_time} seconds")
    #         print(f"type is {type(response)}")
    #         if type(response) is list:
    #             print("\n\n" + json.dumps(response, indent=4))
    #             count = len(response)
    #             print(f"Found {count} terms")
    #         elif type(response) is str:
    #             print("\n\n" + response)
    #         assert True
    #
    #     except (
    #                 PyegeriaException
    #     ) as e:
    #         print_exception_table(e)
    #         assert False, "Invalid request"
    #
    #     finally:
    #         g_client.close_session()

    def test_export_glossary_to_csv(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = g_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            start_time = time.perf_counter()
            glossary_guid = "70ae4d54-05bb-4411-96e6-697d0640a10e"
            file_name = f"/Users/dwolfson/localGit/test_export-{glossary_guid}.csv"
            response = g_client.export_glossary_to_csv(glossary_guid, file_name)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nExported {response} rows to {file_name}")
            assert True
        except (
                    PyegeriaException
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()

    def test_get_glossary_for_term(self, server: str = good_view_server_1):
        server_name = server

        try:
            g_client = GlossaryManager(
                server_name, self.good_platform1_url, user_id="erinoverview"
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            term_guid = "5467f5d4-d821-4fc2-ad71-8af7181826ff"
            response = g_client.get_glossary_for_term(term_guid)

            print(f"type is {type(response)}")
            if type(response) is dict:
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
                    PyegeriaException
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

    def test_get_terms_by_name(self, server: str = good_view_server_2):
        server_name = server

        try:
            g_client = GlossaryManager(
                server_name, self.good_platform1_url, user_id="erinoverview"
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            term_name = "Calico"
            glossary_guid = "70ae4d54-05bb-4411-96e6-697d0640a10e"
            response = g_client.get_terms_by_name(term_name)

            print(f"type is {type(response)}")
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
                    PyegeriaException
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

    def test_get_terms_by_guid(self, server: str = good_view_server_2):
        server_name = server

        try:
            g_client = GlossaryManager(
                server_name, self.good_platform1_url, user_id="erinoverview"
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            term_guid = "7bb48da4-f242-4deb-9293-375bb67bbbcf"

            response = g_client.get_term_by_guid(term_guid, output_format = 'JSON')

            print(f"type is {type(response)}")
            if type(response) is dict:
                print("\n\n" + json.dumps(response, indent=4))
                print(
                    f"Term name is: {response['properties']['displayName']}"
                )
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
                    PyegeriaException
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

    def test_find_glossary_terms(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_2, self.good_platform1_url, self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            # glossary_guid = "017dee20-b8ce-4d74-854b-f2a888a082cd" # small-email glossary
            # glossary_guid = (
            #     "f9b78b26-6025-43fa-9299-a905cc6d1575"  # sustainability glossary
            # )
            glossary_guid = None
            start_time = time.perf_counter()
            response = g_client.find_glossary_terms(
                "*",
                True,
                False,
                True,
                output_format="JSON",
                output_format_set = "Basic-Terms"
            )
            print(f"Duration is {time.perf_counter() - start_time} seconds")
            print(f"Number of terms is: {len(response)}")
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))
                # print_json_list_as_table(response)
                count = len(response)
                print(f"Found {count} terms")
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
                    PyegeriaException
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

    def test_update_term(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_2, self.good_platform1_url, self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            term_guid = "ecb57c19-fb1c-42f4-ab1a-c85b6fe753ea"  # meow
            body = {
                "class": "ReferenceableUpdateRequestBody",
                "elementProperties": {
                    "class": "GlossaryTermProperties",
                    "description": "With alieas",
                    "aliases" : ["t1","xt1"]
                },
            }

            start_time = time.perf_counter()
            g_client.update_term(term_guid, body, True)
            print(f"Duration is {time.perf_counter() - start_time} seconds")

            assert True

        except (
                    PyegeriaException
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()


    def test_load_terms_from_csv(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_2, self.good_platform1_url, self.good_user_3
            )
            token = g_client.create_egeria_bearer_token(self.good_user_3, "secret")
            glossary = "Egeria-Markdown"
            file_path = "/Users/dwolfson/localGit/egeria-v5-1/egeria-workspaces/exchange/loading-bay/glossary"
            file_name = "Test1.om-terms"
            response = g_client.load_terms_from_csv_file(glossary, file_name, file_path)
            print(f"type is {type(response)}")
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
             PyegeriaException,
            FileNotFoundError,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except Exception as e:
            print(e)

        finally:
            g_client.close_session()

    def test_delete_term(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = g_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            start_time = time.perf_counter()
            term_guid = "675d210c-3801-4555-9abe-99bdb45f000a"
            g_client.delete_term(term_guid)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nDeleted term {term_guid}")
            assert True
        except (
                    PyegeriaException
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()


    def test_add_term_to_folder(self, server: str = good_view_server_2):
        try:
            g_client = GlossaryManager(
                server, self.good_platform1_url, user_id=self.good_user_2
                )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")


            term = "d9476777-29de-4c3e-b999-5a0cac40b438"
            folder = "42dbd940-5a33-4620-b7af-af21404921fb"
            relationship_type = "Antonym"
            body = {
                "class": "RelationshipRequestBody",
                "properties": {
                    "class": "GlossaryTermRelationship",
                    # "confidence": 10,
                    # "description": "Why not",
                    # "status": "DRAFT",
                    # "steward": "Martha"
                }
            }

            g_client.add_term_to_folder(folder, term)

            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException,
                ) as e:
            print_exception_table(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

    def test_add_relationship_between_terms(self, server: str = good_view_server_2):
        try:
            g_client = GlossaryManager(
                server, self.good_platform1_url, user_id=self.good_user_2
                )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")


            guid1 = "16fe1b6f-b66c-490e-bc23-a47d0510b433"
            guid2 = "ecf8b8d6-e593-4240-839c-019b820f1897"
            relationship_type = "Antonym"
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "GlossaryTermRelationship"
                    # "confidence": 10,
                    # "description": "Why not",
                    # "status": "DRAFT",
                    # "steward": "Martha"
                }
            }

            g_client.add_relationship_between_terms(guid1, guid2, relationship_type)

            assert True

        except (PyegeriaException
                ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)

        finally:
            g_client.close_session()

    def test_update_relationship_between_terms(self, server: str = good_view_server_2):
        try:
            g_client = GlossaryManager(
                server, self.good_platform1_url, user_id=self.good_user_2
                )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            guid1 = "2852b4e1-4445-44ee-b3aa-dbd1e577cdcb"
            guid2 = "4961c79b-b040-4597-b0d3-5d32dd5f8935"
            relationship_type = "Synonym"
            body = {
                "class": "RelationshipRequestBody",
                "properties": {
                    "class": "GlossaryTermRelationship",
                    "confidence": 15,
                    "description": "Why not",
                    "status": "DRAFT",
                    "steward": "Martha"
                }
            }


            g_client.update_relationship_between_terms(guid1, guid2, relationship_type, body)

            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException,
                ) as e:
            print_exception_table(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

    def test_remove_relationship_between_terms(self, server: str = good_view_server_2):
        try:
            g_client = GlossaryManager(
                server, self.good_platform1_url, user_id=self.good_user_2
                )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            # guid1 = "2852b4e1-4445-44ee-b3aa-dbd1e577cdcb"
            # guid2 = "4961c79b-b040-4597-b0d3-5d32dd5f8935"
            guid1 = "46d4ad19-7627-4a8a-91b2-5b0a65ae328c"
            guid2 = "49e07289-d56f-4c45-9b87-e3d86c11d056"
            relationship_type = "Synonym"



            g_client.remove_relationship_between_terms(guid1, guid2, relationship_type)

            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException,
                ) as e:
            print_exception_table(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

    def test_remove_relationship_between_terms(self, server: str = good_view_server_2):
        try:
            g_client = GlossaryManager(
                server, self.good_platform1_url, user_id=self.good_user_2
                )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            # guid1 = "2852b4e1-4445-44ee-b3aa-dbd1e577cdcb"
            # guid2 = "4961c79b-b040-4597-b0d3-5d32dd5f8935"
            guid1 = "46d4ad19-7627-4a8a-91b2-5b0a65ae328c"
            guid2 = "49e07289-d56f-4c45-9b87-e3d86c11d056"
            relationship_type = "Synonym"

            resp = g_client.make_request("POST","http://localhost:8085/egeria/get_origin")
            print (resp)
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException,
                ) as e:
            print_exception_table(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()