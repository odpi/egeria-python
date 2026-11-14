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

- **Private drafts are zoned exactly to their author** (`EgeriaDraftStore`, D16). An element whose zones include
  the author's own zone and others is shared, never a private draft:
  - save, load and delete refuse it with "a private draft is zoned only to you; publish it to share it";
  - `list` leaves it out and says so in `notes`;
  - prune reports it under `not_private`.
