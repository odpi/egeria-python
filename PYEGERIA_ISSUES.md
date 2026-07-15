# pyegeria / Egeria Upstream Issues

Detailed bug reports for issues hit while building Egeria Explorer, with exact
repro steps so they can be verified and fixed upstream. Compact status tracking
lives in `BACKLOG.md` under "pyegeria Upstream Bugs" (same `PY-#` numbering) —
this document is the expanded version with code you can run directly.

Unless noted otherwise, repro commands assume:
- A running Egeria view server reachable at `https://localhost:9443` (or
  `https://host.docker.internal:9443` from inside a container), view server
  name `qs-view-server`, user `peterprofile` / `secret` (adjust to your env).
- `pip install pyegeria` matching the version noted per issue.

---

## PY-1: `DataDesigner.find_data_value_specifications` calls non-existent `_async_post`

**Status:** fixed — verified 2026-07-14. `_async_post` no longer exists anywhere in
the codebase; `find_data_value_specifications` now routes through the shared
`_async_find_request` helper.

**How to trigger:**
```python
from pyegeria import DataDesigner
mgr = DataDesigner(view_server="qs-view-server", platform_url="https://localhost:9443",
                    user_id="peterprofile", user_pwd="secret")
mgr.create_egeria_bearer_token()
mgr.find_data_value_specifications(search_string="*")
```

**Expected:** a list of `DataValueSpecification` elements matching the search string.

**Actual:** `AttributeError: 'DataDesigner' object has no attribute '_async_post'`

**Root cause:** the method body calls `self._async_post(...)`, which has never
existed in pyegeria. The correct internal method is `_async_make_request`.

**Workaround:** call `mgr._async_make_request("POST", url, body)` directly against
the `/data-value-specifications/by-search-string` endpoint (see
`_search_data_value_specs()` in `data_design_handler.py`).

---

## PY-2: `get_data_value_specifications_by_name("*")` rejects wildcard

**Status:** fixed 2026-07-14. Root cause was in the shared
`_async_get_name_request` helper (`pyegeria/core/_server_client.py`), which
every `get_*_by_name` method funnels through: it mapped the `"*"` convenience
sentinel to the literal string `".*"` instead of `None`. Egeria's by-name
`filter` field is not a regex — it does not treat `".*"` as "match anything",
so this either matched nothing or matched literally. Every sibling helper
(`_async_activity_status_filter_request` and others) already correctly mapped
`"*"` → `None`, which is Egeria's actual "any" sentinel for that field; this
one helper was the outlier. Fixed by aligning it with the rest:
`filter_string = None if filter_string == "*" else filter_string`.

**How to trigger:**
```python
from pyegeria import DataDesigner
mgr = DataDesigner(view_server="qs-view-server", platform_url="https://localhost:9443",
                    user_id="peterprofile", user_pwd="secret")
mgr.create_egeria_bearer_token()
mgr.get_data_value_specifications_by_name("*")
```

**Expected:** all `DataValueSpecification` elements (wildcard listing), matching
the convention used by most other `get_*_by_name` methods in pyegeria.

**Actual:** server error `OPEN-METADATA-400-004: The name passed on the name
parameter of getDataValueSpecificationsByName is null` — the `"*"` sentinel is
not special-cased and gets treated as a literal (invalid) name filter.

**Workaround:** use `_search_data_value_specs()` (hits `/by-search-string`
directly) for listing `DataGrain`/`DataClass` instead of this method.

---

## PY-3: `find_all_solution_blueprints` / `find_all_solution_components` missing in 6.0.12.2

**Status:** fixed/moot — verified 2026-07-14. Both methods exist in the current
codebase (pyegeria 6.0.16.17), well past the 6.0.12.4 floor where they were
added. Was a version-pinning issue, not a code defect.

**How to trigger:**
```python
from pyegeria import SolutionArchitect
mgr = SolutionArchitect(view_server="qs-view-server", platform_url="https://localhost:9443",
                         user_id="peterprofile", user_pwd="secret")
mgr.create_egeria_bearer_token()
mgr.find_all_solution_blueprints()
```

**Expected:** all solution blueprints returned.

**Actual (on pyegeria 6.0.12.2):** `AttributeError` — the method was added in
6.0.12.4 but the container was pinned to 6.0.12.2 at the time.

**Workaround:** use `find_solution_blueprints(search_string="*")` /
`find_solution_components(search_string="*")`, which exist in both versions.

**Note:** verify current pinned version before re-testing — this may already be
fixed by a floor bump.

---

## PY-4: `ServerClient.update_comment` sends `mergeUpdate: true` but server still demands `qualifiedName`

**Status:** done (workaround shipped, not an upstream fix)

**How to trigger:**
```python
from pyegeria import CommentManager  # or whichever OMVS client exposes update_comment
mgr = CommentManager(view_server="qs-view-server", platform_url="https://localhost:9443",
                      user_id="peterprofile", user_pwd="secret")
mgr.create_egeria_bearer_token()
mgr.update_comment(comment_guid="<guid>", body={"commentText": "edited text"})
```

**Expected:** partial update succeeds since `merge_update` defaults to `True`
(only the supplied fields should be required).

**Actual:** `OPEN-METADATA-400-004` demanding `qualifiedName`, even though the
request body already sets `"mergeUpdate": true`.

**Workaround:** `egeria_feedback_handler.py` fetches the comment first via
`get_comment_by_guid`, extracts `qualifiedName`, and builds the update body
manually so it's always present regardless of `mergeUpdate`.

---

## PY-5: `get_notes_for_note_log` broken pre-6.0.14.6, version-sensitive

**Status:** fixed in 6.0.14.6/.7 — **regression risk on any `pip install --upgrade` that lands on 6.0.14.4/.5**

**How to trigger the broken behavior (pyegeria 6.0.14.4 or .5):**
```python
from pyegeria import NoteLogManager  # or whichever OMVS client has the mixin
mgr = NoteLogManager(view_server="qs-view-server", platform_url="https://localhost:9443",
                      user_id="peterprofile", user_pwd="secret")
mgr.create_egeria_bearer_token()
mgr.get_notes_for_note_log(note_log_guid="<guid-of-a-note-log>")
```

**Expected:** the list of notes contained in the note log.

**Actual (6.0.14.4/.5):**
- Default `metadata_element_type_name="Action"` → server error
  `OMAG-REPOSITORY-HANDLER-404-001` ("guid is of type NoteLog rather than Action").
- Passing `metadata_element_type_name="NoteLog"` returns the **log itself**, not
  its notes.
- Large logs (hundreds of entries) time out.

**Fixed in 6.0.14.6+:** default kwargs (no `metadata_element_type_name`
override) now return the notes list, or the sentinel string `"No elements
found"` for a genuinely empty log. **Gotcha:** do NOT pass
`metadata_element_type_name="NoteLog"` anymore — it now returns 0 notes.

**Regression seen 2026-06-17:** a plain `pip install pyegeria --upgrade` inside
the Docker build pulled 6.0.14.4 from PyPI (a point release had been yanked/
reordered), silently emptying the Egeria Explorer Note Logs tab in production.

**Mitigation shipped:** floor-pinned `pyegeria>=6.0.14.6` in both
`Dockerfile-fast-api` and `requirements.txt` (freshstart + quickstart). Note
that `uvicorn --reload` only watches `.py` files — a package upgrade needs an
explicit container/worker restart to take effect, which is why the regression
went unnoticed for a while.

---

## PY-6: `find_note_logs('*')` is O(total notes across every log) at default depth

**Status:** not a pyegeria bug — reclassified 2026-07-14. This is Egeria view
server behavior: `graph_query_depth` controls how much relationship graph the
server computes per element, and defaulting to depth 3 is a deliberate
trade-off (rich results by default), not a defect. pyegeria already exposes
`graph_query_depth=0` for callers who want the cheap listing. No client-side
fix needed; left here for reference/discoverability only.

**How to trigger:**
```python
import time
from pyegeria import NoteLogManager
mgr = NoteLogManager(view_server="qs-view-server", platform_url="https://localhost:9443",
                      user_id="peterprofile", user_pwd="secret")
mgr.create_egeria_bearer_token()

t0 = time.time()
mgr.find_note_logs("*")
print(time.time() - t0)   # ~30-70s on the qs demo data
```

**Expected:** a fast "list of note logs" call, since callers usually just want
names/GUIDs to populate a list UI.

**Actual:** at the default graph query depth, the call inlines **every note
log's full `noteLogEntries` array**. On the qs demo data two system logs hold
~1000 / ~500 entries each, making a supposedly cheap listing call take
30-70 seconds — unusable directly in a request/response HTTP handler.

**Workaround:** `graph_query_depth=0` **is silently accepted via `**kwargs`
even though it's not in the method signature**, and brings this down to ~0.3s
(returns names/qualifiedNames only, no `noteLogSubjects`/`noteLogEntries`).
```python
mgr.find_note_logs("*", graph_query_depth=0)   # ~0.3s
```
`notelog_handler.py`'s list view uses this; detail view does a second,
separately-bounded call (`get_notes_for_note_log(guid, page_size=100)`) for the
actual entries.

**Suggested upstream fix:** either (a) make `graph_query_depth=0` the default
for `find_note_logs`, or (b) document that the entries expansion is
depth-gated and add it explicitly to the method signature instead of leaving
it as an undocumented passthrough kwarg.

---

## PY-7 / PY-8 / PY-11: `as_of_time` missing or silently dropped on several methods

**Status:** mostly fixed — verified 2026-07-14. `find_information_supply_chains`,
`find_governance_definitions`, `find_note_logs`, `find_collections`,
`find_data_structures`, and `get_technology_type_elements` all now route
through shared helpers (`_async_find_request` / `_async_get_name_request`)
that either take `as_of_time` as an explicit named parameter or splat
`**kwargs` directly into the validated request body, so it's threaded through
correctly now.

**`get_valid_metadata_values` reclassified, not a pyegeria fix:** checked the
ground-truth `.http` files — `get-valid-metadata-values/{propertyName}` is a
plain GET endpoint taking only `typeName`/`startFrom`/`pageSize` query params;
`asOfTime` never appears there, only on POST-body search/filter endpoints
elsewhere. The Egeria server doesn't expose historical-query capability on
this endpoint at all, so adding an `as_of_time` param client-side would be
dead code (silently ignored server-side) — the same "looks accepted, has no
effect" failure mode this issue originally complained about, just moved one
layer down. No pyegeria change needed; this would need an Egeria REST API
change to add `asOfTime` support to that endpoint first.

**`get_technology_type_elements`:** now has `**kwargs` and merges them into
the `FilterRequestBody` dict when `body` is not explicitly supplied, so
`as_of_time` passed as a kwarg does reach the body. Fixed.

Surfaced during the LE-3 "time travel" audit (2026-06-21/22). All of the
following accept `as_of_time` either not at all, or only via `**kwargs` where
it's silently swallowed because the method builds its request body from
explicit named parameters instead of forwarding `kwargs` into the body:

| Method | Symptom |
|---|---|
| `ValidMetadataManager.get_valid_metadata_values` | no `as_of_time` param, no `**kwargs` — can't pass it at all |
| `get_technology_type_elements` | same — no param, no `**kwargs` |
| `find_information_supply_chains` | accepts `**kwargs` but ignores `as_of_time` (body built from explicit params) |
| `find_governance_definitions` | same pattern |
| `find_note_logs` | same pattern |
| `find_collections` | same pattern |
| `find_data_structures` | same pattern |

**How to trigger (representative — `find_note_logs`):**
```python
from pyegeria import NoteLogManager
mgr = NoteLogManager(view_server="qs-view-server", platform_url="https://localhost:9443",
                      user_id="peterprofile", user_pwd="secret")
mgr.create_egeria_bearer_token()
# as_of_time is accepted (no TypeError) but has NO effect on the results —
# compare against a call without it; results are identical regardless of date.
r1 = mgr.find_note_logs("*", graph_query_depth=0)
r2 = mgr.find_note_logs("*", graph_query_depth=0, as_of_time="2020-01-01T00:00:00Z")
assert r1 == r2  # true today; should differ if the entity existed with different content at that time
```

For `get_valid_metadata_values` / `get_technology_type_elements`, passing
`as_of_time=...` raises `TypeError: unexpected keyword argument` since there's
no `**kwargs` catch-all at all.

**Expected:** consistent with `find_communities`/`find_projects`/etc., which
already accept and honor `as_of_time` directly — these should follow the same
pattern.

**Impact:** blocks time-travel (viewing metadata as of a past date) in Egeria
Explorer for: Reference Data / Valid Values lists, Tech Type member lists,
Information Supply Chains, Governance definitions, Note Logs, Data Design
specs/structures, and Collections.

**Suggested upstream fix:** add `as_of_time: Optional[str] = None` directly to
each method's signature and thread it into the constructed request body,
matching the already-correct `find_communities`/`find_projects` implementation.

---

## PY-9: Local `as_of_time` fixes not shipped to the deployed pyegeria package

**Status:** likely resolved — verified 2026-07-14. `get_linked_projects`,
`get_collection_members`, and `get_data_field_by_guid` all have `**kwargs` in
current source, and the package is at 6.0.16.17 (past the 6.0.15.5 mentioned
in the original report). Recommend a live-server smoke test to confirm the
currently-installed release actually contains these before closing — the
original complaint was about release/deploy timing, not logic.

Local edits already exist (uncommitted/unreleased) in `project_manager`
(`get_linked_projects`), `collection_manager` (`get_collection_members`), and
`data_designer` (`get_data_field_by_guid`) to add `as_of_time` support — but
the deployed containers `pip install` the released `pyegeria` from PyPI
(6.0.15.5 at time of writing), not an editable install of the local checkout.

**How to trigger:** call any of the three methods above with `as_of_time=...`
against a container running the released package:
```python
mgr.get_linked_projects(guid="<guid>", as_of_time="2026-06-01T00:00:00Z")
# TypeError: get_linked_projects() got an unexpected keyword argument 'as_of_time'
```

**Fix needed:** cut a pyegeria release including these three changes, or mount
the local `pyegeria-python` checkout as an editable install into
`pyegeria-web` for development/testing.

---

## PY-10: (closed, not a bug) Asset detail by-guid "rejecting" `asOfTime`

**Status:** closed — investigated 2026-06-21, confirmed not a defect.

`get_asset_graph_by_guid` / `get_asset_by_guid` **do** honor `asOfTime`
correctly. The original 404/500 reports were caused by test timestamps (2020,
2026-06-01) that predate the entity's repository version after the demo data
was reloaded on 2026-06-17 — Egeria correctly reports "not found at that time"
(`OMAG-REPOSITORY-HANDLER-404-007`), surfaced as 404 by the by-guid retrieve
and 500 by the graph endpoint (the graph endpoint's 500-vs-404 mapping is a
minor rough edge but not the reported bug). No pyegeria/Egeria change needed;
Egeria Explorer's asset detail handler now degrades this to a clean 404 with a
friendly "not present at the selected time" message.

---

## PY-12: `pyegeria.ReferenceDataManager` does not have specification-property or valid-metadata-value methods

**Status:** open — not necessarily a bug, but a sharp edge worth documenting/fixing in method placement or docs.

**Environment:** pyegeria 6.0.16.16.

**How to trigger:**
```python
from pyegeria import ReferenceDataManager
mgr = ReferenceDataManager(view_server="qs-view-server", platform_url="https://localhost:9443",
                            user_id="peterprofile", user_pwd="secret")
mgr.create_egeria_bearer_token()
mgr.get_specification_property_types()
```

**Expected (reasonable assumption):** since `ReferenceDataManager` is the
class already used successfully for `get_valid_metadata_values`/
`lookup_valid_values` elsewhere in this codebase, it's natural to assume all
"valid metadata"-flavored methods (including specification properties) live on
it too.

**Actual:** `AttributeError: 'ReferenceDataManager' object has no attribute
'get_specification_property_types'`

**Root cause:** `ReferenceDataManager` inherits only from `ServerClient`
(it's for *business* reference data — country codes, currency codes, etc.),
**not** from `ValidMetadataManager`. `get_valid_metadata_values` happens to
work on it because that particular method lives on the shared `ServerClient`/
`BaseServerClient` base class, not on `ValidMetadataManager` — which makes the
class boundary easy to misjudge. The specification-property methods
(`get_specification_property_types`, `get_specification_property_by_type`,
`get_specification_property_by_name`, `get_specification_property_by_guid`,
`find_specification_property`) only exist on **`pyegeria.SpecificationProperties`**
(also `ValidMetadataManager` subclasses: `ValidMetadataLists`, `ValidTypeLists`).

**Fix:** use `pyegeria.SpecificationProperties(...)` for these calls instead.

**Suggested upstream improvement:** either (a) add a class-level docstring
note on `ReferenceDataManager` clarifying it does not cover specification
properties/valid metadata values despite the similar naming, or (b) expose a
single unified client (or a documented decision tree) for "which OMVS client
class do I need" across `ReferenceDataManager` / `SpecificationProperties` /
`ValidMetadataLists` / `ValidTypeLists` / `MetadataExpert`, since several of
these overlap in purpose and are easy to reach for interchangeably.

---

## PY-13: `SpecificationProperties.get_specification_property_by_type` always returns 400 regardless of the value passed

**Status:** open, reclassified as Egeria server bug 2026-07-14 — not
actionable in pyegeria. Root cause is server-side (Spring `@RequestParam` enum
binding drifted from the OpenAPI-declared enum, per the original analysis
below). No pyegeria code change will fix a 400 the server returns for every
input; keep the `find_specification_property("*", ...)` workaround in place
and track this against the Egeria server issue tracker. Re-verify once the
in-flight Egeria server fixes land.

**Environment:** pyegeria 6.0.16.16, Egeria view server 6.1-SNAPSHOT.

**How to trigger:**
```python
from pyegeria import SpecificationProperties
import pyegeria
pyegeria.enable_ssl_check = False
pyegeria.disable_ssl_warnings = True

mgr = SpecificationProperties(view_server="qs-view-server", platform_url="https://localhost:9443",
                               user_id="peterprofile", user_pwd="secret")
mgr.create_egeria_bearer_token()

# get_specification_property_types() works and returns e.g. "PlaceholderProperty"
# as one of the keys (PascalCase type names).
types = mgr.get_specification_property_types()
print(list(types.keys())[:5])

# Passing that type name straight through fails:
mgr.get_specification_property_by_type("PlaceholderProperty")
```

**Expected:** the list of specification properties whose type matches
`PlaceholderProperty`.

**Actual:** `pyegeria.core._exceptions.PyegeriaClientException` wrapping an
HTTP 400 from the view server, body:
```json
{"timestamp":"...","status":400,"error":"Bad Request","path":"/servers/qs-view-server/api/open-metadata/valid-metadata/specification-properties/by-type"}
```
with no further detail. This 400 is returned for **every** value tried:
- the plain type name (`"PlaceholderProperty"`)
- the enum-wrapped form shown in the endpoint's own OpenAPI spec, e.g.
  `"SpecificationPropertyType{placeholderProperty}"`
- the same enum-wrapped form, percent-encoded for the `{`/`}` characters

**Extra detail for whoever picks this up:** the OpenAPI schema for
`POST /servers/{serverName}/api/open-metadata/{urlMarker}/specification-properties/by-type`
declares `specificationPropertyType` as a **required query param** with an
`enum` of literal strings that look like Java `toString()` output, e.g.:
```
"SpecificationPropertyType{placeholderProperty}"
"SpecificationPropertyType{replacementAttribute}"
"SpecificationPropertyType{supportedTemplate}"
...
```
Fetch this yourself to confirm against your running server:
```python
import httpx
r = httpx.get("https://localhost:9443/v3/api-docs", headers=mgr.headers, verify=False)
spec = r.json()
print(spec["paths"]["/servers/{serverName}/api/open-metadata/{urlMarker}/specification-properties/by-type"])
```
Every one of these enum literal values, tried verbatim as the query param,
still 400s — suggesting the Spring `@RequestParam` enum converter registered
for this parameter does not actually accept the same string form that
springdoc used to generate the schema's enum listing (i.e., the OpenAPI spec
and the real converter have drifted apart), or there's a related failure with
how `pyegeria` posts the required `ResultsRequestBody` alongside a query
param on the same request. Needs someone with server-side access to add
logging/debug the `@RequestParam` binding for `getSpecificationPropertyByType`.

**Workaround (shipped in `valid_values_handler.py`, both freshstart/quickstart
copies of Egeria Explorer):** use the working
`find_specification_property("*", ...)` (by-search-string) endpoint instead,
and filter client-side on `element["properties"]["identifier"]`, which holds
the camelCase form of the type name (`"PlaceholderProperty"` ->
`"placeholderProperty"`). See PY-14 for a critical performance caveat on that
workaround.

---

## PY-14: `find_specification_property` (and likely other `find_*` methods) is O(n) per element unless `graph_query_depth=0` — same root cause as PY-6

**Status:** not a pyegeria bug — reclassified 2026-07-14, same as PY-6. This
is Egeria view server behavior (graph computation cost scales with
`graph_query_depth`), not a defect; `graph_query_depth=0` is already the
documented, working opt-out for bulk listing calls. No client-side fix
needed.

**Environment:** pyegeria 6.0.16.16.

**How to trigger:**
```python
import time
from pyegeria import SpecificationProperties
import pyegeria
pyegeria.enable_ssl_check = False
pyegeria.disable_ssl_warnings = True

mgr = SpecificationProperties(view_server="qs-view-server", platform_url="https://localhost:9443",
                               user_id="peterprofile", user_pwd="secret")
mgr.create_egeria_bearer_token()

t0 = time.time()
r = mgr.find_specification_property("*", page_size=1000)   # default graph_query_depth=3
print("default depth:", time.time() - t0, "elements:", len(r))

t0 = time.time()
r = mgr.find_specification_property("*", page_size=1000, graph_query_depth=0)
print("depth=0:       ", time.time() - t0, "elements:", len(r))
```

**Expected:** a bulk search/listing call should be roughly linear in the
number of results and fast enough for interactive use (sub-second to a couple
seconds for 1000 elements).

**Actual (measured on qs demo data, 1000-element result set):**
- Default `graph_query_depth=3`: **~50 seconds**
- `graph_query_depth=0`: **~0.6-2 seconds**

Both calls return identical flat `properties` data per element (displayName,
description, preferredValue, identifier, dataType, etc.) — the only
difference at depth 0 is the omission of `mermaidGraph` and any expanded
relationship graph, which most bulk-listing callers don't need anyway.

**Root cause:** same as PY-6 (`find_note_logs`) — the default graph query
depth makes the view server compute a full relationship graph / mermaid
diagram per returned element, turning an O(n) listing into effectively O(n ×
graph-computation-cost). This is at minimum the second unrelated `find_*`
method with this exact performance cliff; there are likely more.

**Workaround:** always pass `graph_query_depth=0` explicitly on any `find_*`
or `get_*` bulk-listing call unless the caller actually needs the
graph/mermaid output. Used in `valid_values_handler.py`'s Specification
Property Values lookup (`find_specification_property("*", page_size=1000,
graph_query_depth=0)`) and `notelog_handler.py`'s note log listing.

**Suggested upstream fix:** either (a) default `graph_query_depth` to `0`
across `find_*`/list-style methods (opt-in to the expensive graph, not
opt-out), or (b) split "list" and "graph" into genuinely separate REST
operations so the expensive computation isn't hidden behind a depth parameter
that's easy to leave at its default.

---

## Quick reference: which OMVS client class for which purpose

| Need | Class | Notes |
|---|---|---|
| Business reference data (country/currency codes) | `ReferenceDataManager` | Does **not** cover specification properties (PY-12, docs-only) |
| Valid metadata values for a property name | `ReferenceDataManager` or `MetadataExpert` | `get_valid_metadata_values` lives on shared `ServerClient` base; no `as_of_time` support — Egeria endpoint doesn't expose it |
| Specification properties (placeholders, guards, action targets, etc.) | `SpecificationProperties` | Avoid `get_specification_property_by_type` (PY-13, Egeria server bug); use `find_specification_property` with `graph_query_depth=0` (PY-14, expected Egeria behavior, not a bug) |
| `DataGrain` / `DataClass` listing | `find_data_value_specifications` / `get_data_value_specifications_by_name("*")` | Both fixed (PY-1, PY-2) — safe to use directly now |
| `DataSpec` (Collection subtype) | `CollectionManager.find_collections(metadata_element_type="DataSpec")` | |
| `DataStructure` / `DataField` | `DataDesigner.find_data_structures` / `find_data_fields` | |
| Solution blueprints/components (any pyegeria version) | `SolutionArchitect.find_solution_blueprints/components(search_string="*")` | Avoid `find_all_*` variants (PY-3) |
| Note logs (list) | `find_note_logs("*", graph_query_depth=0)` | PY-6 |
| Note logs (entries) | `get_notes_for_note_log(guid, page_size=100)` | PY-5 — never pass `metadata_element_type_name="NoteLog"` |
