import asyncio
from pyegeria import EgeriaTech
async def main():
    client = EgeriaTech("erinoverview", "https://localhost:9443", "erinoverview", "erinoverview")
    client.token = client.get_jwt("erinoverview", "erinoverview")
    guid = "acca7cf3-40d4-40fd-9922-5c74075e9651" # Term1
    rels = await client._async_get_related_elements(guid, relationship_type="PreferredTerm", start_at_end=1)
    if rels is None:
        print("Function returned None")
    else:
        print(f"Found {len(rels)} relationships.")
        for r in rels:
            print(r)
asyncio.run(main())
