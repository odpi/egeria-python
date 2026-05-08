import asyncio
from pyegeria.omvs.security_officer import SecurityOfficer
from rich import print

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "garygeeke"
USER_PWD = "secret"
PLATFORM_NAME = "Local OMAG Server Platform"

async def main():
    client = SecurityOfficer(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
    client.create_egeria_bearer_token(USER_ID, USER_PWD)
    
    elements = await client._async_get_elements_by_property_value(
        PLATFORM_NAME, 
        ["displayName", "qualifiedName", "resourceName"]
    )
    print(elements)

if __name__ == "__main__":
    asyncio.run(main())
