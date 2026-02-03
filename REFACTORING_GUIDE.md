# Find Methods Refactoring Guide

## Overview

This guide documents the refactoring of find methods across the pyegeria codebase to use the **kwargs pattern, simplifying method signatures while maintaining full functionality.

## Completed Work

### Phase 1: Core Implementation ✅
- **File**: `pyegeria/core/_server_client.py`
- **Methods Refactored**: 3
  - `_async_find_tags` / `find_tags`
  - `_async_find_search_keywords` / `find_search_keywords`
  - `_async_find_assets` / `find_assets`

### Phase 2: Feedback Methods Migration ✅
- **Migrated**: 6 methods (likes and ratings) from `feedback_manager.py` to `_server_client.py`
- **Tests**: Created `tests/test_server_client.py`
- **Dependencies**: Updated 5 files to use deprecated import path

## The Pattern

### Before (25+ parameters)
```python
async def _async_find_xxx(
    self,
    search_string: str = "*",
    starts_with: bool = True,
    ends_with: bool = False,
    ignore_case: bool = False,
    anchor_domain: Optional[str] = None,
    metadata_element_type: Optional[str] = None,
    metadata_element_subtypes: Optional[list[str]] = None,
    skip_relationships: Optional[list[str]] = None,
    include_only_relationships: Optional[list[str]] = None,
    skip_classified_elements: Optional[list[str]] = None,
    include_only_classified_elements: Optional[list[str]] = None,
    graph_query_depth: int = 3,
    governance_zone_filter: Optional[list[str]] = None,
    as_of_time: Optional[str] = None,
    effective_time: Optional[str] = None,
    relationship_page_size: int = 0,
    limit_results_by_status: Optional[list[str]] = None,
    sequencing_order: Optional[str] = None,
    sequencing_property: Optional[str] = None,
    output_format: str = "JSON",
    report_spec: Optional[str] = None,
    start_from: int = 0,
    page_size: int = 100,
    property_names: Optional[list[str]] = None,
    body: Optional[dict] = None
) -> list | str:
    response = await self._async_find_request(
        url, _type="Type", _gen_output=self._generate_output,
        search_string=search_string,
        starts_with=starts_with,
        ends_with=ends_with,
        # ... 20+ more parameters ...
    )
    return response
```

### After (9 parameters + **kwargs)
```python
async def _async_find_xxx(
    self,
    search_string: str = "*",
    body: Optional[dict | SearchStringRequestBody] = None,
    starts_with: bool = True,
    ends_with: bool = False,
    ignore_case: bool = False,
    start_from: int = 0,
    page_size: int = 100,
    output_format: str = "JSON",
    report_spec: Optional[str | dict] = None,
    **kwargs
) -> list | str:
    """
    [Existing description]
    
    Parameters
    ----------
    search_string : str, default "*"
        String to search for.
    body : dict | SearchStringRequestBody, optional
        Request body. If provided, overrides other parameters.
    starts_with : bool, default True
        Match at start of string.
    ends_with : bool, default False
        Match at end of string.
    ignore_case : bool, default False
        Case-insensitive search.
    start_from : int, default 0
        Starting index for pagination.
    page_size : int, default 100
        Number of results per page.
    output_format : str, default "JSON"
        Output format.
    report_spec : str | dict, optional
        Report specification.
    **kwargs : dict, optional
        Additional parameters:
        - anchor_domain : str - Domain to anchor search
        - metadata_element_type : str - Specific element type
        - metadata_element_subtypes : list[str] - Element subtypes
        - skip_relationships : list[str] - Relationships to skip
        - include_only_relationships : list[str] - Relationships to include
        - skip_classified_elements : list[str] - Classifications to skip
        - include_only_classified_elements : list[str] - Classifications to include
        - classification_names : list[str] - Filter by classifications
        - graph_query_depth : int - Graph traversal depth (default 3)
        - governance_zone_filter : list[str] - Governance zones filter
        - as_of_time : str - Historical query time (ISO 8601)
        - effective_time : str - Effective time (ISO 8601)
        - relationship_page_size : int - Page size for relationships
        - limit_results_by_status : list[str] - Status filter
        - sequencing_order : str - Result ordering
        - sequencing_property : str - Property for sequencing
        - property_names : list[str] - Properties to search
    
    Returns
    -------
    list | str
        Results in requested format.
    
    Raises
    ------
    PyegeriaException
        Communication, format, or Egeria errors.
    """
    # Build params dict with explicit parameters
    params = {
        'search_string': search_string,
        'starts_with': starts_with,
        'ends_with': ends_with,
        'ignore_case': ignore_case,
        'start_from': start_from,
        'page_size': page_size,
        'output_format': output_format,
        'report_spec': report_spec,
        'body': body
    }
    # Merge with kwargs, removing None values
    params.update(kwargs)
    params = {k: v for k, v in params.items() if v is not None}
    
    response = await self._async_find_request(
        url, _type="Type", _gen_output=self._generate_output, **params
    )
    return response
```

## Remaining Work

### Files to Refactor (35+ methods across 20 files)

1. **actor_manager.py** - 5 methods
   - `_async_find_actor_profiles` (line 720)
   - `_async_find_actor_roles` (line 2314)
   - `_async_find_user_identities` (line 3955)
   - `_async_find_contribution_records` (line 4885)
   - `_async_find_contact_details` (line 5816)

2. **asset_catalog.py** - 1 method
   - `_async_find_in_asset_domain` (line 119)

3. **asset_maker.py** - 1 method
   - `_async_find_assets` (line 716)

4. **automated_curation.py** - 1 method
   - `_async_find_engine_actions` (line 2231)

5. **collection_manager.py** - 1 method
   - `_async_find_collections` (line 285)

6. **community_matters_omvs.py** - 1 method
   - `_async_find_communities` (line 194)

7. **data_designer.py** - 3 methods
   - `_async_find_data_structures` (line 812)
   - `_async_find_data_fields` (line 2434)
   - `_async_find_data_classes` (line 4010)

8. **data_discovery.py** - 1 method
   - `_async_find_annotations` (line 531)

9. **data_engineer.py** - 1 method
   - `_async_find_tabular_data_sets` (line 64)

10. **external_links.py** - 1 method
    - `_async_find_external_references` (line 1189)

11. **glossary_manager.py** - 2 methods
    - `_async_find_glossaries` (line 2680)
    - `_async_find_glossary_terms` (line 2993)

12. **governance_officer.py** - 1 method
    - `_async_find_governance_definitions` (line 1826)

13. **location_arena.py** - 1 method
    - `_async_find_locations` (line 964)

14. **metadata_explorer_omvs.py** - 4 methods
    - `_async_find_metadata_elements_with_string` (line 930)
    - `_async_find_elements_for_anchor` (line 1109)
    - `_async_find_elements_in_anchor_domain` (line 1284)
    - `_async_find_elements_in_anchor_scope` (line 1460)

15. **project_manager.py** - 1 method
    - `_async_find_projects` (line 458)

16. **schema_maker.py** - 1 method
    - `_async_find_schema_types` (line 178)

17. **solution_architect.py** - 4 methods
    - `_async_find_information_supply_chains` (line 1764)
    - `_async_find_solution_blueprints` (line 3173)
    - `_async_find_solution_components` (line 4582)
    - `_async_find_solution_roles` (line 5974)

18. **subject_area.py** - 1 method
    - `_async_find_subject_areas` (line 704)

19. **time_keeper.py** - 1 method
    - `_async_find_context_events` (line 1423)

20. **valid_metadata.py** - 1 method
    - `_async_find_specification_property` (line 2569)

## Using the Refactoring Script

### Dry Run (Recommended First)
```bash
# Analyze all OMVS modules
python refactor_find_methods.py --dry-run

# Analyze specific file
python refactor_find_methods.py --dry-run --file pyegeria/omvs/actor_manager.py

# Analyze specific module directory
python refactor_find_methods.py --dry-run --module pyegeria/omvs
```

### Live Refactoring
```bash
# Refactor specific file
python refactor_find_methods.py --file pyegeria/omvs/actor_manager.py

# Refactor all files
python refactor_find_methods.py
```

## Manual Refactoring Steps

For each method:

1. **Update Async Method Signature**
   - Keep 9 explicit parameters
   - Add `**kwargs` at the end
   - Update type hints

2. **Update Implementation**
   - Create params dict with explicit parameters
   - Merge with kwargs
   - Filter None values
   - Pass **params to _async_find_request

3. **Update Documentation**
   - Add **kwargs section to docstring
   - List all possible kwargs parameters
   - Include type hints and descriptions

4. **Update Sync Method**
   - Update signature to match async version
   - Pass parameters using keyword arguments
   - Include **kwargs in call

5. **Test**
   - Run existing tests
   - Verify backward compatibility
   - Test with kwargs parameters

## Benefits

1. **Cleaner Signatures**: 9 explicit params + **kwargs vs 25+ params
2. **Flexibility**: Advanced users can pass all parameters
3. **Maintainability**: Easier to add parameters to _async_find_request
4. **Consistency**: Same pattern across all find methods
5. **Documentation**: Comprehensive **kwargs documentation
6. **Type Safety**: Explicit params maintain IDE support

## Testing

After refactoring each module:

```bash
# Run module-specific tests
pytest tests/test_<module_name>.py -v

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=pyegeria --cov-report=html
```

## Version Control

Recommended commit strategy:

```bash
# After each module
git add pyegeria/omvs/<module_name>.py
git commit -m "refactor: apply **kwargs pattern to <module_name> find methods"

# After testing
git add tests/
git commit -m "test: update tests for <module_name> refactoring"
```

## Progress Tracking

- [x] _server_client.py (3 methods)
- [x] Feedback methods migration (6 methods)
- [x] Test and dependency updates
- [ ] actor_manager.py (5 methods)
- [ ] asset_catalog.py (1 method)
- [ ] asset_maker.py (1 method)
- [ ] automated_curation.py (1 method)
- [ ] collection_manager.py (1 method)
- [ ] community_matters_omvs.py (1 method)
- [ ] data_designer.py (3 methods)
- [ ] data_discovery.py (1 method)
- [ ] data_engineer.py (1 method)
- [ ] external_links.py (1 method)
- [ ] glossary_manager.py (2 methods)
- [ ] governance_officer.py (1 method)
- [ ] location_arena.py (1 method)
- [ ] metadata_explorer_omvs.py (4 methods)
- [ ] project_manager.py (1 method)
- [ ] schema_maker.py (1 method)
- [ ] solution_architect.py (4 methods)
- [ ] subject_area.py (1 method)
- [ ] time_keeper.py (1 method)
- [ ] valid_metadata.py (1 method)

**Total**: 3/38 methods completed (8%)

## Notes

- The refactoring script (`refactor_find_methods.py`) provides analysis and can be extended for automated refactoring
- Manual review is recommended for each change
- Backward compatibility is maintained through **kwargs
- All existing code continues to work without modification