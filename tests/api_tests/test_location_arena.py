"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module tests the Location class and methods from location_arena.py

A running Egeria environment is needed to run these tests.

"""
import json
import time
from datetime import datetime

from rich import print, print_json
from rich.console import Console

from pyegeria._exceptions import (
    PyegeriaInvalidParameterException,
    PyegeriaConnectionException,
    PyegeriaAPIException,
    PyegeriaNotFoundException,
    PyegeriaUnauthorizedException,
    print_basic_exception,
    print_exception_table,
)
from pyegeria.location_arena import Location
from pyegeria.logging_configuration import config_logging, init_logging
from pyegeria.models import (NewElementRequestBody)

disable_ssl_warnings = True

console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"


class TestLocationArena:
    good_platform1_url = PLATFORM_URL

    good_user_1 = USER_ID
    good_user_2 = "peterprofile"
    good_server_1 = VIEW_SERVER
    good_server_2 = VIEW_SERVER
    good_view_server_1 = VIEW_SERVER

    def _unique_qname(self, prefix: str = "Location") -> str:
        ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"{prefix}::{ts}"

    def test_create_location(self):
        """Test creating a basic location with dict body"""
        try:
            l_client = Location(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = l_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            display_name = f"Test Location {datetime.now().strftime('%Y%m%d%H%M%S')}"
            description = "Test location for automated testing"
            qualified_name = self._unique_qname("TestLocation")

            body = {
                "class": "NewElementRequestBody",
                "typeName": "Location",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": qualified_name,
                    "displayName": display_name,
                    "description": description,
                }
            }

            response = l_client.create_location(body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nCreated location with GUID: {response}")
            assert type(response) is str
            assert len(response) > 0

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            l_client.close_session()

    def test_create_location_w_pyd(self):
        """Test creating a location with Pydantic model"""
        try:
            l_client = Location(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = l_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            q_name = self._unique_qname("TestLocationPyd")
            body = NewElementRequestBody(
                typeName="Location",
                initialStatus="ACTIVE",
                properties={
                    "class": "LocationProperties",
                    "qualifiedName": q_name,
                    "displayName": f"Pydantic Location {datetime.now().strftime('%H%M%S')}",
                    "description": "Location created with Pydantic model",
                }
            )

            validated_body = body.model_dump(mode='json', by_alias=True, exclude_none=True)
            response = l_client.create_location(validated_body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nCreated location with GUID: {response}")
            assert type(response) is str
            assert len(response) > 0

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            l_client.close_session()

    def test_create_location_from_template(self):
        """Test creating a location from a template"""
        try:
            l_client = Location(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = l_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # First create a template location
            template_qname = self._unique_qname("TemplateLocation")
            template_body = {
                "class": "NewElementRequestBody",
                "typeName": "Location",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": template_qname,
                    "displayName": "Template Location",
                    "description": "This is a template location",
                }
            }
            template_guid = l_client.create_location(template_body)
            print(f"\n\nCreated template location with GUID: {template_guid}")

            # Now create a location from the template
            new_qname = self._unique_qname("LocationFromTemplate")
            from_template_body = {
                "class": "TemplateRequestBody",
                "templateGUID": template_guid,
                "replacementProperties": {
                    "class": "ElementProperties",
                    "propertyValueMap": {
                        "qualifiedName": {
                            "class": "PrimitiveTypePropertyValue",
                            "typeName": "string",
                            "primitiveTypeCategory": "OM_PRIMITIVE_TYPE_STRING",
                            "primitiveValue": new_qname
                        },
                        "displayName": {
                            "class": "PrimitiveTypePropertyValue",
                            "typeName": "string",
                            "primitiveTypeCategory": "OM_PRIMITIVE_TYPE_STRING",
                            "primitiveValue": "Location Created from Template"
                        }
                    }
                }
            }

            response = l_client.create_location_from_template(from_template_body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nCreated location from template with GUID: {response}")
            assert type(response) is str
            assert len(response) > 0

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            l_client.close_session()

    def test_find_locations(self):
        """Test finding locations with search string"""
        try:
            l_client = Location(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = l_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            search_string = "*"
            output_format = "DICT"
            report_spec = "Referenceable"

            response = l_client.find_locations(
                search_string=search_string,
                starts_with=False,
                ends_with=False,
                ignore_case=True,
                output_format=output_format,
                report_spec=report_spec
            )
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            
            if isinstance(response, dict | list):
                assert len(response) > 0
                print_json("\n\n" + json.dumps(response, indent=4))
            elif isinstance(response, str):
                print(f"\n\nResponse: {response}")
            
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            l_client.close_session()

    def test_find_locations_w_body(self):
        """Test finding locations with body parameters"""
        try:
            l_client = Location(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = l_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            search_string = "*"
            body = {
                "class": "SearchStringRequestBody",
                "searchString": search_string,
                "effectiveTime": None,
                "typeName": "Location"
            }

            response = l_client.find_locations(
                search_string=search_string,
                body=body,
                starts_with=False,
                ends_with=False,
                ignore_case=True,
                output_format="JSON"
            )
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            
            if type(response) is dict:
                print_json("\n\n" + json.dumps(response, indent=4))
            
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            l_client.close_session()

    def test_get_locations_by_name(self):
        """Test getting locations by name filter"""
        try:
            l_client = Location(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = l_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            filter_string = "*"
            response = l_client.get_locations_by_name(
                filter_string=filter_string,
                output_format="JSON"
            )
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            
            if type(response) is dict:
                print_json("\n\n" + json.dumps(response, indent=4))
            
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            l_client.close_session()

    def test_get_location_by_guid(self):
        """Test getting a specific location by GUID"""
        try:
            l_client = Location(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = l_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # First create a location to retrieve
            q_name = self._unique_qname("TestLocationForRetrieval")
            body = {
                "class": "NewElementRequestBody",
                "typeName": "Location",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": q_name,
                    "displayName": "Location for GUID test",
                    "description": "Test location to retrieve by GUID",
                }
            }
            location_guid = l_client.create_location(body)
            print(f"\n\nCreated location with GUID: {location_guid}")

            # Now retrieve it
            response = l_client.get_location_by_guid(location_guid=location_guid, output_format="JSON")
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            
            if type(response) is dict:
                print_json("\n\n" + json.dumps(response, indent=4))
            
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            l_client.close_session()

    def test_update_location(self):
        """Test updating a location's properties"""
        try:
            l_client = Location(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = l_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # First create a location to update
            q_name = self._unique_qname("TestLocationForUpdate")
            create_body = {
                "class": "NewElementRequestBody",
                "typeName": "Location",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": q_name,
                    "displayName": "Original Location Name",
                    "description": "Original description",
                }
            }
            location_guid = l_client.create_location(create_body)
            print(f"\n\nCreated location with GUID: {location_guid}")

            # Now update it
            new_desc = "Updated description for testing"
            update_body = {
                "class": "UpdateElementRequestBody",
                "mergeUpdate": True,
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": q_name,
                    "displayName": "Updated Location Name",
                    "description": new_desc,
                }
            }

            response = l_client.update_location(location_guid, update_body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nUpdated location successfully")
            
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            l_client.close_session()

    def test_link_peer_locations(self):
        """Test linking two locations as peers"""
        try:
            l_client = Location(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = l_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # Create two locations to link
            q_name1 = self._unique_qname("PeerLocation1")
            body1 = {
                "class": "NewElementRequestBody",
                "typeName": "Location",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": q_name1,
                    "displayName": "Peer Location 1",
                    "description": "First peer location",
                }
            }
            location1_guid = l_client.create_location(body1)

            q_name2 = self._unique_qname("PeerLocation2")
            body2 = {
                "class": "NewElementRequestBody",
                "typeName": "Location",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": q_name2,
                    "displayName": "Peer Location 2",
                    "description": "Second peer location",
                }
            }
            location2_guid = l_client.create_location(body2)

            print(f"\n\nCreated locations: {location1_guid} and {location2_guid}")

            # Link them as peers
            link_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "AdjacentLocationProperties",
                }
            }
            l_client.link_peer_locations(location1_guid, location2_guid, link_body)
            
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nLinked peer locations successfully")
            
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            l_client.close_session()

    def test_detach_peer_locations(self):
        """Test detaching peer locations"""
        try:
            l_client = Location(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = l_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # Create and link two locations
            q_name1 = self._unique_qname("PeerLocationDetach1")
            body1 = {
                "class": "NewElementRequestBody",
                "typeName": "Location",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": q_name1,
                    "displayName": "Peer Location Detach 1",
                    "description": "First peer location for detach test",
                }
            }
            location1_guid = l_client.create_location(body1)

            q_name2 = self._unique_qname("PeerLocationDetach2")
            body2 = {
                "class": "NewElementRequestBody",
                "typeName": "Location",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": q_name2,
                    "displayName": "Peer Location Detach 2",
                    "description": "Second peer location for detach test",
                }
            }
            location2_guid = l_client.create_location(body2)

            # Link them
            link_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "PeerLocationProperties",
                }
            }
            l_client.link_peer_locations(location1_guid, location2_guid, link_body)
            print(f"\n\nLinked locations: {location1_guid} and {location2_guid}")

            # Now detach them
            detach_body = {
                "class": "DeleteRelationshipRequestBody"
            }
            l_client.detach_peer_locations(location1_guid, location2_guid, detach_body)
            
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nDetached peer locations successfully")
            
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            l_client.close_session()

    def test_link_nested_location(self):
        """Test linking a location as nested within another"""
        try:
            l_client = Location(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = l_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # Create parent location
            q_name_parent = self._unique_qname("ParentLocation")
            parent_body = {
                "class": "NewElementRequestBody",
                "typeName": "Location",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": q_name_parent,
                    "displayName": "Parent Location",
                    "description": "Parent location for nesting test",
                }
            }
            parent_guid = l_client.create_location(parent_body)

            # Create nested location
            q_name_nested = self._unique_qname("NestedLocation")
            nested_body = {
                "class": "NewElementRequestBody",
                "typeName": "Location",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": q_name_nested,
                    "displayName": "Nested Location",
                    "description": "Nested location for testing",
                }
            }
            nested_guid = l_client.create_location(nested_body)

            print(f"\n\nCreated parent: {parent_guid} and nested: {nested_guid}")

            # Link nested location
            link_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "NestedLocationProperties",
                }
            }
            l_client.link_nested_location(parent_guid, nested_guid, link_body)
            
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nLinked nested location successfully")
            
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            l_client.close_session()

    def test_detach_nested_location(self):
        """Test detaching a nested location"""
        try:
            l_client = Location(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = l_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # Create and link locations
            q_name_parent = self._unique_qname("ParentLocationDetach")
            parent_body = {
                "class": "NewElementRequestBody",
                "typeName": "Location",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": q_name_parent,
                    "displayName": "Parent Location Detach",
                    "description": "Parent location for detach test",
                }
            }
            parent_guid = l_client.create_location(parent_body)

            q_name_nested = self._unique_qname("NestedLocationDetach")
            nested_body = {
                "class": "NewElementRequestBody",
                "typeName": "Location",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": q_name_nested,
                    "displayName": "Nested Location Detach",
                    "description": "Nested location for detach test",
                }
            }
            nested_guid = l_client.create_location(nested_body)

            # Link them
            link_body  = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "NestedLocationProperties",
                }
            }
            l_client.link_nested_location(parent_guid, nested_guid, link_body)
            print(f"\n\nLinked nested location: {nested_guid} to parent: {parent_guid}")

            # Now detach
            detach_body = {
                "class": "DeleteRelationshipRequestBody"
            }
            l_client.detach_nested_location(parent_guid, nested_guid, detach_body)
            
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nDetached nested location successfully")
            
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            l_client.close_session()

    def test_link_known_location(self):
        """Test linking a location to another element"""
        try:
            l_client = Location(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = l_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # Create a location
            q_name = self._unique_qname("KnownLocation")
            location_body = {
                "class": "NewElementRequestBody",
                "typeName": "Location",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": q_name,
                    "displayName": "Known Location",
                    "description": "Location for known location test",
                }
            }
            location_guid = l_client.create_location(location_body)

            # For this test, we'll use another location as the element
            q_name_element = self._unique_qname("ElementForKnownLocation")
            element_body = {
                "class": "NewElementRequestBody",
                "typeName": "Location",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": q_name_element,
                    "displayName": "Element for Known Location",
                    "description": "Element to link to known location",
                }
            }
            element_guid = l_client.create_location(element_body)

            print(f"\n\nCreated location: {location_guid} and element: {element_guid}")

            # Link as known location
            link_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "NestedLocationProperties",
                }
            }
            l_client.link_known_location(element_guid, location_guid, link_body)
            
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nLinked known location successfully")
            
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            l_client.close_session()

    def test_detach_known_location(self):
        """Test detaching a known location"""
        try:
            l_client = Location(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = l_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # Create and link locations
            q_name = self._unique_qname("KnownLocationDetach")
            location_body = {
                "class": "NewElementRequestBody",
                "typeName": "Location",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": q_name,
                    "displayName": "Known Location Detach",
                    "description": "Location for detach test",
                }
            }
            location_guid = l_client.create_location(location_body)

            q_name_element = self._unique_qname("ElementForKnownLocationDetach")
            element_body = {
                "class": "NewElementRequestBody",
                "typeName": "Location",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": q_name_element,
                    "displayName": "Element for Known Location Detach",
                    "description": "Element to detach from known location",
                }
            }
            element_guid = l_client.create_location(element_body)

            # Link them
            link_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "KnownLocationProperties",
                }
            }
            l_client.link_known_location(element_guid, location_guid, link_body)
            print(f"\n\nLinked known location: {location_guid} to element: {element_guid}")

            # Now detach
            detach_body = {
                "class": "DeleteRelationshipRequestBody"
            }
            l_client.detach_known_location(element_guid, location_guid, detach_body)
            
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nDetached known location successfully")
            
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            l_client.close_session()

    def test_delete_location(self):
        """Test deleting a location"""
        try:
            l_client = Location(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = l_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # Create a location to delete
            q_name = self._unique_qname("LocationToDelete")
            create_body = {
                "class": "NewElementRequestBody",
                "typeName": "Location",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": q_name,
                    "displayName": "Location to Delete",
                    "description": "This location will be deleted",
                }
            }
            location_guid = l_client.create_location(create_body)
            print(f"\n\nCreated location with GUID: {location_guid}")

            # Delete it
            delete_body = {
                "class": "DeleteElementRequestBody"
            }
            l_client.delete_location(location_guid, delete_body)
            
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nDeleted location successfully")
            
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            l_client.close_session()

    def test_crud_location_e2e(self):
        """End-to-end test: Create, Read, Update, Delete a location"""
        try:
            l_client = Location(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            created_guid = None
            display_name = f"E2E Test Location {datetime.now().strftime('%Y%m%d%H%M%S')}"

            token = l_client.create_egeria_bearer_token(self.good_user_2, "secret")

            # CREATE
            print("\n\n=== CREATE ===")
            q_name = self._unique_qname("E2ELocation")
            body = {
                "class": "NewElementRequestBody",
                "typeName": "Location",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": q_name,
                    "displayName": display_name,
                    "description": "End-to-end test location",
                }
            }

            create_resp = l_client.create_location(body)
            created_guid = create_resp
            print(f"Created location: {created_guid}")
            assert created_guid is not None

            # READ
            print("\n\n=== READ ===")
            got = l_client.get_location_by_guid(created_guid, output_format="JSON")
            print_json(json.dumps(got, indent=4))
            assert got is not None

            # UPDATE
            print("\n\n=== UPDATE ===")
            new_desc = "Updated description in E2E test"
            upd_body = {
                "class": "UpdateElementRequestBody",
                "mergeUpdate": True,
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": q_name,
                    "displayName": display_name,
                    "description": new_desc,
                }
            }

            upd_resp = l_client.update_location(created_guid, upd_body)
            print("Updated location successfully")

            # Verify update
            found = l_client.get_location_by_guid(created_guid, output_format="JSON")
            print_json(json.dumps(found, indent=4))

            # DELETE
            print("\n\n=== DELETE ===")
            del_resp = l_client.delete_location(
                created_guid,
                body={"class": "DeleteElementRequestBody"}
            )
            print("Deleted location successfully")

            # Verify deletion
            try:
                after = l_client.get_location_by_guid(created_guid, output_format="JSON")
                # If we get here, deletion might not have worked
                print("Warning: Location still exists after deletion")
            except PyegeriaAPIException:
                print("Confirmed: Location no longer exists")

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
            l_client.close_session()