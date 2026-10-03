# Hand-off: wire the `my_egeria` app into Egeria-Workspaces

Audience: maintainers of the **egeria-workspaces** repo.
Goal: expose the main **MyEgeria** Textual app in the portal (browser) and keep
it runnable in a terminal, alongside the existing `my_profile` app.

This is the same integration pattern already used for `my_profile` (see
`EGERIA_WORKSPACES_INTEGRATION.md` for the full design rationale). This file
lists only what is **new** and what egeria-workspaces must add/change.

---

## What changed in egeria-python (already done)

| Item | Value |
|------|-------|
| New app | **MyEgeria** (full app, not the `my_profile` demo) |
| App module | `my_egeria.my_egeria_app` (renamed from `my_egeria.my_egeria` to avoid a package/module name collision) |
| Terminal entry point | `my_egeria` → `my_egeria.main:main` |
| Browser entry point | `serve_my_egeria` → `my_egeria.serve:serve_my_egeria` |
| Listen host env | `MY_EGERIA_HOST` (default `0.0.0.0`) — shared by all served apps |
| Listen port env | `MY_EGERIA_PORT` (default `8021`) |

Both entry points are installed by `pip install pyegeria` (no separate package).
`serve_my_egeria` serves the app with the `textual-serve` library (a pyegeria
dependency — no `textual` CLI or `textual-dev` needed); each browser WebSocket
connection gets its own isolated app instance — no code difference between
terminal and browser modes.

**Requires a pyegeria release with the 2026-10 packaging fix.** Earlier wheels
installed the app one level too deep (`site-packages/my_egeria/my_egeria/...`), so
the `my_egeria`, `my_profile`, `serve_my_egeria` and `serve_my_profile` commands
failed in every pip install. The app now installs as the top-level `my_egeria`
package (`site-packages/my_egeria/...`). Anything that launched the app by **file
path** under the old nested layout must switch to the entry points.

**Use Python 3.13, not 3.14.** Textual (6.1.0 through the current 8.2.8) fails on
Python 3.14 with `assert task is not None` in `textual/rlock.py`; My Profile hits
it at startup. Build the image on `python:3.13-slim`.

### Port allocation (current)

| App        | Port | Serve entry point  |
|------------|------|--------------------|
| my_profile | 8020 | `serve_my_profile` |
| my_egeria  | 8021 | `serve_my_egeria`  |
| *(next)*   | 8022 |                    |

---

## What egeria-workspaces needs to do

### 1. Confirm the base image has current pyegeria

The image used for the Textual app services must have a pyegeria build that
includes the `serve_my_egeria` entry point and the `my_egeria_app` module rename.
If the image pins an older pyegeria, bump it. Do not pin an older `textual`;
let pyegeria's own dependency choose it. No extra packages are needed: `textual`
and `textual-serve` come with pyegeria.

### 2. Add a compose service (quickstart)

Copy the existing `my-profile` block in `egeria-quickstart.yaml` and change the
command, ports, and port env var:

```yaml
  my-egeria:
    image: python:3.12-slim          # or the shared pyegeria base image
    container_name: quickstart-my-egeria
    working_dir: /app
    command: serve_my_egeria         # entry point installed by pyegeria
    networks:
      - egeria_network
    ports:
      - "8021:8021"                  # host port : container port
    environment:
      EGERIA_PLATFORM_URL:  "https://host.docker.internal:9443"
      EGERIA_VIEW_SERVER:   "qs-view-server"
      EGERIA_USER:          "${QUICKSTART_PERSONA_USER:-erinoverview}"
      EGERIA_USER_PASSWORD: "${QUICKSTART_PERSONA_PASSWORD:-secret}"
      MY_EGERIA_HOST:       "0.0.0.0"
      MY_EGERIA_PORT:       "8021"
    depends_on:
      egeria-main:
        condition: service_healthy
```

For **freshstart**, use the same block but omit `EGERIA_USER` /
`EGERIA_USER_PASSWORD` so the app's own login screen prompts for credentials
(Option A in `EGERIA_WORKSPACES_INTEGRATION.md`). Per-session process spawning
(Option B) is unchanged and still deferred.

### 3. Add an nginx / proxy route

WebSocket upgrade headers are **required** (textual serve uses WebSockets):

```nginx
location /my-egeria/ {
    proxy_pass http://my-egeria:8021/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
}
```

### 4. Add a portal button (Egeria-Workspaces-Web)

```html
<a href="/my-egeria/" target="_blank" class="portal-card">
  MyEgeria
</a>
```

Use the proxied path `/my-egeria/` (not a raw `localhost:8021`), and
`target="_blank"` for a new tab or an `<iframe>` for embedded mode.

---

## Required env vars (unchanged)

These are read by pyegeria config from OS env, with priority over any config
file. They must be present in the `my-egeria` service environment:

| Variable               | Example (quickstart)                | Notes                           |
|------------------------|-------------------------------------|---------------------------------|
| `EGERIA_PLATFORM_URL`  | `https://host.docker.internal:9443` | Egeria platform REST endpoint   |
| `EGERIA_VIEW_SERVER`   | `qs-view-server`                    | View server name                |
| `EGERIA_USER`          | `erinoverview`                      | Active persona (quickstart)     |
| `EGERIA_USER_PASSWORD` | `secret`                            | Password (quickstart)           |
| `MY_EGERIA_HOST`       | `0.0.0.0`                           | Listen host for textual-serve   |
| `MY_EGERIA_PORT`       | `8021`                              | Listen port for textual-serve   |
| `MY_EGERIA_PUBLIC_URL` | `https://<site>/my-egeria`          | Where the app is published behind a proxy. Only its **path** (and default scheme) is used: the host follows each browser's own address (from `X-Forwarded-Host`/`Host`), so one setting works for localhost, the machine name and a demo hostname. `MY_PROFILE_PUBLIC_URL` is the My Profile equivalent; `MY_EGERIA_PUBLIC_URL` is used for either app if the app's own is not set. |

---

## Verifying the hand-off

1. **Terminal:** `my_egeria` launches the TUI (the startup check now uses the
   same `EGERIA_*` variables and defaults as the table below).
2. **Local browser:** `MY_EGERIA_PORT=8021 serve_my_egeria`, then open
   `http://localhost:8021/`.
3. **Through the portal:** the `/my-egeria/` route loads the app and the
   WebSocket connects (check browser dev-tools network tab for a `101 Switching
   Protocols` on the WS request).

If the app loads but cannot reach Egeria, recheck `EGERIA_PLATFORM_URL` /
`EGERIA_VIEW_SERVER` and that the service is on `egeria_network`.

---

## Notes / gotchas

- The app module was renamed `my_egeria.my_egeria` → `my_egeria.my_egeria_app`.
  egeria-workspaces should **not** reference the module path or a file path
  directly — only the `serve_my_egeria` / `serve_my_profile` / `my_egeria` entry
  points, which are stable. (The packaging fix above moved the installed files.)
- If you template the compose service, keep one `MY_*_PORT` per app; only
  `MY_EGERIA_HOST` is shared.
- "Adding more apps" recipe lives in `EGERIA_WORKSPACES_INTEGRATION.md`
  (egeria-python side: add `serve_<app>()` + entry point; workspaces side:
  compose service + proxy route + portal button).
