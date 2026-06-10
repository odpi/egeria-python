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
async def test_create_connection(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    ts = int(time.time())
    body = {
        "class": "NewElementRequestBody",
        "properties": {
            "class": "ConnectionProperties",
            "qualifiedName": f"TestConnection::Create::{ts}",
            "displayName": "Test Create Connection",
            "description": "A connection for standalone testing"
        }
    }
    print(f"\nCreating connection with body: {body}")
    conn_guid = connection_maker.create_connection(body)
    print(f"Created connection GUID: {conn_guid}")
    assert conn_guid is not None
    # Cleanup
    connection_maker.delete_connection(conn_guid, {"class": "DeleteElementRequestBody"})

@pytest.mark.asyncio
async def test_get_connection_by_guid(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    ts = int(time.time())
    conn_guid = connection_maker.create_connection({
        "class": "NewElementRequestBody",
        "properties": {"class": "ConnectionProperties", "qualifiedName": f"TestConnection::GetByGUID::{ts}"}
    })
    
    output_format = "JSON"
    report_spec = None
    print(f"\nGetting connection by GUID: {conn_guid}, output_format={output_format}, report_spec={report_spec}")
    response = connection_maker.get_connection_by_guid(conn_guid, output_format=output_format, report_spec=report_spec)
    print(f"Get Connection Response: {json.dumps(response, indent=4) if output_format in ('JSON', 'DICT', 'LIST') else response}")
    assert response is not None
    
    # Cleanup
    connection_maker.delete_connection(conn_guid, {"class": "DeleteElementRequestBody"})

@pytest.mark.asyncio
async def test_update_connection(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    ts = int(time.time())
    conn_guid = connection_maker.create_connection({
        "class": "NewElementRequestBody",
        "properties": {"class": "ConnectionProperties", "qualifiedName": f"TestConnection::Update::{ts}"}
    })
    
    body = {
        "class": "UpdateElementRequestBody",
        "properties": {"class": "ConnectionProperties", "description": "Updated via standalone test"}
    }
    print(f"\nUpdating connection {conn_guid} with body: {body}")
    connection_maker.update_connection(conn_guid, body)
    
    # Cleanup
    connection_maker.delete_connection(conn_guid, {"class": "DeleteElementRequestBody"})

@pytest.mark.asyncio
async def test_delete_connection(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    ts = int(time.time())
    conn_guid = connection_maker.create_connection({
        "class": "NewElementRequestBody",
        "properties": {"class": "ConnectionProperties", "qualifiedName": f"TestConnection::Delete::{ts}"}
    })
    
    body = {"class": "DeleteElementRequestBody"}
    print(f"\nDeleting connection {conn_guid} with body: {body}")
    connection_maker.delete_connection(conn_guid, body)

@pytest.mark.asyncio
async def test_create_connection_from_template(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    body = {
        "class": "TemplateRequestBody",
        "templateGUID": "dummy-template",
        "properties": {"class": "ConnectionProperties", "qualifiedName": "TemplateConnectionTest"}
    }
    print(f"\nCreating connection from template with body: {body}")
    try:
        connection_maker.create_connection_from_template(body)
    except Exception as e:
        print(f"Expected failure or error: {e}")

@pytest.mark.asyncio
async def test_find_connections(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    search_string = "*"
    output_format = "LIST"
    report_spec = None
    print(f"\nFinding connections: search_string={search_string}, output_format={output_format}, report_spec={report_spec}")
    response = connection_maker.find_connections(search_string=search_string, output_format=output_format, report_spec=report_spec)
    print(f"Find Connections Result: {json.dumps(response, indent=4) if output_format in ('JSON', 'DICT', 'LIST') else response}")
    assert response is not None

@pytest.mark.asyncio
async def test_get_connections_by_name(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    name = "*"
    output_format = "DICT"
    report_spec = None
    print(f"\nGetting connections by name: name={name}, output_format={output_format}, report_spec={report_spec}")
    response = connection_maker.get_connections_by_name(name=name, output_format=output_format, report_spec=report_spec)
    print(f"Get Connections By Name Result: {json.dumps(response, indent=4) if output_format in ('JSON', 'DICT', 'LIST') else response}")
    assert response is not None

@pytest.mark.asyncio
async def test_create_connector_type(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    ts = int(time.time())
    body = {
        "class": "NewElementRequestBody",
        "properties": {
            "class": "ConnectorTypeProperties",
            "qualifiedName": f"TestConnectorType::Create::{ts}",
            "displayName": "Test Create ConnectorType",
            "connectorProviderClassName": "org.odpi.egeria.test.TestProvider"
        }
    }
    print(f"\nCreating connector type with body: {body}")
    ct_guid = connection_maker.create_connector_type(body)
    print(f"Created connector type GUID: {ct_guid}")
    assert ct_guid is not None
    # Cleanup
    connection_maker.delete_connector_type(ct_guid, {"class": "DeleteElementRequestBody"})

@pytest.mark.asyncio
async def test_get_connector_type_by_guid(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    ts = int(time.time())
    ct_guid = connection_maker.create_connector_type({
        "class": "NewElementRequestBody",
        "properties": {"class": "ConnectorTypeProperties", "qualifiedName": f"TestCT::GetByGUID::{ts}", "connectorProviderClassName": "Test"}
    })
    
    output_format = "JSON"
    report_spec = None
    print(f"\nGetting connector type by GUID: {ct_guid}, output_format={output_format}, report_spec={report_spec}")
    response = connection_maker.get_connector_type_by_guid(ct_guid, output_format=output_format, report_spec=report_spec)
    print(f"Get Connector Type Response: {json.dumps(response, indent=4) if output_format in ('JSON', 'DICT', 'LIST') else response}")
    assert response is not None
    
    # Cleanup
    connection_maker.delete_connector_type(ct_guid, {"class": "DeleteElementRequestBody"})

@pytest.mark.asyncio
async def test_update_connector_type(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    ts = int(time.time())
    ct_guid = connection_maker.create_connector_type({
        "class": "NewElementRequestBody",
        "properties": {"class": "ConnectorTypeProperties", "qualifiedName": f"TestCT::Update::{ts}", "connectorProviderClassName": "Test"}
    })
    
    body = {
        "class": "UpdateElementRequestBody",
        "properties": {"class": "ConnectorTypeProperties", "description": "Updated connector type"}
    }
    print(f"\nUpdating connector type {ct_guid} with body: {body}")
    connection_maker.update_connector_type(ct_guid, body)
    
    # Cleanup
    connection_maker.delete_connector_type(ct_guid, {"class": "DeleteElementRequestBody"})

@pytest.mark.asyncio
async def test_delete_connector_type(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    ts = int(time.time())
    ct_guid = connection_maker.create_connector_type({
        "class": "NewElementRequestBody",
        "properties": {"class": "ConnectorTypeProperties", "qualifiedName": f"TestCT::Delete::{ts}", "connectorProviderClassName": "Test"}
    })
    
    body = {"class": "DeleteElementRequestBody"}
    print(f"\nDeleting connector type {ct_guid} with body: {body}")
    connection_maker.delete_connector_type(ct_guid, body)

@pytest.mark.asyncio
async def test_create_connector_type_from_template(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    body = {
        "class": "TemplateRequestBody",
        "templateGUID": "dummy-template",
        "properties": {"class": "ConnectorTypeProperties", "qualifiedName": "TemplateCTTest"}
    }
    print(f"\nCreating connector type from template with body: {body}")
    try:
        connection_maker.create_connector_type_from_template(body)
    except Exception as e:
        print(f"Expected failure or error: {e}")

@pytest.mark.asyncio
async def test_find_connector_types(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    search_string = "*"
    output_format = "LIST"
    report_spec = None
    print(f"\nFinding connector types: search_string={search_string}, output_format={output_format}, report_spec={report_spec}")
    response = connection_maker.find_connector_types(search_string=search_string, output_format=output_format, report_spec=report_spec)
    print(f"Find Connector Types Result: {json.dumps(response, indent=4) if output_format in ('JSON', 'DICT', 'LIST') else response}")
    assert response is not None

@pytest.mark.asyncio
async def test_get_connector_types_by_name(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    name = "*"
    output_format = "DICT"
    report_spec = None
    print(f"\nGetting connector types by name: name={name}, output_format={output_format}, report_spec={report_spec}")
    response = connection_maker.get_connector_types_by_name(name=name, output_format=output_format, report_spec=report_spec)
    print(f"Get Connector Types By Name Result: {json.dumps(response, indent=4) if output_format in ('JSON', 'DICT', 'LIST') else response}")
    assert response is not None

@pytest.mark.asyncio
async def test_create_endpoint(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    ts = int(time.time())
    body = {
        "class": "NewElementRequestBody",
        "properties": {
            "class": "EndpointProperties",
            "qualifiedName": f"TestEndpoint::Create::{ts}",
            "displayName": "Test Create Endpoint",
            "networkAddress": "localhost:8080"
        }
    }
    print(f"\nCreating endpoint with body: {body}")
    ep_guid = connection_maker.create_endpoint(body)
    print(f"Created endpoint GUID: {ep_guid}")
    assert ep_guid is not None
    # Cleanup
    connection_maker.delete_endpoint(ep_guid, {"class": "DeleteElementRequestBody"})

@pytest.mark.asyncio
async def test_get_endpoint_by_guid(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    ts = int(time.time())
    ep_guid = connection_maker.create_endpoint({
        "class": "NewElementRequestBody",
        "properties": {"class": "EndpointProperties", "qualifiedName": f"TestEP::GetByGUID::{ts}", "networkAddress": "localhost"}
    })
    
    output_format = "JSON"
    report_spec = None
    print(f"\nGetting endpoint by GUID: {ep_guid}, output_format={output_format}, report_spec={report_spec}")
    response = connection_maker.get_endpoint_by_guid(ep_guid, output_format=output_format, report_spec=report_spec)
    print(f"Get Endpoint Response: {json.dumps(response, indent=4) if output_format in ('JSON', 'DICT', 'LIST') else response}")
    assert response is not None
    
    # Cleanup
    connection_maker.delete_endpoint(ep_guid, {"class": "DeleteElementRequestBody"})

@pytest.mark.asyncio
async def test_update_endpoint(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    ts = int(time.time())
    ep_guid = connection_maker.create_endpoint({
        "class": "NewElementRequestBody",
        "properties": {"class": "EndpointProperties", "qualifiedName": f"TestEP::Update::{ts}", "networkAddress": "localhost"}
    })
    
    body = {
        "class": "UpdateElementRequestBody",
        "properties": {"class": "EndpointProperties", "description": "Updated endpoint"}
    }
    print(f"\nUpdating endpoint {ep_guid} with body: {body}")
    connection_maker.update_endpoint(ep_guid, body)
    
    # Cleanup
    connection_maker.delete_endpoint(ep_guid, {"class": "DeleteElementRequestBody"})

@pytest.mark.asyncio
async def test_delete_endpoint(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    ts = int(time.time())
    ep_guid = connection_maker.create_endpoint({
        "class": "NewElementRequestBody",
        "properties": {"class": "EndpointProperties", "qualifiedName": f"TestEP::Delete::{ts}", "networkAddress": "localhost"}
    })
    
    body = {"class": "DeleteElementRequestBody"}
    print(f"\nDeleting endpoint {ep_guid} with body: {body}")
    connection_maker.delete_endpoint(ep_guid, body)

@pytest.mark.asyncio
async def test_create_endpoint_from_template(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    body = {
        "class": "TemplateRequestBody",
        "templateGUID": "dummy-template",
        "properties": {"class": "EndpointProperties", "qualifiedName": "TemplateEPTest"}
    }
    print(f"\nCreating endpoint from template with body: {body}")
    try:
        connection_maker.create_endpoint_from_template(body)
    except Exception as e:
        print(f"Expected failure or error: {e}")

@pytest.mark.asyncio
async def test_find_endpoints(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    search_string = "*"
    output_format = "DICT"
    report_spec = None
    print(f"\nFinding endpoints: search_string={search_string}, output_format={output_format}, report_spec={report_spec}")
    response = connection_maker.find_endpoints(search_string=search_string, output_format=output_format, report_spec=report_spec)
    print(f"Find Endpoints Result: {json.dumps(response, indent=4) if output_format in ('JSON', 'DICT', 'LIST') else response}")
    assert response is not None

@pytest.mark.asyncio
async def test_get_endpoints_by_name(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    name = "*"
    output_format = "DICT"
    report_spec = None
    print(f"\nGetting endpoints by name: name={name}, output_format={output_format}, report_spec={report_spec}")
    response = connection_maker.get_endpoints_by_name(name=name, output_format=output_format, report_spec=report_spec)
    print(f"Get Endpoints By Name Result: {json.dumps(response, indent=4) if output_format in ('JSON', 'DICT', 'LIST') else response}")
    assert response is not None

@pytest.mark.asyncio
async def test_get_endpoint_by_guid(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    guid = "'e70dc0e4-98aa-48e5-bfe5-9cd546ee331e"
    output_format = "JSON"
    report_spec = None
    print(f"\nGetting endpoints by GUID: guid={guid}, output_format={output_format}, report_spec={report_spec}")
    response = connection_maker.get_endpoint_by_guid(guid=guid, output_format=output_format, report_spec=report_spec, graph_query_depth=5)
    print(f"Get Endpoints By Name Result: {json.dumps(response, indent=4) if output_format in ('JSON', 'DICT', 'LIST') else response}")
    assert response is not None

@pytest.mark.asyncio
async def test_get_endpoints_by_network_address(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    network_address = "*"
    output_format = "JSON"
    report_spec = None
    print(f"\nGetting endpoints by network address: network_address={network_address}, output_format={output_format}, report_spec={report_spec}")
    response = connection_maker.get_endpoints_by_network_address(network_address=network_address, output_format=output_format, report_spec=report_spec)
    print(f"Get Endpoints By Network Address Result: {json.dumps(response, indent=4) if output_format in ('JSON', 'DICT', 'LIST') else response}")
    assert response is not None

@pytest.mark.asyncio
async def test_get_endpoints_for_asset(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    asset_guid = "dummy-asset-guid"
    output_format = "DICT"
    report_spec = None
    print(f"\nGetting endpoints for asset: asset_guid={asset_guid}, output_format={output_format}, report_spec={report_spec}")
    try:
        response = connection_maker.get_endpoints_for_asset(asset_guid, output_format=output_format, report_spec=report_spec)
        print(f"Get Endpoints For Asset Result: {json.dumps(response, indent=4) if output_format in ('JSON', 'DICT', 'LIST') else response}")
        assert response is not None
    except Exception as e:
        print(f"Expected failure or error: {e}")

@pytest.mark.asyncio
async def test_link_connection_connector_type(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    print("\nLinking connection to connector type...")
    try:
        connection_maker.link_connection_connector_type("conn-guid", "ct-guid", {"class": "NewRelationshipRequestBody"})
    except Exception as e:
        print(f"Expected failure or error: {e}")

@pytest.mark.asyncio
async def test_detach_connection_connector_type(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    print("\nDetaching connection from connector type...")
    try:
        connection_maker.detach_connection_connector_type("conn-guid", "ct-guid", {"class": "DeleteRelationshipRequestBody"})
    except Exception as e:
        print(f"Expected failure or error: {e}")

@pytest.mark.asyncio
async def test_link_connection_endpoint(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    print("\nLinking connection to endpoint...")
    try:
        connection_maker.link_connection_endpoint("conn-guid", "ep-guid", {"class": "NewRelationshipRequestBody"})
    except Exception as e:
        print(f"Expected failure or error: {e}")

@pytest.mark.asyncio
async def test_detach_connection_endpoint(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    print("\nDetaching connection from endpoint...")
    try:
        connection_maker.detach_connection_endpoint("conn-guid", "ep-guid", {"class": "DeleteRelationshipRequestBody"})
    except Exception as e:
        print(f"Expected failure or error: {e}")

@pytest.mark.asyncio
async def test_link_embedded_connection(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    print("\nLinking embedded connection...")
    try:
        connection_maker.link_embedded_connection("conn-guid", "embed-guid", {"class": "NewRelationshipRequestBody"})
    except Exception as e:
        print(f"Expected failure or error: {e}")

@pytest.mark.asyncio
async def test_detach_embedded_connection(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    print("\nDetaching embedded connection...")
    try:
        connection_maker.detach_embedded_connection("conn-guid", "embed-guid", {"class": "DeleteRelationshipRequestBody"})
    except Exception as e:
        print(f"Expected failure or error: {e}")

@pytest.mark.asyncio
async def test_link_asset_to_connection(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    print("\nLinking asset to connection...")
    try:
        connection_maker.link_asset_to_connection("asset-guid", "conn-guid", {"class": "NewRelationshipRequestBody"})
    except Exception as e:
        print(f"Expected failure or error: {e}")

@pytest.mark.asyncio
async def test_detach_asset_from_connection(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    print("\nDetaching asset from connection...")
    try:
        connection_maker.detach_asset_from_connection("asset-guid", "conn-guid", {"class": "DeleteRelationshipRequestBody"})
    except Exception as e:
        print(f"Expected failure or error: {e}")

@pytest.mark.asyncio
async def test_link_endpoint_to_it_asset(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    print("\nLinking endpoint to IT asset...")
    try:
        connection_maker.link_endpoint_to_it_asset("asset-guid", "ep-guid", {"class": "NewRelationshipRequestBody"})
    except Exception as e:
        print(f"Expected failure or error: {e}")

@pytest.mark.asyncio
async def test_detach_endpoint_from_it_asset(connection_maker):
    await connection_maker._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    print("\nDetaching endpoint from IT asset...")
    try:
        connection_maker.detach_endpoint_from_it_asset("asset-guid", "ep-guid", {"class": "DeleteRelationshipRequestBody"})
    except Exception as e:
        print(f"Expected failure or error: {e}")
