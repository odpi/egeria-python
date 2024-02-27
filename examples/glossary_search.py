"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is an example of how to use the Glossary Browser View Service - and a start at some query tests.


"""
from pyegeria import Platform, CoreServerConfig, RegisteredInfo, GlossaryBrowser, ServerOps
import json

mdr = "active-metadata-store"
mdr_view = "view-server"
plat = "https://127.0.0.1:9443"

op_client = ServerOps(mdr,plat,'garygeeke')
op_client.add_archive_file("content-packs/CocoSustainabilityArchive.omarchive")

glossary_guid = "f9b78b26-6025-43fa-9299-a905cc6d1575"  # sustainability glossary

# find glossaries in active-metadata-store - need to use view-server
g_client = GlossaryBrowser(mdr_view, plat,'erinoverview')

token = g_client.create_egeria_bearer_token("peterprofile", "secret")
response = g_client.find_glossaries('*', starts_with=False, ends_with=False,
                                    ignore_case=True,page_size=0, effective_time=None)

print(f"Found {len(response)} glossaries")
print(type(response))
print(f"\n\n Glossary info:\n{json.dumps(response, indent=4)}")

# Being renovated..
#
# lastTime = time.perf_counter()
#     terms = findGlossaryTerms(mdrServerName, devPlatformName,
#                               devPlatformURL, erinsUserId, 'Email1.*',
#                               MyOrg_BG_GUID,['ACTIVE'])
#     printDmpTermElements('-->', terms)
#     print(f" Time to scan 10,000 terms and filter by Status is {time.perf_counter() - lastTime}")
#     lastTime = time.perf_counter()
#     terms = findGlossaryTerms(mdrServerName, devPlatformName,
#                               devPlatformURL, erinsUserId,
#                               '.*77.*', MyOrg_BG_GUID,
#                               ["ACTIVE"])
#     print(terms)
#     print(f" Time to search 10,000 terms for 77 and  filter by Status is {time.perf_counter() - lastTime}")
#
#     lastTime = time.perf_counter()
#     terms = findGlossaryTerms(mdrServerName, devPlatformName,
#                               devPlatformURL, erinsUserId,
#                               '.*77.*', MyOrg_BG_GUID,
#                               ["DRAFT"])
#     print(terms)
#     print(f" Time to search 10,000 terms for 77 and  filter by Status is {time.perf_counter() - lastTime}")
#
#     print("done")