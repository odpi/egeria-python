<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# pyegeria/omvs

40+ service-specific OMVS (Open Metadata View Service) clients — one file
per OMVS, each a class extending `ServerClient`
(`pyegeria/core/_server_client.py`). See `__init__.py` for the full
module-to-class mapping (`ActionAuthor`, `ActorManager`, `AssetCatalog`,
`ClassificationExplorer`, `CollectionManager`, `GlossaryManager`,
`GovernanceOfficer`, `MetadataExpert`, `SolutionArchitect`, ...).

Conventions every client follows:
- Every public method has an `_async_*` implementation plus a sync wrapper
  calling `asyncio.get_event_loop().run_until_complete(...)`.
- All public methods are decorated with `@dynamic_catch`.
- **Ground truth for API URLs and request bodies is `pyegeria/http
  clients/Egeria-api-*.http`** — check these files before constructing a
  URL or request body; don't assume. `scripts/omvs_audit.py` automates
  this cross-check.

`pyegeria/egeria_tech_client.py`'s `EgeriaTech` facade lazily proxies
attribute access across all of these via `__getattr__` — don't
instantiate them eagerly there.

When adding a new OMVS method, add its test to the matching file in
`tests/functional-tests/`.
