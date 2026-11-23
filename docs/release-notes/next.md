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
  - **On Egeria 6.3, counts from type-specific searches (for example `find_data_assets`) can be incomplete and are
    reported as "at least N".** `get_relationships`, `get_related_elements` and the `find_metadata_elements` family
    (by type, by name, by property value) report their end. Their totals count only what Egeria lets the caller see:
    elements in zones the caller can't read are left out on every path; elements anchored to a Promise are left out
    unless the request asks for lineage (`pyegeria.lineage_visible()`).

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

- **My Profile: work with communities directly (#601, Peter Coldicott).**
  - Press `Enter` on a community in the main screen's User Associations to open it.
  - **Find Community** on the Other Functions menu opens the Communities screen ready to search.
  - A community now shows its **resources**: what it lists with `ResourceList`, and what is `ScopedBy` it.
  - If you aren't a member, the community screen offers **Join Community** (Contributor or Observer).
  - Blog posts and resources have a **feedback** screen: like/unlike, a 1–5 star rating with an optional review
    (one per person; rating again replaces it), and comments.
  - The main screen reloads after you join, leave or create-and-join a community.
  - Feedback reads use the same paging rules as the rest of My Profile: counts say "at least N" unless Egeria
    confirms the end.
  - See `docs/my_egeria_manual.md` and `docs/My-Egeria-Doc.md`.

- **A report column can show related information** (PY-53, `Column.source`). `class:<Classification>[.<property>]`
  shows a classification property (`class:Branch.scope`; `class:Campaign,Task` lists every one present),
  `rel:<end>.<property>` a property of the relationship (`rel:projectTargets.label`), and `of:<end>.<attribute>` an
  attribute of the related element. A relationship column and an element column of one end line up by position, a
  related element without the value shows "—" in its place; when none has it, the cell is blank (never "None"). The validator refuses an unknown classification,
  end or property. New in Projects (Project Kind, covering all six project-kind classifications; Target Labels) and the new File-Folders spec (Branch).
- **A report spec can say it needs Egeria 6.4** (PY-49, annotation `min_egeria_version`). Run against an older
  platform, it stops before sending anything, with "needs Egeria 6.4". Decisions and Data Values use it.
- **New Platform-Report spec** (PY-49). `get_platform_report(..., output_format="DICT")` now shows the platform's URL,
  origin, start time, build and public properties and the servers it hosts, each as "name (STATUS)". The Platforms
  spec keeps only what the platform element carries.
- **Catalog-Target shows the CatalogTarget relationship** (PY-53). Its columns come from the relationship of the
  connector you asked about (catalog target name, metadata collection and source, connection name, permitted
  synchronization, delete method, templates, configuration properties), and the target's own name and type come
  from the target. The spec runs `get_catalog_targets`, which needs the integration connector's GUID and is now on
  the report-spec allowlist.

## Planned for pyegeria 6.4 or the next release

- **No default password, and no built-in identity outside a named demo profile.** pyegeria 6.4 or the next release drops the quickstart
  defaults (`erinoverview` / `secret`): a client gets credentials only from its arguments, the environment,
  config.json, or a demo profile named explicitly.
  - **The command-line tools lose their demo-password fallback.** Until 6.4, `hey_egeria` and the other CLIs read the
    password only from `--password` / `--user_pass` and the `EGERIA_USER_PASSWORD` environment variable, and fall back
    to the QuickStart demo password otherwise. They don't read `config.json` or `.env` for it, so a password set only
    there isn't used. From 6.4 they read it the same way as the library, and a command with no password set fails with
    "No password to sign in to Egeria…". **Set the `EGERIA_USER_PASSWORD` environment variable now**: see
    [Setting your Egeria password](../setting-your-egeria-password.md).


## Changed

- **No built-in password or admin credential in the library, from this release** (PY-33, PY-35; 6.3.0 still had the
  demo-password fallback). `resolve_egeria_credentials` no longer
  falls back to a built-in password, and the library's `ADMIN_USER` / `ADMIN_PASSWORD` reads and its settings model
  have no literal defaults either. With no password set, `create_egeria_bearer_token` raises
  `PyegeriaInvalidParameterException` ("No password to sign in to Egeria as '<user>' …") before any request is sent.
  **A behaviour change:** before, the request went to Egeria and came back as a 401, so code that catches that 401 for
  a missing password should catch the new exception. The CLIs keep their demo-password fallback until 6.4 (above).
  See [Setting your Egeria password](../setting-your-egeria-password.md).
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


- **Content status: four finds now return every status by default** (PY-27). `find_data_assets`,
  `get_data_assets_by_category`, `find_authored_elements` and `find_authored_elements_by_category` used to limit
  results to content status ACTIVE, which hid every element created without a content status (Egeria stores none
  for those; on a demo server, 2026-11-17, 1,246 of 3,937 data assets). They now send no content-status filter, so Egeria
  returns elements of any status, including those with none and DRAFT, DEPRECATED and REJECTED ones. **To get the
  previous result, pass `content_status_list=["ACTIVE"]`.** A list you pass is sent unchanged.
- **A by-name or by-type lookup refuses a missing name** (PY-63). A `None`, `""` or `"*"` name or key is refused
  before anything is sent, with "<call> needs a name; use <find> to list all", because the Egeria 6.4 by-name and by-type
  endpoints refuse it (each one checked answered HTTP 400; "*" there is an exact match). `hey_egeria ... deployed-servers` now
  defaults to `View Server` instead of `*`.
- **An `of:` report column is checked against the entity type at its relationship end** (PY-61). The validator used to
  accept `of:<list>.<attribute>` if any entity type had the attribute; it now checks the entity type(s) at that end of the
  relationship and their supertypes, both from the 6.4 typedefs, and refuses a wrong-end attribute naming the relationship,
  the end, its type and the attribute. A list whose end type is not in the tables is checked loosely and gets a warning.
- **A preview asks Egeria only for the rows it shows** (PY-19). A report run with `page_to=N` made its requests
  for `min(N, 100)` rows, not always 100, so it reads at most one page past `N`. Paging is
  unchanged otherwise: a short or empty page does not end the read, only Egeria's null does, and a run that stopped at
  `N` still says so ("stopped at the N rows asked for; there may be more"). Full reads are untouched.
- **`find_digital_product_catalogs` lists catalogs** (PY-71). It sent no type filter and so listed every Collection
  (a live `find("*")` returned Agreements). It now asks for `DigitalProductCatalog` unless you pass
  `metadata_element_subtypes`, and it and `get_digital_product_catalogs_by_name` format `output_format="DICT"`, `"MD"` and
  the others (they had no output generator and raised `TypeError`).
- **Unity Catalog report specs take the caller's search and show real columns** (PY-56). The UC-Catalog-Element specs
  no longer pin the search to "Unity Catalog Catalog::": the prefix is a `qualified_name_prefix` constraint
  (`find_elements_by_property_value(..., qualified_name_prefix=...)`) ANDed with the search string you pass. The six
  UC-*-Element specs no longer list the create-from-template inputs (`uc_catalog`, `uc_schema`, `uc_table`, `host_url`,
  `port`, `network_address` ...), which are not properties of the element found and were always blank.
- **29 by-name helpers answer "everything" with their find** (PY-64). `get_<x>_by_name("*")` (or no name) runs
  `find_<x>("*")` where a live check on Egeria 6.4 showed both return the same element type and shape and have the
  same `output_format` and `report_spec` defaults: note logs, search keywords, actor profiles, roles, user identities,
  contribution records, perspectives, contact details, assets, software capabilities, collections, glossaries,
  communities, locations, subject areas, business capabilities, valid value definitions, statements of applicability,
  connections, connector types, endpoints, data structures, data fields, data value specifications, external
  references, external identifiers, governance definitions, schema attributes and design patterns. The rest keep the
  PY-63 refusal (their find returned nothing, timed out, differs in defaults, or was not proven).
  When `*` is routed to a find, the find's `page_size` (100) applies unless you pass one; the helpers' own default
  is 0 (or 500 for design patterns). A real name given as `filter_string=` or another name keyword is never routed.
- **Egeria 400 errors are not labelled server errors** (PY-58). A request Egeria refuses (HTTP 400) raises
  `PyegeriaBadRequestException`, a `PyegeriaInvalidParameterException` (and still a `PyegeriaAPIException`), with
  Egeria's own message and message id, instead of "SERVER_ERROR_500". `get_platforms_by_name("*")` returns the
  platforms of the default type ("OMAG Server Platform").
- **Generated report specs show only columns a find can fill, and lead with name, qualified name and guid**
  (PY-49, PY-62). Columns that no find ever filled are gone (about 1,500 of 8,600), the file inputs of the Secrets
  Store Element spec among them (PY-57); every generated spec shows display name, qualified name and guid where its
  type has them (34 specs gained columns). The Unity Catalog specs now target real types (Namespace, SoftwareServer,
  DeployedDatabaseSchema, ...).
- **The Subscription Type spec and Dr.Egeria command are removed** (PY-49): Egeria has no such type. The hand-written
  specs were checked against the 6.4 type tables; the columns that could not be checked are in
  `docs/audits/PY-49-q7-unverified-columns.md`.
- **The registered-service "URL Marker" column fills** (PY-49): it read the wrong key and was always empty.


- **Data Scope carries every field Egeria 6.4 defines, and Description is removed from it** (PY-25).
  **Behaviour change:** `Classify Data Scope` and `Update Data Scope` no longer have a **Description** attribute.
  It was sent as `additionalProperties` (a text into a map) and Data Scope has no description, so it never worked;
  use **Additional Properties** for key/value pairs. The commands now take the collection, validity and coverage start
  and end times, **Min/Max Longitude, Latitude and Height**, **Scope Elements**, Effective From and To, and Extended
  Properties, and send each under its Egeria name. **The six bounds must be numbers** (`-10.5`, `35`): text that isn't
  a number is refused before anything is sent, and they go to Egeria as numbers. `Create Data Lens` gains the same
  validity and coverage periods and sends its bounds as numbers too.
- **A failed read is not "none"** (PY-22). **Behaviour changes:** initiating a survey, with no action target name
  given, now stops with "the action targets of survey X could not be read ... pass action_target_name" when it cannot
  read them from the survey type (it used to guess `serverToSurvey`); and `karma_leaderboard` returns `None`
  (unknown), not `[]`, when it could not read every contribution record, so a caller shows "couldn't be read" rather
  than "no contributors". `[]` now means the records were read in full and nobody qualifies.
- **Exceptions say when Egeria hid the element** (PY-24). `PyegeriaException.not_visible` is True when Egeria refused
  a read because the element is hidden from the caller (`OMAG-REPOSITORY-HANDLER-400-010`,
  `OPEN-METADATA-SECURITY-403-007`, `OPEN-METADATA-SECURITY-403-020`), and the API, bad-request and not-found
  exceptions carry `egeria_message_id`, as the unauthorized one already did.
- **Reading a search keyword by GUID works** (PY-28). `get_search_keyword_by_guid` posts to
  `.../search-keywords/{guid}/retrieve`; the old path answered 404.
- **`class:` report columns match a classification's subtypes** (PY-59). `class:PolicyManagementPoint` also fills from a
  PolicyEnforcementPoint, `class:ProjectKind` from a Campaign, Task, Experiment, GlossaryProject or GovernanceProject,
  and so on (23 classifications have supertypes). The supertypes come from the 6.4 typedefs
  (`CLASSIFICATION_SUPERTYPES`); a supertype does not fill a subtype column.
- **Governance-level columns show the level name** (PY-60). Confidentiality, Confidence, Criticality, Impact and
  Retention classification columns read e.g. "Confidential", "Authoritative", "High", "Regulated Lifetime" instead of 1, 3.
  DICT and JSON keep the integer; a number outside the enum shows as "7 (unknown level)", and a missing property stays
  blank.
- **Status attributes offer all five element statuses** (PY-68). The Dr.Egeria `Status` attribute looked up the valid
  metadata property `Status`, which Egeria does not have, so the templates listed no values. It now looks up `status`
  and the templates offer ACTIVE, DELETED, INVALID, OTHER and UNKNOWN.
- **The spec-cache says "not effective for this read"** (PY-70). When Egeria answers OMAG-REPOSITORY-HANDLER-400-010 for a
  pinned spec, the reason no longer says the element is gone or "no longer visible". `karma_leaderboard` is declared to
  return `list[dict] | None` (None when its find failed).
- **`hey_egeria ... deployed-servers` is one command** (PY-66). It was registered twice and the second silently replaced
  the first.

## Fixes

- **Authoring validation is strict** (PY-15). A spec's find method must return its target type (or a super type),
  and every column key must be an attribute of the target type, a key the output formatter derives, a documented
  related-element or annotation field, or (for a generated -DrE- spec) a Dr.Egeria command attribute. An unknown
  key is refused by name. The old loose check remains only as `validate(..., legacy=True)`, with a warning per key.
- **Activity Status offers FOR_INFO** (PY-21). The generated Dr.Egeria `activity_status` columns (Meeting, Note, Review,
  ToDo ...) listed 13 of Egeria's 14 ActivityStatus values; FOR_INFO is now offered after PAUSED.
- **`start_at_end` reaches Egeria** (PY-23). pyegeria sent `startAtEnd`; the query parameter is `startingAtEnd`, so Egeria
  ignored it. The related-element finds now send `startingAtEnd`.
- **A failed valid-values lookup is not "no valid values"** (PY-67). `get_valid_metadata_values` raises when Egeria
  cannot be asked, and is never cached as empty; `[]` means Egeria answered with none. Offline `generate_dr_help` and
  template output says "valid values not read (no Egeria connection)" or "(Egeria lookup failed: <Type>)" instead of
  dropping the line, and a failed sign-in counts as no connection.
- **Classification commands send Effective From, Effective To and Extended Properties** (PY-69). Every Dr.Egeria
  classification command sent only its own fields and dropped these three.
- **Generated report specs carry fresh data** (PY-54). `md_processing/data/generated_format_sets.json` was regenerated
  by `refresh_specs --merge-reports` (it had stale target types and `glossary_term` keys); nothing reads it at runtime.
- **Related-information report columns are settled** (PY-55). The actor list (Contacts) and note log name columns
  (Journal Entry) are `of:` source columns filled from the real relationship lists, and the folder names column on
  `find_glossaries` is client-derived; the old helpers that ran actor names together and cut the last two characters of
  note log names are no longer needed.
- **The deployment-status fallback matches Egeria** (PY-21). It offered `REJECTED_FOR_DEPLOYMENT`; Egeria's value is
  `REJECTED`.
- **Dr.Egeria Certification and License send the right fields** (PY-43, PY-50). Link and Update send `coverageStart` /
  `coverageEnd` (they sent `startDate` / `endDate`, which Egeria dropped). Link and Update Certification refuse
  Entitlements, Obligations and Restrictions with words naming the Certification Type, where they belong, instead of
  dropping them silently, and the command templates no longer offer them.
- **A Dr.Egeria command that needs Egeria 6.4 fails on an older platform** (PY-48). It was reported as a pass with
  nothing written. The runner now counts only `success`, `deferred` and `read` as succeeded; any other status, or none,
  is a failure with the status in the words.
- **`add_search_keyword_to_element` creates a keyword with its text** (PY-41). It sent `keyword`, which Egeria ignores;
  it now sends `displayName` (and the description, if given). `FindPropertyNames` sends `metadataElementTypeName`
  (PY-44), so the relationship type is applied.
- **Markdown output no longer prints "None" for an unset property** (PY-39). In FORM and MD the heading stays and the
  body is blank; in REPORT and MERMAID the property is left out.
- **The `start_date` / `planned_end_date` rename warning is shown** (PY-42): it is a `FutureWarning`, not a
  `DeprecationWarning` that Python hides outside `__main__`.
- **Dr.Egeria accepts every key a Properties class reads** (PY-45, PY-46). The properties table follows public
  setters through the whole superclass chain (for example `ResourceList`'s `resourceUse` and `label`, and the query
  options of `FindPropertyNames`), and strict validation checks a spec's columns against the Egeria type name
  (`License Type` is `LicenseType`).
- **`validate_compact_specs` reports 0 errors, and a regeneration is stable** (PY-51, PY-52). It accepts the Egeria 6.4
  type names, `generated_format_sets.json` leaves out empty optional fields and is current, and a template generated
  with no Egeria connection says "valid values not read" instead of dropping the line.
- **Two unparsable deprecated scripts are removed** (PY-36); a test parses every file under `commands/`.

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
