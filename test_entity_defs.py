import asyncio
from pyegeria.omvs.valid_metadata import ValidMetadataManager
from rich import print

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "erinoverview"
USER_PWD = "secret"

async def main():
    client = ValidMetadataManager(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
    client.create_egeria_bearer_token(USER_ID, USER_PWD)
    
    print("Fetching raw entity defs...")
    # Try the /api/open-metadata/valid-metadata base
    url = f"{PLATFORM_URL}/servers/{VIEW_SERVER}/api/open-metadata/valid-metadata/open-metadata-types/entity-defs"
    resp = await client._async_make_request("GET", url)
    payload = resp.json()
    print("Payload keys:", payload.keys())
    for key in ("typeDefList", "typeDefs", "elements"):
        if key in payload:
            val = payload[key]
            print(f"{key} is a {type(val)}")
            if isinstance(val, list):
                print(f"{key} length: {len(val)}")
                if len(val) > 0:
                    print(f"First element: {val[0]}")
            elif isinstance(val, dict):
                print(f"{key} keys: {val.keys()}")
                for k, v in val.items():
                    print(f"  {k} is a {type(v)}")
    
    print("\nCalling get_all_entity_defs()...")
    entity_defs = client.get_all_entity_defs()
    if isinstance(entity_defs, list):
        print(f"Found {len(entity_defs)} entity defs.")
        if len(entity_defs) > 0:
            print("First few names:", [e.get('name') for e in entity_defs[:5]])
    else:
        print(f"Result: {entity_defs}")

if __name__ == "__main__":
    asyncio.run(main())
