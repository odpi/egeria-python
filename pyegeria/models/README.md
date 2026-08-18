<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# pyegeria/models

Pydantic models for Egeria REST request/response bodies.

- `models.py` — the main model set: `PyegeriaModel` (the shared base —
  `alias_generator=to_camel_case`, `extra='ignore'`, `populate_by_name=True`)
  and the request-body class hierarchy (`RequestBody` → `GetRequestBody` →
  `ResultsRequestBody` → `FindRequestBody`/`FilterRequestBody`/
  `SearchStringRequestBody`, plus `NewRelationshipRequestBody`,
  `UpdateRelationshipRequestBody`, `DeleteElementRequestBody`,
  `DeleteRelationshipRequestBody`, `DeleteClassificationRequestBody`, and
  more). Every OMVS client's `validate_*_request()` helpers
  (`pyegeria/core/_server_client.py`) validate against classes defined
  here.
- `collection_models.py` — Collection-specific property models.

**The `extra='ignore'` gotcha** (see root `CLAUDE.md`): because
`PyegeriaModel` ignores unknown fields instead of rejecting them, a model
here that's missing a field the real Egeria DTO has will silently drop any
caller-supplied value for it — no exception, no warning. When adding a new
request-body field, cross-check the real body shape in `pyegeria/http
clients/Egeria-api-*.http` (the ground truth), not just "did it validate."

When adding a new model here, follow the existing pattern: field names in
`snake_case`, relying on `to_camel_case` aliasing to produce the wire
`camelCase` name, with an explicit `Field(alias=...)` override only where
the camelCase conversion wouldn't match (e.g. `class_` → `"class"`, or a
name with an all-caps acronym like `GUID`).
