<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# tests/micro-tests/my_profile

Tests for the `MyProfileApp` Textual TUI in
`my_egeria/my_egeria/DemoCode/My_Profile/` — not the `pyegeria.omvs.my_profile`
OMVS client, which is covered in `tests/functional-tests/`.

The suite runs two ways from the same test code.

```bash
# Fake backend (default) — no server needed, nothing is written anywhere
pytest tests/micro-tests/my_profile/

# Live backend — real Egeria at https://localhost:9443
PYEG_LIVE_EGERIA=1 pytest tests/micro-tests/my_profile/

# Just the tests that actually switch
PYEG_LIVE_EGERIA=1 pytest tests/micro-tests/my_profile/ -m live_capable
```

## ⚠️ Live mode writes to your Egeria instance

Live mode is not read-only. It really does create digital subscriptions,
really does initiate a governance action process, and really would create a
personal profile if the configured user did not already have one. Point it at
a development instance, not anything you care about.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `PYEG_LIVE_EGERIA` | unset (fake) | `1`/`true`/`yes`/`on` switches the suite to the live backend |
| `PYEG_PLATFORM_URL` | `https://localhost:9443` | Egeria platform URL |
| `PYEG_SERVER_NAME` | `qs-view-server` | View server name |
| `PYEG_USER_ID` | `garygeeke` | User to authenticate as |
| `PYEG_USER_PWD` | `secret` | Password |

In live mode these are also exported as `EGERIA_PLATFORM_URL` /
`EGERIA_VIEW_SERVER` / `EGERIA_USER` / `EGERIA_USER_PASSWORD` during
`pytest_configure`, so the app's own `load_app_config()` resolves to the same
server. That has to happen before collection finishes, because `load_app_config()`
caches on first call.

If `PYEG_LIVE_EGERIA=1` is set but the server will not issue a bearer token,
every live-capable test skips with the reason. The server is probed once per
session, so an unreachable server costs a fraction of a second rather than a
screenful of connection errors.

## Fake mode never touches the network

An autouse fixture blocks `httpx` for the whole folder whenever
`PYEG_LIVE_EGERIA` is off, so a fake-mode test that leaves an Egeria call
unmocked fails immediately:

```
UnexpectedNetworkCall: test_foo tried to reach https://localhost:9443/... while
running against fakes. Patch the Egeria client/function through the `backend`
fixture (backend.patch / backend.always_fake), or mark the test
`@pytest.mark.allow_network` if the call is genuinely intended.
```

This is what keeps the suite consistent. Before the guard existed, four tests
quietly reached a real server in "fake" mode — usually because the behaviour
under test was mocked but something *adjacent* was not (entering
`MyProfileApp.run_test()` runs `on_mount`, which builds a real `MyProfile`
client regardless of what the test itself patched). Those tests passed on a
machine with a server running and behaved differently on one without.

`stub_profile_client()` in `test_my_profile_app.py` is the helper for that
specific case: any test that enters `app.run_test()` should call it.

## How the switch works

`egeria_backend.py` provides the `backend` fixture. The important method is
`backend.patch(target, returns=...)`:

- **fake mode** — replaces `target` with `MagicMock(return_value=returns)`
- **live mode** — replaces it with `MagicMock(wraps=<the real object>)`, so the
  call reaches Egeria *and* the mock still records it

Because a wrapping mock records calls, assertions about **how** the app called
Egeria (report-spec names, params, verbs) are written once and hold in both
modes. Only assertions about the returned **data** need to differ, and those go
through `backend.expect(actual, fake=..., live=<predicate>)`: exact equality
against the fixture in fake mode, a structural check in live mode.

Other helpers:

| Helper | Use |
|---|---|
| `backend.always_fake(target, ...)` | Paths a live server cannot produce on demand — injected exceptions, deliberately empty result sets. These test the app's own error handling, so they stay faked in both modes. |
| `backend.unique(name)` | Suffixes a name with a random hex in live mode only. Egeria enforces `qualifiedName` uniqueness, so a live write test reusing a fixed name passes once and then 409s forever. |
| `backend.apply_connection(app)` | Points a `Dummy*App` test harness at the active backend. |
| `backend.patch_object(cls, attr, repl)` | Non-Egeria patching (UI widgets) — same in both modes. |

Live-only fixtures discover real inputs from the server rather than using
synthetic GUIDs, and skip with a specific reason when the server has no
suitable data: `live_my_profile`, `live_team_role_name`, `live_tech_type_name`,
`live_catalog_template`.

## Adding a test that touches Egeria

1. Take the `backend` fixture and mark the test `@pytest.mark.live_capable`.
2. Replace `@patch("module.symbol")` with
   `backend.patch("module.symbol", returns=<fake payload>)`.
3. Keep call-args assertions unconditional; route value assertions through
   `backend.expect(...)`.
4. If the test needs a specific element to exist, add a live-discovery fixture
   rather than hardcoding a GUID.
5. If the path is an injected error or an empty result, use
   `backend.always_fake(...)` and leave the `live_capable` marker off.
6. If the test enters `MyProfileApp.run_test()`, call `stub_profile_client(...)`
   so `on_mount`'s profile load is mocked too.

The network guard will tell you if you miss one.

## Known live-mode outcomes

- `test_create_profile_screen_create_profile` **skips** live when the configured
  user already has a profile. `add_my_profile` creates the profile for the
  *calling* user and the server rejects a second one
  (`OMVS-MY-PROFILE-400-001`), so the path is only reachable for a user who has
  none yet.
- `test_tech_type_templates_callback_success` **creates a real metadata element**
  from a real catalog template on every live run, and deliberately does not
  clean it up — the target is a disposable test instance that gets reloaded from
  scratch regularly, so teardown would add failure modes for no benefit. If you
  ever do need to prune, search display names for the `pytest-` prefix.

## What live mode has caught so far

Worth knowing, because it is the argument for running live periodically.
`tech_type_templates_callback` had three stacked defects that full mocking hid
completely — the mocked `AutomatedCuration` accepted a nonexistent method called
with a malformed body built from keys that do not exist:

1. it called `initiate_gov_action_process(body=...)`, which takes
   `action_type_qualified_name` and has no `body` parameter → `TypeError`;
2. it read `full_template.get("Catalog Template GUID")`, a key that appears
   neither in the server payload nor anywhere in the codebase → `templateGUID`
   was always `None`;
3. it sent `replacementProperties: {}`, which the server rejects with
   *"missing type id property 'class'"* — the field must be absent.

All three are fixed in `tech_types_handler.py`. The lesson for new tests: an
assertion against a `MagicMock` proves the app called *something*, not that it
called the right thing with a body the server accepts.
