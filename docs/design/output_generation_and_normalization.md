# Design Document: Output Generation and Parameter Normalization

## Overview

This document describes the refactored approach for generating formatted output (Markdown, DICT, HTML, etc.) in `pyegeria`. It addresses inconsistencies between "Find" methods (using `search_string`) and "Get" methods (using `filter_string`), and ensures consistent handling of `**kwargs` across the output pipeline.

## Problem Statement

Historically, different OMVS managers implemented their own output generation wrappers. This led to several issues:
1.  **Duplicate Logic**: Code for resolving report specifications and dynamically discovering additional property methods was duplicated across dozens of files.
2.  **Parameter Mismatch**: "Find" methods use `search_string` (substring match), while "Get" methods use `filter_string` (exact match). Many output formatters expected one or the other, causing `TypeError` when called via generic request helpers.
3.  **Built-in Shadowing**: Frequent bugs occurred where the Python built-in `filter` function was accidentally passed instead of a `filter_string` parameter.
4.  **Kwargs Inconsistency**: `**kwargs` were not consistently passed through to the underlying `generate_output` function, making it difficult to pass rendering flags.

## Solution: Centralized Formatting Pipeline

The solution introduces a centralized "glue" method in the `ServerClient` base class and standardizes the signatures of manager-level generators.

### 1. The Centralized Wrapper: `_generate_formatted_output`

LocationArena: `pyegeria/core/_server_client.py`

This method acts as the single entry point for all formatting needs. It performs the following tasks:
- **Format Resolution**: Uses `resolve_output_formats` to pick the correct report spec based on `entity_type`, `output_format`, and `report_spec`.
- **Dynamic Method Discovery**: Inspects the resolved report spec for a `get_additional_props` function. If found, it dynamically binds the method from the current manager instance (e.g., `_extract_term_additional_properties`).
- **Query Normalization**: Normalizes the input query string using a priority-based fallback: explicit `query_string` -> `search_string` -> `filter_string`.
- **Safe Kwargs Handling**: Forwards `**kwargs` to the underlying formatter while cleaning up redundant keys to avoid "multiple values for keyword argument" errors.

### 2. Standardized Manager Generators

Manager-level generator methods (e.g., `_generate_collection_output`) are refactored to be thin wrappers around the centralized method.

**New Signature Pattern:**
```python
def _generate_something_output(
    self, 
    elements: dict | list[dict], 
    query_string: Optional[str] = None,
    element_type_name: Optional[str] = None, 
    output_format: str = "DICT",
    report_spec: dict | str = None, 
    **kwargs
) -> str | list[dict]:
    return self._generate_formatted_output(
        elements=elements,
        query_string=query_string,
        entity_type=element_type_name or "DefaultType",
        output_format=output_format,
        extract_properties_func=self._extract_specific_properties,
        report_spec=report_spec,
        **kwargs
    )
```

### 3. Output Formatter Enhancements

LocationArena: `pyegeria/view/output_formatter.py`

- `generate_output` now accepts `**kwargs`.
- It handles parameter normalization internally: if `search_string` is `None`, it attempts to retrieve it from `kwargs.get('filter_string')`. This ensures that even direct calls remain robust.

## Master-Detail Pattern and Recursive Formatting

The output system has been extended to support complex metadata hierarchies through a Master-Detail pattern and recursive formatting.

### 1. Master-Detail Definition
Report specifications (`FormatSet`) can now define columns with a `detail_spec` attribute. This attribute points to another named report specification that should be used to render the nested elements associated with that column.

### 2. Supported Formats
- **REPORT (Markdown)**: Renders a vertical section for each detail column, recursively calling the formatter.
- **LIST (Markdown Table)**: Displays a compact summary in the main table row and appends a linked detail section below the table.
- **DICT**: Includes nested lists of formatted dictionaries, matching the detail specification.
- **TABLE (CLI)**: Draws the structured table: nested collections by the column's render intent, sub-tables as
  separate tables after the main one.

### 3. Recursive Formatting Control: `include_preamble`
To prevent redundant report headers when the formatter calls itself recursively, `generate_output` now accepts an `include_preamble` boolean (default `True`). This flag is automatically disabled for recursive detail calls.

### 4. Smart Summarization
When rendering nested collections in horizontal formats (`LIST` and CLI `TABLE`), the system draws them by the column's render intent (names joined, bullets, key–values) instead of just providing a count (e.g., "Team A, Team B" instead of "2 items"); past `max_items` it says "+N more".

### 5. Native values, rendered at the edge (6.2.37)

Values used to be stringified while an element was read (`populate_common_columns` joined relationships into
"a, b", classifications into "A, B" and zones into "a, b"), so every output type, DICT included, started from
strings. Since 6.2.37 extraction keeps a **native layer** beside each column's text:

- related elements as `{guid, qualifiedName, displayName, type}` (`related_ref`);
- classifications as `{name, properties?}`, zones as a list;
- property values as they come (lists stay lists).

Each column dict carries the native value under `native` and the text under `value`. The text is derived from the
native value by one function, `_legacy_text` (qualifiedName first, or the display name when the column sets
`label: display_name`), so the default outputs are byte-identical to what they were.

Renderers choose which to read:

- the default DICT/TABLE rows and the text outputs read `value` (the flat text);
- `dict_shape="native"` DICT rows and the structured TABLE (`table_shape="structured"`,
  `pyegeria/view/structured_table.py`) read `native`;
- LIST cells and the CLI's Rich table draw lists, maps and related elements from `native` by the column's render
  intent (`markdown_cell_from_native`, `run_report.render_structured_table`).

The shape is carried into a find method's own generator by a context variable (`dict_shape_for_call`), so no OMVS
signature changed. What each list request sent (page size, graph depth, relationship filters) is recorded per call
in another context variable (`recording_list_requests`), never on the shared client: the executor reads it to say
"more may exist" when a page was full, and to tell an empty relationship that was read ("none") from one that was
not requested ("not read"). See "Complex values" in `docs/output-formats-and-report-specs.md`.

## Unified Execution Pipeline

The `format_set_executor.py` (`exec_report_spec` and `_async_run_report`) has been refactored to use the centralized `generate_output` pipeline for all narrative formats. This ensures that features like master-detail and smart summarization are consistently available whether calling SDK methods directly or executing report specs through CLI tools.

### Runtime Safety in Report Execution

- **Missing `target_type`**: If a resolved report spec has `target_type = None`, the executor logs a warning and falls back to `Referenceable` to keep LIST/REPORT rendering stable.
- **Validation Errors**: Pydantic `ValidationError` exceptions raised during request/body coercion are printed via `print_validation_error` and then re-raised for upstream handling.

## Search vs Filter Semantics

- **Find Methods**: Use `search_string`. These typically perform substring or regex matching on the server.
- **Get Methods**: Use `filter_string`. These typically perform exact value matching on specific properties.
- **In Output**: The distinction is primarily for the preamble/header of the generated report. The centralized pipeline ensures that whichever string was used to fetch the data is the one displayed in the "Search criteria" or "Filter" section of the output.

## Handling Kwargs

- **Pass-through**: `**kwargs` are forwarded from the initial manager call -> `_async_find_request` (or similar) -> Output Generator -> `_generate_formatted_output` -> `generate_output`.
- **Usage**: Extra kwargs are accepted and selectively consumed by the formatter/executor (for example `report_spec`, filter/search aliases, and formatting flags). Unknown kwargs remain non-breaking and are ignored by layers that do not use them.

## Migration Guide for New Managers

When adding a new OMVS manager:
1. Define your property extractor (e.g., `_extract_my_entity_properties`).
2. Implement a thin `_generate_my_entity_output` method using the centralized `_generate_formatted_output`.
3. Ensure all string parameters in your generator have default values of `None`.
4. Use keyword arguments when calling the generator from your `find_*` or `get_*` methods.
