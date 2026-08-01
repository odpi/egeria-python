# Pyegeria / Egeria Issue Tracker

Merged from the former `PYEGERIA_ISSUES.md` (Egeria Explorer usage bugs,
started 2026-06) and `PYEGERIA_GAPS.md` (exception/validation infrastructure
gaps, started 2026-07-31) into one file, with every entry re-verified against
the current codebase as of 2026-07-31 rather than trusting old status claims.

**Layer classification** — every entry is tagged with where the defect
actually lives, since that determines who can fix it:
- **Pyegeria** — a defect in this repo's own code (`pyegeria/`). Fixable
  here directly.
- **Egeria Server** — the view server / repository returns wrong or
  inconsistent behavior; no pyegeria client-side change can fix it. Track
  against the Egeria server issue tracker.
- **Not a bug** — deliberate behavior, a deployment/version-pinning issue,
  or a docs/class-organization sharp edge rather than a defect.

**Status values:** `open` (found, not yet reviewed) · `fixed` (patched in
this repo, verified) · `wont-fix` (owner decided against it, reason noted) ·
`n/a` (not a bug / nothing to fix here).

**Numbering:** unified as `ISSUE-#`, sequential by section. Old references
carried forward in parens for traceability (`PY-#` from the original issues
doc, `GAP-#` from the gaps doc). Note: the original issues doc's header
claimed compact status tracking also lived in `BACKLOG.md` under a
"pyegeria Upstream Bugs" section using the same `PY-#` numbering — checked
git history, that section never existed in `BACKLOG.md`. That
cross-reference was already stale; not carried forward here.

Unless noted otherwise, repro commands assume a running Egeria view server
reachable at `https://localhost:9443`, view server name `qs-view-server`,
user `erinoverview` / `secret` (adjust to your env) — updated from the
original `peterprofile` since several of the old repro snippets used a
class (`NoteLogManager`, `CommentManager`) that doesn't exist in the current
package; replaced with `EgeriaTech`, which does.

---

## Section 1 — Pyegeria bugs, fixed

### ISSUE-1 (PY-1): `DataDesigner.find_data_value_specifications` called non-existent `_async_post`

**Status:** fixed, re-verified 2026-07-31 — `_async_post` no longer exists
anywhere in the codebase (`grep -rn "_async_post\b" pyegeria/` returns
nothing); `find_data_value_specifications` now routes through the shared
`_async_find_request` helper.

```python
from pyegeria import DataDesigner
mgr = DataDesigner(view_server="qs-view-server", platform_url="https://localhost:9443",
                    user_id="erinoverview", user_pwd="secret")
mgr.create_egeria_bearer_token()
mgr.find_data_value_specifications(search_string="*")
```

---

### ISSUE-2 (PY-2): `get_data_value_specifications_by_name("*")` rejected the wildcard

**Status:** fixed, re-verified 2026-07-31 — the shared
`_async_get_name_request` helper (`_server_client.py`) still correctly maps
`filter_string = None if filter_string == "*" else filter_string`, aligned
with every sibling helper's "any" sentinel handling.

Root cause was the `"*"` convenience sentinel being sent to Egeria as the
literal string `".*"` instead of `None` — Egeria's by-name `filter` field is
not a regex, so `".*"` either matched nothing or matched literally.

```python
from pyegeria import DataDesigner
mgr = DataDesigner(view_server="qs-view-server", platform_url="https://localhost:9443",
                    user_id="erinoverview", user_pwd="secret")
mgr.create_egeria_bearer_token()
mgr.get_data_value_specifications_by_name("*")
```

---

### ISSUE-3 (PY-5): `get_notes_for_note_log` broken on pyegeria 6.0.14.4/.5

**Status:** fixed, re-verified 2026-07-31 (live). The default
`metadata_element_type_name="Action"` in `_async_get_notes_for_note_log`
(`_server_client.py`) looks superficially like it could still trigger the
originally-reported 404, but a live call against a real note log guid
(`901aab3a-e6f9-4bd1-8899-f013150fbcd4`) returned the correct note list (1
note, no error) — confirmed by direct test, not just by reading the code.

Originally on 6.0.14.4/.5: the default caused
`OMAG-REPOSITORY-HANDLER-404-001` ("guid is of type NoteLog rather than
Action"); passing `metadata_element_type_name="NoteLog"` returned the log
itself, not its notes. Fixed in 6.0.14.6+.

**Regression risk carried forward:** a `pip install pyegeria --upgrade`
that lands on exactly 6.0.14.4/.5 (a yanked/reordered PyPI point release)
would resurface this. Floor-pin `pyegeria>=6.0.14.6` in any deployment that
installs from PyPI rather than an editable local checkout. Also: do NOT
pass `metadata_element_type_name="NoteLog"` — it returns 0 notes even on
fixed versions.

```python
from pyegeria import EgeriaTech
client = EgeriaTech(view_server="qs-view-server", platform_url="https://localhost:9443",
                     user_id="erinoverview", user_pwd="secret")
client.create_egeria_bearer_token()
client.get_notes_for_note_log(note_log_guid="<guid-of-a-note-log>")
```

---

### ISSUE-4 (PY-7/8/11): `as_of_time` missing or silently dropped on several find methods

**Status:** fixed, re-verified 2026-07-31 — `find_information_supply_chains`,
`find_governance_definitions`, `find_note_logs`, `find_collections`,
`find_data_structures`, and `get_technology_type_elements` all route
through shared helpers (`_async_find_request` / `_async_get_name_request`)
that take `as_of_time` as an explicit named parameter or splat `**kwargs`
into the validated request body.

`get_valid_metadata_values` was reclassified, not a pyegeria fix — see
ISSUE-11 (Egeria Server section): the underlying REST endpoint is a plain
GET that never accepted `asOfTime` in the first place.

Originally (surfaced during a "time travel" audit): all of the following
accepted `as_of_time` either not at all, or silently swallowed it because
the method built its request body from explicit named parameters instead
of forwarding kwargs — `find_information_supply_chains`,
`find_governance_definitions`, `find_note_logs`, `find_collections`,
`find_data_structures`, `get_technology_type_elements`.

```python
from pyegeria import EgeriaTech
client = EgeriaTech(view_server="qs-view-server", platform_url="https://localhost:9443",
                     user_id="erinoverview", user_pwd="secret")
client.create_egeria_bearer_token()
r1 = client.find_note_logs("*", graph_query_depth=0)
r2 = client.find_note_logs("*", graph_query_depth=0, as_of_time="2020-01-01T00:00:00Z")
# Fixed: r2 now genuinely reflects historical state instead of being identical to r1.
```

---

### ISSUE-5 (PY-9): local `as_of_time` fixes not shipped to the deployed package

**Status:** fixed / moot, re-verified 2026-07-31 — `get_linked_projects`,
`get_collection_members`, and `get_data_field_by_guid` all accept
`as_of_time` (directly or via `**kwargs`) in current source. This was a
deployment-timing issue, not a code defect — see the "Not a bug" section,
ISSUE-12.

---

### ISSUE-6 (GAP-1): `PyegeriaAPIException` was a catch-all; typed subclasses existed but weren't raised

**Status:** fixed 2026-07-31. `_async_make_request` in
`_base_server_client.py` now branches on `related_http_code` and raises
`PyegeriaNotFoundException` (404) / `PyegeriaUnauthorizedException`
(401/403) instead of the generic `PyegeriaAPIException`. Both exception
classes re-parented from `PyegeriaException` to subclass
`PyegeriaAPIException` (with `__init__` calling `PyegeriaException.__init__`
directly, bypassing `PyegeriaAPIException.__init__`'s `response.json()`
call, since these two are now also raised for bare HTTP error responses
with no JSON body — see ISSUE-7) so all 63 existing
`except PyegeriaAPIException` handlers found across the codebase keep
working unchanged.

**Regression caught and fixed post-merge:** bypassing
`PyegeriaAPIException.__init__` also skipped the line that sets
`self.related_http_code`, which existing code relies on
(`except PyegeriaAPIException as e: if e.related_http_code == 404`). Fixed
by setting it explicitly in both subclasses' `__init__`.

```python
from pyegeria import EgeriaTech
from pyegeria.core._exceptions import PyegeriaNotFoundException
client = EgeriaTech(view_server="qs-view-server", platform_url="https://localhost:9443",
                     user_id="erinoverview", user_pwd="secret")
client.create_egeria_bearer_token()
try:
    client.get_digital_product_by_guid("00000000-0000-0000-0000-000000000000")
except PyegeriaNotFoundException as e:
    print(e.related_http_code)  # 404
```

---

### ISSUE-7 (GAP-6): expired/invalid bearer token had no specific exception and no auto-renew

**Status:** fixed 2026-07-31. Connects to the (now closed) `BACKLOG.md`
issue "Bearer token expires mid-run on long `dr_egeria --process` batches."

Confirmed by direct repro against `qs-view-server`: a bad/expired bearer
token returns a bare HTTP 401 with an **empty response body** — no JSON,
nothing to distinguish "expired" from "wrong credentials" from
"insufficient permission." Since there's no way to detect "expired"
specifically from the response, `_async_make_request` now treats any 401
as a candidate for "the token might be stale": if the client holds stored
credentials, it calls the already-existing
`_async_create_egeria_bearer_token()` once and retries the original
request once before giving up. Default-on, no opt-out flag; at most one
retry ever (internal `_retry_on_auth` guard).

**Bonus bug found and fixed while implementing this:**
`_async_create_egeria_bearer_token()` (both the `BaseServerClient` and
`BasePlatformClient` copies) sent the token-creation POST with
`headers=self.headers` — which still carried the stale Authorization header
being replaced. The `/api/token` endpoint rejects requests with a bad
Authorization header outright (confirmed via direct curl repro), so the
refresh call itself always 401'd, silently defeating the whole mechanism
(both this new auto-retry and the pre-existing manual "call this if your
token expired" use case). Fixed to send a plain `Content-Type`-only header
for that one request.

**Verified live:** corrupted a real client's Authorization header, made a
real API call, confirmed exactly one auto-retry occurred and the call
succeeded transparently with a freshly-obtained token.

---

### ISSUE-8 (GAP-5): `get_collection_members` silently dropped non-Collection members

**Status:** fixed 2026-07-31. `_type` was overloaded in
`_async_get_results_body_request` for two purposes — genuine results
filtering (correct for most of its ~30 callers, e.g. "attached comments are
always type Comment") vs. a pure output-rendering hint (wrong only for
`_async_get_collection_members`'s `/{guid}/members` endpoint, since a
collection's members are never guaranteed to share its own type — e.g. a
`WorkItemList`'s members are `Project`s).

Rather than dropping the default filter for all ~30 callers, added an
explicit `filter_results_by_type: bool = True` parameter (default preserves
existing behavior everywhere) and set it `False` only at the one
confirmed-broken call site. Checked `get_collection_hierarchy` (same file,
same `_type="Collection"` default) separately — its endpoint's own docs say
"return a hierarchy of nested collections," so that filter is legitimate
and was left unchanged. Also added `"body"` to the `"Collection Members"`
FormatSet's `optional_params` in `base_report_formats.py` so report callers
can pass a fully custom body.

Live-verified against the original golden anchor (`WorkItemList` guid
`0affb580-fa81-4d00-9438-b26faf11845d`) — now correctly returns all 5
`Project`-typed members instead of an empty list.

---

### ISSUE-9 (GAP-3): malformed `as_of_time` reached pydantic as a raw `ValidationError`

**Status:** fixed 2026-07-31. Scope turned out bigger than originally
suspected: `as_of_time` is inherited by the whole get/find/search model
family (`GetRequestBody` and its ~4 subclasses), and 51
`.model_validate(...)`/`.validate_python(...)` call sites in
`_server_client.py` shared the same unguarded-validation pattern. Added a
generic `ServerClient._validate_body(validator, body)` static helper
(handles both the `self._xxx_adapter.validate_python` and
`SomeModel.model_validate` call shapes uniformly) that catches
`pydantic.ValidationError` and re-raises as
`PyegeriaInvalidParameterException` naming the offending field(s). Routed
all 49 active call sites through it (2 were already commented out).

```python
from pyegeria import EgeriaTech
client = EgeriaTech(view_server="qs-view-server", platform_url="https://localhost:9443",
                     user_id="erinoverview", user_pwd="secret")
client.create_egeria_bearer_token()
client.find_collections("*", as_of_time="null")
# Now: PyegeriaInvalidParameterException citing the asOfTime field.
# Previously: raw pydantic_core.ValidationError.
```

---

### ISSUE-10 (GAP-2): `user_id`/`server_name` with URL-unsafe characters weren't validated

**Status:** fixed 2026-07-31. `user_id` is embedded raw (no URL-encoding)
into several URL paths (e.g. `pyegeria/omvs/server_operations.py`'s
`.../users/{self.user_id}/status`). Neither `validate_server_name` nor
`validate_user_id` previously checked for characters unsafe in a URL path,
and `validate_user_id` wasn't even called during client construction.

Note: the original report's exact symptom ("a raw `httpx.InvalidURL`
propagates") didn't fully match what was found — the existing bare
`except Exception` in `_async_make_request` already wrapped it as the
generic `PyegeriaUnknownException`, just not a helpful, specific type.

Added a shared `_validate_url_path_safe(value, param_name)` check in
`_validators.py` (rejects ASCII control characters and URL-structural
characters `/ ? # \` plus whitespace), wired into both
`validate_server_name` (already called in both client constructors, so
`server_name` was fixed for free) and `validate_user_id` (now also called
explicitly in both constructors). Now raises
`PyegeriaInvalidParameterException` immediately at construction time,
naming the exact bad character.

```python
from pyegeria.omvs.server_operations import ServerOps
ServerOps("qs-view-server", "https://localhost:9443", user_id="bad\x00user", user_pwd="secret")
# Now: PyegeriaInvalidParameterException at construction, naming the character.
```

---

## Section 2 — Pyegeria: version-pinning / deployment, not code defects

### ISSUE-11 (PY-3): `find_all_solution_blueprints`/`find_all_solution_components` missing in 6.0.12.2

**Status:** n/a — re-verified 2026-07-31, both methods exist in current
source. Was a version-pinning issue at the time (container pinned to
6.0.12.2, methods added in 6.0.12.4), not a code defect.

---

### ISSUE-12 (PY-9): local `as_of_time` fixes not shipped to a deployed container

**Status:** n/a — same root cause class as ISSUE-11. The fix landed in
source; the failure mode was a deployed container `pip install`-ing an
older released version instead of using an editable local checkout. Cut a
release / mount the local checkout as editable for dev+test to avoid this
recurring.

---

### ISSUE-13 (GAP-4): `pyegeria.core.mcp_server` pinned to a stale `mcp` package API

**Status:** n/a — re-verified 2026-07-31. `pyegeria/core/mcp_server.py` at
HEAD already imports `from mcp.server.mcpserver import MCPServer` (the
current API) and imports/runs cleanly with `mcp==2.0.0` installed in this
repo's venv (confirmed:
`python3 -c "from pyegeria.core import mcp_server"` succeeds). The
originally-reported `ModuleNotFoundError` was observed against a
**different, stale installed pyegeria wheel** inside the separate
`quickstart-pyegeria-web` container, not this dev tree — a
deployment/versioning gap in that other project, not a fix needed here.

---

## Section 3 — Egeria server bugs (not fixable in pyegeria)

### ISSUE-14 (PY-4): `update_comment` demands `qualifiedName` even with `mergeUpdate: true`

**Status:** open (Egeria server) — workaround shipped in application code,
not a pyegeria fix. Passing `"mergeUpdate": true` should allow a partial
update (only supplied fields required), but the server still demands
`qualifiedName` regardless.

**Workaround:** fetch the element first via `get_comment_by_guid`, extract
`qualifiedName`, and always include it in the update body regardless of
`mergeUpdate`.

```python
from pyegeria import EgeriaTech
client = EgeriaTech(view_server="qs-view-server", platform_url="https://localhost:9443",
                     user_id="erinoverview", user_pwd="secret")
client.create_egeria_bearer_token()
client.update_comment(comment_guid="<guid>", body={"commentText": "edited text"})
# OMAG-METADATA-400-004 demanding qualifiedName even though mergeUpdate: true is set.
```

---

### ISSUE-15 (PY-6, PY-14): `find_*`/list-style methods are O(n × graph-computation-cost) at default `graph_query_depth`

**Status:** n/a / reclassified as expected Egeria behavior — not a defect.
`graph_query_depth` controls how much relationship graph the server
computes per returned element; defaulting to depth 3 is a deliberate
trade-off (rich results by default). Confirmed on both `find_note_logs`
(PY-6, ~30-70s at default depth on demo data with large logs) and
`find_specification_property` (PY-14, ~50s vs ~0.6-2s at depth 0 for a
1000-element result set) — same root cause, two different methods.

**Workaround, already in use:** always pass `graph_query_depth=0` on any
bulk-listing call unless the caller genuinely needs the graph/mermaid
output — it's accepted via `**kwargs` even on methods that don't list it in
their signature.

**Possible future Egeria-side improvement** (not a bug, a suggestion):
default `graph_query_depth` to `0` for list-style methods (opt-in to the
expensive graph rather than opt-out), or split "list" and "graph" into
separate REST operations.

---

### ISSUE-16 (PY-10): asset detail by-guid appeared to "reject" `asOfTime`

**Status:** n/a — investigated and confirmed not a defect.
`get_asset_graph_by_guid`/`get_asset_by_guid` do honor `asOfTime` correctly;
the original 404/500 reports were caused by test timestamps that predated
the entity's repository version after demo data was reloaded — Egeria
correctly reports "not found at that time." The graph endpoint returning
500 instead of 404 for this case is a minor rough edge, not the originally
reported bug.

---

### ISSUE-17 (PY-13): `SpecificationProperties.get_specification_property_by_type` always returns 400

**Status:** open (Egeria server), re-verified 2026-07-31 (live) — still
reproduces exactly as described. Root cause is server-side: the OpenAPI
schema declares `specificationPropertyType` as a required enum query param
with values like `"SpecificationPropertyType{placeholderProperty}"`, but
every form of that value (plain, enum-wrapped, percent-encoded) still 400s
— the Spring `@RequestParam` enum binding appears to have drifted from the
OpenAPI-declared enum. No pyegeria code change can fix a 400 the server
returns for every input.

**Workaround (shipped in application code):** use
`find_specification_property("*", ...)` (by-search-string) instead, and
filter client-side on `element["properties"]["identifier"]` (camelCase form
of the type name).

```python
from pyegeria import SpecificationProperties
mgr = SpecificationProperties(view_server="qs-view-server", platform_url="https://localhost:9443",
                               user_id="erinoverview", user_pwd="secret")
mgr.create_egeria_bearer_token()
types = mgr.get_specification_property_types()
mgr.get_specification_property_by_type(list(types.keys())[0])
# Still 400s for every input, confirmed 2026-07-31.
```

---

### ISSUE-18 (part of PY-7/8/11): `get_valid_metadata_values` has no `asOfTime` support

**Status:** n/a — reclassified, not a pyegeria fix. Checked the
ground-truth `.http` files: `get-valid-metadata-values/{propertyName}` is a
plain GET endpoint taking only `typeName`/`startFrom`/`pageSize` query
params; `asOfTime` never appears there, only on POST-body search/filter
endpoints elsewhere. The Egeria server doesn't expose historical-query
capability on this endpoint at all — adding an `as_of_time` param
client-side would be dead code (silently ignored server-side). Would need
an Egeria REST API change to add `asOfTime` support to this endpoint first.

---

## Section 4 — Docs / class-organization sharp edges (not bugs)

### ISSUE-19 (PY-12): `ReferenceDataManager` has no specification-property or valid-metadata-value methods

**Status:** open (docs/organization), re-verified 2026-07-31 — still true.
`ReferenceDataManager` inherits only from `ServerClient` (it's for
*business* reference data — country codes, currency codes, etc.), not from
`ValidMetadataManager`. `get_valid_metadata_values` happens to work on it
because that method lives on the shared `ServerClient` base, not on
`ValidMetadataManager` — easy to misjudge the class boundary from that
alone. The specification-property methods
(`get_specification_property_types`, `get_specification_property_by_type`,
`get_specification_property_by_name`, `get_specification_property_by_guid`,
`find_specification_property`) only exist on
**`pyegeria.SpecificationProperties`** (also on `ValidMetadataManager`
subclasses `ValidMetadataLists`, `ValidTypeLists`).

**Fix:** use `pyegeria.SpecificationProperties(...)` for these calls
instead of `ReferenceDataManager`.

**Suggested improvement:** either a class-level docstring note on
`ReferenceDataManager` clarifying the boundary, or a single unified
decision tree for "which OMVS client class do I need" across
`ReferenceDataManager` / `SpecificationProperties` / `ValidMetadataLists` /
`ValidTypeLists` / `MetadataExpert`, since several overlap in purpose.

---

## Quick reference: which OMVS client class for which purpose

| Need | Class | Notes |
|---|---|---|
| Business reference data (country/currency codes) | `ReferenceDataManager` | Does **not** cover specification properties (ISSUE-19, docs-only) |
| Valid metadata values for a property name | `ReferenceDataManager` or `MetadataExpert` | `get_valid_metadata_values` lives on shared `ServerClient` base; no `as_of_time` support — Egeria endpoint doesn't expose it (ISSUE-18) |
| Specification properties (placeholders, guards, action targets, etc.) | `SpecificationProperties` | Avoid `get_specification_property_by_type` (ISSUE-17, Egeria server bug); use `find_specification_property` with `graph_query_depth=0` (ISSUE-15) |
| `DataGrain` / `DataClass` listing | `find_data_value_specifications` / `get_data_value_specifications_by_name("*")` | Both fixed (ISSUE-1, ISSUE-2) |
| `DataSpec` (Collection subtype) | `CollectionManager.find_collections(metadata_element_type="DataSpec")` | |
| `DataStructure` / `DataField` | `DataDesigner.find_data_structures` / `find_data_fields` | |
| Solution blueprints/components (any pyegeria version) | `SolutionArchitect.find_solution_blueprints/components(search_string="*")` | Avoid `find_all_*` variants on old versions (ISSUE-11) |
| Note logs (list) | `find_note_logs("*", graph_query_depth=0)` | ISSUE-15 |
| Note logs (entries) | `get_notes_for_note_log(guid, page_size=100)` | ISSUE-3 — never pass `metadata_element_type_name="NoteLog"` |
| Collection members | `get_collection_members(collection_guid)` | ISSUE-8 — now returns members of any type, not just the collection's own type |

---

## Section 5 — New issues found after this file's initial cleanup, open

### ISSUE-20: `Analytic Parameters`/`Report Parameters` stringify every value, breaking list-valued analytic function params (e.g. `type_map`)

**Status:** fixed 2026-08-01 (Pyegeria — `md_processing/v2/report.py`),
found 2026-07-31 while building an Analytic Function demo (Projects/Terms
comparison) for the Local Dashboards sample.

**What:** `parse_key_value()` (`md_processing/v2/utils.py`) parses every
Dictionary-style attribute value (simple/list/table form) as a plain string
— there's no JSON/type coercion. `_report_additional_properties()`
(`md_processing/v2/report.py:132-135`) then does
`{str(k): str(v) for k, v in analytic_params.items() if v is not None}`
before `json.dumps(...)` into the stored `analyticParams` key. For a scalar
param (`window: 90d`, `type_name: Project`) this round-trips fine — the
string IS the value. But for a param whose real type is a list (e.g.
`counts_by_type`/`growth_series`'s `type_map: list[tuple[str, str]]`), the
markdown author's only way to express it is typing the literal text
`type_map: [["Projects", "Project"], ["Terms", "GlossaryTerm"]]` on one
line — `parse_key_value` stores that whole thing as ONE string value, which
then gets `str()`'d (no-op, already a string) and JSON-encoded as a STRING,
not a real JSON array. At read time (`local_dashboards_handler.py`'s
`json.loads(raw_analytic_params)`, or any other consumer), `type_map` comes
back as a Python `str`, not a `list`. When `format_set_executor.py`'s
`_run_analytic_function` forwards it as a kwarg,
`counts_by_type(type_map="[[\"Projects\", \"Project\"], ...]")` tries to
iterate the string character-by-character and unpack each character into
`(label, type_name)` → `ValueError: not enough values to unpack (expected
2, got 1)`.

**Where seen:** live repro — created a throwaway `Report` via `Create
Report` with `Report Spec: Analytic Demo - Assets by Type Breakdown` and
`Analytic Parameters: type_map: [["Projects", "Project"], ["Terms",
"GlossaryTerm"]]`. `--validate`/`--process` both succeeded (no attribute-
level error — the value parses as *a* string just fine). Fetching the
created element's `additionalProperties.analyticParams` showed
`{"type_map": "[[\"Projects\", \"Project\"], [\"Terms\", \"GlossaryTerm\"]]"}`
— the outer JSON is valid, but `type_map`'s VALUE is itself a string, not a
nested array. Calling `POST /api/report-specs/execute` with that exact
params dict reproduced the crash: `"not enough values to unpack (expected
2, got 1)"`. Cleaned up the throwaway Report afterward (`AssetMaker.delete_asset`).

**Impact:** any analytic function whose parameter type is a list/dict
(`counts_by_type`'s `type_map`, `growth_series`'s custom `type_map`,
`metric_trend`'s `metric_params`) cannot be set via Dr.Egeria's `Analytic
Parameters` (or `Report Parameters`, same code path) today — only flat
scalar params (`type_name`, `window`, `points`, `collection_guid`, etc.)
work. Worked around in the Local Dashboards sample/tutorial by sticking to
`count_elements(type_name=...)` (scalar) instead of `counts_by_type`
(list) for the Projects-vs-Terms comparison.

**Fix:** added `_coerce_analytic_value()` in `md_processing/v2/report.py` —
attempts `json.loads(v)` per-value before it's packed into the
`analyticParams` JSON blob, falling back to the original string if it isn't
valid JSON. Applied in `_report_additional_properties()`'s `Analytic
Parameters` handling (`Create Report`) and, since `View Report`
(`md_processing/v2/view.py`) turned out to have a second, related gap —
`Analytic Parameters` wasn't handled there **at all**, falling through to
the generic per-attribute branch and being treated as one param literally
named `analytic_parameters` holding the whole dict — added a matching
`Analytic Parameters` branch there too (merges flat into `params`, coerced,
mirroring the existing `Report Parameters` branch immediately above it).

Deliberately scoped to `analyticParams` only, not `_REPORT_PARAM_ATTRS` or
`Report Parameters` — those remain `Map<String,String>` at the Egeria
element level (a real constraint, not a bug) and must stay strings;
`analyticParams` is a single JSON-encoded blob consumed purely by Python's
own `**kwargs` at execution time, where real types matter.

**Verified live** (not just `--validate`): created a throwaway `Report`
with the exact original repro (`type_map: [["Projects", "Project"],
["Terms", "GlossaryTerm"]]`), confirmed `additionalProperties.analyticParams`
now stores `type_map` as a real nested JSON array, then called
`POST /api/report-specs/execute` with it — `counts_by_type` returned the
correct per-type breakdown (`Projects: 29, Terms: 591`) instead of
crashing. Also caught and fixed a second latent bug the same coercion
exposes: an `int`-typed scalar param (`points: 3`) previously round-tripped
as the string `"3"` too, which broke `growth_series` outright
(`TypeError: unsupported operand type(s) for -: 'str' and 'int'`) — now
correctly coerces to a real `int`. Ran
`tests/micro-tests/test_overview_metrics.py`,
`test_gen_report_specs.py`, `test_base_report_formats_mermaid.py` (34
tests) — all pass, no regressions. Cleaned up the throwaway Report
afterward. Not yet released to PyPI — still pinned at `6.0.17.8` in
egeria-workspaces-fs's `requirements.txt`; needs a version bump when the
next release goes out.

---

*(Add new entries at the end of the appropriate section as they're found.
Keep the format: status, layer classification, what, where seen, candidate
fix — so entries are self-contained enough to hand to whoever eventually
reviews/fixes them.)*
