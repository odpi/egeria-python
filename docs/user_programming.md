<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# pyegeria Programming Guide

This guide provides an overview of how to use the `pyegeria` Python library to interact with Egeria.

### Core Concepts

`pyegeria` is designed around a set of client classes that correspond to Egeria's Open Metadata View Services (OMVS). These clients handle communication with the Egeria platform, authentication, and provide high-level Pythonic APIs for working with metadata.

### The Client Hierarchy

1.  **`BaseServerClient`**: The foundation class that manages the `httpx` session, authentication headers, and core request/response logic.
2.  **`ServerClient`**: Extends `BaseServerClient` with Egeria-specific patterns like GUID resolution, qualified name creation, and request body validation using Pydantic models.
3.  **OMVS Clients**: Individual classes for each Egeria service (e.g., `GlossaryManager`, `AssetCatalog`, `DataDesigner`). These contain the actual business logic.
4.  **Role-Based Facades**: Convenient entry points that group multiple OMVS clients by user role (e.g., `EgeriaTech`, `EgeriaCat`).

### Configuration System

`pyegeria` features a centralized configuration system that allows you to set defaults for all clients in one place. **You do not need to call any configuration function explicitly for the common case** — configuration is loaded automatically the first time a client is instantiated.

### How Configuration Loads

Under the hood, `config.py` exposes a module-level `settings` proxy. When any client (e.g. `EgeriaTech`) is instantiated, its `__init__` accesses `settings.Environment.egeria_platform_url` and similar values. That first access triggers a lazy load of the full configuration from your environment and config files.

The load order (highest wins):
1.  **Explicit constructor arguments** — values passed directly override everything.
2.  **OS environment variables** — take priority over config file values.
3.  **`.env` file** — loaded from the current working directory (or the path in `PYEGERIA_ROOT_PATH`).
4.  **`config.json`** — a JSON configuration file located via `PYEGERIA_ROOT_PATH` / `PYEGERIA_CONFIG_FILE`.
5.  **Built-in defaults** — hardcoded safe fallbacks.

Once loaded, the configuration is cached for the lifetime of the process — subsequent client instantiations reuse it without re-reading files.

### Common Configuration Variables

| Variable | Description |
| :--- | :--- |
| `EGERIA_PLATFORM_URL` | The base URL of your Egeria platform. |
| `EGERIA_VIEW_SERVER` | The name of the View Server to use. |
| `EGERIA_USER` | The default user ID for authentication. |
| `EGERIA_USER_PASSWORD` | The password for the default user. |
| `EGERIA_LOCAL_QUALIFIER` | A prefix used when generating `qualifiedNames`. |
| `PYEGERIA_ROOT_PATH` | Directory where `config.json` and `.env` are located. |
| `PYEGERIA_CONFIG_FILE` | Override the config filename (default: `config.json`). |

### Setup Examples

**Default case — no code required.**  
Place a `.env` in your **working directory** (where you run the script from, not necessarily where the script file lives) or set OS environment variables, then just instantiate a client:

```bash
# .env
EGERIA_PLATFORM_URL=https://localhost:9443
EGERIA_VIEW_SERVER=view-server
EGERIA_USER=erinoverview
EGERIA_USER_PASSWORD=secret
EGERIA_LOCAL_QUALIFIER=PDR
```

```python
from pyegeria import EgeriaTech

# Config is loaded automatically on first instantiation
client = EgeriaTech()
client.create_egeria_bearer_token()
assets = client.list_assets()
```

**Providing explicit credentials** — config still loads for any unspecified values:

```python
from pyegeria import EgeriaTech

client = EgeriaTech(user_id="IvorPadlock", user_pwd="secret")
client.create_egeria_bearer_token()
```

**Custom `.env` file** — the only case where an explicit call is needed.  
Call `load_app_config` *before* any client is instantiated, otherwise the auto-load will already have run:

```python
from pyegeria import load_app_config, EgeriaTech

load_app_config(env_file="/path/to/my-project.env")

client = EgeriaTech()
client.create_egeria_bearer_token()
```

**Inspecting the active configuration** — useful for debugging:

```python
from pyegeria import pretty_print_config

pretty_print_config()  # prints a table showing each value and its source
```

**Accessing config values directly in code:**

```python
from pyegeria import get_app_config

cfg = get_app_config()
print(cfg.Environment.egeria_platform_url)
print(cfg.User_Profile.user_name)
```

### Using the Clients

### Automatic Initialization

Because of the centralized configuration, you can often initialize a client without any arguments if your environment is set up:

```python
from pyegeria import EgeriaTech

# Automatically picks up server, url, user, etc. from configuration
client = EgeriaTech()

## Create a bearer token (uses credentials from config)
client.create_egeria_bearer_token()

# Use any of the available methods
assets = client.list_assets()
```

### Role-Based Facade Clients

For most users, the role-based facade clients are the easiest way to start:

-   **`EgeriaTech`**: For technical users (data engineers, scientists). Includes `AssetCatalog`, `DataDesigner`, `GlossaryManager`, and more.
-   **`EgeriaCat`**: For catalog-oriented tasks. Combines `AssetCatalog`, `GlossaryManager`, `ProjectManager`, and `MyProfile`.
-   **`EgeriaConfig`**: For platform and server configuration.
-   **`EgeriaOps`**: For operational monitoring and management.

### Lazy Loading

The facade clients use **lazy loading**. Sub-clients (like `GlossaryManager` inside `EgeriaTech`) are only instantiated when you first access a method or attribute belonging to them. This keeps the initial footprint small.

```python
client = EgeriaTech()
# GlossaryManager is NOT yet instantiated

client.list_glossaries()
# GlossaryManager is now instantiated and cached
```

### Naming Conventions and Helpers

### Qualified Names

In Egeria, most elements require a unique `qualifiedName`. `pyegeria` provides a helper method `__create_qualified_name__` (available on all OMVS clients) to help generate these consistently.

```python
# Generates "PDR::Glossary::My-New-Glossary" 
# (assuming EGERIA_LOCAL_QUALIFIER=PDR)
qname = client.__create_qualified_name__("Glossary", "My New Glossary")
```

The helper:
1.  Prepends the `local_qualifier` (if set).
2.  Uses the provided type name.
3.  Cleans the display name (strips whitespace, replaces spaces with hyphens).

### Advanced Usage

### Direct OMVS Client Usage

You can also use individual OMVS clients directly if you only need a specific service:

```python
from pyegeria.omvs.glossary_manager import GlossaryManager

# Still supports automatic configuration
glossary_client = GlossaryManager()
```

### Async API

Most methods have an underlying asynchronous implementation (prefixed with `_async_`). While the public API is generally synchronous for ease of use in scripts and notebooks, you can use the async versions if building an asynchronous application:

```python
import asyncio
from pyegeria import EgeriaTech

async def main():
    client = EgeriaTech()
    client.create_egeria_bearer_token()
    
    # Use the async variant
    assets = await client._async_find_in_asset_domain("*")
    print(assets)

asyncio.run(main())
```

### Long-Running Sessions

Applications that keep a pyegeria client alive for extended periods — Jupyter notebooks, portal servers, scheduled jobs, or any process that runs longer than a few minutes — will encounter two challenges if left unaddressed: **idle-connection expiry** and **bearer-token expiry**.

#### Connection management

The httpx session underlying every pyegeria client is configured with:

| Setting | Value | Why |
| :--- | :--- | :--- |
| `keepalive_expiry` | 20 s | Retires idle connections before a typical reverse proxy (nginx/Caddy default: 60–75 s) closes them server-side. Without this, a long-idle connection silently dies and the next request fails with a timeout or protocol error. |
| `connect` timeout | 10 s | Distinguishes a refused/unreachable host from a slow-but-alive one quickly. |
| `max_keepalive_connections` | 5 | Limits open idle sockets to avoid resource exhaustion in server processes hosting many clients. |

These settings are transparent to application code; they apply automatically to every client instance. If you are deploying behind a proxy with a non-standard idle timeout, you can create your own client subclass and override the `AsyncClient` constructor.

#### Automatic token refresh

When an Egeria-issued bearer token expires, the server returns HTTP 401. The client detects this and automatically calls `_async_refresh_egeria_bearer_token()` once, then retries the failed request transparently.

This only works for tokens created by pyegeria itself (via `create_egeria_bearer_token()`). Tokens supplied externally via `set_bearer_token()` are not auto-refreshed; the caller is responsible for renewing them before they expire and calling `set_bearer_token()` again.

```python
# Egeria-issued token: auto-refreshed on 401
client = EgeriaTech()
client.create_egeria_bearer_token()

# External token: caller manages expiry
client2 = EgeriaTech()
client2.set_bearer_token(my_token)
# When my_token expires, call set_bearer_token() again with a fresh one
```

#### Async applications — avoid `create_egeria_bearer_token()` inside coroutines

The sync `create_egeria_bearer_token()` method calls `asyncio.get_event_loop().run_until_complete(...)` internally. Calling it from within a running async context (FastAPI route, async Jupyter cell, etc.) raises `RuntimeError: This event loop is already running`.

Use the async variant instead:

```python
# In a FastAPI route or any async function:
async def make_client():
    client = EgeriaTech()
    await client._async_create_egeria_bearer_token()
    return client
```

If you are building a FastAPI service that creates a fresh client per request, the pattern is:

```python
from egeria_auth import async_apply_token  # if using egeria-workspaces

async def _get_client():
    client = EgeriaTech()
    await async_apply_token(client)   # applies X-Egeria-Token from request context, or fetches a fresh one
    return client

@app.get("/my-endpoint")
async def my_endpoint():
    client = await _get_client()
    ...
```

See `egeria-workspaces/PyegeriaWebHandler/egeria_auth.py` for the reference implementation.

### Error Handling

`pyegeria` defines a hierarchy of exceptions in `pyegeria.core._exceptions`. It is recommended to catch `PyegeriaException` for general error handling:

```python
from pyegeria.core._exceptions import PyegeriaException

try:
    client.create_glossary(name="ExistingGlossary")
except PyegeriaException as e:
    print(f"An error occurred: {e}")
```

| Exception class | When raised |
| :--- | :--- |
| `PyegeriaTimeoutException` | Request exceeded the `time_out` parameter (default 30 s) or the 10 s connect timeout. |
| `PyegeriaConnectionException` | Host is unreachable or refused the connection. |
| `PyegeriaClientException` | Server returned a 4xx status (including 401 after auto-refresh failed). |
| `PyegeriaAPIException` | Server returned 200/201 but the inner `relatedHTTPCode` indicates an error. |
| `PyegeriaUnknownException` | Unexpected exception during the request. |
