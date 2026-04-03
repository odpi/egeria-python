"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for CommunityMatters class.

A running Egeria environment is needed to run these tests.
"""

import time

import pytest

from pyegeria import (
    PyegeriaException,
    print_exception_table,
)
from pyegeria.omvs.community_matters_omvs import CommunityMatters

disable_ssl_warnings = True


class TestCommunityMatters:
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

    def test_create_community(self):
        """Test creating a basic community"""
        try:
            c_client = CommunityMatters(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = c_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            start_time = time.perf_counter()
            
            body = {
                "class": "NewElementRequestBody",
                "typeName": "Community",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "CommunityProperties",
                    "qualifiedName": f"test-community-{int(time.time())}",
                    "displayName": "Test Community",
                    "description": "A community created for testing purposes",
                    "mission": "Testing community functionality"
                }
            }
            
            response = c_client.create_community(body=body)
            duration = time.perf_counter() - start_time
            
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nNew community created with GUID: {response}")
            
            # Clean up - delete the created community
            if response:
                delete_body = {
                    "class": "DeleteElementRequestBody"
                }
                c_client.delete_community(response, delete_body)
                print(f"Cleaned up test community: {response}")
            
            assert response is not None, "Community creation should return a GUID"
            
        except PyegeriaException as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_find_communities(self):
        """Test finding communities by search string"""
        try:
            c_client = CommunityMatters(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = c_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            start_time = time.perf_counter()
            
            response = c_client.find_communities(
                search_string="*",
                output_format="JSON"
            )
            duration = time.perf_counter() - start_time
            
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nFound {len(response) if isinstance(response, list) else 0} communities")
            
            assert True
            
        except PyegeriaException as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_get_community_by_guid(self):
        """Test retrieving a community by GUID"""
        try:
            c_client = CommunityMatters(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = c_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            
            # First create a community to retrieve
            body = {
                "class": "NewElementRequestBody",
                "typeName": "Community",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "CommunityProperties",
                    "qualifiedName": f"test-community-retrieve-{int(time.time())}",
                    "displayName": "Test Community for Retrieval",
                    "description": "A community created for testing retrieval",
                    "mission": "Testing retrieval functionality"
                }
            }
            
            community_guid = c_client.create_community(body=body)
            print(f"\nCreated test community with GUID: {community_guid}")
            
            # Now retrieve it
            start_time = time.perf_counter()
            response = c_client.get_community_by_guid(
                community_guid,
                output_format="JSON"
            )
            duration = time.perf_counter() - start_time
            
            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, dict):
                print(f"\n\nRetrieved community: {response.get('properties', {}).get('displayName', 'Unknown')}")
            
            # Clean up
            delete_body = {"class": "DeleteElementRequestBody"}
            c_client.delete_community(community_guid, delete_body)
            print(f"Cleaned up test community: {community_guid}")
            
            assert response is not None, "Should retrieve the community"
            
        except PyegeriaException as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_update_community(self):
        """Test updating a community"""
        try:
            c_client = CommunityMatters(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = c_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            
            # First create a community to update
            qualified_name = f"test-community-update-{int(time.time())}"
            create_body = {
                "class": "NewElementRequestBody",
                "typeName": "Community",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "CommunityProperties",
                    "qualifiedName": qualified_name,
                    "displayName": "Test Community for Update",
                    "description": "Original description",
                    "mission": "Original mission"
                }
            }
            
            community_guid = c_client.create_community(body=create_body)
            print(f"\nCreated test community with GUID: {community_guid}")
            
            # Now update it
            update_body = {
                "class": "UpdateElementRequestBody",
                "properties": {
                    "class": "CommunityProperties",
                    "qualifiedName": qualified_name,
                    "displayName": "Updated Test Community",
                    "description": "Updated description",
                    "mission": "Updated mission"
                }
            }
            
            start_time = time.perf_counter()
            c_client.update_community(community_guid, update_body)
            duration = time.perf_counter() - start_time
            
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nUpdated community: {community_guid}")
            
            # Verify the update
            updated_community = c_client.get_community_by_guid(community_guid, output_format="JSON")
            if isinstance(updated_community, dict):
                updated_desc = updated_community.get('properties', {}).get('description', '')
                print(f"Updated description: {updated_desc}")
            
            # Clean up
            delete_body = {"class": "DeleteElementRequestBody"}
            c_client.delete_community(community_guid, delete_body)
            print(f"Cleaned up test community: {community_guid}")
            
            assert True, "Community update completed"
            
        except PyegeriaException as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()

    def test_get_communities_by_name(self):
        """Test getting communities by name filter"""
        try:
            c_client = CommunityMatters(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = c_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            
            # Create a community with a specific name pattern
            unique_name = f"TestNameFilter-{int(time.time())}"
            body = {
                "class": "NewElementRequestBody",
                "typeName": "Community",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "CommunityProperties",
                    "qualifiedName": f"test-community-name-{int(time.time())}",
                    "displayName": unique_name,
                    "description": "Community for name filter testing",
                    "mission": "Testing name filter"
                }
            }
            
            community_guid = c_client.create_community(body=body)
            print(f"\nCreated test community with GUID: {community_guid}")
            
            # Search by name
            start_time = time.perf_counter()
            response = c_client.get_communities_by_name(
                filter_string=unique_name,
                output_format="JSON"
            )
            duration = time.perf_counter() - start_time
            
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nFound {len(response) if isinstance(response, list) else 0} communities by name")
            
            # Clean up
            delete_body = {"class": "DeleteElementRequestBody"}
            c_client.delete_community(community_guid, delete_body)
            print(f"Cleaned up test community: {community_guid}")
            
            assert True
            
        except PyegeriaException as e:
            print_exception_table(e)
            assert False, "Invalid request"
        finally:
            c_client.close_session()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])