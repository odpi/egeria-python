# Egeria Python — Backlog

Consolidated work list. Update status when items start or finish.
Status: `open` · `in-progress` · `done` · `deferred`

---

## 🟡 Medium Priority — ServerClient missing async comment methods

**Status:** open
**Added:** 2026-07-02

`tests/functional-tests/test_comments.py` has 9 failing tests, all `AttributeError` on `pyegeria.core._server_client.ServerClient` for methods that don't exist: `async_add_comment_to_element`, `async_add_comment_reply`, `async_update_comment`, `async_setup_accepted_answer`, `async_setup_clear_answer`, `async_remove_comment_from_element`, `async_get_comment_by_guid`, `async_get_attached_comments`, `async_find_comments`.

Confirmed pre-existing and unrelated to Dr.Egeria command work — same 9 failures occur with or without changes to `md_processing/data/compact_commands/`. Run `pytest tests/functional-tests/test_comments.py -m unit` to reproduce.

**Fix:** Either implement the missing `async_*` comment methods on `ServerClient` (if comment support was intended to live there), or update the tests to target wherever comment methods actually live now (possibly moved to a different client class during a refactor).

---

## 🟢 Low Priority — Produced Guards has no valid values constraint

**Status:** open
**Added:** 2026-07-02

The new `Produced Guards` attribute (`Action Author` family, on `Governance Action Type Base` bundle — used by `Create Governance Action Type` / `Create Governance Action Process Step`) is a `Simple List` of strings with no `valid_values` constraint. Unlike `Domain Identifier`-style Enum attributes (which list every allowed value in `valid_values`, e.g. `ALL;DATA;PRIVACY;...`), guard names are process-author-defined labels rather than a fixed global enum, so there's no universal list to seed it with today.

**Future validation idea:** once real governance action processes exist with real guard names in use, consider whether `Produced Guards` values should be validated against something more specific than free text — e.g. cross-checked against the `Guard`/`Next Governance Action Process Step` relationship attributes actually declared in the same process, so a typo'd guard name that never matches a real transition gets caught at validate time instead of silently producing a dead-end step. Not blocking Phase 1 or Phase 2 — flagging so it isn't forgotten once there's real usage data to design the check against.

---

## 🟡 Medium Priority — SalesForecast regression fixtures need a baseline seed sequence

**Status:** open
**Added:** 2026-07-02

47 of the failures across `tests/dr-egeria-command-tests/dr_test_*.md` (validate mode) are all the same root cause: `Referenced element 'X' ... not found`, where `X` is a specific named element from a "SalesForecast" demo scenario (a pipeline, a master collection, an agreement, glossary terms, a governance zone) plus a couple of similar campaigns ("Clinical Trials Management", "Sustainability"). Confirmed directly against the live server (`localhost:9443`) that zero `SalesForecast` elements currently exist — `client.find_collections('SalesForecast')` returns "No elements found".

This means the `Create` commands that would establish this baseline dataset are scattered across several of the `dr_test_*.md` files rather than living together, and nothing has actually run them in `--process` mode against this server (or the server was reset since they last were). Every `Link`/`Attach`/`Detach`/`Unlink` command elsewhere that references one of those named elements by qualified name fails to resolve it.

**Fix:** collect up the `Create` commands that establish the SalesForecast baseline (and the couple of campaign elements), work out the correct dependency order, and either (a) run them once in `--process` mode against whichever server these fixtures are meant to run against, or (b) consolidate them into a dedicated seed file that `run_dr_tests.py` (or a setup step before it) runs first. Not blocking Action Author Phase 1/2 — pre-existing gap, unrelated to those commands.

---

## 🟡 Medium Priority — Bearer token expires mid-run on long `dr_egeria --process` batches

**Status:** open
**Added:** 2026-07-08

Running `dr_egeria <100+ command file> --process` against `localhost:9443` (e.g. the generated `dr-egeria-help-*.md`, ~100+ commands) took ~1h20m end to end and started failing every remaining command with HTTP 401 partway through — the bearer token created at the start of the run expired before the run finished, and nothing re-authenticates or refreshes it mid-batch. Confirmed directly in `logs/pyegeria.log`: the "Create Risk" term's `_async_create_element_body_request` call at 23:12:14 got a 401 (`Client error '401' for url .../glossary-manager/glossaries/terms`), as did every command after it in that run (~6+ trailing Solution Architect `Link` commands all failed the same way). Re-running the single "Create Risk" term in isolation (a few seconds) succeeded immediately with the same credentials — confirming it's a token-lifetime/duration issue, not a bad request or bad credentials.

**Fix:** either (a) proactively refresh/recreate the bearer token partway through a long batch (e.g. every N commands or every N minutes) inside the v2 dispatcher's command loop, or (b) on a 401 mid-batch, transparently re-authenticate and retry the failed command once before surfacing it as a failure. Without one of these, any `--process` run over enough commands to exceed the token's lifetime will silently corrupt the back half of a large Glossary/help-doc sync — as happened here for the regenerated `dr-egeria-help-2026-07-07T20:51:10.md` run.
