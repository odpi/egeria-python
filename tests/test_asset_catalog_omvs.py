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

from pyegeria import PyegeriaException, print_basic_exception, PyegeriaInvalidParameterException
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria.asset_catalog import AssetCatalog
from pyegeria.automated_curation import AutomatedCuration
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
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            search_string = "Postgres"
            response = g_client.find_in_asset_domain(
                search_string, starts_with=True, ends_with=False, ignore_case=True, output_format="DICT",report_spec="Referenceable"
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
            PyegeriaException, PyegeriaInvalidParameterException,
        ) as e:
            print_basic_exception(e)
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

    def test_get_asset_graph(self, server: str = good_view_server_2):
        try:
            server_name = server
            asset_guid = "315ffa25-fa2e-4e20-a11c-df57f093db1b"
            a_client = AssetCatalog(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = a_client.create_egeria_bearer_token(self.good_user_2, "secret")

            response = a_client.get_asset_graph(asset_guid, output_format="JSON", report_spec="Asset-Graph")
            print(f"type is {type(response)}")
            if isinstance(response, dict | list):
                print("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                print(f"Found {count} assets")
            elif type(response) is str:
                print("\n\n" + response)
            assert True
        except (
            PyegeriaException, PyegeriaInvalidParameterException,
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_asset_mermaid_graph(self, server: str = good_view_server_2):
        try:
            server_name = server
            asset_guid = "525733dc-76f0-4b38-8e64-9677397b92d1"
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
            PyegeriaException, PyegeriaInvalidParameterException,
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_asset_lineage_graph(self, server: str = good_view_server_2):
        try:
            server_name = server
            asset_guid = "890d26a8-a740-42c0-8585-801274bbf8f1"
            a_client = AssetCatalog(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = a_client.create_egeria_bearer_token(self.good_user_2, "secret")

            effective_time = None
            as_of_time = None
            relationship_types = None
            limit_to_isc_q_name = None
            hilight_isc_q_name = None

            response = a_client.get_asset_lineage_graph(asset_guid, effective_time,
                                                        as_of_time, relationship_types,
                                                        limit_to_isc_q_name, hilight_isc_q_name,
                                                        all_anchors = False, start_from = 0, page_size = 0, output_format="DICT",
                                                        report_spec = "Common-Mermaid"

                                                        )
            print(f"type is {type(response)}")
            if isinstance(response, dict | list):
                print("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                print(f"Found {count} pieces")
            elif type(response) is str:
                print("\n\n" + response)
            assert True
        except (
            PyegeriaException, PyegeriaInvalidParameterException,
        ) as e:
            print_basic_exception(e)
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
        self, server: str = good_view_server_2
    ):
        try:
            server_name = server
            metadata_collection_id = (
                "9905c3cb-94c5-4494-9229-0d6f69c0b842"  # Coco Template Archive
            )
            a_client = AssetCatalog(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )
            # type_name = "SoftwareServer"
            type_name = "FileFolder"
            token = a_client.create_egeria_bearer_token(self.good_user_2, "secret")

            response = a_client.get_assets_by_metadata_collection_id(
                metadata_collection_id, type_name, output_format="DICT",report_spec="Referenceable"
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

    def test_get_asset_catalog_types(self, server: str = good_view_server_2):
        try:
            server_name = server
            a_client = AssetCatalog(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = a_client.create_egeria_bearer_token(self.good_user_2, "secret")

            response = a_client.get_asset_types()
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
            b_client = AutomatedCuration(server_name, self.good_platform1_url, user_id=self.good_user_2)


            token = a_client.create_egeria_bearer_token(self.good_user_2, "secret")
            token = b_client.create_egeria_bearer_token(self.good_user_2, "secret")
            file_folder_template_guid = b_client.get_template_guid_for_technology_type(
                "FileFolder template"
            )
            body = {
                "templateGUID": file_folder_template_guid,
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
