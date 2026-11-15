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
  This replaces the password scrub and `_get_subclient` patch that token-only callers needed. **`user_pwd=None` is
  unchanged**: it still takes the configured password, which CLIs rely on.

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

- **`AuthoringRefused.answer`** (pyegeria.authoring): every refusal now carries a machine-readable `answer`, which is
  `"absent"` (Egeria holds no such artifact that you can see, said only on a confirmed end), `"unknown"` (whether
  Egeria holds it couldn't be told; never to be read as "none") or `"refused"` (anything else, the default).
  `ANSWER_ABSENT`, `ANSWER_UNKNOWN` and `ANSWER_REFUSED` are exported. Branch on `answer`, not on the words. It's
  backward compatible: `AuthoringRefused` is still a `ValueError`, and its words are unchanged.
