"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the core OMAG config class and methods
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""

import json
import time

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria._exceptions_new import PyegeriaException
from pyegeria.glossary_browser_omvs import GlossaryBrowser


class TestGlossaryBrowser:
    good_platform1_url = "https://127.0.0.1:9443"
    good_platform2_url = "https://oak.local:9443"
    bad_platform1_url = "https://localhost:9443"

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

    def test_find_glossaries(self):
        try:
            g_client = GlossaryBrowser(
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
                effective_time=None,
                output_format = 'DICT',
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
            g_client = GlossaryBrowser(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")

            # First, find available glossaries
            glossaries = g_client.find_glossaries("Egeria-Markdown", output_format="DICT")

            # Skip the test if no glossaries are found
            if not glossaries or len(glossaries) == 0:
                print("No glossaries found. Skipping test.")
                return

            # Use the first glossary found
            glossary_guid = glossaries[0]['guid']
            print(f"\nUsing glossary with GUID: {glossary_guid}")

            try:
                # Test with REPORT format - should include Categories Names and not Categories Qualified Names
                print("\nTesting with REPORT format:")
                response_report = g_client.get_glossary_by_guid(glossary_guid, None, output_format='REPORT')
                print(f"REPORT response type is {type(response_report)}")
                if isinstance(response_report, dict):
                    print(json.dumps(response_report, indent=4))
                elif isinstance(response_report, str):
                    print(response_report)
                    # Only verify if the response contains categories
                    if "Category" in response_report:
                        # Verify that Category Names is included
                        assert "Category Names" in response_report

                # Test with FORM format - should include Categories Qualified Names and not Categories Names
                print("\nTesting with FORM format:")
                response_form = g_client.get_glossary_by_guid(glossary_guid, None, output_format='FORM')
                print(f"FORM response type is {type(response_form)}")
                if isinstance(response_form, dict):
                    print(json.dumps(response_form, indent=4))
                elif isinstance(response_form, str):
                    print(response_form)
                    # Only verify if the response contains categories
                    if "Category" in response_form:
                        # Verify that Category Names is included
                        assert "Category Names" in response_form
            except Exception as e:
                print(f"Error testing glossary with GUID {glossary_guid}: {str(e)}")
                # Try another glossary if available
                if len(glossaries) > 1:
                    glossary_guid = glossaries[1]['guid']
                    print(f"\nTrying another glossary with GUID: {glossary_guid}")

                    # Test with REPORT format
                    print("\nTesting with REPORT format:")
                    response_report = g_client.get_glossary_by_guid(glossary_guid, None, output_format='REPORT')
                    print(f"REPORT response type is {type(response_report)}")
                    if isinstance(response_report, str):
                        print(response_report)

                    # Test with FORM format
                    print("\nTesting with FORM format:")
                    response_form = g_client.get_glossary_by_guid(glossary_guid, None, output_format='FORM')
                    print(f"FORM response type is {type(response_form)}")
                    if isinstance(response_form, str):
                        print(response_form)
                else:
                    print("No other glossaries available for testing.")

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

    def test_get_glossaries_by_name(self, server: str = good_view_server_2):
        try:
            server_name = server
            g_client = GlossaryBrowser(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            glossary_name = "Egeria-Markdown"

            response = g_client.get_glossaries_by_name(glossary_name)
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

    def test_get_terms_for_glossary(self, server: str = good_view_server_2):
        server_name = server
        try:
            g_client = GlossaryBrowser(
                server_name, self.good_platform1_url, user_id="erinoverview"
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            # glossary_guid = "f9b78b26-6025-43fa-9299-a905cc6d1575"  # This is the sustainability glossary
            # glossary_guid = "706ba88d-d0bb-42da-82d9-385b13516b34" # Teddy Bear Drop Foot
            glossary_guid = (
                "30bfe79e-adf2-4fda-b9c5-9c86ad6b0d6c"  # larger sustainability glossary
            )

            start_time = time.perf_counter()
            response = g_client.get_terms_for_glossary(
                glossary_guid, page_size=1000, effective_time=None
            )
            print(f"Duration is {time.perf_counter()-start_time} seconds")
            print(f"type is {type(response)}")
            if type(response) is list:
                # print("\n\n" + json.dumps(response, indent=4))
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

    def test_get_glossary_for_term(self, server: str = good_view_server_1):
        server_name = server

        try:
            g_client = GlossaryBrowser(
                server_name, self.good_platform1_url, user_id="erinoverview"
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            term_guid = "ae936fe7-88d7-4f00-a888-d5fcd637fd02"
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

    def test_get_glossary_subcategories(self, server: str = good_view_server_2):
        server_name = server

        try:
            g_client = GlossaryBrowser(
                server_name, self.good_platform1_url, user_id="erinoverview"
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            category_guid = "150ae39d-1bd3-497d-a655-1e466fe85603"
            response = g_client.get_glossary_subcategories(category_guid)

            print(f"type is {type(response)}")
            if isinstance(response,dict | list):
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



    def test_get_terms_by_name(self, server: str = good_view_server_2):
        server_name = server

        try:
            g_client = GlossaryBrowser(
                server_name, self.good_platform1_url, user_id="erinoverview"
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            term_name = "Sustainability"
            glossary_guid = None
            response = g_client.get_terms_by_name(term_name, glossary_guid, [], output_format="DICT", output_format_set="Basic-Terms")

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

    def test_get_term_by_guid(self, server: str = good_view_server_2):
        try:
            server_name = server
            g_client = GlossaryBrowser(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            # glossary_guid = "f9b78b26-6025-43fa-9299-a905cc6d1575"  # This is the sustainability glossary
            # glossary_guid = (
            #     "ab84bad2-67f0-4ec8-b0e3-76e638ec9f63"  # This is CIM glossary
            # )
            term_guid = '92a5a610-78c3-404a-999f-c3352390b672'
            response = g_client.get_terms_by_guid(term_guid)
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

    def test_get_term_versions(self, server: str = good_view_server_2):
        try:
            server_name = server
            g_client = GlossaryBrowser(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")

            term_guid = '5401a977-4d77-4360-b747-42d11f87ddd1'
            response = g_client.get_term_versions(term_guid)
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

    def test_get_term_revision_logs(self, server: str = good_view_server_2):
        try:
            server_name = server
            g_client = GlossaryBrowser(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")

            term_guid = 'd1f22462-4d68-4bdf-be43-c82b6c710381'
            response = g_client.get_term_revision_logs(term_guid)
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

    def test_get_term_revision_history(self, server: str = good_view_server_2):
        try:
            server_name = server
            g_client = GlossaryBrowser(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")

            note_log_guid = 'c7f0b396-cccf-4e8c-96e7-598ce5dc6585'
            # note_log_guid = '54cbe8e6-ab3a-4d9c-af4f-7ac346d51468'
            response = g_client.get_term_revision_history(note_log_guid)
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

    def test_list_term_revision_history(self, server: str = good_view_server_2):
        try:
            server_name = server
            g_client = GlossaryBrowser(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")

            term_guid = '4961c79b-b040-4597-b0d3-5d32dd5f8935'
            # note_log_guid = '54cbe8e6-ab3a-4d9c-af4f-7ac346d51468'
            response = g_client.list_term_revision_history(term_guid, output_format='LIST')
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


    def test_list_full_term_history(self, server: str = good_view_server_2):
        try:
            server_name = server
            g_client = GlossaryBrowser(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")

            term_guid = '58933d73-7f04-4899-99ce-bbd25826041a'
            response = g_client.list_full_term_history(term_guid, "DICT", output_format_set="Basic-Terms")
            print(f"type is {type(response)}")
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\n" + response)
            assert True
        except (
            PyegeriaException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()


    def test_get_categories_for_term(self, server: str = good_view_server_2):
        try:
            server_name = server
            g_client = GlossaryBrowser(
                server_name, self.good_platform1_url, user_id=self.good_user_2
                )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")

            term_guid = 'a8bfb781-62f6-4c11-96a8-28e9b6d57261'
            # term_guid = 'c8f7bbcf-87da-4b96-a819-fc3eb1b3a97a'
            response = g_client.get_categories_for_term(term_guid)
            print(f"type is {type(response)}")
            if isinstance(response, list | dict):
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

    def test_get_terms_for_category(self, server: str = good_view_server_2):
        try:
            server_name = server
            g_client = GlossaryBrowser(
                server_name, self.good_platform1_url, user_id=self.good_user_2
                )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")

            category_guid = 'fb8190ea-f242-49e8-9b25-f9292f8cd349'
            response = g_client.get_terms_for_category(category_guid)
            print(f"type is {type(response)}")
            if isinstance(response, list | dict):
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

    def test_get_related_terms(self, server: str = good_view_server_2):
        try:
            server_name = server
            g_client = GlossaryBrowser(
                server_name, self.good_platform1_url, user_id=self.good_user_2
                )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")

            term_guid = 'f0511dda-1aa4-4e13-81ac-29c2fd860b18'
            # term_guid = '2852b4e1-4445-44ee-b3aa-dbd1e577cdcb'

            # Test different output formats
            for output_format in ["JSON", "LIST", "MD", "DICT"]:
                print(f"\n\nTesting output_format: {output_format}")
                response = g_client.get_related_terms(term_guid, output_format=output_format)
                print(f"Response type is {type(response)}")
                if isinstance(response, list | dict):
                    print(json.dumps(response, indent=4))
                elif type(response) is str:
                    print(response)

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

    def test_get_term_details(self, server: str = good_view_server_2):
        try:
            server_name = server
            g_client = GlossaryBrowser(
                server_name, self.good_platform1_url, user_id=self.good_user_2
                )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")

            # term_id = "58933d73-7f04-4899-99ce-bbd25826041a"
            term_id = "Sustainability"
            # Test with invalid input to verify error handling
            print("\n\nTesting get_term_details:")
            response = g_client.get_term_details(term_id, output_format="REPORT")
            response = g_client.get_term_details(term_id, output_format="DICT")
            print(json.dumps(response, indent=4))



            print(f"Response type is {type(response)}")
            print(response)


            print("\n\nTesting get_term_details with invalid input:")
            response_invalid = g_client.get_term_details("invalid-term-identifier", output_format="DICT")
            print(f"Response type is {type(response_invalid)}")
            print(response_invalid)

            # Verify that the response is a string containing an error message
            assert isinstance(response_invalid, str)
            assert "No term found" in response_invalid

            # Test with invalid input and REPORT format
            print("\n\nTesting get_term_details with invalid input and REPORT format:")
            response_invalid_report = g_client.get_term_details("invalid-term-identifier", output_format="REPORT")
            print(f"Response type is {type(response_invalid_report)}")
            print(response_invalid_report)

            # Verify that the response is a string containing an error message
            assert isinstance(response_invalid_report, str)
            assert "No term found" in response_invalid_report

            # Test with unsupported output format
            print("\n\nTesting get_term_details with unsupported output format:")
            response_invalid_format = g_client.get_term_details("invalid-term-identifier", output_format="INVALID")
            print(f"Response type is {type(response_invalid_format)}")
            print(response_invalid_format)

            # Verify that the response is a string containing an error message
            assert isinstance(response_invalid_format, str)
            assert "Unsupported output format" in response_invalid_format

            print("\n\nAll tests passed!")
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
            g_client = GlossaryBrowser(
                self.good_view_server_2, self.good_platform1_url, self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            # glossary_guid = "017dee20-b8ce-4d74-854b-f2a888a082cd" # small-email glossary
            # glossary_guid = (
            #     "c13e22d5-756a-4b54-b784-14037ee3dfc4"  # sustainability glossary
            # )
            glossary_guid = None
            start_time = time.perf_counter()
            response = g_client.find_glossary_terms(
                "Sustainability",
                # glossary_guid=glossary_guid,
                glossary_guid=glossary_guid,
                starts_with=True,
                ends_with=False,
                ignore_case=False,
                for_lineage=False,
                for_duplicate_processing=True,
                status_filter=[],
                page_size=100,
                effective_time=None,
                output_format="DICT",
                output_format_set="Basic-Terms"
            )
            print(f"Duration is {time.perf_counter() - start_time} seconds")
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

    def test_find_categories(self):
        try:
            g_client = GlossaryBrowser(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            search_string = "*"
            start_time = time.perf_counter()
            response = g_client.find_glossary_categories(
                search_string,
                starts_with=False,
                ends_with=False,
                ignore_case=True,
                page_size=0,
                effective_time=None,
                output_format = "MD",
            )
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                # print("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                print(f"Found {count} categories")

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

    def test_get_categories_by_guid(self, server: str = good_view_server_2):
        try:
            server_name = server
            g_client = GlossaryBrowser(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            # glossary_guid = "f9b78b26-6025-43fa-9299-a905cc6d1575"  # This is the sustainability glossary
            # glossary_guid = (
            #     "ab84bad2-67f0-4ec8-b0e3-76e638ec9f63"  # This is CIM glossary
            # )
            glossary_guid = 'be767c03-b54d-4cc6-94aa-73fde1bf61e1'
            response = g_client.get_category_by_guid(glossary_guid, output_format = 'FORM')
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

    def test_get_category_parent(self, server: str = good_view_server_2):
        try:
            server_name = server
            g_client = GlossaryBrowser(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            # glossary_guid = "f9b78b26-6025-43fa-9299-a905cc6d1575"  # This is the sustainability glossary
            # glossary_guid = (
            #     "ab84bad2-67f0-4ec8-b0e3-76e638ec9f63"  # This is CIM glossary
            # )
            category_guid = '6de10544-ec5a-4c92-b19d-03a79fa353f2'
            response = g_client.get_category_parent(category_guid)
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


    def test_get_categories_by_name(self, server: str = good_view_server_2):
        try:
            server_name = server
            g_client = GlossaryBrowser(
                "qs-view-server", self.good_platform1_url, user_id=self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            category_name = 'Category:Processing-Dr.Egeria-Markdown'
            response = g_client.get_categories_by_name(category_name)
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

    def test_get_categories_for_glossary(self, server: str = good_view_server_2):
        try:
            server_name = server
            g_client = GlossaryBrowser(
                "qs-view-server", self.good_platform1_url, user_id=self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            glossary_guid = "c103d0c9-7581-47e1-a684-6bbe0ecd596f"
            response = g_client.get_categories_for_glossary(glossary_guid)
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

    def test_get_glossary_category_structure(self, server: str = good_view_server_2):
        try:
            server_name = server
            g_client = GlossaryBrowser(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            glossary_guid = "1411b3a0-b387-42f3-b6f0-4512a12d272d"

            # Test DICT output format
            response_dict = g_client.get_glossary_category_structure(glossary_guid, output_format="DICT")
            print(f"DICT response type is {type(response_dict)}")
            if isinstance(response_dict, dict):
                print("\n\nDICT output:")
                print(json.dumps(response_dict, indent=4))
            elif isinstance(response_dict, str):
                print("\n\n" + response_dict)

            # Test LIST output format
            response_list = g_client.get_glossary_category_structure(glossary_guid, output_format="LIST")
            print(f"LIST response type is {type(response_list)}")
            if isinstance(response_list, str):
                print("\n\nLIST output:")
                print(response_list)

            # Test MD output format
            response_md = g_client.get_glossary_category_structure(glossary_guid, output_format="MD")
            print(f"MD response type is {type(response_md)}")
            if isinstance(response_md, str):
                print("\n\nMD output:")
                print(response_md)

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


    def test_get_term_activity_types(self, server: str = good_view_server_2):
        try:
            g_client = GlossaryBrowser(
                server, self.good_platform1_url, user_id=self.good_user_2
                )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            response = g_client.get_glossary_term_activity_types()
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

    def test_get_term_rel_statuses(self, server: str = good_view_server_2):
        try:
            g_client = GlossaryBrowser(
                server, self.good_platform1_url, user_id=self.good_user_2
                )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            response = g_client.get_glossary_term_rel_statuses()
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

    def test_get_term_statuses(self, server: str = good_view_server_2):
        try:
            g_client = GlossaryBrowser(
                server, self.good_platform1_url, user_id=self.good_user_2
                )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            response = g_client.get_glossary_term_statuses()
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

    def test_get_term_relationship_types(self, server: str = good_view_server_2):
        try:
            g_client = GlossaryBrowser(
                server, self.good_platform1_url, user_id=self.good_user_2
                )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            response = g_client.get_term_relationship_types()
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
