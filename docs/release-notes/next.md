# pyegeria (next release, unreleased)

Notes collected on `release/next` for the next release. The version number is set when it's cut.

## New

- **`NO_PASSWORD`: opt out of the configured default password** (`from pyegeria.core._no_password import
  NO_PASSWORD`). Pass `user_pwd=NO_PASSWORD` to any client (`EgeriaTech`, `EgeriaCat`, `Egeria`, `EgeriaConfig`, the
  OMVS classes, `BaseServerClient`, `BasePlatformClient`), typically with a bearer token for a signed-in user. The
  client then holds no password (`user_pwd is None`, `use_default_password is False`), and so does every sub-client
  `EgeriaTech` builds and every helper client pyegeria builds for it. The configured password
  (`settings.User_Profile.user_pwd`) is never used, so when the token expires the request fails with a 401
  (`PyegeriaUnauthorizedException`) instead of the one auto-retry signing in again as the configured (demo) user.
  Every client pyegeria builds to act for another (sub-clients and helpers) now goes through one
  `pyegeria.core._helper_client.helper_client`: the caller's bearer token set once (exactly one `Bearer ` prefix), and
  the caller's own password or none, never the configured default, even when the token arrived through
  `set_bearer_token`.
  This replaces the password scrub and `_get_subclient` patch that token-only callers needed. **`user_pwd=None` is
  unchanged**: it still takes the configured password, which CLIs rely on.
- **`AuthoringRefused.answer`** (pyegeria.authoring): every refusal now carries a machine-readable `answer`, which is
  `"absent"` (Egeria holds no such artifact that you can see, said only on a confirmed end), `"unknown"` (whether
  Egeria holds it couldn't be told; never to be read as "none") or `"refused"` (anything else, the default).
  `ANSWER_ABSENT`, `ANSWER_UNKNOWN` and `ANSWER_REFUSED` are exported. Branch on `answer`, not on the words. It's
  backward compatible: `AuthoringRefused` is still a `ValueError`, and its words are unchanged.

- **`pyegeria.authoring.can_edit(kind, ref, client)` / `async_can_edit`** returns `{"answer": "yes"|"no"|"unknown",
  "why"}`, read as the user. Egeria has no edit-rights API, so:
  - **yes:** your own private draft, or a held spec, Report or sheet you created (`versions.createdBy`) or own
    (Ownership names your user id);
  - **no:** a built-in spec, or nothing in Egeria you can read;
  - **unknown:** everything else, including a failed read. Callers hide an edit link on unknown, and the authoring
    API still checks when the artifact is opened and published.
- **`pyegeria.authoring.used_by(kind, label, client)` / `async_used_by`** answers "what uses this spec, Report or
  sheet?" as `{"items": [{"kind", "name", "qualified_name", "via"}], "complete", "notes"}`. Every read is live, as
  the user (no shared index, no cache):
  - a spec's Reports (by their `reportSpec`) and its consumer folders;
  - a Report's sheets (DataSetContent);
  - a sheet's consumer folders.

  `via` is one of the closed set `VIA_KEYS` (`reportSpec`, `CollectionMembership`, `DataSetContent`): machine keys
  for the caller to put into words. `complete` is True only when every read reached a confirmed end. An empty answer
  that isn't complete is "nothing found in what Egeria returned", never "used by none".

  The artifact is resolved first, through Egeria's exact unique-name read. If it can't be resolved, `used_by` raises
  `AuthoringRefused` with `answer` "absent" (only on Egeria's own not-found) or "unknown". A built-in spec that Egeria
  doesn't hold still has its Reports listed. A Report's `reportSpec` matches the label exactly, case-sensitively,
  after one `ReportSpec::` prefix is stripped; the legacy `ReportType::` prefix is also stripped, until pyegeria 7.
  Call it on demand, when the user asks.
- **Paging:** `get_elements` (read by type) is `findMetadataElements` underneath, so it's now NULL_NOT_END and
  gate-trusted on a #9453 platform like the other find paths. The dashboard sheet list passes its client, so on
  such a platform it can be confirmed complete.
- **Paging: one version gate per upstream fix, with odpi/egeria #9454 added** (`pyegeria.core.paging`). The gate
  used to know one fix (#9453, the find paths). It now holds a table, `FIXES`, with each fix's SNAPSHOT build
  cutoff, the first release carrying it, and whether later lines' SNAPSHOTs carry it. `METHOD_NEEDS` says which
  fixes each read needs, and a read is trusted only on a platform carrying all of them. `platform_fixes(client)`
  / `async_platform_fixes` return the set of fixes a platform carries, from one `/api/about` read per platform,
  cached as before. `platform_promoted` and `gate_from_about` keep working as before, meaning "carries #9453".
  `PYEGERIA_TRUSTED_END=off` still turns every fix off, and there is still no "force on".
  - **#9454** (970092b9) makes `get_relationships` and `get_related_elements` send `[]` for a filtered page and
    null only at the end. On a platform carrying it (a 6.3-SNAPSHOT built at or after 2026-11-15T07:26Z, or any
    later line's SNAPSHOT), both reads are now trusted, so their results can be confirmed complete. No release is
    trusted for #9454 until it is confirmed in a tagged release (expected 6.3.0).
  - **Without #9454**, `get_relationships` stays NULL_NOT_END: "at least N", never a total. Its async name,
    `_async_get_relationships` (what report specs page under), is now NULL_NOT_END too. It wasn't before, but it
    is the same server call. `get_related_elements` keeps today's paging there.
  - The saved-query delete and the dashboard-sheet link reads now pass their client, so they can be confirmed
    complete on a #9454 platform. With no change to them, `used_by` and My Egeria's network list can too.

## Planned for pyegeria 7 (expected early January 2027)

- **No default password, and no built-in identity outside a named demo profile.** pyegeria 7 drops the quickstart
  defaults (`erinoverview` / `secret`): a client gets credentials only from its arguments, the environment,
  config.json, or a demo profile named explicitly.

## Deprecations

- **`pyegeria.view.base_report_formats.load_egeria_report_specs` is deprecated and will be removed in pyegeria 7
  (expected early January 2027).** It is the legacy loader for the May-2026 `ReportType::` collections. Egeria-held
  report specs are `ReportSpec::` elements, and they load through the spec cache:
  `pyegeria.view.egeria_spec_cache.sync_report_specs` (the system of record, which reads both markers and serves the
  consumer index and the authoring API). The legacy loader raises a `DeprecationWarning` once per process. Until it
  is removed it keeps working, unchanged in what it searches. It now pages through Egeria's results, backs off its
  retries after a read Egeria didn't confirm complete, and reports an empty result as "No legacy ReportType
  collections found (Egeria-held specs load through the spec cache)".

## Changed

- `md_processing/md_processing_utils/properties_class_fields.py` is now regenerated from Egeria c61bad65.
- `ProjectProperties` gains `scope`; 25 SchemaType-family classes drop `queries`, matching #9448's `SchemaTypeProperties`
  change.
- Dr.Egeria and authoring validation now follow Egeria 6.3's type system, so a `queries` attribute or column is no
  longer sent or accepted.

## Fixes (spec cache)

- **The EGERIA report-spec tier is cached per identity** (`pyegeria.view.egeria_spec_cache`). It used to be held in
  one shared slot, which a server with threaded, per-request identities (the Portal) could race:
  - A reload for a new user marked the slot as that user's before its disk load finished, while the slot still held
    the previous user's specs.
  - A concurrent request for the new user in that window got the previous user's tier, private specs included, and
    `egeria_tier_info` could return that user's provenance.

  Now each identity has its own entry, held in a bounded LRU (64 entries). An entry is built whole and swapped in
  with one locked assignment. `egeria_tier_info`, and the name check used while specs load, read only the caller's
  own entry.
- **`spec_identity(None)` now means "explicitly no one"**: no private cache loads and no fetched copy is served,
  whether or not the process is declared multi-user. Before, None was read as "not set" and fell back to the
  process's own identity. An empty identity means no one too.

## Fixes

- **The exact unique-name read no longer signs in with the settings default password** (`pyegeria.core.unique_name`).
  When the caller has no unique-name read of its own (a `CollectionManager`, say), pyegeria builds a
  `ClassificationExplorer` on the same platform. It now acts exactly as the caller:
  - The explorer gets the caller's token and is built with `user_pwd=NO_PASSWORD`, so it never holds a password. Before, a caller that had cleared its password (as Studio
    and EA do) gave the explorer the settings default. A 401 auto-retry could then sign in again as that default user.
  - With no token, the explorer uses only `carried_password(client)`: a password the caller itself holds, or the
    caller's own `NO_PASSWORD` opt-out. If the caller has neither, the answer is
    "unknown" and Egeria isn't called.
  - The token is shared bare. Before, the `"Bearer ..."` header value was set as the token, which gave `"Bearer
    Bearer ..."`.
  - A caller without real `view_server` and `platform_url` strings (a fake, or anything that isn't a client) gets
    "unknown". No client is built.
  - The explorer is closed after the read.

## Fixes (drafts)

- **Private drafts are zoned exactly to their author** (`EgeriaDraftStore`, D16). An element whose zones include
  the author's own zone and others is shared, never a private draft:
  - save, load and delete refuse it with "a private draft is zoned only to you; publish it to share it";
  - `list` leaves it out and says so in `notes`;
  - prune reports it under `not_private`.
