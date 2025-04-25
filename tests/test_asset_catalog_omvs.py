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

from pyegeria import INTEGRATION_GUIDS, TEMPLATE_GUIDS
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria.asset_catalog_omvs import AssetCatalog

# from pyegeria.md_processing_utils import print_json_list_as_table

# from pyegeria.admin_services import FullServerConfig

disable_ssl_warnings = True


class TestAssetCatalog:
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
    good_view_server_2 = "qs-view-server"
    bad_server_1 = "coco"
    bad_server_2 = ""

    def test_find_in_asset_domain(self):
        try:
            g_client = AssetCatalog(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            search_string = "Unity"
            response = g_client.find_in_asset_domain(
                search_string, starts_with=True, ends_with=False, ignore_case=True
            )
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                # print("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                print(f"Found {count} asset")
                for i in range(count):
                    # print(f"Found asset: {response[i]['glossaryProperties']['qualifiedName']} with id of {response[i]['elementHeader']['guid']}")
                    print(json.dumps(response[i], indent=4))
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

    def test_find_several_in_asset_domain(self):
        try:
            g_client = AssetCatalog(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            asset = ["Set up new clinical trial", "unity", "number", "week"]

            for a in asset:
                start_time = time.perf_counter()
                response = g_client.find_in_asset_domain(
                    a,
                    starts_with=True,
                    ends_with=False,
                    ignore_case=False,
                    time_out=120,
                )
                duration = time.perf_counter() - start_time

                if type(response) is list:
                    # print("\n\n" + json.dumps(response, indent=4))
                    count = len(response)
                    print(f"Found {count} assets for search {a} in {duration} seconds")
                    # for i in range(count):
                    #     # print(f"Found asset: {response[i]['glossaryProperties']['qualifiedName']} with id of {response[i]['elementHeader']['guid']}")
                    #     print(json.dumps(response[i], indent=4))
                elif type(response) is str:
                    print("\n\n" + response)

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()

    def test_get_asset_graph(self, server: str = good_view_server_1):
        try:
            server_name = server
            asset_guid = "8a578f0d-f7ae-4255-b4a5-236241fa5449"
            a_client = AssetCatalog(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = a_client.create_egeria_bearer_token(self.good_user_2, "secret")

            response = a_client.get_asset_graph(asset_guid)
            print(f"type is {type(response)}")
            if type(response) is dict:
                print("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                print(f"Found {count} assets")
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
            a_client.close_session()

    def test_get_asset_mermaid_graph(self, server: str = good_view_server_1):
        try:
            server_name = server
            asset_guid = "8a578f0d-f7ae-4255-b4a5-236241fa5449"
            a_client = AssetCatalog(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = a_client.create_egeria_bearer_token(self.good_user_2, "secret")

            response = a_client.get_asset_mermaid_graph(asset_guid)
            print(f"type is {type(response)}")
            if type(response) is dict:
                print("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                print(f"Found {count} pieces")
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
            a_client.close_session()

    def test_get_asset_lineage_graph(self, server: str = good_view_server_2):
        try:
            server_name = server
            asset_guid = "8a578f0d-f7ae-4255-b4a5-236241fa5449"
            a_client = AssetCatalog(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = a_client.create_egeria_bearer_token(self.good_user_2, "secret")

            effective_time = None
            as_of_time = None
            relationship_types = None
            limit_to_isc_q_name = "InformationSupplyChain:Sustainability Reporting"
            hilight_isc_q_name = None

            response = a_client.get_asset_lineage_graph(asset_guid, effective_time,
                                                        as_of_time, relationship_types,
                                                        limit_to_isc_q_name, hilight_isc_q_name,
                                                        )
            print(f"type is {type(response)}")
            if type(response) is dict:
                print("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                print(f"Found {count} pieces")
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
            a_client.close_session()

    def test_get_asset_lineage_mermaid_graph(self, server: str = good_view_server_1):
        try:
            server_name = server
            asset_guid = "8a578f0d-f7ae-4255-b4a5-236241fa5449"
            a_client = AssetCatalog(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = a_client.create_egeria_bearer_token(self.good_user_2, "secret")

            response = a_client.get_asset_lineage_mermaid_graph(asset_guid)
            print(f"type is {type(response)}")
            if type(response) is dict:
                print("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                print(f"Found {count} pieces")
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
            a_client.close_session()

    def test_get_assets_by_metadata_collection_id(
        self, server: str = good_view_server_1
    ):
        try:
            server_name = server
            metadata_collection_id = (
                "74a786b2-d6d7-401d-b8c1-7d798f752c55"  # Coco Template Archive
            )
            a_client = AssetCatalog(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = a_client.create_egeria_bearer_token(self.good_user_2, "secret")

            response = a_client.get_assets_by_metadata_collection_id(
                metadata_collection_id, "SoftwareServer"
            )
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
            a_client.close_session()

    def test_get_asset_catalog_types(self, server: str = good_view_server_1):
        try:
            server_name = server
            a_client = AssetCatalog(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = a_client.create_egeria_bearer_token(self.good_user_2, "secret")

            response = a_client.get_asset_catalog_types()
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
            a_client.close_session()

    def test_create_folder_asset_body(self, server: str = good_view_server_1):
        try:
            server_name = server
            a_client = AssetCatalog(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = a_client.create_egeria_bearer_token(self.good_user_2, "secret")
            body = {
                "templateGUID": TEMPLATE_GUIDS["FileFolder template"],
                "isOwnAnchor": True,
                "placeholderPropertyValues": {
                    "clinicalTrialId": "TransMorg-1",
                    "clinicalTrialName": "TransMorgification",
                    "hospitalName": "Bedlam",
                    "deployedImplementationType": "FileFolder",
                    "fileSystemName": "Bedlam-Hospital-Systems",
                    "directoryName": "TransMorg-Clinical-Trials-Weeklies",
                    "directoryPathName": "Dungeon/lab",
                    "contactName": "Dr Jekyll",
                    "contactDept": "Pharmacology",
                    "dateReceived": "23-06-24",
                    "description": "Clinical trial data folder",
                },
            }

            response = a_client.create_element_from_template(body)
            print(f"type is {type(response)}")
            if type(response) is dict:
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
            a_client.close_session()
