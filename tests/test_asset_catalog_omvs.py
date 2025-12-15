"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module tests the AssetCatalog class and methods from asset_catalog.py

A running Egeria environment is needed to run these tests.

"""
import json
import time
from datetime import datetime

from rich import print, print_json
from rich.console import Console

from pyegeria import PyegeriaException, print_basic_exception, PyegeriaInvalidParameterException
from pyegeria._exceptions import (
    PyegeriaInvalidParameterException,
    PyegeriaConnectionException,
    PyegeriaAPIException,
    PyegeriaNotFoundException,
    PyegeriaUnauthorizedException,
    print_basic_exception,
    print_exception_table,
    print_validation_error,
)
from pyegeria.logging_configuration import config_logging, init_logging
from pyegeria.asset_catalog import AssetCatalog
from pydantic import ValidationError

disable_ssl_warnings = True

console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "erinoverview"
USER_PWD = "secret"


class TestAssetCatalog:
    good_platform1_url = PLATFORM_URL

    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    good_user_3 = "peterprofile"
    good_server_1 = "simple-metadata-store"
    good_server_2 = "laz_kv"
    good_view_server_1 = "view-server"
    good_view_server_2 = VIEW_SERVER

    def test_find_in_asset_domain(self):
        """Test finding assets in the asset domain with search string"""
        asset_client = None
        try:
            asset_client = AssetCatalog(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = asset_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            search_string = "Postgres"
            response = asset_client.find_in_asset_domain(
                search_string,
                starts_with=True,
                ends_with=False,
                ignore_case=True,
                output_format="DICT",
                report_spec="Referenceable"
            )
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                count = len(response)
                print(f"Found {count} assets")
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nResponse: " + response)
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            if asset_client:
                asset_client.close_session()

    def test_find_multiple_assets(self):
        """Test finding multiple different assets with various search strings"""
        asset_client = None
        try:
            asset_client = AssetCatalog(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = asset_client.create_egeria_bearer_token(self.good_user_2, "secret")

            search_terms = ["Unity", "File", "number", "week"]

            for term in search_terms:
                start_time = time.perf_counter()
                response = asset_client.find_in_asset_domain(
                    term,
                    starts_with=True,
                    ends_with=False,
                    ignore_case=False,
                    output_format="JSON"
                )
                duration = time.perf_counter() - start_time

                if type(response) is list:
                    count = len(response)
                    print(f"Found {count} assets for search '{term}' in {duration:.2f} seconds")
                elif type(response) is str:
                    print(f"Response for '{term}': {response}")

            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            if asset_client:
                asset_client.close_session()

    def test_get_asset_graph(self):
        """Test retrieving an asset graph for a specific asset"""
        asset_client = None
        try:
            asset_client = AssetCatalog(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = asset_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # Use a known asset GUID from your environment
            asset_guid = "8be11e8d-3964-40c7-88cd-403526725523"

            response = asset_client.get_asset_graph(
                asset_guid,
                output_format="DICT",
                report_spec="Asset-Graph"
            )
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"Response type: {type(response)}")
            if isinstance(response, (dict, list)):
                print("\n\n" + json.dumps(response, indent=4))
                if isinstance(response, list):
                    print(f"Found {len(response)} elements in asset graph")
            elif type(response) is str:
                print("\n\nResponse: " + response)
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            if asset_client:
                asset_client.close_session()

    def test_get_asset_mermaid_graph(self):
        """Test retrieving an asset graph in Mermaid format"""
        asset_client = None
        try:
            asset_client = AssetCatalog(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = asset_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            asset_guid = "8be11e8d-3964-40c7-88cd-403526725523"

            response = asset_client.get_asset_mermaid_graph(asset_guid)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"Response type: {type(response)}")
            if type(response) is dict:
                print("\n\n" + json.dumps(response, indent=4))
                print(f"Found {len(response)} elements")
            elif type(response) is str:
                console.print("\n\n" + response)
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            if asset_client:
                asset_client.close_session()

    def test_get_asset_lineage_graph(self):
        """Test retrieving asset lineage graph"""
        asset_client = None
        try:
            asset_client = AssetCatalog(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = asset_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            asset_guid = "8be11e8d-3964-40c7-88cd-403526725523"
            effective_time = None
            as_of_time = None
            relationship_types = None
            limit_to_isc_q_name = None
            hilight_isc_q_name = None

            response = asset_client.get_asset_lineage_graph(
                asset_guid,
                effective_time,
                as_of_time,
                relationship_types,
                limit_to_isc_q_name,
                hilight_isc_q_name,
                all_anchors=False,
                start_from=0,
                page_size=0,
                output_format="DICT",
                report_spec="Common-Mermaid"
            )
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"Response type: {type(response)}")
            if isinstance(response, (dict, list)):
                print("\n\n" + json.dumps(response, indent=4))
                if isinstance(response, list):
                    print(f"Found {len(response)} elements in lineage")
            elif type(response) is str:
                print("\n\nResponse: " + response)
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            if asset_client:
                asset_client.close_session()

    def test_get_asset_lineage_mermaid_graph(self):
        """Test retrieving asset lineage in Mermaid format"""
        asset_client = None
        try:
            asset_client = AssetCatalog(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = asset_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            asset_guid = "8a578f0d-f7ae-4255-b4a5-236241fa5449"

            response = asset_client.get_asset_lineage_mermaid_graph(asset_guid)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"Response type: {type(response)}")
            if type(response) is dict:
                print("\n\n" + json.dumps(response, indent=4))
                print(f"Found {len(response)} elements")
            elif type(response) is str:
                print("\n\nResponse: " + response)
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            if asset_client:
                asset_client.close_session()

    def test_get_assets_by_metadata_collection_id(self):
        """Test retrieving assets by metadata collection ID"""
        asset_client = None
        try:
            asset_client = AssetCatalog(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = asset_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # Coco Template Archive
            metadata_collection_id = "9905c3cb-94c5-4494-9229-0d6f69c0b842"
            type_name = "FileFolder"

            response = asset_client.get_assets_by_metadata_collection_id(
                metadata_collection_id,
                type_name,
                output_format="DICT",
                report_spec="Referenceable"
            )
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"Response type: {type(response)}")
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))
                print(f"Found {len(response)} assets")
            elif type(response) is str:
                print("\n\nResponse: " + response)
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            if asset_client:
                asset_client.close_session()

    def test_get_asset_types(self):
        """Test retrieving available asset types"""
        asset_client = None
        try:
            asset_client = AssetCatalog(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = asset_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            response = asset_client.get_asset_types()
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"Response type: {type(response)}")
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))
                print(f"Found {len(response)} asset types")
            elif type(response) is str:
                print("\n\nResponse: " + response)
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            if asset_client:
                asset_client.close_session()

    def test_asset_search_workflow(self):
        """End-to-end test: Search for assets, retrieve details, and explore relationships"""
        asset_client = None
        try:
            asset_client = AssetCatalog(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = asset_client.create_egeria_bearer_token(self.good_user_2, "secret")

            # SEARCH
            print("\n\n=== SEARCH ===")
            search_string = "File"
            search_results = asset_client.find_in_asset_domain(
                search_string,
                starts_with=True,
                ends_with=False,
                ignore_case=True,
                output_format="JSON"
            )
            
            if isinstance(search_results, list) and len(search_results) > 0:
                print(f"Found {len(search_results)} assets matching '{search_string}'")
                
                # Get first asset's GUID
                first_asset = search_results[0]
                asset_guid = first_asset.get("elementHeader", {}).get("guid")
                
                if asset_guid:
                    # GET GRAPH
                    print("\n\n=== GET ASSET GRAPH ===")
                    graph = asset_client.get_asset_graph(
                        asset_guid,
                        output_format="JSON"
                    )
                    print(f"Retrieved asset graph for {asset_guid}")
                    
                    # GET LINEAGE
                    print("\n\n=== GET ASSET LINEAGE ===")
                    try:
                        lineage = asset_client.get_asset_lineage_graph(
                            asset_guid,
                            output_format="JSON"
                        )
                        print(f"Retrieved asset lineage for {asset_guid}")
                    except PyegeriaAPIException:
                        print(f"No lineage found for asset {asset_guid}")
            else:
                print(f"No assets found matching '{search_string}'")

            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            if asset_client:
                asset_client.close_session()
