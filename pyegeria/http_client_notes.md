# Notes on pyegeria vs. the `http clients/` example collection

The `pyegeria/http clients/*.http` files are periodically replaced wholesale with a fresh
copy from an Egeria distribution (`egeria-platform-*/assembly/opt/http-client-collections`),
so any comments added directly inside those files get wiped out on the next copy. This file
holds the same kind of note durably, outside that directory.

## Known intentional divergences from the `.http` examples

### License / Certification: implemented in `classification_explorer.py`, not `governance_officer.py`

Both `governance-officer` and `classification-explorer` expose real, working REST endpoints
for `updateLicense`, `unlicenseElement`, `updateCertification`, `decertifyElement` (confirmed
against the 6.1 distribution — both view services genuinely offer this operation, not an
example-file duplication bug). pyegeria only implements each **once**, in
`pyegeria/omvs/classification_explorer.py`, to avoid a same-named-method collision under
`EgeriaTech`'s generic `__getattr__` delegation (`self.client.decertify_element(...)` would
otherwise resolve to whichever subclient happens to come first in `_subclient_map`).

`governance_officer.py` keeps only `license_element`/`certify_element` (the create-side calls,
which don't collide — Classification Explorer's create methods are named differently:
`add_license_to_element`/`add_certification_to_element`).

If you ever need the `governance-officer`-specific URL variant specifically (rather than the
functionally-equivalent `classification-explorer` one), it isn't implemented — add it back
under a non-colliding name (e.g. `governance_update_license`) rather than reintroducing the
collision.

### `full_omag_server_config.py`: `set_server_user_password` removed (dead code)

`server-user-password` was never a real endpoint (confirmed against `ConfigPropertiesResource.java`
— only `server-user-id` exists there). This method always 404'd if called, and had no callers
anywhere in this repo, so it was removed outright (2026-08-14 session) rather than kept as a
documented dead end. If a future Egeria version adds a real `server-user-password` endpoint,
re-add it fresh against that controller rather than restoring this version.

## Audit history

- 2026-08-14: Egeria team audit of `view-services`/`view-server-generic-services` `.http`
  collections (missing + broken endpoint examples) — cross-checked against pyegeria, several
  real bugs found and fixed across `action_author.py`, `asset_maker.py`, `connection_maker.py`,
  `governance_officer.py`, `classification_explorer.py`, `collection_manager.py`,
  `runtime_manager.py`, `project_manager.py`, `reference_data.py`.
- 2026-08-14: Egeria team error-only audit of the remaining `.http` collections (admin-services,
  platform-services, server-operations, repository-services, conformance suite,
  omf-metadata-management, connector/demo files) — cross-checked against pyegeria:
  - Fixed the `/users/{userId}/servers/...` stale URL shape (and `integration_daemon` →
    `integration-daemon` hyphenation) in `server_operations.py` (integration-daemon status,
    connector config, restart, refresh, and engine-host governance-engine summaries).
  - Confirmed pyegeria doesn't implement the raw repository-services entity/relationship/type-def
    GET-vs-POST-only endpoints, or the generic OMF `open-metadata-store` API at all — those audit
    findings don't apply here (nothing to fix, not implemented).
  - Confirmed no bypass of the centralized bearer-token request path in the admin/platform/
    server-operations clients, except `platform_services.get_platform_origin()`, which
    intentionally hits the unauthenticated `/api/about` endpoint directly via `httpx` — correct
    as-is, not a bug.
  - Found `set_server_user_password` calls a nonexistent endpoint (see above).
