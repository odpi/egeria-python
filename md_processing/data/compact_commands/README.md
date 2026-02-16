# Compact Command Specifications

This directory contains refactored, compact JSON specifications for Dr. Egeria commands. These specifications are designed to eliminate duplication and provide a more maintainable way to define the attributes and behaviors of metadata commands.

## Strategy and Approach

The "Compact" format moves away from the flat, redundant structure of the legacy `commands.json` towards a normalized, hierarchical model.

### Key Concepts

1.  **Attribute Definitions**: Standardized definitions for every metadata attribute used across commands. This includes data types, descriptions, cardinality, and UI styles.
2.  **Bundles**: Groups of attributes that represent common Egeria types or reusable patterns (e.g., `Referenceable`, `Glossary Base`). Bundles can **inherit** from other bundles, creating a hierarchy that mimics the Egeria Open Metadata Type System.
3.  **Commands**: Specific operations (e.g., `Create Glossary`, `Update Project`) that reference a **base bundle** and optionally add **custom attributes**.

### Advantages

-   **Single Source of Truth**: Attributes are defined once and reused everywhere.
-   **Reduced Maintenance**: Changes to a common attribute (like a description or validation rule) automatically propagate to all commands using it.
-   **Type Safety**: Mimics the Egeria type hierarchy, ensuring consistency between the client and the platform.
-   **Readability**: Command definitions are much smaller and focus on what makes the command unique.

## How it Works

### Loading Mechanism

The `md_processing` library automatically detects and loads these files during initialization:

-   **Location**: All `.json` files in `md_processing/data/compact_commands/` are scanned.
-   **Global Resolution**: Attribute and bundle definitions are gathered from **all** files in the directory before commands are expanded. This allows a command in one file to use a bundle defined in another (e.g., a Glossary command referencing the `Referenceable` bundle defined in a base file).
-   **Preferential Use**: Commands defined in these compact files take precedence over any commands with the same name in the legacy `commands.json`. This allows for a gradual, file-by-file migration.

### Configuration

The behavior can be controlled via constants in `md_processing/md_processing_utils/md_processing_constants.py`:

-   `USE_COMPACT_RESOURCES`: (Boolean) Enable/disable loading compact specs. Defaults to `True`.
-   `COMPACT_RESOURCE_DIR`: The path to this directory.
-   `COMPACT_FAMILIES`: A list of command families to load. If empty, all families found in the directory are loaded.

## JSON Structure

### 1. Attribute Definitions
The `attribute_definitions` map contains the full metadata for each attribute.
```json
"attribute_definitions": {
  "Qualified Name": {
    "variable_name": "qualified_name",
    "description": "Unique identifier for the element.",
    "style": "Simple",
    "input_required": true,
    "min_cardinality": 1,
    "max_cardinality": 1,
    "level": "Basic"
  }
}
```

### 2. Bundles
Bundles organize attributes and support single inheritance.
```json
"bundles": {
  "Referenceable": {
    "own_attributes": ["Qualified Name", "Additional Properties"]
  },
  "Asset Base": {
    "inherits": "Referenceable",
    "own_attributes": ["Display Name", "Description"]
  }
}
```

### 3. Commands
Commands compose bundles and custom attributes to define an operation.
```json
"commands": {
  "Create Asset": {
    "verb": "Create",
    "family": "Asset Manager",
    "bundle": "Asset Base",
    "custom_attributes": ["Owner"]
  }
}
```

## Adding New Commands

To add or refactor commands into the compact format:

1.  Create a new JSON file in this directory (e.g., `commands_my_service_compact.json`).
2.  Add any new `attribute_definitions` required for your service.
3.  Define or reuse `bundles` to capture the common structure.
4.  Add the `commands` themselves, referencing the bundles.
5.  Restart the application; the system will automatically pick up the new file and merge it into the active command set.

## Implementation Details

The core logic for parsing and expanding these specifications resides in:
- `md_processing/md_processing_utils/parse_compact_export.py`: Handles JSON parsing, inheritance resolution, and expansion. It includes a robust loader that handles minor JSON syntax issues (like trailing commas or unescaped quotes in nested strings) often found in exports.
- `md_processing/md_processing_utils/compact_loader.py`: Orchestrates directory-wide loading and conversion to legacy schema.
