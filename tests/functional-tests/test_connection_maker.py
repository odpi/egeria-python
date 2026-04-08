"""
Unit tests for the ConnectionMaker OMVS client.
"""

import pytest
from pyegeria.omvs.connection_maker import ConnectionMaker
from pyegeria.models.models import (
    NewElementRequestBody,
    UpdateElementRequestBody,
    DeleteElementRequestBody,
    GetRequestBody,
    FilterRequestBody,
    SearchStringRequestBody,
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
)
import asyncio
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
        conn = await connection_maker._async_get_connection_by_guid(conn_guid, get_body)
        assert conn["element"]["elementHeader"]["guid"] == conn_guid
        
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
        ct = await connection_maker._async_get_connector_type_by_guid(ct_guid, get_body)
        assert ct["element"]["elementHeader"]["guid"] == ct_guid
        
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
        ep = await connection_maker._async_get_endpoint_by_guid(ep_guid, get_body)
        assert ep["element"]["elementHeader"]["guid"] == ep_guid
        
        # 3. Delete Endpoint
        delete_body = {"class": "DeleteElementRequestBody"}
        await connection_maker._async_delete_endpoint(ep_guid, delete_body)
        
    except Exception as e:
        pytest.fail(f"Endpoint lifecycle failed: {e}")
