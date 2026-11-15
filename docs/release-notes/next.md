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

## Fixes

- **The exact unique-name read no longer signs in with the settings default password** (`pyegeria.core.unique_name`).
  When the caller has no unique-name read of its own (a `CollectionManager`, say), pyegeria builds a
  `ClassificationExplorer` on the same platform. It now acts exactly as the caller:
  - The explorer gets the caller's token and no password. Before, a caller that had cleared its password (as Studio
    and EA do) gave the explorer the settings default. A 401 auto-retry could then sign in again as that default user.
  - With no token, the explorer uses only a password the caller itself holds. If the caller has neither, the answer is
    "unknown" and Egeria isn't called.
  - The token is shared bare. Before, the `"Bearer ..."` header value was set as the token, which gave `"Bearer
    Bearer ..."`.
  - A caller without real `view_server` and `platform_url` strings (a fake, or anything that isn't a client) gets
    "unknown". No client is built.
  - The explorer is closed after the read.
