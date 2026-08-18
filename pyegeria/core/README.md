<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# pyegeria/core

Transport, auth, and config — the layered HTTP stack every OMVS client
builds on, plus shared config/exception/validation infrastructure.

| File | Role |
|---|---|
| `_base_platform_client.py` → `_base_server_client.py` → `_server_client.py` | Layered HTTP stack: platform-level connectivity → server-level auth/session → the shared request/validate/response helpers (`_async_make_request`, `_async_new_relationship_request`, `_async_delete_element_request`, etc.) every `pyegeria/omvs/*.py` client inherits from. |
| `config.py` | Pydantic-settings config; precedence = explicit args > OS env > `.env` > `config.json` > defaults. |
| `_exceptions.py` | The `PyegeriaException` hierarchy — see `pyegeria/README.md`'s "Exceptions in pyegeria" section for the full class list and usage. |
| `_validators.py` | Shared request-body/parameter validation helpers. |
| `_globals.py` | Shared constants (e.g. max paging size). |
| `utils.py` | Shared helpers: `body_slimmer`, `make_format_set_name_from_type`, `dynamic_catch`, camelCase/PascalCase conversion, etc. |
| `relationship_multiplicity.py` | `async_is_multi_link()`/`async_get_relationship_category()` — detects MULTI_LINK relationship types via `ValidMetadataManager.get_all_relationship_defs()`'s `relationshipCategory` field. |
| `logging_configuration.py` | Loguru sink setup. |
| `mcp_adapter.py`, `mcp_server.py` | MCP (Model Context Protocol) server integration. |
| `load_config.py` | Config-file loading helper. |
| `clipboard.py` | Small clipboard-copy utility used by some CLI commands. |
| `create_tech_guid_lists.py` | Helper for building technology-type GUID lookup lists. |

**Gotcha** (see the root `CLAUDE.md`): a request-body Pydantic model in
`pyegeria/models/models.py` missing a field silently drops it rather than
erroring, since every model inherits `PyegeriaModel`'s `extra='ignore'`.
Check a model's fields against the real body in `pyegeria/http clients/
Egeria-api-*.http` before assuming "it validated without error" means a
field will actually be sent.
