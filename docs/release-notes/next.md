# pyegeria (next release, unreleased)

Notes collected on `release/next` for the next release. The version number is set when it's cut. Items that shipped
in 6.2.42 (`NO_PASSWORD`, `AuthoringRefused.answer`, `can_edit`, `used_by`, the per-identity spec cache, the
unique-name read fix, `get_elements` paging, and the `load_egeria_report_specs` deprecation) are in the 6.2.42
notes and are not repeated here.

## New

- **Paging: one version gate per upstream fix, with odpi/egeria #9454 added** (`pyegeria.core.paging`). The gate
  used to know one fix (#9453, the find paths). It now holds a table, `FIXES`, with each fix's SNAPSHOT build
  cutoff, the first release carrying it, and whether later lines' SNAPSHOTs carry it. `METHOD_NEEDS` says which
  fixes each read needs, and a read is trusted only on a platform carrying all of them. `platform_fixes(client)`
  / `async_platform_fixes` return the set of fixes a platform carries, from one `/api/about` read per platform,
  cached as before. `platform_promoted` and `gate_from_about` keep working as before, meaning "carries #9453".
  `PYEGERIA_TRUSTED_END=off` still turns every fix off, and there is still no "force on".
  - **#9454** (970092b9) makes `get_relationships` and `get_related_elements` send `[]` for a filtered page and
    null only at the end. On a platform carrying it (a 6.3-SNAPSHOT built at or after 2026-11-15T07:26Z, or any
    later line's SNAPSHOT), both reads are now trusted, so their results can be confirmed complete. Releases from
    6.3.0 on are trusted too: the Egeria V6.3 tag (a81af02c) carries 970092b9, and #9453 (2a27dad5) as well.
  - **Without #9454**, `get_relationships` stays NULL_NOT_END: "at least N", never a total. Its async name,
    `_async_get_relationships` (what report specs page under), is now NULL_NOT_END too. It wasn't before, but it
    is the same server call. `get_related_elements` keeps today's paging there.
  - The saved-query delete and the dashboard-sheet link reads now pass their client, so they can be confirmed
    complete on a #9454 platform. With no change to them, `used_by` and My Egeria's network list can too.

- **Limit Result by Status is a list of element statuses, with three lifecycle filters beside it** (Dr.Egeria Create
  Report / View Report, the report-spec executor).
  - Limit Result by Status is a Simple List of Egeria's element statuses (UNKNOWN, ACTIVE, INVALID, DELETED, OTHER),
    default ACTIVE, checked before sending. A lifecycle value such as DRAFT is dropped with a warning that points at
    the new filters, instead of reaching Egeria as a 400. Older forms (`['ACTIVE']`, JSON lists) still parse.
  - New attributes Limit Result by Content Status, Limit Result by Deployment Status and Limit Result by Activity
    Status, valued from Egeria's ContentStatus, DeploymentStatus and ActivityStatus. They are sent only by find
    methods that take `content_status_list` / `deployment_status_list` / `activity_status_list`
    (`format_set_executor.LIFECYCLE_FILTERS`); elsewhere they are dropped with an `UnknownFilterWarning`.
  - The attribute table marks a dropped value with "⚠️ Warning".
- **`defaultValueOverride` is sent when the target type declares it** (PY-4). Before, pyegeria withheld it and
  reported "not applied".
- **Dr.Egeria Project Scope maps to `ProjectProperties.scope`** (PY-5 / EG-14).

## Planned for pyegeria 7 (expected early January 2027)

- **No default password, and no built-in identity outside a named demo profile.** pyegeria 7 drops the quickstart
  defaults (`erinoverview` / `secret`): a client gets credentials only from its arguments, the environment,
  config.json, or a demo profile named explicitly.


## Changed

- `md_processing/md_processing_utils/properties_class_fields.py` is now regenerated from Egeria c61bad65.
- `ProjectProperties` gains `scope`; 25 SchemaType-family classes drop `queries`, matching #9448's `SchemaTypeProperties`
  change.
- Dr.Egeria and authoring validation now follow Egeria 6.3's type system, so a `queries` attribute or column is no
  longer sent or accepted.
- **MCP report runs page to their max rows and say their count** (PY-17; the MCP part of PY-16). Today these are
  the `run_report` tool, `mcp_adapter.run_report` and `_execute_egeria_call_blocking`. A list format is paged up to
  the caller's `page_size`, else `MCP_MAX_ROWS` (100), as `preview` is, so a filtered first page doesn't read as
  "nothing". The result is otherwise unchanged and gains `count`.
- **`result_count(result)`** (`pyegeria.view.format_set_executor`) gives `{"count", "count_text", "complete",
  "end", "reason"}` for a find run's result. `count_text` is "N" only when the end is confirmed; otherwise it is
  "at least N", and `reason` says why. For a result that isn't a counted find (an analytic, a chart, text) it gives
  None. Use it to show a count, rather than reading `end` yourself.


## Fixes

- **Authoring validation is strict** (PY-15). A spec's find method must return its target type (or a super type),
  and every column key must be an attribute of the target type, a key the output formatter derives, a documented
  related-element or annotation field, or (for a generated -DrE- spec) a Dr.Egeria command attribute. An unknown
  key is refused by name. The old loose check remains only as `validate(..., legacy=True)`, with a warning per key.
- **Status values match Egeria** (PY-21). The deployment-status fallback offered `REJECTED_FOR_DEPLOYMENT`;
  Egeria's value is `REJECTED`. The seed report specs' activity-status columns (Actor Manager, Feedback, Projects)
  now offer `FOR_INFO`.

## Fixes (drafts)

- **`EgeriaDraftStore.list` and `prune_drafts` find the author's drafts on a live Egeria** (PY-18). The list used
  to search property values for `".*"`, which Egeria matches as literal text, not as a pattern, so on a real server
  it listed no drafts and prune removed none. It now reads each kind by type (ReportSpec, Report, Dashboard), with
  the author's zone as the filter, paged like the other by-type reads: complete on a platform with the #9453 fix,
  "at least N" before it. The exact-zone rule and the "at least" notes are unchanged. Found by the D16 privacy run
  on laz (2026-11-15).
- **Private drafts are zoned exactly to their author** (`EgeriaDraftStore`, D16). An element whose zones include
  the author's own zone and others is shared, never a private draft:
  - save, load and delete refuse it with "a private draft is zoned only to you; publish it to share it";
  - `list` leaves it out and says so in `notes`;
  - prune reports it under `not_private`.
