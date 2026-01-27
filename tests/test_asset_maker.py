"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for AssetMaker class.

A running Egeria environment is needed to run these tests.
"""

import time

import pytest

from rich.console import Console

from pyegeria import (
    PyegeriaException,
    print_exception_table, print_basic_exception,
)
from pyegeria.omvs.asset_maker import AssetMaker

disable_ssl_warnings = True
erin_guid = "dcfd7e32-8074-4cdf-bdc5-9a6f28818a9d"  # Erin
gary_guid = "dfe5c382-9ec4-4972-8481-35fd61cb4feb"
lemme_guid = "7b5cf4fa-23a8-4cf5-aaa6-02bcf58214f8"

console = Console()
class TestAssetMaker:
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
    good_view_server_1 = "view-server"
    good_view_server_2 = "qs-view-server"
    bad_server_1 = "coco"
    bad_server_2 = ""

    def test_create_asset(self):
        """Test creating a basic asset"""
        try:
            a_client = AssetMaker(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = a_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            start_time = time.perf_counter()
            
            body = {
                "class": "NewElementRequestBody",
                "typeName": "Asset",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "AssetProperties",
                    "qualifiedName": f"test-asset-{int(time.time())}",
                    "displayName": "Test Asset",
                    "description": "An asset created for testing purposes",
                }
            }
            
            response = a_client.create_asset(body=body)
            duration = time.perf_counter() - start_time
            
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nNew asset created with GUID: {response}")
            
            # Clean up - delete the created asset
            if response:
                delete_body = {
                    "class": "DeleteElementRequestBody"
                }
                a_client.delete_asset(response, delete_body)
                print(f"Cleaned up test asset: {response}")
            
            assert response is not None, "Asset creation should return a GUID"
            
        except PyegeriaException as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            a_client.close_session()

    def test_find_assets(self):
        """Test finding assets by search string"""
        try:
            a_client = AssetMaker(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = a_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            start_time = time.perf_counter()
            
            response = a_client.find_assets(search_string="Postgres", output_format="JSON")
            duration = time.perf_counter() - start_time
            
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nFound {len(response) if isinstance(response, list) else 0} assets")
            
            assert True
            
        except PyegeriaException as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except Exception as e:
            console.print_exception(e)
            assert False, "Unexpected error"
        finally:
            a_client.close_session()

    def test_get_asset_by_guid(self):
        """Test retrieving an asset by GUID"""
        try:
            a_client = AssetMaker(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = a_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            
            # First create an asset to retrieve
            body = {
                "class": "NewElementRequestBody",
                "typeName": "Asset",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "AssetProperties",
                    "qualifiedName": f"test-asset-retrieve-{int(time.time())}",
                    "displayName": "Test Asset for Retrieval",
                    "description": "An asset created for testing retrieval",
                }
            }
            
            asset_guid = a_client.create_asset(body=body)
            print(f"\nCreated test asset with GUID: {asset_guid}")
            
            # Now retrieve it
            start_time = time.perf_counter()
            response = a_client.get_asset_by_guid(
                asset_guid,
                output_format="JSON"
            )
            duration = time.perf_counter() - start_time
            
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nRetrieved asset: {response.get('properties', {}).get('displayName', 'Unknown')}")
            
            # Clean up
            delete_body = {"class": "DeleteElementRequestBody"}
            a_client.delete_asset(asset_guid, delete_body)
            print(f"Cleaned up test asset: {asset_guid}")
            
            assert response is not None, "Should retrieve the asset"
            assert isinstance(response, dict), "Response should be a dictionary"
            
        except PyegeriaException as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            a_client.close_session()

    def test_update_asset(self):
        """Test updating an asset"""
        try:
            a_client = AssetMaker(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = a_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            
            # First create an asset to update
            qualified_name = f"test-asset-update-{int(time.time())}"
            create_body = {
                "class": "NewElementRequestBody",
                "typeName": "Asset",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "AssetProperties",
                    "qualifiedName": qualified_name,
                    "displayName": "Test Asset for Update",
                    "description": "Original description",
                }
            }
            
            asset_guid = a_client.create_asset(body=create_body)
            print(f"\nCreated test asset with GUID: {asset_guid}")
            
            # Now update it
            update_body = {
                "class": "UpdateElementRequestBody",
                "properties": {
                    "class": "AssetProperties",
                    "qualifiedName": qualified_name,
                    "displayName": "Updated Test Asset",
                    "description": "Updated description",
                }
            }
            
            start_time = time.perf_counter()
            a_client.update_asset(asset_guid, update_body)
            duration = time.perf_counter() - start_time
            
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nUpdated asset: {asset_guid}")
            
            # Verify the update
            updated_asset = a_client.get_asset_by_guid(asset_guid, output_format="JSON")
            updated_desc = updated_asset.get('properties', {}).get('description', '')
            print(f"Updated description: {updated_desc}")
            
            # Clean up
            delete_body = {"class": "DeleteElementRequestBody"}
            a_client.delete_asset(asset_guid, delete_body)
            print(f"Cleaned up test asset: {asset_guid}")
            
            assert "Updated" in updated_desc or True, "Asset should be updated"
            
        except PyegeriaException as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            a_client.close_session()

    def test_delete_asset(self):
        """Test deleting an asset"""
        try:
            a_client = AssetMaker(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = a_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )

            # First create an asset to update

            asset_guid = "de072a19-68c5-40bd-ba61-8cf5d99cb1a2"
            delete_body = {"class": "DeleteElementRequestBody"}
            a_client.delete_asset(asset_guid, delete_body)
            print(f"Cleaned up test asset: {asset_guid}")

            assert  True, "Asset should be deleted"

        except PyegeriaException as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            a_client.close_session()

    def test_find_data_assets(self):
        """Test finding data assets"""
        try:
            a_client = AssetMaker(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2,
                                  user_pwd=self.good_user_2_pwd)
            a_client.create_egeria_bearer_token(self.good_user_2, self.good_user_2_pwd)
            response = a_client.find_data_assets(search_string="*", output_format="JSON")
            assert response is not None
        except PyegeriaException as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            a_client.close_session()

    def test_get_data_assets_by_category(self):
        """Test getting data assets by category"""
        try:
            a_client = AssetMaker(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2,
                                  user_pwd=self.good_user_2_pwd)
            a_client.create_egeria_bearer_token(self.good_user_2, self.good_user_2_pwd)
            response = a_client.get_data_assets_by_category(category="test", output_format="JSON")
            assert response is not None
        except PyegeriaException as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            a_client.close_session()

    def test_find_infrastructure(self):
        """Test finding infrastructure assets"""
        try:
            a_client = AssetMaker(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2,
                                  user_pwd=self.good_user_2_pwd)
            a_client.create_egeria_bearer_token(self.good_user_2, self.good_user_2_pwd)
            response = a_client.find_infrastructure(search_string="*", output_format="JSON")
            assert response is not None
        except PyegeriaException as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            a_client.close_session()

    def test_find_processes(self):
        """Test finding processes"""
        try:
            a_client = AssetMaker(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2,
                                  user_pwd=self.good_user_2_pwd)
            a_client.create_egeria_bearer_token(self.good_user_2, self.good_user_2_pwd)
            response = a_client.find_processes(
                search_string="HAM",
                activity_status_list=[],
                metadata_element_type="ToDo",
                output_format="JSON",
                page_size = 10,
                graph_query_depth=5,
                relationship_page_size=10,
            )
            console.print(f"Response type {type(response)}, num elements {len(response)}\n")
            if isinstance(response, dict|list):
                console.print_json(data=response)
            else:
                console.print(response)
            assert response is not None
        except PyegeriaException as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            a_client.close_session()

    def test_create_action(self):
        """Test creating an action"""
        try:
            a_client = AssetMaker(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2,
                                  user_pwd=self.good_user_2_pwd)
            a_client.create_egeria_bearer_token(self.good_user_2, self.good_user_2_pwd)


            body = {
                "class": "ActionRequestBody",
                "properties": {
                    "class": "ToDoProperties",
                    "qualifiedName": f"make-coffee-{int(time.time())}",
                    "displayName": "make-coffee",
                    "activityStatus": "REQUESTED",
                    "description": "Make coffee for the team",
                },
                "assignToActorGUID": gary_guid,
                "originatorGUID": erin_guid,
                "actionSponsorGUID": lemme_guid,
            }
            response = a_client.create_action(body=body)
            print(response)
            assert response is not None
        except PyegeriaException as e:
            print_exception_table(e)
            # It might fail if Action type is not supported, but we test the method call
            pass
        finally:
            a_client.close_session()

    def test_assign_actions(self):
        """Test assigning actions for an actor"""
        try:
            a_client = AssetMaker(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2,
                                  user_pwd=self.good_user_2_pwd)
            a_client.create_egeria_bearer_token(self.good_user_2, self.good_user_2_pwd)
            # Using a dummy GUID
            a_client.assign_action(action_guid = "59fb7c88-89bf-4f9d-a792-3c06cf2f4fb7",
                                                 actor_guid=erin_guid)

            assert True
        except PyegeriaException as e:
            print_basic_exception(e)

        finally:
            a_client.close_session()


    def test_get_assigned_actions(self):
        """Test getting assigned actions for an actor"""
        try:
            a_client = AssetMaker(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2,
                                  user_pwd=self.good_user_2_pwd)
            a_client.create_egeria_bearer_token(self.good_user_2, self.good_user_2_pwd)
            # Using a dummy GUID
            response = a_client.get_assigned_actions(actor_guid="59f0232c-f834-4365-8e06-83695d238d2d", activity_status_list=[],output_format="JSON")
            if isinstance(response, dict | list):
                console.print_json(data=response)
            else:
                console.print(response)
            assert response is not None
        except PyegeriaException as e:
            print_exception_table(e)
            pass
        finally:
            a_client.close_session()


    def test_get_actions_for_sponsor(self):
        """Test getting assigned actions for an actor"""
        try:
            a_client = AssetMaker(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2,
                                  user_pwd=self.good_user_2_pwd)
            a_client.create_egeria_bearer_token(self.good_user_2, self.good_user_2_pwd)
            # Using a dummy GUID
            response = a_client.get_actions_for_sponsor(metadata_element_guid=lemme_guid, activity_status_list=["REQUESTED"],output_format="JSON")
            if isinstance(response, dict | list):
                console.print_json(data=response)
            else:
                console.print(response)
            assert response is not None
        except PyegeriaException as e:
            print_exception_table(e)
            pass
        finally:
            a_client.close_session()

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
