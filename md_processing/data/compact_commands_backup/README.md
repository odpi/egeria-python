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

-   **LocationArena**: All `.json` files in `md_processing/data/compact_commands/` are scanned.
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

#### Alternate Names Guidance

When providing `alternate_names` for a command, it is recommended to specify **only the object part** of the command (e.g., `"Solution Component"` instead of `"Link Solution Component"`).

Dr. Egeria automatically expands these names using the **verb family** of the primary command. For example, if a command is in the `Link` family (which includes `Link`, `Attach`, `Add`, `Unlink`, `Detach`, `Remove`), providing `"Solution Component"` as an alternate name will automatically allow all of the following:
- `Link Solution Component`
- `Attach Solution Component`
- `Add Solution Component`
- `Unlink Solution Component` (if the command supports the Unlink verb family)
- etc.

If you specify a full phrase like `"Attach Solution Component"`, the system will still extract the object part and apply the verb expansion logic, but specifying just the object is cleaner and more standard.

### Maintenance and Best Practices

- **Avoid Hardcoding Logic**: Do not add special-purpose logic to parsers or processors to accommodate specification errors. If an attribute should be optional (e.g., `Display Name` for technical links), update the `input_required` flag in the relevant `attribute_definition` or `bundle`.
- **Inheritance vs Redundancy**: Leverage `bundles` to manage common attributes. If a property is missing across a command family, check if it should be added to a base bundle (like `Link Command Base`) rather than individual commands.
- **Test Before Emit**: Use the `validate_compact_json.py` script to ensure that changes to the specification do not break inheritance chains or cross-references.

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

## Validation

A validation script is provided to ensure the integrity and quality of the compact specifications:
- `md_processing/md_processing_utils/validate_compact_json.py`: This script checks for duplicate keys, missing mandatory attributes (`style`, `variable_name`), empty descriptions, and broken cross-references (unknown attributes or bundles).

To run the validation:
```bash
python3 md_processing/md_processing_utils/validate_compact_json.py
```
or using `uv`:
```bash
uv run python md_processing/md_processing_utils/validate_compact_json.py
```
It is recommended to run this script whenever new attributes, bundles, or commands are added or modified.
