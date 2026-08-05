# Pyegeria / Egeria Issue Tracker

Merged from the former `PYEGERIA_ISSUES.md` (Egeria Explorer usage bugs,
started 2026-06) and `PYEGERIA_GAPS.md` (exception/validation infrastructure
gaps, started 2026-07-31) into one file, with every entry re-verified against
the current codebase as of 2026-07-31 rather than trusting old status claims.
Reorganized 2026-08-04 so **open issues are at the top** and fixed/not-a-bug
entries live in the Appendix — read top-to-bottom for "what's still
outstanding," jump to the Appendix only when you need the history of
something already resolved.

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

**Numbering:** unified as `ISSUE-#`, sequential in the order each was found
— stable across the 2026-08-04 reorg (an issue keeps its number regardless
of which section it now sits in), so old references stay valid. Old
references carried forward in parens for traceability (`PY-#` from the
original issues doc, `GAP-#` from the gaps doc). Note: the original issues
doc's header claimed compact status tracking also lived in `BACKLOG.md`
under a "pyegeria Upstream Bugs" section using the same `PY-#` numbering —
checked git history, that section never existed in `BACKLOG.md`. That
cross-reference was already stale; not carried forward here.

Unless noted otherwise, repro commands assume a running Egeria view server
reachable at `https://localhost:9443`, view server name `qs-view-server`,
user `erinoverview` / `secret` (adjust to your env) — updated from the
original `peterprofile` since several of the old repro snippets used a
class (`NoteLogManager`, `CommentManager`) that doesn't exist in the current
package; replaced with `EgeriaTech`, which does. **Caveat added 2026-08-04**
(see ISSUE-29): different demo users can see genuinely different data for
the same query, thanks to governance zone visibility — don't assume a
result mismatch is a pyegeria bug before checking whether the same user was
used on both sides of the comparison.

---

# Open Issues

## Pyegeria — fixable here

### ISSUE-21: `ClassificationExplorer.get_scoped_elements`/`get_scopes` sync wrappers pass `output_format` into the wrong positional slot

**Status:** open, found 2026-08-03 while live-verifying the new Curation
family's `Link Element To Scope` command (`md_processing/v2/curation.py`).

**Layer:** Pyegeria (`pyegeria/omvs/classification_explorer.py`).

**What:** `get_scoped_elements(scope_guid, body=None, output_format="JSON",
report_spec=None, start_from=0, page_size=0, **kwargs)` calls
`self._async_get_scoped_elements(scope_guid, body, output_format,
report_spec, start_from, page_size, **kwargs)` positionally, but
`_async_get_scoped_elements`'s own parameter order doesn't match — the
`output_format` string ends up landing in the `page_size` slot of the
`ResultsRequestBody` pydantic model, which then rejects it (`page_size`
must be an int). Same bug shape in `get_scopes`. Repro:

```python
from pyegeria import EgeriaTech
client = EgeriaTech("qs-view-server", "https://localhost:9443", user_id="erinoverview")
client.create_egeria_bearer_token("erinoverview", "secret")
client.classification_manager.get_scoped_elements("<any-guid>")
# pydantic_core._pydantic_core.ValidationError: 1 validation error for ResultsRequestBody
# page_size: Input should be a valid integer, unable to parse string as an integer [input_value='JSON', ...]
```

**Impact:** cannot read back ScopedBy relationships through these two
convenience methods at all (any call fails, regardless of arguments) —
had to fall back to `add_scope_to_element`'s own SUCCESS status as
verification evidence for `Link Element To Scope`, rather than an
independent readback, since this repo has no other exposed way to list
ScopedBy relationships. Doesn't block the `add_scope_to_element`/
`clear_scope_from_element` write path used by Curation and Actor
Manager's `Link Perspective to Question` — only the read-back path.

**Candidate fix:** align `_async_get_scoped_elements`/`_async_get_scopes`'s
parameter order with what their sync wrappers pass, or switch the wrappers
to keyword-only calls — not attempted here, out of scope for the Curation
family work in progress. **Update 2026-08-04:** confirmed this exact bug
shape is not isolated — see ISSUE-25 (`find_root_elements` had the
identical problem, fixed) and ISSUE-27 (~50 more unaudited call sites of
the same shape).

---

### ISSUE-23: `max_mermaid_node_count` defaults to 5 across every shared find/get request helper, silently truncating server-generated mermaid graphs

**Status:** open at the pyegeria-default level (the user is raising the
shared default from 5 to 10 separately); worked around explicitly in
egeria-workspaces-fs across all detail-view call sites that render a
mermaid diagram — `isc_handler.py`, `mermaid_handler.py`,
`solution_architect_handler.py`, `tech_catalog_handler.py`,
`digital_products_handler.py`, `action_center_handler.py`,
`actor_handler.py`, `community_handler.py`, `context_events_handler.py`,
`data_design_handler.py`, `external_links_handler.py`,
`glossary_handler.py`, `governance_definitions_handler.py`,
`lineage_handler.py` (asset graph only, see ISSUE-24 for the lineage
graph endpoint), `location_handler.py`, `perspectives_handler.py`,
`reference_data_handler.py` — found 2026-08-04 investigating a report
that Egeria Explorer's Information Supply Chain view wasn't rendering the
full chain. `audit_handler.py`'s two `get_element_by_guid` calls are
deliberately left at `graphQueryDepth: 0` (a lightweight side-panel
lookup with no relationship traversal, so no mermaid graph is generated
there anyway) and `notelog_handler.py` doesn't render mermaid fields —
both confirmed not affected, not just skipped.

**Two distinct fix shapes were needed depending on the call site**,
learned the hard way after an initial fix silently didn't work:
- If the portal handler passes **no** `body=` argument (stays `None`),
  a `max_mermaid_node_count=250` kwarg on the outer call correctly
  threads through — every `_by_guid`/`find_*` wrapper method in pyegeria
  follows the same `params.update(kwargs); ...; **params` idiom that
  forwards it into the shared helper's own `max_mermaid_node_count`
  parameter.
- If the portal handler already builds an explicit `body={"class":
  "GetRequestBody", ...}` dict (common wherever `as_of_time` needs to be
  conditionally added), `_async_get_guid_request`/`_async_find_request`
  validate that body **as-is** and silently ignore the sibling
  `max_mermaid_node_count`/`graph_query_depth` kwargs entirely — the
  field must be embedded directly in the body dict
  (`"maxMermaidNodeCount": 250`) instead.
- A third shape: `get_solution_blueprint_by_guid`/
  `get_solution_component_by_guid` hit dedicated `.../retrieve` REST
  endpoints whose own `graph_query_depth` **parameter is dead** — never
  reaches the request at all, body or no body. Passing an explicit
  `AnyTimeRequestBody` with `graphQueryDepth`/`maxMermaidNodeCount` set
  is the only way to raise it (verified live: 74 → 187 mermaid lines).
  **Update 2026-08-04:** `get_info_supply_chain_by_guid`/
  `get_solution_role_by_guid` have the identical shape — see ISSUE-26.

**Layer:** Pyegeria (`pyegeria/core/_server_client.py`).

**What:** `_async_find_request`, `_async_get_name_request`, and
`_async_get_guid_request` — the three shared helpers behind essentially
every `find_*`/`get_*_by_guid` OMVS method — all declare
`max_mermaid_node_count: int = 5`, which gets sent to the server as
`maxMermaidNodeCount` in the request body. The server caps the generated
mermaid flowchart at that many nodes. 5 is far too small for any real
graph with more than a handful of related elements — a value seemingly
picked as a lightweight default for broad/unbounded listings, not for a
"show me everything about one element" detail view, but it applies
identically to both.

**Where seen:** live repro against a Coco Pharmaceuticals demo server —
`SolutionArchitect.find_information_supply_chains("Open Metadata Highway
Information Supply Chain")`'s `mermaidGraph` field was 165 lines at the
default `max_mermaid_node_count=5`, vs. 619 lines at `250` (graph actually
complete at that point — verified by also trying `50`/`100`, no further
growth past ~200). `graph_query_depth` (default 3), by contrast, made no
measurable difference for any information supply chain tested (1 through
10) — the node-count cap, not query depth, is the actual bottleneck for
mermaid graph completeness. Every OMVS wrapper method that calls one of
these three shared helpers (`find_information_supply_chains`,
`get_element_by_guid`, `find_solution_blueprints`,
`find_solution_components`, `get_solution_component_by_guid`, etc.)
inherits the same 5-node cap unless the caller explicitly overrides it —
confirmed via grep that essentially none of egeria-workspaces-fs's
`PyegeriaWebHandler` handlers do (`isc_handler.py`, now fixed;
`solution_architect_handler.py`, `tech_catalog_handler.py`,
`mermaid_handler.py`, `digital_products_handler.py`, `audit_handler.py`
all still rely on the pyegeria default).

**Candidate fix (still open):** raise the shared `max_mermaid_node_count`
default itself (planned separately by the repo owner, 5 → 10) — the
per-handler overrides above are generous enough (250) that they don't
depend on that change, but the two "dead parameter" methods
(`get_solution_blueprint_by_guid`/`get_solution_component_by_guid`) would
benefit from an actual fix to thread `graph_query_depth`/
`max_mermaid_node_count` into their request the same way every other
`_by_guid` method does, rather than requiring callers to know the
`AnyTimeRequestBody` workaround.

---

### ISSUE-24: `AssetCatalog._async_get_asset_lineage_graph_by_guid` hardcodes `queryGraphDepth: 5` with no override parameter at all

**Status:** open, found 2026-08-04 alongside ISSUE-23 while auditing
`egeria-workspaces-fs/.../lineage_handler.py`'s mermaid-graph call sites.

**Layer:** Pyegeria (`pyegeria/omvs/asset_catalog.py`).

**What:** unlike every other `_by_guid` method in this codebase,
`_async_get_asset_lineage_graph_by_guid` builds its `AssetLineageGraphRequestBody`
manually with `"queryGraphDepth": 5` hardcoded, and does not spread
`**kwargs` into that body at all — the method's own `**kwargs` parameter
exists but is never used. There is currently no way to override this from
a caller, unlike `get_asset_graph_by_guid` (a different, sibling method on
the same class going through `_async_get_results_body_request`, which
**does** correctly forward a `max_mermaid_node_count` kwarg — confirmed
and fixed in `lineage_handler.py`'s `get_asset_graph` route this session).

**Where seen:** `egeria-workspaces-fs/compose-configs/*/PyegeriaWebHandler/lineage_handler.py`'s
`get_asset_lineage_graph` route (`/api/lineage/asset/{guid}/lineage-graph`)
— serves `mermaidGraph`/`fullLineageMermaidGraph`/`edgeMermaidGraph` for
the lineage explorer's full end-to-end diagram, exactly the kind of view
most likely to need a depth greater than 5 for a long pipeline. Left
unmodified in the portal since there's no parameter to pass.

**Candidate fix:** add `graph_query_depth`/`max_mermaid_node_count`
parameters to `_async_get_asset_lineage_graph_by_guid`/
`get_asset_lineage_graph_by_guid`, threading them into
`queryGraphDepth`/a new `maxMermaidNodeCount` body field (need to confirm
the server actually honors a `maxMermaidNodeCount` field on
`AssetLineageGraphRequestBody` specifically — this body class differs
from the more common `GetRequestBody`/`ResultsRequestBody` shapes seen
elsewhere in this file).

---

### ISSUE-26: `get_info_supply_chain_by_guid`/`get_solution_role_by_guid` accept `graph_query_depth`/`max_mermaid_node_count` but never use them — same "dead parameter" shape as ISSUE-23's third case

**Status:** open, found 2026-08-04 while chasing ISSUE-25's repro further
(checking whether the by-GUID retrieve returns a richer graph than
by-search-string).

**Layer:** Pyegeria (`pyegeria/omvs/solution_architect.py`).

**What:** `_async_get_info_supply_chain_by_guid` and
`_async_get_solution_role_by_guid` declare `graph_query_depth` and accept
`**kwargs`, but when `body` is `None` they send **no body at all**
(`self._async_make_request("POST", url, **kwargs)` — note there's no body
positional argument in that call). If a caller tries to pass
`graph_query_depth`/`max_mermaid_node_count` explicitly, they land in
`**kwargs` and get forwarded straight into `_async_make_request()`, which
doesn't accept them — a `TypeError` on every attempt, confirmed live:

```python
from pyegeria import SolutionArchitect
sa = SolutionArchitect("qs-view-server", "https://localhost:9443", user_id="erinoverview")
sa.create_egeria_bearer_token("erinoverview", "secret")
sa.get_info_supply_chain_by_guid("<any-guid>", graph_query_depth=10, max_mermaid_node_count=10)
# TypeError: BaseServerClient._async_make_request() got an unexpected keyword argument 'max_mermaid_node_count'
```

Exact same shape already documented in ISSUE-23's "third shape" for
`get_solution_blueprint_by_guid`/`get_solution_component_by_guid` — this
confirms two more sibling methods have it too.

**Impact:** cannot control the mermaid graph depth/node count on a by-GUID
retrieve for an information supply chain or solution role at all, short of
passing a fully custom `body` dict (the `AnyTimeRequestBody` workaround
ISSUE-23 already validated live: `{"class": "AnyTimeRequestBody",
"graphQueryDepth": ..., "maxMermaidNodeCount": ...}`).

**Candidate fix:** when `body is None`, build a body dict from the
declared parameters (mirroring how every other `_by_guid` method in this
file does it) instead of sending no body / dumping stray kwargs into
`_async_make_request`. Same fix needed at
`get_solution_blueprint_by_guid`/`get_solution_component_by_guid` per
ISSUE-23 — worth doing all four together.

---

### ISSUE-27: ~50 more sync methods delegate to their async counterpart with an all-positional argument list — unaudited for the same scrambling bug as ISSUE-21/25

**Status:** open, found 2026-08-04 as a byproduct of the ISSUE-25 sentinel
audit.

**Layer:** Pyegeria (`classification_explorer.py`, `runtime_manager.py`,
`project_manager.py`, `automated_curation.py`, `glossary_manager.py`).

**What:** grep for `self\._async_\w+\(\s*\n(?:\s+\w+,?\s*\n)+\s*\)` (a
multi-line, all-positional call with no `=`, `*`, or `**` on any line) in
`pyegeria/omvs/*.py` turns up ~50 more call sites, mostly write/action
methods (set/clear classification, add/remove relationship) that don't
carry `graph_query_depth` — so ISSUE-25's sentinel-injection method (which
specifically hunted for that one parameter) couldn't confirm or rule them
out. ISSUE-21 and ISSUE-25's `find_root_elements` finding both prove this
call shape is a real, recurring risk in this codebase whenever a
delegate's parameter order doesn't exactly match the caller's.

**Candidate fix:** for each of the ~50 call sites, diff the caller's
positional argument order against the target method's actual parameter
order (the same manual check done for `find_root_elements` in ISSUE-25)
and convert to keyword arguments wherever they've drifted. Not attempted
here — flagged for a dedicated follow-up pass.

---

### ISSUE-28: `get_specification_property_by_guid` raises a bare `NameError: name 'validate_guid' is not defined` — cannot be called at all

**Status:** open, found 2026-08-04 as a byproduct of the ISSUE-25 sentinel
audit.

**Layer:** Pyegeria — affects `SpecificationProperties`,
`ValidMetadataManager`, `ValidMetadataLists`, `ValidTypeLists` (all share
the same `get_specification_property_by_guid` implementation via
inheritance).

**What:** a missing import — `validate_guid` is referenced but never
imported in whichever module defines this method. Every call fails
immediately with `NameError`, regardless of arguments:

```python
from pyegeria import SpecificationProperties
mgr = SpecificationProperties(view_server="qs-view-server", platform_url="https://localhost:9443", user_id="erinoverview")
mgr.create_egeria_bearer_token("erinoverview", "secret")
mgr.get_specification_property_by_guid("<any-guid>")
# NameError: name 'validate_guid' is not defined
```

**Candidate fix:** add the missing `from pyegeria.core._validators import
validate_guid` (or wherever the shared helper lives) import. Not attempted
here — a one-line fix, but outside the scope of the ISSUE-25 pass that
found it.

---

### ISSUE-31: `MetadataExpert.delete_metadata_element` crashes with `AttributeError: 'NoneType' object has no attribute 'model_dump'` when called with no explicit body

**Status:** open, found 2026-08-04/05 while cleaning up throwaway test
elements created during the ISSUE-32 (`Note` type) live verification.

**Layer:** Pyegeria (`pyegeria/core/_server_client.py`).

**What:** `_async_open_metadata_delete_body_request(url, body=None)` calls
`self.validate_open_metadata_delete_request(body)` and immediately calls
`.model_dump(...)` on the result — but `validate_open_metadata_delete_request`
returns `None` (not a default `OpenMetadataDeleteRequestBody()` instance)
when `body` is `None`, so the very next line always crashes for the common
"just delete it, no special options" case:

```python
from pyegeria import EgeriaTech
client = EgeriaTech("qs-view-server", "https://localhost:9443", user_id="erinoverview")
client.create_egeria_bearer_token("erinoverview", "secret")
client.metadata_expert.delete_metadata_element("<any-guid>")
# AttributeError: 'NoneType' object has no attribute 'model_dump'
```

**Workaround (used during this investigation):** always pass an explicit
`body={"class": "OpenMetadataDeleteRequestBody"}` — works correctly once a
non-`None` body is supplied.

**Candidate fix:** `validate_open_metadata_delete_request` should construct
and return a default `OpenMetadataDeleteRequestBody()` when `body is None`,
matching the pattern every other `validate_*_request` helper in this file
uses (they all handle the "no body given" case by building sensible
defaults, not returning `None`). Not attempted here — found in passing,
outside the scope of the `Note` type work that surfaced it.

---

### ISSUE-30: `updateNote` REST operation (`POST .../feedback-manager/notes/{noteGUID}`) returns 404 on a live server, despite matching the documented `.http` ground truth exactly

**Status:** open (Egeria Server), found 2026-08-05 while live-verifying the
ISSUE-32 `Note` type fix end-to-end (create worked; update did not).

**Layer:** Egeria Server — not fixable in pyegeria. `_async_update_note`'s
URL (`{command_root}feedback-manager/notes/{note_guid}`) was double-checked
against `Egeria-api-feedback-manager.http`'s `@name updateNote` worked
example and matches it exactly, method and body shape included; this isn't
a pyegeria URL-construction bug.

**What:** confirmed via both pyegeria and a raw `curl` (bypassing pyegeria
entirely) against a freshly-created, real `Note` element on `qs-view-server`
— both get a bare HTTP 404 with no Egeria FFDC error body, just a generic
Spring "Not Found" response, meaning the operation doesn't appear to be
routed/registered on this server at all:

```bash
curl -sk -X POST "https://localhost:9443/servers/qs-view-server/api/open-metadata/feedback-manager/notes/<real-note-guid>" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"class":"UpdateElementRequestBody","mergeUpdate":true,"properties":{"class":"NoteProperties","typeName":"Note","displayName":"x"}}'
# {"timestamp":"...","status":404,"error":"Not Found","path":"/servers/qs-view-server/api/open-metadata/feedback-manager/notes/<guid>"}
```

**Impact:** `update_note`/`_async_update_note` cannot be verified working
end-to-end on this server today — create + fetch both work correctly
(confirmed live, see ISSUE-32), but update is blocked. Not related to the
`Note` type change itself (same 404 shape would occur regardless of
`typeName`) — looks like a genuine gap in this endpoint's registration on
the current server build.

**Candidate fix:** none client-side. Worth confirming against a different/
newer Egeria server build whether this is a temporary gap in the specific
redeploy used for this session, or a real, currently-unreleased endpoint.

---

## Dr.Egeria / compact-spec design gap

### ISSUE-22: `Ownership`/`Impact`/`Confidence`/`Confidentiality`/`Criticality` classification `status` field expects an int enum, not the free-text value the Dr.Egeria "Status" attribute style implies

**Status:** open, found 2026-08-03 during a live smoke test of `Classify
Impact` (Curation family).

**Layer:** Not strictly a pyegeria bug — a Dr.Egeria compact-spec design
gap (`md_processing/data/compact_commands/commands_curation_compact.json`,
`Status` attribute, style `Simple`) combined with `curation.py`'s field
mapping (`_GOVERNANCE_SHARED_FIELDS = {"Status": "status", ...}`).

**What:** `ImpactProperties`/etc.'s real `status` field is an integer
`GovernanceClassificationStatus` enum ordinal (per
`Egeria-api-classification-explorer.http`'s worked example: `"status" : 0`),
not a free-text string. Passing `"ACTIVE"` (a plausible-looking value given
the attribute's `Simple` style) doesn't error — it's silently dropped by
the server, and the classification's `statusIdentifier` (the field's
readback name) stays at its default `0`.

**Where seen:** live repro — `Classify Impact` with `Status: ACTIVE`,
`Level Identifier: 2`, `Steward`/`Source`/`Description` set. Fetching the
classified element back showed `severityLevel: "2"`, `steward`, `source`,
`notes` all correct, but `statusIdentifier: "0"` regardless of the `Status`
value sent — confirms `status` never took effect as text.

**Candidate fix:** change the `Status` attribute's style to `Valid Value`/
`Enum` with the real `GovernanceClassificationStatus` ordinal labels (needs
confirming the exact enum from the Egeria type system rather than guessing
further), authored in Tinderbox per the usual compact-spec workflow — not
attempted here, since it's a spec authoring change, not a Curation
processor-wiring bug. Doesn't block Impact/Confidence/etc. classification
overall — `severityLevel`, `steward`, `source`, `notes` all confirmed
working correctly.

---

## Egeria Server — not fixable in pyegeria

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

## Docs / class-organization sharp edges

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

# Quick reference: which OMVS client class for which purpose

| Need | Class | Notes |
|---|---|---|
| Business reference data (country/currency codes) | `ReferenceDataManager` | Does **not** cover specification properties (ISSUE-19, docs-only) |
| Valid metadata values for a property name | `ReferenceDataManager` or `MetadataExpert` | `get_valid_metadata_values` lives on shared `ServerClient` base; no `as_of_time` support — Egeria endpoint doesn't expose it (ISSUE-18) |
| Specification properties (placeholders, guards, action targets, etc.) | `SpecificationProperties` | Avoid `get_specification_property_by_type` (ISSUE-17, Egeria server bug); use `find_specification_property` with `graph_query_depth=0` (ISSUE-15); `get_specification_property_by_guid` currently broken outright (ISSUE-28) |
| `DataGrain` / `DataClass` listing | `find_data_value_specifications` / `get_data_value_specifications_by_name("*")` | Both fixed (ISSUE-1, ISSUE-2) |
| `DataSpec` (Collection subtype) | `CollectionManager.find_collections(metadata_element_type="DataSpec")` | |
| `DataStructure` / `DataField` | `DataDesigner.find_data_structures` / `find_data_fields` | |
| Solution blueprints/components (any pyegeria version) | `SolutionArchitect.find_solution_blueprints/components(search_string="*")` | Avoid `find_all_*` variants on old versions (ISSUE-11) |
| Note logs (list) | `find_note_logs("*", graph_query_depth=0)` | ISSUE-15 |
| Note logs (entries) | `get_notes_for_note_log(guid, page_size=100)` | ISSUE-3 — never pass `metadata_element_type_name="NoteLog"` |
| Collection members | `get_collection_members(collection_guid)` | ISSUE-8 — now returns members of any type, not just the collection's own type |
| Comparing results across two runs/environments that don't match | — | Check whether the same user's credentials were used in both — governance zone visibility can legitimately change results per-user (ISSUE-29) before assuming a pyegeria bug |

---

# Appendix: Closed / Not-a-bug entries

## Fixed (Pyegeria)

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

### ISSUE-25: `graph_query_depth` silently dropped (or scrambled) by ~20 sync/async OMVS wrapper methods — the actual root cause behind ISSUE-23/24's symptoms

**Status:** fixed 2026-08-04 (Pyegeria — 8 files). Found while investigating a live
repro: `SolutionArchitect.find_information_supply_chains("Onboarding")`
returned a 3-node mermaid graph vs. 5 nodes for the equivalent raw REST call,
and neither `graph_query_depth` nor `max_mermaid_node_count` appeared to
change the result no matter what the caller passed.

**Root cause:** two distinct bug shapes, found via a runtime audit (not just
reading code) — every public sync method with a `graph_query_depth`
parameter across all `pyegeria/omvs/*.py` classes was instantiated, called
with a sentinel value, and `ServerClient._async_make_request` was
monkeypatched to capture the actual outgoing JSON body, to see whether the
sentinel ever reached the wire:

1. **Silent drop.** A sync wrapper (or an async method one layer further in)
   declares `graph_query_depth` as a parameter but never forwards it into the
   call it delegates to — the delegate's own default (always `3`) is what
   actually reaches the server, regardless of what the caller passed. This
   was the exact mechanism behind the reported repro:
   `SolutionArchitect.find_information_supply_chains`'s sync wrapper listed
   `graph_query_depth` in its signature but omitted it from the call to
   `_async_find_information_supply_chains` entirely. (`max_mermaid_node_count`
   was *not* affected the same way — it only ever reaches these methods via
   `**kwargs`, which does forward correctly — but since
   `_async_find_request`'s default of 10 already exceeds the graph size in
   the repro, raising it further couldn't add the missing nodes either;
   the 3-vs-5-node gap was purely a depth problem, and depth was the one
   parameter that had been silently stuck at 3 the whole time.)

2. **Positional scramble (same shape as ISSUE-21).** A sync wrapper calls its
   async counterpart, or a `find_all_*` convenience wrapper calls its
   `find_*` counterpart, using an all-positional argument list that doesn't
   match the target's actual parameter order. Beyond just losing
   `graph_query_depth`, this shifts *every subsequent argument* into the
   wrong slot. Two of these were bad enough that the method could never be
   called successfully at all —
   `SolutionArchitect.find_all_solution_blueprints`/`find_all_solution_components`
   raised `TypeError: ... takes from 1 to 11 positional arguments but 12
   were given` on every call (confirmed live before the fix), and
   `find_all_information_supply_chains` similarly overflowed
   (`... but 27 were given`). `ClassificationExplorer.find_root_elements`
   was more insidious — it didn't crash, but silently sent `output_format`
   (a string) into the `graphQueryDepth` body field, `report_spec` into
   `output_format`, `timeout` into `report_spec`, and `body` into `timeout`,
   dropping the caller's actual `body` entirely; found only because pydantic
   validation happened to reject the string-into-int case
   (`graphQueryDepth: Input should be a valid integer ... input_value='JSON'`)
   — a positional scramble that validation doesn't happen to catch would
   fail silently the same way ISSUE-21 did. **This general shape isn't fully
   swept yet — see ISSUE-27 for ~50 more unaudited call sites.**

**Fixed (verified via the same sentinel-injection harness, now 0 false
negatives across all ~734 methods with a `graph_query_depth` parameter):**
- `solution_architect.py`: `find_information_supply_chains` (drop),
  `find_all_information_supply_chains` (scramble/crash),
  `find_all_solution_blueprints` (scramble/crash),
  `find_all_solution_components` (scramble/crash),
  `find_all_solution_roles` (drop)
- `classification_explorer.py`: `get_element_by_guid` (drop),
  `find_root_elements` (scramble)
- `runtime_manager.py`: `get_platforms_by_name`, `get_platform_by_guid`,
  `get_server_by_guid`, `get_servers_by_name` (all: async-layer drop, one
  level past the sync wrapper, which already forwarded correctly)
- `product_manager.py`: `get_digital_products_by_name`,
  `get_digital_product_catalogs_by_name` (async-layer drop)
- `collection_manager.py`: `find_digital_products` — also fixes
  `DigitalBusiness.find_digital_products` and
  `GlossaryManager.find_digital_products`, both inherited from here
  (dead parameter: `graph_query_depth`, `metadata_element_type_name`,
  `metadata_element_subtypes`, `include_only_relationships`,
  `skip_relationships`, and `**kwargs` were all accepted but never placed
  into the hand-built `DeploymentStatusSearchString` body dict at all)
- `data_discovery.py`: `get_annotations_by_name`, `get_annotation_by_guid`
  (drop)
- `asset_catalog.py`: `get_assets_by_metadata_collection_id` (dead
  parameter — `graph_query_depth`, `include_only_relationships`,
  `skip_relationships` accepted but never placed into the hand-built body;
  **unverified against a live server** that the endpoint's body actually
  accepts `graphQueryDepth`/`includeOnlyRelationships`/`skipRelationships`
  under those exact names — the `.http` ground-truth file has no worked
  example with a body for this endpoint, so the names were inferred from
  the same fields' spelling everywhere else in this codebase, not confirmed
  live)
- `reference_data.py`: `get_valid_value_definitions_by_name` (drop)

**Not a bug — false positive from the same sweep, left alone:**
`get_typedef_by_name` (present on `ValidMetadataManager` and inherited by
`ValidMetadataLists`/`ValidTypeLists`/`SpecificationProperties`) also never
forwards `graph_query_depth`, but its REST endpoint
(`open-metadata-types/name/{name}`) is a plain GET with no request body at
all — same class as ISSUE-18 (`get_valid_metadata_values`). The parameter
is simply dead on that endpoint; there's nowhere to forward it to.

**Also found, promoted to their own tracked entries:** the same sentinel
sweep and its follow-up investigation surfaced three more distinct
findings, each now tracked separately rather than buried here —
ISSUE-26 (`get_info_supply_chain_by_guid`/`get_solution_role_by_guid` dead
parameters), ISSUE-27 (~50 unaudited all-positional call sites), and
ISSUE-28 (`NameError` breaking `get_specification_property_by_guid`).

**Consequence for ISSUE-23/24:** ISSUE-23 (raising the shared
`max_mermaid_node_count` default) and ISSUE-24
(`AssetCatalog._async_get_asset_lineage_graph_by_guid`'s hardcoded
`queryGraphDepth: 5`) are still open and still worth doing, but neither
would have fixed the reported symptom on its own — a configurable default
has nowhere useful to land while the value that's supposed to carry it
never reaches the request. This issue was the actual blocker; ISSUE-23/24
remain valid, narrower follow-ups on top of it.

**Postscript — the original repro's 3-vs-5 node gap was ultimately not a bug
at all.** After the fix above, live-verified with the user's exact raw REST
body (`searchString: "Onboarding"`, `startsWith: false`, `ignoreCase: true`,
no explicit `graphQueryDepth`/`maxMermaidNodeCount`) run through
`find_information_supply_chains`: pyegeria's `iscimplementationMermaidGraph`
for "New Employee Onboarding" was byte-for-byte the graph the user was
comparing against — the "3 nodes" vs. "5 nodes" difference was two valid but
different ways of counting the same mermaid text (3 `@{shape:...}` content
nodes vs. 5 total numbered flowchart boxes once the two `subgraph` container
boxes — "Context" and "Implementation" — are also counted, which is what a
person eyeballing the rendered diagram would naturally do). No truncation,
no depth issue, no forwarding bug in this specific case — the ISSUE-25 fix
above was still correct and necessary (confirmed via the runtime
sentinel-injection audit), it just wasn't the explanation for this
particular before/after comparison. **A second, genuinely separate effect
was layered on top of this in the user's actual comparison — see ISSUE-29
(governance zone visibility differs by user identity).**

**One more minor casing fix found and fixed along the way:**
`find_information_supply_chains` built its URL with
`f"...?addImplementation={add_implementation}"` where `add_implementation`
is a Python `bool` — this interpolates as `True`/`False` (capitalized)
rather than the lowercase `true`/`false` a REST boolean query parameter
normally expects. Live-verified this had no actual effect against the
current `qs-view-server` (Spring's boolean query-param binding is
case-insensitive, so `implementation` data was already coming back
correctly) — but fixed to `str(add_implementation).lower()` anyway for
robustness against stricter servers, matching the casing convention already
used at the sibling `get_info_supply_chain_by_guid` call site in the same
file.

---

### ISSUE-32: `create_note`/`update_note` used `"Notification"` as a placeholder `typeName`/`class` — replaced with the real `Note` type now that it's shipped (Egeria PR #9191)

**Status:** fixed 2026-08-05 (Pyegeria — `pyegeria/core/_server_client.py`,
`md_processing/v2/feedback.py`), found/actioned same day the user redeployed
Egeria with the new type.

**Background:** Dr.Egeria's `Create Note` command was already a known,
explicitly-flagged placeholder — its compact-spec entry
(`md_processing/data/compact_commands/commands_feedback_compact.json`) reads
*"PARSE-ONLY STUB: no NoteProperties/NoteLogEntryProperties type exists
anywhere in pyegeria yet — a new Egeria type is in progress. ... do NOT wire
a processor for this command until the type ships and is confirmed."* with
`OM_TYPE: "Notification"` as the placeholder. Separately,
`ServerClient.create_note`/`update_note` (the note-log-entry creation/update
methods used by `_async_add_journal_entry` and directly by tests) built
their default request bodies with `"class": "NotificationProperties",
"typeName": "Notification"` for the same reason — no dedicated type existed.

**What changed:** confirmed via the actual Egeria source (not the stale
local `egeria-v6/egeria` checkout, which was 13 commits behind — checked
`git fetch` + `origin/main` directly) that commit `8d3b8d9a99` ("Add Note
type - a subtype of Notification", merged via PR #9191) added a real
`Note` `EntityDef` (typeGUID `391f73ff-c184-41b6-8620-310b4284039f`,
superType `Notification`, model area 0160 "Notes" — the same area as
`NoteLog`/`AttachedNoteLogEntry`, confirming `Note` is exactly the proper
type for what `create_note` already builds via the `AttachedNoteLogEntry`
relationship, not a separate new concept). `NoteProperties extends
NotificationProperties` with **zero new fields** — purely a type-identity
fix, no new attributes needed anywhere.

**Verified live** (user redeployed Egeria with the new type same day):
- `ValidMetadataManager.get_typedef_by_name("Note")` confirms the type is
  registered on `qs-view-server` (`beanClassName: NoteProperties`, correct
  GUID).
- Created a real `Note`-typed element end-to-end via the fixed
  `create_note` default body (no manual override needed) and fetched it
  back — `elementHeader.type.typeName == "Note"`, confirmed.
- Cleaned up all throwaway test elements afterward
  (`MetadataExpert.delete_metadata_element`, see ISSUE-31 for a bug hit
  along the way).

**Fixed:**
- `_server_client.py`: `_async_create_note`/`create_note` and
  `_async_update_note`/`update_note` — default body's `"class"`/`"typeName"`
  changed from `"NotificationProperties"`/`"Notification"` to
  `"NoteProperties"`/`"Note"` (6 docstring sample-body occurrences too, for
  consistency); the dead/vestigial `prop` type-list arguments passed to
  `_async_create_element_body_request`/`_async_update_element_body_request`
  updated to match (`['NoteProperties']`/`['Note']`) even though currently
  unused by the validation code, to avoid leaving stale documentation of
  intent.
- `md_processing/v2/feedback.py`: `FeedbackProcessor`'s `"Note" in
  object_type` branch — `set_element_prop_body("Notification", ...)` →
  `set_element_prop_body("Note", ...)` (this one has real effect — produces
  `"class": "NoteProperties", "typeName": "Note"`); `set_update_body(...)`'s
  first argument also updated for consistency, though that helper doesn't
  actually use it (dead parameter, confirmed by reading the function body).

**Update 2026-08-05 — Dr.Egeria's `Create Note` command is now fully wired,
not just unblocked at the SDK level.** The Tinderbox-only bottleneck this
entry originally described no longer applies — as of the same day, compact-
spec edits go through the Dr.Egeria Spec Editor's local REST API instead
(`commands/tech/spec_editor.py`, `http://localhost:8420`; see `CLAUDE.md`'s
"Dr.Egeria Spec Editor" section and the `dr-egeria-command-sync` skill).
Using that API: `Create Note`'s `OM_TYPE` changed `"Notification"` →
`"Note"`, its stub description replaced with a real one, and
`"Commented On Element"` (the same reference attribute `Create Comment`
already uses, conveniently pre-aliased `"Associated Element"`) added to its
`custom_attributes` — the spec previously had no way to say what element a
note was about at all. `refresh_specs --merge-reports` regenerated
templates/help/report-specs; unit tests pass. Registered
`FeedbackProcessor` for `Create Note` in `setup_dispatcher()` and
implemented its `Create` branch (previously a stub with no code at all): it
now creates a dedicated `NoteLog` for the target element
(`_async_create_note_log`) and the `Note` entry on it
(`_async_create_note`, using the fixed `Note`/`NoteProperties` typing from
above). **Verified live end-to-end**, not just `--validate`: processed a
throwaway `dr_test_create_note_smoketest.md`, confirmed
`elementHeader.type.typeName == "Note"` on the created element via direct
fetch, then cleaned up both the `Note` and its `NoteLog`
(`MetadataExpert.delete_metadata_element`, see ISSUE-31 for a bug hit
along the way). Note: each `Create Note` call currently creates its own
private `NoteLog` rather than reusing an existing one on repeated notes
against the same element — not wrong (a `NoteLog` can hold many notes,
this just doesn't dedupe), flagged as a possible future improvement, not
attempted here.

**Still not fixed:**
- `update_note`'s underlying REST operation 404s on this server regardless
  of the type fix — see ISSUE-30, unrelated to this change, blocks live
  verification of the update path specifically (create + fetch are
  confirmed working). `Create Note`'s compact spec has no companion
  `Update Note` command at all today (only `Create` was ever defined), so
  this doesn't block Dr.Egeria usage — only direct SDK callers of
  `update_note`/`_async_update_note`.
- **Fixed 2026-08-05, same day, follow-up session:** the orphaned
  `"Create Journal Entry"` registration flagged above is resolved — see
  ISSUE-33.

---

### ISSUE-33: `Create Journal Activity`/`Create Log Activity` used the `Notification` placeholder typeName; renamed to match real `JournalEntry`/`ActivityEntry` types, and the orphaned dead `Create Journal Entry` registration from ISSUE-32 is now a real, working command

**Status:** fixed 2026-08-05 (Pyegeria + Dr.Egeria compact spec, same day as
ISSUE-32, follow-up in the same session). User question: since `JournalEntry`
is a real `Notification` subtype, why is Dr.Egeria's command called `Journal
Activity` instead — could it be renamed for consistency?

**Investigation, grounded in the actual Egeria type system and docs (not
guessed):**
- Live type query confirmed `JournalEntry`, `ActivityEntry`, `BlogEntry` are
  all real, distinct `Notification` subtypes (siblings of `Note` from
  ISSUE-32) — `superType: Notification` for all three, live on
  `qs-view-server`.
- Fetched `egeria-project.org/concepts/notification/`,
  `/types/1/0160-Notes/`, and `/types/1/0135-Actions-For-People/` before
  proceeding (per explicit user instruction) — confirmed `Note` and
  `JournalEntry`/`ActivityEntry`/`BlogEntry` are siblings under the *same*
  `NoteLog` + `AttachedNoteLogEntry` mechanism (`AttachedNoteLogEntry`
  connects a NoteLog to "an Action (**typically a Notification**)" — not
  restricted to one subtype), differing only in target (any element, for
  `Note`; the calling user's own profile, for the other three) and
  visibility (`JournalEntry` private; `ActivityEntry`/`BlogEntry` public).
- This also surfaced that `Create Journal Activity`/`Create Log Activity`
  (bundle `My Journal Base`, mapping to `my_profile.py`'s
  `journal_my_activity`/`log_my_activity`) were **not registered in the
  dispatcher at all** — a bigger gap than a naming mismatch. `Create Blog
  Entry` already had the correct `OM_TYPE: "BlogEntry"` but was equally
  unregistered.
- Confirmed the pre-existing `reg("Create Journal Entry", FeedbackProcessor)`
  (ISSUE-32's finding) was genuinely dead/orphaned — no command by that name
  existed in the compact spec, and its code branch referenced attributes
  that don't exist anywhere in `commands_feedback_compact.json`. Renaming
  `Journal Activity` → `Journal Entry` would otherwise collide with that
  dead registration, so it was removed first.

**Fixed, via the Dr.Egeria Spec Editor's REST API** (compact spec — see
ISSUE-32's entry for why raw JSON edits aren't used):
- Deleted `Create Journal Activity`, created `Create Journal Entry`
  (`OM_TYPE: "JournalEntry"`, `alternate_names: ["Journal Activity"]`).
- Deleted `Create Log Activity`, created `Create Activity Entry`
  (`OM_TYPE: "ActivityEntry"`, `alternate_names: ["Log Activity"]`) — same
  consistency rationale as the Journal rename, so it wasn't left half-fixed.
- `refresh_specs --merge-reports` regenerated templates/help/report-specs;
  unit tests pass.

**Fixed, code (`md_processing/dr_egeria.py`, `md_processing/v2/feedback.py`):**
- Removed the dead `reg("Create Journal Entry", FeedbackProcessor)` +
  its broken code branch.
- Registered `Create Journal Entry`, `Create Activity Entry`, `Create Blog
  Entry` → `FeedbackProcessor`.
- Implemented one shared branch (`object_type in ("Journal Entry",
  "Activity Entry", "Blog Entry")`) dispatching to
  `my_profile._async_journal_my_activity`/`_async_log_my_activity`/
  `_async_blog_my_activity` respectively.

**Verified live, all three, end-to-end** (not just `--validate`): processed
a throwaway smoke-test doc through the real `dr_egeria --process` pipeline —
all three `SUCCESS` with real GUIDs — then fetched each back and confirmed
`elementHeader.type.typeName` was exactly `JournalEntry`/`ActivityEntry`/
`BlogEntry` respectively. Cleaned up all three afterward.

**Not touched:** `my_profile.py`'s journal/log/blog-my-activity NoteLogs
(the containers these entries were created in) — unlike `Create Note`'s
throwaway per-note `NoteLog`, these are the user's own persistent
activity-stream containers and weren't deleted during cleanup, only the
three created entries were.

**Downstream propagation completed same session:** templates regenerated
and mirrored into `egeria-workspaces-fs`/`egeria-advisor` (old
`Create_Journal_Activity.md`/`Create_Log_Activity.md` deleted, new
`Create_Journal_Entry.md`/`Create_Activity_Entry.md` added, confirmed via
`git status` in both downstream repos); `docs/dr_egeria_manual.md`'s
Feedback family description updated; `egeria-workspaces-fs/portal-docs/
tools/dr-egeria/templates-basic.md`'s Journal Entry example corrected to
use real attribute names (`Display Name`/`Description`, not the
placeholder `Subject`/`Entry` it previously showed) and noted the sibling
commands; dr-egeria Glossary (help Terms) regenerated and reprocessed
against the live server.

---

### ISSUE-34: `MetadataExpert._async_find_metadata_elements` accepted `start_from`/`page_size`/`graph_query_depth` but never used any of them — reported directly by the user, with the correct fix already identified

**Status:** fixed 2026-08-05 (Pyegeria — `pyegeria/omvs/metadata_expert.py`).

**Layer:** Pyegeria.

**What:** the method built its request with a bare URL and the caller's
`body` passed straight through unmodified:

```python
url = f"{base_path(self, self.view_server)}/metadata-elements/by-search-conditions"
response = await self._async_make_request("POST", url, body_slimmer(body), timeout=timeout)
```

No query string, and `start_from`/`page_size`/`graph_query_depth` were
silently dropped — never merged into `body`, never appended to `url`. The
sync wrapper `find_metadata_elements` correctly forwarded all three
parameters down to this async method; the drop happened one layer further
in.

**Root-caused against the `.http` ground truth** (both worked examples in
`Egeria-api-metadata-expert.http` for `by-search-conditions`), confirming
two different fix shapes were needed for the three parameters:
- `startFrom`/`pageSize` never appear in either worked-example body —
  confirmed (cross-checking `Egeria-api-solution-architect.http`'s
  `by-name?addImplementation=true&startFrom=0&pageSize=10`) they're URL
  query parameters for this family of endpoint, not body fields.
- `graphQueryDepth`, by contrast, **is** a body field here — the second
  worked example (`findMetadataElements (nested condition)`) shows
  `"graphQueryDepth": 10` inside the `FindRequestBody`.

**Fix:** appended `?startFrom={start_from}&pageSize={page_size}` to the
URL; merged `graphQueryDepth` into `body` only when the caller's own body
dict didn't already set it explicitly (preserves an explicit caller value
rather than overwriting it).

**Verified:**
- Runtime capture (mocked `_async_make_request`) confirmed all three reach
  the wire correctly: `?startFrom=20&pageSize=50` in the URL,
  `"graphQueryDepth": 7` in the body.
- Confirmed a caller-supplied `graphQueryDepth` in `body` is preserved,
  not overwritten by the parameter default.
- Live call against `qs-view-server` (`find_metadata_elements` searching
  `InformationSupplyChain` by `displayName LIKE "Onboarding"`) succeeds
  and returns results.

---

## Not a bug / n/a

### ISSUE-5 (PY-9): local `as_of_time` fixes not shipped to the deployed package

**Status:** fixed / moot, re-verified 2026-07-31 — `get_linked_projects`,
`get_collection_members`, and `get_data_field_by_guid` all accept
`as_of_time` (directly or via `**kwargs`) in current source. This was a
deployment-timing issue, not a code defect — see ISSUE-12, below.

---

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

### ISSUE-29: Information Supply Chain search results/mermaid graphs differ by user identity — governance zone visibility, not a pyegeria bug

**Status:** n/a (Egeria Server — deliberate zone-based visibility
filtering), found 2026-08-04 chasing down the last piece of ISSUE-25's
original repro.

**Layer:** Egeria Server (governance zone / visible-zones configuration).

**What:** the exact same `find_information_supply_chains` search, run at
the same instant against the same view server, returns materially
different data depending on which user's credentials are used. Live-
verified side-by-side for "New Employee Onboarding Information Supply
Chain":
- `peterprofile`: implementation graph shows 5 `SoftwareServer`s
  (`coco-hrim`, `NL payroll`, `CA payroll`, `UK payroll`, `ocopages`)
- `erinoverview`: implementation graph shows only 2 (`coco-hrim`,
  `ocopages`) — the 3 payroll systems are filtered out entirely

Confirmed via raw `curl` against `/api/token` + the `by-search-string`
endpoint directly, with zero pyegeria code involved — same request body,
same moment, different user, different result. Not a caching artifact
(re-ran both back-to-back) and not explained by anything on the client
side.

**Where seen:** originally surfaced as part of ISSUE-25's repro
investigation — initially looked like a "3 nodes vs 5 nodes" pyegeria bug,
but turned out to be two unrelated effects layered together: a
node-counting-convention difference (see ISSUE-25's postscript, resolved,
not a bug) plus this genuine zone-visibility difference (this entry).

**Why not a bug:** pyegeria faithfully returns whatever the server sends
for the credentials it's given. The 3 payroll systems are presumably
scoped to a governance zone `erinoverview`/`IvorPadlock` aren't members of,
while `peterprofile` (likely a broader-access/admin-style demo user) can
see them. This is Egeria's zone-based security model working as designed,
not a pyegeria defect — nothing here is client-side fixable.

**Worth knowing:** if comparing pyegeria output against a raw REST call or
Egeria Explorer UI result and results don't match, check whether the same
user/credentials were used in both before assuming a client-side bug —
this cost real investigation time in ISSUE-25's process. Added a pointer
to this in the Quick Reference table above and in this file's intro.

---

*(Add new entries at the top of the appropriate Open Issues subsection as
they're found; move an entry to the Appendix once it's fixed/reclassified,
keeping its original `ISSUE-#`. Keep the format: status, layer
classification, what, where seen, candidate fix — so entries are
self-contained enough to hand to whoever eventually reviews/fixes them.)*
