import asyncio
from pyegeria import EgeriaTech

async def main():
    client = EgeriaTech(
        "qs-view-server", 
        "https://localhost:9443", 
        "peterprofile", 
        "secret"
    )
    guid = await client.__async_get_guid__(display_name="Pipeline", qualified_name="DigitalProduct::SalesForecast::Pipeline::1.2")
    print("GUID IS:", guid)

asyncio.run(main())
