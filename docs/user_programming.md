<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# pyegeria Programming Guide

This guide provides an overview of how to use the `pyegeria` Python library to interact with Egeria.

## Core Concepts

`pyegeria` is designed around a set of client classes that correspond to Egeria's Open Metadata View Services (OMVS). These clients handle communication with the Egeria platform, authentication, and provide high-level Pythonic APIs for working with metadata.

### The Client Hierarchy

1.  **`BaseServerClient`**: The foundation class that manages the `httpx` session, authentication headers, and core request/response logic.
2.  **`ServerClient`**: Extends `BaseServerClient` with Egeria-specific patterns like GUID resolution, qualified name creation, and request body validation using Pydantic models.
3.  **OMVS Clients**: Individual classes for each Egeria service (e.g., `GlossaryManager`, `AssetCatalog`, `DataDesigner`). These contain the actual business logic.
4.  **Role-Based Facades**: Convenient entry points that group multiple OMVS clients by user role (e.g., `EgeriaTech`, `EgeriaCat`).

## Configuration System

`pyegeria` features a centralized configuration system that allows you to set defaults for all clients in one place.

### Configuration Precedence

When a client is initialized, it resolves its settings (like `platform_url` or `user_id`) using the following precedence:

1.  **Explicit Arguments**: Values passed directly to the class constructor.
2.  **Environment Variables**: OS environment variables (prefixed with `PYEGERIA_` or as standard Egeria names).
3.  **`.env` File**: Variables defined in a `.env` file in the current working directory.
4.  **`config.json`**: A JSON configuration file.
5.  **Built-in Defaults**: Hardcoded safe defaults.

### Common Configuration Variables

| Variable | Description |
| :--- | :--- |
| `EGERIA_PLATFORM_URL` | The base URL of your Egeria platform. |
| `EGERIA_VIEW_SERVER` | The name of the View Server to use. |
| `EGERIA_USER` | The default user ID for authentication. |
| `EGERIA_USER_PASSWORD` | The password for the default user. |
| `EGERIA_LOCAL_QUALIFIER` | A prefix used when generating `qualifiedNames`. |

### Setup Example

**`.env` file:**
```bash
EGERIA_PLATFORM_URL=https://localhost:9443
EGERIA_VIEW_SERVER=view-server
EGERIA_USER=erinoverview
EGERIA_USER_PASSWORD=secret
EGERIA_LOCAL_QUALIFIER=PDR
```

## Using the Clients

### Automatic Initialization

Because of the centralized configuration, you can often initialize a client without any arguments if your environment is set up:

```python
from pyegeria import EgeriaTech

# Automatically picks up server, url, user, etc. from configuration
client = EgeriaTech()

# Create a bearer token (uses credentials from config)
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

## Naming Conventions and Helpers

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

## Advanced Usage

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

## Error Handling

`pyegeria` defines a hierarchy of exceptions in `pyegeria.core._exceptions`. It is recommended to catch `PyegeriaException` for general error handling:

```python
from pyegeria.core._exceptions import PyegeriaException

try:
    client.create_glossary(name="ExistingGlossary")
except PyegeriaException as e:
    print(f"An error occurred: {e}")
```
