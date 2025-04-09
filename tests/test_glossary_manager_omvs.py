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

from pyegeria import GlossaryManager
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria.core_omag_server_config import CoreServerConfig
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
                self.good_view_server_1,
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
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()

    def test_update_glossary(self):
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
            glossary_guid = "70ae4d54-05bb-4411-96e6-697d0640a10e"
            start_time = time.perf_counter()
            body = {
                "class": "ReferenceableRequestBody",
                "elementProperties": {
                    "class": "GlossaryProperties",
                    "displayName": "puddys-universe",
                    "qualified_name": "Glossary:puddys-universe",
                },
            }

            g_client.update_glossary(glossary_guid, body, True)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nUpdated glossary {glossary_guid}")
            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()

    def test_delete_glossary(self):
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
            glossary_guid = "2a7b7423-335b-4b0f-9dfe-af73621b465d"
            g_client.delete_glossary(glossary_guid)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nDeleted glossary {glossary_guid}")
            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()

    #
    #       Catagories
    #
    def test_create_category(self):
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
            display_name = "category1"
            description = "A category used for test"
            glossary_guid = "2acae812-5a0d-431f-806d-a874cd2da64d" # Egeria-Markdown
            response = g_client.create_category(
                glossary_guid,display_name, description,
            )
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nNew category {display_name} created with GUID of {response}")
            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()

    def test_update_category(self):
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
            category_guid = "264432d9-609f-4b88-a484-af482895c0a5"
            display_name = "puddys-universe"
            description = "A category used for testing"
            update_description = "Updated description and display name"

            start_time = time.perf_counter()


            g_client.update_category(category_guid, display_name, description, update_description=update_description
                                     )
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nUpdated glossary {display_name}, {category_guid}")
            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()

    def test_delete_category(self):
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
            category_guid = "264432d9-609f-4b88-a484-af482895c0a5"
            g_client.delete_category(category_guid)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nDeleted category {category_guid}")
            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()

    def test_set_parent_category(self):
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
            parent_guid = "e14b80c6-346c-4e7c-89c6-b5ed92ddbd33"
            child_guid = "e164ba97-f5eb-42f2-b52e-cd72f484d18d"
            start_time = time.perf_counter()

            g_client.set_parent_category(parent_guid, child_guid)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nLinked category {child_guid} to parent {parent_guid}")
            assert True
        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException,
                ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()

    def test_add_term_to_category(self):
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
            # term_guid = "16400f1d-657c-4949-91ff-cd018c429b8d" # Directive
            term_guid = "367300ea-b11e-41bb-ba16-1de1aead75dd" # Command
            g_client.add_term_to_category(term_guid, category_guid)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nAdded term to category {category_guid}")
            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()

    def test_remove_term_from_category(self):
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
            term_guid = "16400f1d-657c-4949-91ff-cd018c429b8d"
            g_client.remove_term_from_category(term_guid, category_guid)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nAdded term to category {category_guid}")
            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()








    def test_find_glossaries(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            response = g_client.find_glossaries(
                # "*",
                "Sustainability Glossary",
                starts_with=False,
                ends_with=False,
                ignore_case=True,
                page_size=0,
                effective_time=None,
            )
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                # print("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                print(f"Found {count} glossaries")
                for i in range(count):
                    print(
                        f"Found glossary: {response[i]['glossaryProperties']['qualifiedName']} with id of {response[i]['elementHeader']['guid']}"
                    )
                print(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
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
            glossary_guid = '805afd91-7ed2-4fb8-bc2e-c2d4def5b98f'
            response = g_client.get_glossary_by_guid(glossary_guid)
            print(f"type is {type(response)}")
            if type(response) is dict:
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\n" + response)
            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

    def test_get_glossaries_by_name(self, server: str = good_view_server_1):
        try:
            server_name = server
            g_client = GlossaryManager(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            glossary_name = "puddys-universe"

            response = g_client.get_glossaries_by_name(glossary_name)
            print(f"type is {type(response)}")
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))

            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()




    def test_get_terms_for_glossary(self, server: str = good_view_server_1):
        server_name = server
        try:
            g_client = GlossaryManager(
                server_name, self.good_platform1_url, user_id="erinoverview"
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            # glossary_guid = "f9b78b26-6025-43fa-9299-a905cc6d1575"  # This is the sustainability glossary
            # glossary_guid = "706ba88d-d0bb-42da-82d9-385b13516b34" # Teddy Bear Drop Foot
            # glossary_guid = (
            #     "c13e22d5-756a-4b54-b784-14037ee3dfc4"  # larger sustainability glossary
            # )
            glossary_guid = "70ae4d54-05bb-4411-96e6-697d0640a10e"

            start_time = time.perf_counter()
            response = g_client.get_terms_for_glossary(
                glossary_guid, page_size=500, effective_time=None
            )
            print(f"Duration is {time.perf_counter()-start_time} seconds")
            print(f"type is {type(response)}")
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                print(f"Found {count} terms")
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

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
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
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
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

    def test_get_terms_by_name(self, server: str = good_view_server_1):
        server_name = server

        try:
            g_client = GlossaryManager(
                server_name, self.good_platform1_url, user_id="erinoverview"
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            term_name = "GlossaryTerm: puddie - 2024-10-18T13:51:52.356216"
            glossary_guid = "70ae4d54-05bb-4411-96e6-697d0640a10e"
            response = g_client.get_terms_by_name(term_name, glossary_guid, ["DRAFT"])

            print(f"type is {type(response)}")
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
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
            term_guid = "a9c7112f-f199-4f76-a9e6-aa7cee77f008"
            response = g_client.get_terms_by_guid(term_guid, output_format = 'form')

            print(f"type is {type(response)}")
            if type(response) is dict:
                print("\n\n" + json.dumps(response, indent=4))
                print(
                    f"Term name is: {response['glossaryTermProperties']['displayName']}"
                )
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
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
                glossary_guid=glossary_guid,
                starts_with=True,
                ends_with=False,
                for_lineage=False,
                ignore_case=True,
                for_duplicate_processing=True,
                status_filter=[],
                page_size=10,
                effective_time=None,
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
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

    def test_update_term(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_1, self.good_platform1_url, self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            term_guid = "a27b20a9-3c1a-4d80-b92f-9c877c193385"  # meow
            body = {
                "class": "ReferenceableUpdateRequestBody",
                "elementProperties": {
                    "class": "GlossaryTermProperties",
                    "description": "Woof Woof",
                },
            }

            start_time = time.perf_counter()
            g_client.update_term(term_guid, body, True)
            print(f"Duration is {time.perf_counter() - start_time} seconds")

            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

    def test_undo_update_term(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_1, self.good_platform1_url, self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            term_guid = "a27b20a9-3c1a-4d80-b92f-9c877c193385"  # meow

            start_time = time.perf_counter()
            g_client.undo_term_update(term_guid)
            print(f"Duration is {time.perf_counter() - start_time} seconds")

            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
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
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
            FileNotFoundError,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        except Exception as e:
            print(e)

        finally:
            g_client.close_session()

    def test_delete_term(self):
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
            term_guid = "50c7668a-9cef-4c1e-bd9d-dde99c03a310"
            g_client.delete_term(term_guid)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nDeleted term {term_guid}")
            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()
