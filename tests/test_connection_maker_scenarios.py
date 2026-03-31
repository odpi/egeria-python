
import pytest
import time
import asyncio
from pyegeria.omvs.connection_maker import ConnectionMaker

# Testing constants
VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "garygeeke"
USER_PWD = "secret"

@pytest.fixture
async def connection_maker():
    client = ConnectionMaker(VIEW_SERVER, PLATFORM_URL, USER_ID, USER_PWD)
    await client._async_create_egeria_bearer_token(USER_ID, USER_PWD)
    return client

@pytest.mark.asyncio
async def test_full_connection_setup_scenario(connection_maker):
    """
    Scenario:
    1. Create an Endpoint
    2. Create a Connector Type
    3. Create a Connection
    4. Attach Connector Type to Connection
    5. Attach Endpoint to Connection
    6. Verify (via retrieve)
    7. Clean up (detach and delete)
    """
    ts = int(time.time())
    
    try:
        # 1. Create Endpoint
        ep_body = {
            "class": "NewElementRequestBody",
            "properties": {
                "class": "EndpointProperties",
                "qualifiedName": f"Scenario::Endpoint::{ts}",
                "displayName": "Scenario Endpoint",
                "networkAddress": "localhost:9000"
            }
        }
        response = await connection_maker._async_create_endpoint(ep_body)
        ep_guid = response.get("guid") if isinstance(response, dict) else response
        assert ep_guid is not None
        
        # 2. Create Connector Type
        ct_body = {
            "class": "NewElementRequestBody",
            "properties": {
                "class": "ConnectorTypeProperties",
                "qualifiedName": f"Scenario::ConnectorType::{ts}",
                "displayName": "Scenario ConnectorType",
                "connectorProviderClassName": "org.odpi.egeria.test.ScenarioProvider"
            }
        }
        response = await connection_maker._async_create_connector_type(ct_body)
        ct_guid = response.get("guid") if isinstance(response, dict) else response
        assert ct_guid is not None
        
        # 3. Create Connection
        conn_body = {
            "class": "NewElementRequestBody",
            "properties": {
                "class": "ConnectionProperties",
                "qualifiedName": f"Scenario::Connection::{ts}",
                "displayName": "Scenario Connection"
            }
        }
        response = await connection_maker._async_create_connection(conn_body)
        conn_guid = response.get("guid") if isinstance(response, dict) else response
        assert conn_guid is not None
        
        # 4. Attach Connector Type
        rel_body = {"class": "NewRelationshipRequestBody"}
        await connection_maker._async_link_connection_connector_type(conn_guid, ct_guid, rel_body)
        
        # 5. Attach Endpoint
        await connection_maker._async_link_connection_endpoint(conn_guid, ep_guid, rel_body)
        
        # 6. Retrieve and Verify
        conn_resp = await connection_maker._async_get_connection_by_guid(conn_guid, {"class": "GetRequestBody"})
        assert conn_resp["element"]["elementHeader"]["guid"] == conn_guid
        # Note: Depending on the OMVS implementation, the attached elements might appear in the response 
        # or require separate retrieve calls. For now, we verify the primary element.
        
        # 7. Clean up (Detach and Delete)
        del_rel_body = {"class": "DeleteRelationshipRequestBody"}
        await connection_maker._async_detach_connection_connector_type(conn_guid, ct_guid, del_rel_body)
        await connection_maker._async_detach_connection_endpoint(conn_guid, ep_guid, del_rel_body)
        
        del_body = {"class": "DeleteElementRequestBody"}
        await connection_maker._async_delete_connection(conn_guid, del_body)
        await connection_maker._async_delete_connector_type(ct_guid, del_body)
        await connection_maker._async_delete_endpoint(ep_guid, del_body)
        
    except Exception as e:
        pytest.fail(f"Scenario failed: {e}")
