import asyncio
import sys
import os
from pyegeria.omvs.collection_manager import CollectionManager
from pyegeria.omvs.glossary_manager import GlossaryManager
from pyegeria.core.config import get_app_config

async def main():
    config = get_app_config()
    client = CollectionManager(
        view_server="view-server",
        platform_url="https://127.0.0.1:9443",
        user_id="peterprofile",
        user_pwd="peterprofile"
    )
    g_client = GlossaryManager(
        view_server="view-server",
        platform_url="https://127.0.0.1:9443",
        user_id="peterprofile",
        user_pwd="peterprofile"
    )
    
    # 1. First find the "Command" term
    res = await g_client._async_find_glossary_terms("Command")
    if isinstance(res, str) or not res:
        print("No Command term found")
        return
    term_guid = res[0]['elementHeader']['guid']
    print(f"Term GUID: {term_guid}")
    
    # 2. Get its attached collections
    cols = await client._async_get_attached_collections(term_guid)
    if isinstance(cols, str):
        print("No collections attached to term")
        return
        
    for c in cols:
        c_guid = c['elementHeader']['guid']
        name = c.get('properties', {}).get('displayName', 'Unknown')
        print(f"Attached to collection: {name} ({c_guid})")
        
        if "Writing" in name:
            print(f"Attempting to remove term from {name}...")
            # 3. Detach it
            try:
                await client._async_remove_from_collection(c_guid, term_guid)
                print("Detached via PyEgeria successfully! (No python exception)")
            except Exception as e:
                print(f"Exception during detach: {e}")
                
            # 4. Re-fetch
            cols_after = await client._async_get_attached_collections(term_guid)
            after_names = [cc.get('properties', {}).get('displayName', 'Unknown') for cc in (cols_after if not isinstance(cols_after, str) else [])]
            print(f"Collections after detach: {after_names}")
            break

if __name__ == "__main__":
    asyncio.run(main())
