"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the glossary manager class and methods
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""
import time

import pytest
import asyncio
import json

from contextlib import nullcontext as does_not_raise

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

from pyegeria.core_omag_server_config import CoreServerConfig

from pyegeria.glossary_browser_omvs import GlossaryBrowser
from pyegeria.utils import print_json_list_as_table

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

    def test_find_glossaries(self):
        try:
            g_client = GlossaryBrowser(self.good_view_server_1, self.good_platform1_url,
                                       user_id=self.good_user_2)

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            response = g_client.find_glossaries('*', starts_with=False, ends_with=False,
                                                ignore_case=True,page_size=0, effective_time=None)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                # print("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                print(f"Found {count} glossaries")
                for i in range(count):
                    print(f"Found glossary: {response[i]['glossaryProperties']['qualifiedName']} with id of {response[i]['elementHeader']['guid']}")
                    # print(json.dumps(response[i],indent = 4))
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
            g_client.close_session()

    def test_get_glossary_by_guid(self, server:str = good_view_server_1):
        try:
            server_name = server
            g_client = GlossaryBrowser(server_name, self.good_platform1_url,
                                       user_id=self.good_user_2)

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            glossary_guid = "f9b78b26-6025-43fa-9299-a905cc6d1575"  # This is the sustainability glossary
            response = g_client.get_glossary_by_guid(glossary_guid, server_name)
            print(f"type is {type(response)}")
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                print(f"Found {count} terms")
            elif type(response) is str:
                print("\n\n" + response)
            assert True
        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
                print_exception_response(e)
                assert False, "Invalid request"
        
        finally:
            g_client.close_session()


    def test_get_glossaries_by_name(self, server: str = good_view_server_1):
        try:
            server_name = server
            g_client = GlossaryBrowser(server_name, self.good_platform1_url,
                                       user_id=self.good_user_2)

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            glossary_name = "Sustainability Glossary"

            response = g_client.get_glossaries_by_name(glossary_name)
            print(f"type is {type(response)}")
            if type(response) is dict:
                print("\n\n" + json.dumps(response, indent=4))

            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
                print_exception_response(e)
                assert False, "Invalid request"
        
        finally:
            g_client.close_session()


    def test_get_terms_for_glossary(self, server:str = good_view_server_1):
        server_name = server
        try:
            g_client = GlossaryBrowser(server_name, self.good_platform1_url,
                                       user_id="erinoverview")

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            # glossary_guid = "f9b78b26-6025-43fa-9299-a905cc6d1575"  # This is the sustainability glossary
            # glossary_guid = "706ba88d-d0bb-42da-82d9-385b13516b34" # Teddy Bear Drop Foot
            glossary_guid = "c13e22d5-756a-4b54-b784-14037ee3dfc4" # larger sustainability glossary

            start_time = time.perf_counter()
            response = g_client.get_terms_for_glossary(glossary_guid, page_size=500, effective_time=None)
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
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
            
        finally:
            g_client.close_session()


    def test_get_glossary_for_term(self, server:str = good_view_server_1):
        server_name = server

        try:
            g_client = GlossaryBrowser(server_name, self.good_platform1_url,
                                       user_id="erinoverview")

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
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
            
        finally:
            g_client.close_session()


    def test_get_terms_by_name(self, server:str = good_view_server_1):
        server_name = server

        try:
            g_client = GlossaryBrowser(server_name, self.good_platform1_url,
                                       user_id="erinoverview")

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            term_name = "Facility"
            glossary_guid = "f9b78b26-6025-43fa-9299-a905cc6d1575"
            response = g_client.get_terms_by_name(term_name, glossary_guid, ["ACTIVE"])

            print(f"type is {type(response)}")
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))
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
            g_client.close_session()


    def test_find_glossary_terms(self):
        try:
            g_client = GlossaryBrowser(self.good_view_server_1, self.good_platform1_url,sync_mode=True)

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            # glossary_guid = "017dee20-b8ce-4d74-854b-f2a888a082cd" # small-email glossary
            glossary_guid = "f9b78b26-6025-43fa-9299-a905cc6d1575"  # sustainability glossary
            start_time = time.perf_counter()
            response = g_client.find_glossary_terms('*', glossary_guid=glossary_guid, starts_with=True,
                                                    ends_with= False, for_lineage=False, for_duplicate_processing=True,
                                                    status_filter=[], page_size=10, effective_time=None)
            print(f"Duration is {time.perf_counter() - start_time} seconds")
            if type(response) is list :
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
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
            
        finally:
            g_client.close_session()



