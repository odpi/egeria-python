# pyegeria gaps and issues

Running log of gaps/rough edges found *in the `pyegeria` library itself*
(not this app's handler code) while building out the Portal test strategy.
Entries here are candidates for upstream fixes — **do not act on any of
these against the pyegeria repo without explicit approval**; this file is
the tracking mechanism, not an authorization to patch.

Status values: `logged` (found, not yet reviewed) · `approved` (owner said
fix it) · `fixed-upstream` (patched in pyegeria) · `wont-fix` (owner decided
against it, reason noted).

---

## 1. `PyegeriaAPIException` is a catch-all; typed subclasses exist but aren't raised for it

**Status:** fixed-upstream (2026-07-31). `_async_make_request` in
`_base_server_client.py` now branches on `related_http_code` and raises
`PyegeriaNotFoundException` (404) / `PyegeriaUnauthorizedException`
(401/403) instead of the generic `PyegeriaAPIException` for those cases.
Both exception classes were re-parented from `PyegeriaException` to
subclass `PyegeriaAPIException` (with `__init__` calling
`PyegeriaException.__init__` directly, bypassing
`PyegeriaAPIException.__init__`'s `response.json()` call, since these two
are also now raised for bare HTTP error responses with no JSON body — see
item #6) so all 63 existing `except PyegeriaAPIException` handlers found
across the codebase keep working unchanged. Also updated
`tests/functional-tests/test_client.py`'s `meow`/401 case, which now
correctly expects `PyegeriaUnauthorizedException` instead of the generic
`PyegeriaClientException`. Verified: `pytest tests/ -m unit` and
`tests/functional-tests/test_client.py` both clean (same 2 pre-existing,
unrelated live-server failures as baseline).

**Regression found and fixed post-merge (2026-07-31):** the owner hit
`AttributeError: 'PyegeriaNotFoundException' object has no attribute
'related_http_code'` running the `automated_curation` and
`product_manager` scenario test suites — existing code (correctly) does
`except PyegeriaAPIException as e: if e.related_http_code == 404`, but
bypassing `PyegeriaAPIException.__init__` (to avoid its unconditional
`response.json()` call) also skipped the one line that sets
`self.related_http_code`. Fixed by setting it explicitly in both
subclasses' `__init__`: prefer `additional_info.get("relatedHTTPCode")`
(the Egeria-wrapped-200 case), falling back to the response's real HTTP
status code (the bare-HTTP-error case). Verified against the exact
reported scenario (`get_digital_product_by_guid` on a deleted product) and
re-ran both scenario suites — `product_manager` fully green,
`automated_curation`'s one remaining failure is the unrelated, already-
tracked "no catalog template registered" server gap.

**What:** `pyegeria.core._exceptions` defines `PyegeriaNotFoundException` and
`PyegeriaUnauthorizedException` as distinct exception classes, but
`_base_server_client.py`'s `_async_make_request` never actually raises them.
Every "Egeria wrapped an error in an HTTP 200 response" case (Egeria's own
`relatedHTTPCode` pattern — auth failures, not-found, etc.) raises the
generic `PyegeriaAPIException` instead, regardless of what `relatedHTTPCode`
says. Callers have to inspect `.related_http_code` at runtime to tell a 401
from a 404 from a 500-from-Egeria.

**Where seen:** `egeria_error_mapping.py` (this repo) — had to build the
whole mapper around `.related_http_code`/`.response_code` inspection instead
of a clean `except PyegeriaNotFoundException` / `except
PyegeriaUnauthorizedException`, specifically because those classes are
defined-but-dead.

**Candidate fix:** in `_async_make_request`, when constructing
`PyegeriaAPIException`, branch on `related_http_code` and raise
`PyegeriaNotFoundException`/`PyegeriaUnauthorizedException` (etc.) instead
of the generic class where a specific one already exists.

---

## 2. `httpx.InvalidURL` isn't wrapped

**Status:** fixed-upstream (2026-07-31). Confirmed the underlying mechanism
was real (`user_id` is embedded raw into URL paths in several places, e.g.
`pyegeria/omvs/server_operations.py`'s `.../users/{self.user_id}/status`,
with no URL-encoding), but empirically the exact symptom didn't quite match
the original report: a bad `user_id` today gets caught by
`_async_make_request`'s bare `except Exception` and wrapped as
`PyegeriaUnknownException` — not a fully raw/uncaught `httpx.InvalidURL`,
but also not a helpful, specific type.

Added a shared `_validate_url_path_safe(value, param_name)` check in
`_validators.py` (rejects ASCII control characters and URL-structural
characters `/ ? # \` plus whitespace) and wired it into both
`validate_server_name` and `validate_user_id`. `validate_server_name` was
already called in both `_base_platform_client.py` and
`_base_server_client.py`'s constructors, so `server_name` was fixed for
free; `user_id` was never validated in either constructor at all (only
null/empty-checked deep inside one unrelated method), so added an explicit
call there too. Now raises `PyegeriaInvalidParameterException` immediately
at construction time, naming the exact bad character, instead of
surfacing however-many method calls later as a generic exception. Verified
live: a `user_id` with an embedded null byte now fails at construction
with a clear message; normal construction and `test_client.py`'s
`meow`/`woof` 401/404 cases unaffected.

**What:** A non-printable character in a caller-supplied `server`/`user_id`
param (reaching pyegeria's client construction) causes a raw
`httpx.InvalidURL` to propagate — not one of pyegeria's own exception types.
Every other client-construction failure path in `_base_server_client.py`
wraps things into `PyegeriaConnectionException`/`PyegeriaInvalidParameterException`;
this one specific path doesn't.

**Where seen:** Schemathesis fuzzing `server`/`user_id` query params on
`/api/collections/*` and `/api/projects/*` (this repo's
`tests/test_schema_fuzz.py`) surfaced it directly.

**Candidate fix:** catch `httpx.InvalidURL` in the same place other
constructor validation errors get wrapped, and re-raise as
`PyegeriaInvalidParameterException`.

---

## 3. Malformed `as_of_time` reaches pydantic as a raw `ValidationError`

**Status:** fixed-upstream (2026-07-31). Scope turned out bigger than
originally reported: `as_of_time` is inherited by the whole get/find/search
model family (`GetRequestBody` and its ~4 subclasses), and I counted 51
`.model_validate(...)`/`.validate_python(...)` call sites in
`_server_client.py` sharing the same unguarded-validation pattern — not
just the 2 sites named here. Rather than patch only those 2, added a
generic `ServerClient._validate_body(validator, body)` static helper
(handles both the `self._xxx_adapter.validate_python` and
`SomeModel.model_validate` call shapes uniformly, since both are just
callables taking the raw dict) that catches `pydantic.ValidationError` and
re-raises as `PyegeriaInvalidParameterException` naming the offending
field(s) via `additional_info["validation_errors"]`. Mechanically routed
all 49 active call sites (2 were already commented out) through it.
Live-verified: `as_of_time="null"` now raises a clear
`PyegeriaInvalidParameterException` citing the `asOfTime` field, instead of
a raw `pydantic_core.ValidationError`; confirmed normal valid requests are
unaffected (`pytest tests/ -m unit` clean, plus a live `find_collections`
call still returns results normally).

**What:** Passing a non-datetime string (e.g. the literal `"null"`) as
`as_of_time` propagates all the way to a `pydantic_core.ValidationError`
when pyegeria builds the internal `SearchStringRequestBody`/`GetRequestBody`
model — not caught or translated by pyegeria itself.

**Where seen:** same Schemathesis run as #2, fuzzing the `as_of_time` query
param on `/api/projects*`.

**Candidate fix:** validate/parse `as_of_time` at the pyegeria client-method
boundary (before building the request body) and raise
`PyegeriaInvalidParameterException` on failure, consistent with how other
malformed inputs are handled elsewhere in the same file.

---

## 4. `pyegeria.core.mcp_server` is pinned to a stale `mcp` package API, can't be imported, and this repo forked it instead of extending it

**Status:** wont-fix (2026-07-31) — already correct at HEAD. Confirmed
`pyegeria/core/mcp_server.py` in this repo already imports
`from mcp.server.mcpserver import MCPServer` (the current API) and imports
cleanly with `mcp==2.0.0` installed in this repo's venv
(`python3 -c "from pyegeria.core import mcp_server"` succeeds). The
`ModuleNotFoundError` described below was observed against a **different,
stale installed pyegeria wheel** inside the separate `quickstart-pyegeria-web`
container, not this dev tree. No code change needed here — if that
container is still on an old pyegeria version, that's a
deployment/versioning fix needed in that project, not an egeria-python
code fix.

**What:** `pyegeria/core/mcp_server.py` does
`from mcp.server.fastmcp.exceptions import ValidationError` and
`from mcp.server.fastmcp import FastMCP`, both of which come from an older
`mcp` package API. This container runs `mcp>=2.0.0`, where `FastMCP` was
renamed/relocated to `mcp.server.mcpserver.MCPServer`. As a result,
`pyegeria.core.mcp_server` **cannot be imported at all** in this
environment:

```
ModuleNotFoundError: No module named 'mcp.server.fastmcp'
```

Consequence: this repo's own `PyegeriaWebHandler/mcp_server.py` had to be
written against the new `mcp` API from scratch (`from mcp.server.mcpserver
import MCPServer, Context`) rather than importing and extending pyegeria's
server object with its own Dr.Egeria-specific tools. Its four report-facing
tools (`list_reports`, `find_report_specs`, `describe_report`, `run_report`)
don't reimplement report logic — they call straight into
`pyegeria.core.mcp_adapter`, the same module pyegeria's own (broken) server
uses — but the `MCPServer` construction and `@server.tool()` registration
for those four tools is now duplicated across two files instead of living
in one. That's a standing drift risk: if `mcp_adapter`'s signatures or
pyegeria's own tool registration change, nothing enforces this repo's
hand-written wrappers staying in sync.

**Where seen:** direct inspection of
`/usr/local/lib/python3.12/site-packages/pyegeria/core/mcp_server.py`
inside `quickstart-pyegeria-web`, prompted by comparing it against this
repo's local `mcp_server.py` after fixing an unrelated bug in the latter
(module-level `EGERIA_ROOT_PATH`/`EGERIA_INBOX_PATH` constants captured at
import time — see `mcp_server.py`'s inline comment, 2026-07-31).

**Candidate fix:** update `pyegeria/core/mcp_server.py` to the current `mcp`
package API (`mcp.server.mcpserver.MCPServer` in place of
`mcp.server.fastmcp.FastMCP`, and whatever the corresponding
`ValidationError`/`Context` import paths are now). Once that's done, this
repo's `mcp_server.py` could import pyegeria's server object directly and
register only the Dr.Egeria-specific tools onto it, eliminating the
duplicated `MCPServer` construction and the four hand-wired report-tool
wrappers.

---

## 5. `get_collection_members` silently drops non-Collection members when `body` is omitted

**Status:** fixed-upstream (2026-07-31). `_type` was overloaded in
`_async_get_results_body_request` for two purposes — genuine results
filtering (correct for most of its ~30 callers, e.g. "attached comments are
always type Comment") vs. a pure output-rendering hint (wrong only for
`_async_get_collection_members`'s `/{guid}/members` endpoint, since a
collection's members are never guaranteed to share its own type). Rather
than dropping the default filter for all callers (risking the ~29 that
correctly rely on it), added an explicit `filter_results_by_type: bool =
True` parameter (default preserves existing behavior everywhere) and set
it `False` only at the one confirmed-broken call site. Checked
`get_collection_hierarchy` (same file, same `_type="Collection"` default)
separately — its endpoint's own docs say "return a hierarchy of nested
collections," so that filter is legitimate and was left unchanged. Also
added `"body"` to the `"Collection Members"` FormatSet's `optional_params`
in `base_report_formats.py` (confirmed this FormatSet isn't Dr.Egeria-
compact-command-derived, safe to hand-edit) so report callers can still
pass a fully custom body. Live-verified against the exact golden anchor
from the original report (`WorkItemList` guid
`0affb580-fa81-4d00-9438-b26faf11845d`) — now correctly returns all 5
`Project`-typed members instead of an empty list.

**What:** `pyegeria/core/_server_client.py`'s `_async_get_results_body_request`
builds a default request body when the caller passes `body=None`, and that
default hardcodes `metadataElementTypeName=_type` (here `_type="Collection"`,
from `CollectionManager.get_collection_members`'s internal call). That field
filters the **returned members**, not the collection being queried — so any
collection whose members aren't themselves `Collection`-typed (e.g. a
`WorkItemList` whose members are `Project` entities) comes back with an
empty member list, even though the collection genuinely has members.

**Where seen:** user ran the "Collection Members" report (Reports screen,
Egeria Explorer) against guid `0affb580-fa81-4d00-9438-b26faf11845d` (the
same `WorkItemList` used as a golden anchor throughout this test-strategy
work, confirmed via `GET /api/collections/{guid}` to have exactly 5
`Project`-typed members) and got an empty list. Traced to
`pyegeria/view/base_report_formats.py:2058-2072`'s `"Collection Members"`
`FormatSet` — its `ActionParameter` doesn't list `body` in
`optional_params`, so `format_set_executor.py` never passes one, always
hitting the default-body branch. By contrast, this repo's own
`collections_handler.py:204-209` passes an explicit
`body={"class": "ResultsRequestBody", "graphQueryDepth": 0}` (no
`metadataElementTypeName` key) for the same underlying call, which is why
`/api/collections/{guid}` returns the correct 5 members for this exact
guid.

**Candidate fix:** either (a) stop hardcoding `metadataElementTypeName=_type`
in the default-body branch of `_async_get_results_body_request` — a
collection's *members* aren't guaranteed to share the collection's own
type — or (b) add `"body"` to the `"Collection Members"` FormatSet's
`optional_params`/`spec_params` in `base_report_formats.py` so callers (like
the Reports screen) can override the default and get unfiltered members,
matching what `collections_handler.py` already does correctly.

---

## 6. Expired/invalid bearer token: no specific exception, no auto-renew

**Status:** fixed-upstream (2026-07-31). Raised during review of item #1
(same file/method), not originally in this log — connects directly to
`BACKLOG.md`'s "Bearer token expires mid-run on long `dr_egeria --process`
batches" (2026-07-08).

**What:** confirmed via direct repro against `qs-view-server`: a bad/expired
bearer token returns a bare HTTP 401 with an **empty response body** — no
JSON, nothing to distinguish "expired" from "wrong credentials" from
"insufficient permission." Nothing previously re-authenticated or retried
on this; every subsequent call in a long batch would just keep failing once
the token expired.

**Fix:** `_async_make_request`'s `except (HTTPStatusError, ...)` branch now
treats any 401 as a candidate for "the token might be stale" — if the
client holds stored credentials, it calls the already-existing
`_async_create_egeria_bearer_token()` once and retries the original request
once before giving up. Default-on, no opt-out flag; at most one retry ever
(guarded by an internal `_retry_on_auth` parameter).

**Bonus bug found and fixed while implementing this:**
`_async_create_egeria_bearer_token()` (both the `BaseServerClient` and
`BasePlatformClient` copies) sent the token-creation POST request with
`headers=self.headers` — which still carries the stale/expired
`Authorization` header being replaced. The `/api/token` endpoint rejects
requests with a bad Authorization header outright (confirmed via direct
curl repro), so the refresh call itself always 401'd, silently defeating
the whole mechanism (both the pre-existing manual-call use case and this
new auto-retry). Fixed to send a plain `Content-Type`-only header for this
one request.

**Verified live:** corrupted a real client's `Authorization` header,
issued a real API call, confirmed exactly one auto-retry occurred and the
call succeeded transparently with a freshly-obtained token. Also confirmed
`tests/functional-tests/test_client.py`'s `meow`/401 case and `pytest tests/
-m unit` are unaffected beyond the expected exception-type change (see
item #1).

---

*(Add new entries above this line as they're found. Keep the format:
status, what, where seen, candidate fix — so entries are self-contained
enough to hand to whoever eventually reviews/fixes them upstream.)*
