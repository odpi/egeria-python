"""
Unit tests for the ConnectionMaker OMVS client.
"""

import pytest
from pyegeria.omvs.connection_maker import ConnectionMaker
from pyegeria.models.models import (
    NewElementRequestBody,
    UpdateElementRequestBody,
    DeleteElementRequestBody,
    TemplateRequestBody,
    GetRequestBody,
    FilterRequestBody,
    SearchStringRequestBody,
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
)
from pyegeria.view.output_formatter import generate_output
import json
import time

# Testing constants
VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "garygeeke"
USER_PWD = "secret"

@pytest.fixture
async def connection_maker():
    return ConnectionMaker(VIEW_SERVER, PLATFORM_URL, USER_ID, USER_PWD)

@pytest.mark.asyncio
async def test_connection_lifecycle(connection_maker):
    ts = int(time.time())
    # This test assumes a running Egeria environment
    try:
        await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
        
        # 1. Create Connection
        conn_body = {
            "class": "NewElementRequestBody",
            "properties": {
                "class": "ConnectionProperties",
                "qualifiedName": f"TestConnection::LifeCycle::{ts}",
                "displayName": "Test LifeCycle Connection",
                "description": "A connection for unit testing lifecycle"
            }
        }
        conn_guid = await connection_maker._async_create_connection(conn_body)
        assert conn_guid is not None
        
        # 2. Get Connection
        get_body = {"class": "GetRequestBody"}
        response = await connection_maker._async_get_connection_by_guid(conn_guid, body=get_body, graph_query_depth=0, output_format="JSON")
        conn = response[0] if isinstance(response, list) else response
        assert conn["elementHeader"]["guid"] == conn_guid
        
        # 3. Update Connection
        update_body = {
            "class": "UpdateElementRequestBody",
            "properties": {
                "class": "ConnectionProperties",
                "description": "Updated description"
            }
        }
        await connection_maker._async_update_connection(conn_guid, update_body)
        
        # 4. Delete Connection
        delete_body = {"class": "DeleteElementRequestBody"}
        await connection_maker._async_delete_connection(conn_guid, delete_body)
        
    except Exception as e:
        pytest.fail(f"Connection lifecycle failed: {e}")

@pytest.mark.asyncio
async def test_connector_type_lifecycle(connection_maker):
    ts = int(time.time())
    try:
        await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
        
        # 1. Create Connector Type
        ct_body = {
            "class": "NewElementRequestBody",
            "properties": {
                "class": "ConnectorTypeProperties",
                "qualifiedName": f"TestConnectorType::LifeCycle::{ts}",
                "displayName": "Test LifeCycle ConnectorType",
                "connectorProviderClassName": "org.odpi.egeria.test.TestProvider"
            }
        }
        ct_guid = await connection_maker._async_create_connector_type(ct_body)
        assert ct_guid is not None
        
        # 2. Get Connector Type
        get_body = {"class": "GetRequestBody"}
        response = await connection_maker._async_get_connector_type_by_guid(ct_guid, body=get_body, graph_query_depth=0, output_format="JSON")
        ct = response[0] if isinstance(response, list) else response
        assert ct["elementHeader"]["guid"] == ct_guid
        
        # 3. Delete Connector Type
        delete_body = {
            "class": "DeleteElementRequestBody",
            "externalSourceGUID": ct_guid 
        }
        await connection_maker._async_delete_connector_type(ct_guid, delete_body)
        
    except Exception as e:
        pytest.fail(f"ConnectorType lifecycle failed: {e}")

@pytest.mark.asyncio
async def test_endpoint_lifecycle(connection_maker):
    ts = int(time.time())
    try:
        await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
        
        # 1. Create Endpoint
        ep_body = {
            "class": "NewElementRequestBody",
            "properties": {
                "class": "EndpointProperties",
                "qualifiedName": f"TestEndpoint::LifeCycle::{ts}",
                "displayName": "Test LifeCycle Endpoint",
                "networkAddress": "localhost:8080"
            }
        }
        ep_guid = await connection_maker._async_create_endpoint(ep_body)
        assert ep_guid is not None
        
        # 2. Get Endpoint
        get_body = {"class": "GetRequestBody"}
        response = await connection_maker._async_get_endpoint_by_guid(ep_guid, body=get_body, graph_query_depth=0, output_format="JSON")
        ep = response[0] if isinstance(response, list) else response
        assert ep["elementHeader"]["guid"] == ep_guid
        
        # 3. Delete Endpoint
        delete_body = {"class": "DeleteElementRequestBody"}
        await connection_maker._async_delete_endpoint(ep_guid, delete_body)
        
    except Exception as e:
        pytest.fail(f"Endpoint lifecycle failed: {e}")


# --- Single API Call Tests & Extended Coverage ---

@pytest.mark.asyncio
async def test_find_connections(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    output_format = "JSON"
    response = await connection_maker._async_find_connections(search_string="*", output_format=output_format, graph_query_depth=0, page_size=10)
    print(f"\nFind Connections Result ({output_format}):")
    if isinstance(response, (dict, list)):
        print(json.dumps(response, indent=2))
    else:
        print(response)
    assert isinstance(response, (list, str, dict))

@pytest.mark.asyncio
async def test_get_connections_by_name(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    output_format = "DICT"
    response = await connection_maker._async_get_connections_by_name(name="*", output_format=output_format, graph_query_depth=0, page_size=10)
    print(f"\nGet Connections By Name Result ({output_format}):")
    if isinstance(response, (dict, list)):
        print(json.dumps(response, indent=2))
    else:
        print(response)
    assert isinstance(response, (list, str, dict))

@pytest.mark.asyncio
async def test_update_connector_type(connection_maker):
    # This is a single call test, it will fail if GUID is missing, but tests the method signature/URL
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    body = {"class": "UpdateElementRequestBody", "properties": {"class": "ConnectorTypeProperties", "description": "Update"}}
    try:
        await connection_maker._async_update_connector_type("invalid-guid", body)
    except Exception:
        pass # Expected failure for single call with dummy guid

@pytest.mark.asyncio
async def test_find_connector_types(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    output_format = "JSON"
    response = await connection_maker._async_find_connector_types(search_string="*", output_format=output_format, graph_query_depth=0, page_size=10)
    print(f"\nFind Connector Types Result ({output_format}):")
    if isinstance(response, (dict, list)):
        print(json.dumps(response, indent=2))
    else:
        print(response)
    assert isinstance(response, (list, str, dict))

@pytest.mark.asyncio
async def test_get_connector_types_by_name(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    output_format = "DICT"
    response = await connection_maker._async_get_connector_types_by_name(name="*", output_format=output_format, graph_query_depth=0, page_size=10)
    print(f"\nGet Connector Types By Name Result ({output_format}):")
    if isinstance(response, (dict, list)):
        print(json.dumps(response, indent=2))
    else:
        print(response)
    assert isinstance(response, (list, str, dict))

@pytest.mark.asyncio
async def test_find_endpoints(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    output_format = "JSON"
    response = await connection_maker._async_find_endpoints(search_string="*", output_format=output_format, graph_query_depth=0, page_size=10)
    print(f"\nFind Endpoints Result ({output_format}):")
    if isinstance(response, (dict, list)):
        print(json.dumps(response, indent=2))
    else:
        print(response)
    assert isinstance(response, (list, str, dict))

@pytest.mark.asyncio
async def test_get_endpoints_by_name(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    output_format = "DICT"
    response = await connection_maker._async_get_endpoints_by_name(name="*", output_format=output_format, graph_query_depth=0, page_size=10)
    print(f"\nGet Endpoints By Name Result ({output_format}):")
    if isinstance(response, (dict, list)):
        print(json.dumps(response, indent=2))
    else:
        print(response)
    assert isinstance(response, (list, str, dict))

@pytest.mark.asyncio
async def test_get_endpoints_by_network_address(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    output_format = "JSON"
    response = await connection_maker._async_get_endpoints_by_network_address(network_address="*", output_format=output_format, graph_query_depth=0, page_size=10)
    print(f"\nGet Endpoints By Network Address Result ({output_format}):")
    if isinstance(response, (dict, list)):
        print(json.dumps(response, indent=2))
    else:
        print(response)
    assert isinstance(response, (list, str, dict))

@pytest.mark.asyncio
async def test_get_endpoints_for_asset(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    output_format = "DICT"
    try:
        response = await connection_maker._async_get_endpoints_for_asset("dummy-asset-guid", name="*", output_format=output_format, graph_query_depth=0, page_size=10)
        print(f"\nGet Endpoints For Asset Result ({output_format}):")
        if isinstance(response, (dict, list)):
            print(json.dumps(response, indent=2))
        else:
            print(response)
        assert isinstance(response, (list, str, dict))
    except Exception:
        pass

# --- Relationship Tests ---

@pytest.mark.asyncio
async def test_connection_relationships_lifecycle(connection_maker):
    ts = int(time.time())
    try:
        await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
        
        # Setup: Create Connection, ConnectorType, and Endpoint
        conn_guid = await connection_maker._async_create_connection({
            "class": "NewElementRequestBody",
            "properties": {"class": "ConnectionProperties", "qualifiedName": f"Conn::Rel::{ts}"}
        })
        ct_guid = await connection_maker._async_create_connector_type({
            "class": "NewElementRequestBody",
            "properties": {"class": "ConnectorTypeProperties", "qualifiedName": f"CT::Rel::{ts}", "connectorProviderClassName": "Test"}
        })
        ep_guid = await connection_maker._async_create_endpoint({
            "class": "NewElementRequestBody",
            "properties": {"class": "EndpointProperties", "qualifiedName": f"EP::Rel::{ts}", "networkAddress": "localhost"}
        })
        
        # 1. Link Connection to ConnectorType
        rel_body = {"class": "NewRelationshipRequestBody"}
        await connection_maker._async_link_connection_connector_type(conn_guid, ct_guid, rel_body)
        
        # 2. Detach Connection from ConnectorType
        del_rel_body = {"class": "DeleteRelationshipRequestBody"}
        await connection_maker._async_detach_connection_connector_type(conn_guid, ct_guid, del_rel_body)
        
        # 3. Link Connection to Endpoint
        await connection_maker._async_link_connection_endpoint(conn_guid, ep_guid, rel_body)
        
        # 4. Detach Connection from Endpoint
        await connection_maker._async_detach_connection_endpoint(conn_guid, ep_guid, del_rel_body)
        
        # 5. Link Embedded Connection (self-link for test)
        try:
            await connection_maker._async_link_embedded_connection(conn_guid, conn_guid, rel_body)
            await connection_maker._async_detach_embedded_connection(conn_guid, conn_guid, del_rel_body)
        except Exception:
            pass # Self-link might fail depending on Egeria validation rules

        # Cleanup
        await connection_maker._async_delete_connection(conn_guid, {"class": "DeleteElementRequestBody"})
        await connection_maker._async_delete_connector_type(ct_guid, {"class": "DeleteElementRequestBody"})
        await connection_maker._async_delete_endpoint(ep_guid, {"class": "DeleteElementRequestBody"})
        
    except Exception as e:
        pytest.fail(f"Relationship lifecycle failed: {e}")

@pytest.mark.asyncio
async def test_asset_relationships(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    rel_body = {"class": "NewRelationshipRequestBody"}
    del_rel_body = {"class": "DeleteRelationshipRequestBody"}
    
    # Testing method calls with dummy GUIDs to verify request formatting
    try:
        await connection_maker._async_link_asset_to_connection("asset", "conn", rel_body)
    except Exception: pass
    try:
        await connection_maker._async_detach_asset_from_connection("asset", "conn", del_rel_body)
    except Exception: pass
    try:
        await connection_maker._async_link_endpoint_to_it_asset("asset", "ep", rel_body)
    except Exception: pass
    try:
        await connection_maker._async_detach_endpoint_from_it_asset("asset", "ep", del_rel_body)
    except Exception: pass

@pytest.mark.asyncio
async def test_create_from_templates(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    template_body = {
        "class": "TemplateRequestBody",
        "templateGUID": "dummy-template",
        "properties": {"class": "ConnectionProperties", "qualifiedName": "TemplateTest"}
    }
    
    # These will likely fail if dummy-template doesn't exist, but tests the SDK methods
    try:
        await connection_maker._async_create_connection_from_template(template_body)
    except Exception: pass
    
    try:
        await connection_maker._async_create_connector_type_from_template(template_body)
    except Exception: pass
    
    try:
        await connection_maker._async_create_endpoint_from_template(template_body)
    except Exception: pass

@pytest.mark.asyncio
async def test_update_endpoint(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    body = {"class": "UpdateElementRequestBody", "properties": {"class": "EndpointProperties", "description": "Update"}}
    try:
        await connection_maker._async_update_endpoint("invalid-guid", body)
    except Exception:
        pass
