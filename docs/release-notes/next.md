# pyegeria (next release, unreleased)

Notes collected on `release/next` for the next release. The version number is set when it's cut.

## Deprecations

- **`pyegeria.view.base_report_formats.load_egeria_report_specs` is deprecated and will be removed in pyegeria 7
  (expected early January 2027).** It is the legacy loader for the May-2026 `ReportType::` collections. Egeria-held
  report specs are `ReportSpec::` elements, and they load through the spec cache:
  `pyegeria.view.egeria_spec_cache.sync_report_specs` (the system of record, which reads both markers and serves the
  consumer index and the authoring API). The legacy loader raises a `DeprecationWarning` once per process. Until it
  is removed it keeps working, unchanged in what it searches. It now pages through Egeria's results, backs off its
  retries after a read Egeria didn't confirm complete, and reports an empty result as "No legacy ReportType
  collections found (Egeria-held specs load through the spec cache)".

- **`AuthoringRefused.answer`** (pyegeria.authoring): every refusal now carries a machine-readable `answer`, which is
  `"absent"` (Egeria holds no such artifact that you can see, said only on a confirmed end), `"unknown"` (whether
  Egeria holds it couldn't be told; never to be read as "none") or `"refused"` (anything else, the default).
  `ANSWER_ABSENT`, `ANSWER_UNKNOWN` and `ANSWER_REFUSED` are exported. Branch on `answer`, not on the words. It's
  backward compatible: `AuthoringRefused` is still a `ValueError`, and its words are unchanged.

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
