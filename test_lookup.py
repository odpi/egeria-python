import asyncio
from pyegeria import EgeriaTech
import os

async def run():
    client = EgeriaTech()
    name = "DigitalProduct::SalesForecast::Pipeline::1.2"
    print(f"Looking up {name}...")
    guid = await client.__async_get_guid__(qualified_name=name)
    print("Found GUID via __async_get_guid__ QN:", guid)
    guid2 = await client.__async_get_guid__(display_name=name)
    print("Found GUID via __async_get_guid__ Display Name:", guid2)
    guid3 = await client._async_get_guid_for_name(name)
    print("Found GUID via _async_get_guid_for_name:", guid3)
    
if __name__ == "__main__":
    asyncio.run(run())
