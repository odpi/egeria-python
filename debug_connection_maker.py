
import asyncio
from pyegeria.omvs.connection_maker import ConnectionMaker
import logging

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)

async def debug_create_connection():
    VIEW_SERVER = "qs-view-server"
    PLATFORM_URL = "https://localhost:9443"
    USER_ID = "garygeeke"
    USER_PWD = "secret"

    client = ConnectionMaker(VIEW_SERVER, PLATFORM_URL, USER_ID, USER_PWD)
    
    try:
        print("Creating token...")
        await client._async_create_egeria_bearer_token(USER_ID, USER_PWD)
        print("Token created.")

        import time
        ts = int(time.time())
        conn_body = {
            "class": "NewElementRequestBody",
            "properties": {
                "class": "ConnectionProperties",
                "qualifiedName": f"DebugConnection::{ts}",
                "displayName": "Debug Connection",
                "description": "A connection for debugging"
            }
        }
        
        print("Creating connection...")
        guid = await client._async_create_connection(conn_body)
        print(f"Connection created with GUID: {guid}")

        print("Retrieving connection...")
        conn = await client._async_get_connection_by_guid(guid, {"class": "GetRequestBody"})
        import json
        print(f"Connection retrieved: {json.dumps(conn, indent=2)}")

        print("Testing connector type lifecycle...")
        ct_body = {
            "class": "NewElementRequestBody",
            "properties": {
                "class": "ConnectorTypeProperties",
                "qualifiedName": f"DebugConnectorType::{ts}",
                "displayName": "Debug ConnectorType",
                "connectorProviderClassName": "org.odpi.egeria.test.TestProvider"
            }
        }
        ct_guid = await client._async_create_connector_type(ct_body)
        print(f"ConnectorType created with GUID: {ct_guid}")

        print("Deleting ConnectorType...")
        await client._async_delete_connector_type({
            "class": "DeleteElementRequestBody",
            "externalSourceGUID": ct_guid
        })
        print("ConnectorType deleted.")
        
    except Exception as e:
        print(f"Error occurred: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_create_connection())
