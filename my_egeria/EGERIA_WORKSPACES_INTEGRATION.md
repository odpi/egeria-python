# my_egeria integration into egeria-workspaces

Design notes for what needs to be implemented in the egeria-workspaces repo
to host my_egeria Textual apps as browser-accessible tools via the portal.

> **Per-app hand-offs:** for the concrete, copy-paste steps to wire a specific
> app, see the `HANDOFF_egeria_workspaces_*.md` files. The main MyEgeria app is
> in `HANDOFF_egeria_workspaces_my_egeria.md`.

---

## How it works

`textual serve` turns any Textual app into a browser app — each WebSocket
connection gets its own isolated app instance. The portal button simply links
to the app's URL (new tab or iframe). No code difference between terminal and
browser modes; the same installed app serves both.

---

## Required env vars (consumed by pyegeria config)

All of these are already read by `load_app_config()` from OS env vars with
priority over any config file. They must be present in the compose environment
for each my_egeria service.

| Variable               | Example (quickstart)              | Notes                              |
|------------------------|-----------------------------------|------------------------------------|
| `EGERIA_PLATFORM_URL`  | `https://host.docker.internal:9443` | Egeria platform REST endpoint     |
| `EGERIA_VIEW_SERVER`   | `qs-view-server`                  | View server name                   |
| `EGERIA_USER`          | `erinoverview`                    | Active persona / logged-in user    |
| `EGERIA_USER_PASSWORD` | `secret`                          | Password for that user             |

For the **quickstart** environment these are fixed per persona and set at
compose startup. For **freshstart** they must be set per logged-in user
(see Session management below).

---

## Compose service — quickstart

Add one service per Textual app to `egeria-quickstart.yaml`.
`my_profile_app` is the first; additional apps follow the same pattern.

```yaml
  my-profile:
    image: python:3.12-slim          # or a shared pyegeria base image
    container_name: quickstart-my-profile
    working_dir: /app
    command: serve_my_profile        # entry point installed by pyegeria
    networks:
      - egeria_network
    ports:
      - "8020:8020"                  # host port : container port
    environment:
      EGERIA_PLATFORM_URL:  "https://host.docker.internal:9443"
      EGERIA_VIEW_SERVER:   "qs-view-server"
      EGERIA_USER:          "${QUICKSTART_PERSONA_USER:-erinoverview}"
      EGERIA_USER_PASSWORD: "${QUICKSTART_PERSONA_PASSWORD:-secret}"
      MY_EGERIA_HOST:       "0.0.0.0"
      MY_PROFILE_PORT:      "8020"
    depends_on:
      egeria-main:
        condition: service_healthy
```

`QUICKSTART_PERSONA_USER` / `QUICKSTART_PERSONA_PASSWORD` can be set in the
quickstart `.env` file so the persona is baked in at stack startup.

### Port allocation (proposed)

| App             | Port | Serve entry point   |
|-----------------|------|---------------------|
| my_profile      | 8020 | `serve_my_profile`  |
| my_egeria       | 8021 | `serve_my_egeria`   |
| *(next app)*    | 8022 |                     |

---

## Compose service — freshstart

The freshstart environment has real user credentials that differ per session.
Two approaches, in order of complexity:

### Option A — Single instance, app handles login (simplest, do this first)
Same compose block as quickstart but without `EGERIA_USER` / `EGERIA_USER_PASSWORD`
in the environment. The Textual app's existing login screen (`CreateProfileScreen`)
prompts the user for credentials in the browser. No portal changes needed.

### Option B — Per-session process spawning (proper multi-user)
The portal's login flow calls a small management API that:
1. Spawns `textual serve --port <dynamic-port> serve_my_profile` with the
   authenticated user's credentials as env vars.
2. Returns the URL to the portal, which opens it.
3. Cleans up (kills the process) on session logout / timeout.

This requires a lightweight process manager service in the freshstart compose
stack. Implementation deferred until Option A is validated.

---

## Nginx / proxy routing

To avoid exposing raw ports, route through the existing nginx proxy so the
portal can link to paths rather than port numbers:

```nginx
# In httpd.conf / proxy.yml
location /my-profile/ {
    proxy_pass http://my-profile:8020/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";  # required for WebSocket
    proxy_set_header Host $host;
}
```

The WebSocket upgrade headers are **required** — textual serve uses WebSockets.

The portal button then links to `/my-profile/` instead of `localhost:8020`.

---

## Portal button wiring (Egeria-Workspaces-Web)

Each portal card/button for a my_egeria app needs:
- A link target of `/my-profile/` (or the proxied path)
- `target="_blank"` to open in a new tab, or an `<iframe>` for embedded mode

```html
<a href="/my-profile/" target="_blank" class="portal-card">
  My Profile
</a>
```

For persona selection: the portal's persona picker sets
`QUICKSTART_PERSONA_USER` in the `.env` file (or via a management endpoint)
before the stack starts, or restarts the `my-profile` service with the new
env var if hot-switching is needed.

---

## Dockerfile / base image

The compose service above uses `python:3.12-slim`. In practice, use a shared
base image that has `pyegeria` (and therefore `my_egeria`) already installed:

```dockerfile
FROM python:3.12-slim
RUN pip install pyegeria          # installs my_egeria and all entry points
```

Or reuse the existing `Dockerfile-jupyter` / `Dockerfile-egeria-platform`
build if those already have pyegeria installed — just add the `serve_my_profile`
command as a new service pointing at the same image.

---

## Adding more apps

When additional Textual apps are ready:

1. Add a `serve_<app>()` function to `my_egeria/serve.py` in egeria-python.
2. Add the `serve_<app>` entry point to `pyproject.toml`.
3. Add a compose service in egeria-workspaces (copy the `my-profile` block,
   change port and entry point).
4. Add a proxy route in nginx.
5. Add a portal button.
