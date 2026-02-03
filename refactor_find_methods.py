#!/usr/bin/env python3
"""
Automated refactoring script to apply **kwargs pattern to find methods.

This script:
1. Identifies find methods that use _async_find_request
2. Simplifies their signatures by moving advanced parameters to **kwargs
3. Updates the implementation to use params dict
4. Adds comprehensive **kwargs documentation
"""

import re
import os
from pathlib import Path
from typing import List, Tuple, Optional

# Standard parameters to keep explicit
EXPLICIT_PARAMS = [
    'search_string',
    'body',
    'starts_with',
    'ends_with',
    'ignore_case',
    'start_from',
    'page_size',
    'output_format',
    'report_spec'
]

# Parameters that should go into **kwargs
KWARGS_PARAMS = [
    'anchor_domain',
    'metadata_element_type',
    'metadata_element_subtypes',
    'skip_relationships',
    'include_only_relationships',
    'skip_classified_elements',
    'include_only_classified_elements',
    'graph_query_depth',
    'governance_zone_filter',
    'as_of_time',
    'effective_time',
    'relationship_page_size',
    'limit_results_by_status',
    'sequencing_order',
    'sequencing_property',
    'property_names',
    'classification_names'
]

KWARGS_DOCUMENTATION = """**kwargs : dict, optional
        Additional parameters supported by the underlying find request:
        
        - anchor_domain : str - Domain to anchor the search
        - metadata_element_type : str - Specific metadata element type
        - metadata_element_subtypes : list[str] - List of metadata element subtypes
        - skip_relationships : list[str] - Relationship types to skip
        - include_only_relationships : list[str] - Only include these relationship types
        - skip_classified_elements : list[str] - Skip elements with these classifications
        - include_only_classified_elements : list[str] - Only include elements with these classifications
        - classification_names : list[str] - Filter by classification names
        - graph_query_depth : int - Depth of graph traversal (default 3)
        - governance_zone_filter : list[str] - Filter by governance zones
        - as_of_time : str - Historical query time (ISO 8601 format)
        - effective_time : str - Effective time for the query (ISO 8601 format)
        - relationship_page_size : int - Page size for relationships
        - limit_results_by_status : list[str] - Filter by element status
        - sequencing_order : str - Order of results
        - sequencing_property : str - Property to sequence by
        - property_names : list[str] - Specific properties to search"""


def find_async_find_methods(file_path: str) -> List[Tuple[int, str]]:
    """Find all async find methods that use _async_find_request."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to find async def _async_find_xxx methods
    pattern = r'(async def _async_find_\w+\([^)]+\)[^:]*:)'
    matches = []
    
    for match in re.finditer(pattern, content):
        start_pos = match.start()
        # Count line number
        line_num = content[:start_pos].count('\n') + 1
        method_name = re.search(r'async def (_async_find_\w+)', match.group(1)).group(1)
        
        # Check if this method uses _async_find_request
        # Look ahead in the content to see if it calls _async_find_request
        method_end = content.find('\n    async def ', start_pos + 1)
        if method_end == -1:
            method_end = content.find('\n    def ', start_pos + 1)
        if method_end == -1:
            method_end = len(content)
        
        method_body = content[start_pos:method_end]
        if '_async_find_request' in method_body:
            matches.append((line_num, method_name))
    
    return matches


def extract_method_signature(file_path: str, line_num: int) -> Tuple[str, List[str]]:
    """Extract the full method signature and parameter list."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Start from the line and collect until we find the closing ):
    signature_lines = []
    i = line_num - 1
    paren_count = 0
    started = False
    
    while i < len(lines):
        line = lines[i]
        signature_lines.append(line.rstrip())
        
        # Count parentheses
        for char in line:
            if char == '(':
                paren_count += 1
                started = True
            elif char == ')':
                paren_count -= 1
        
        if started and paren_count == 0 and '):' in line:
            break
        i += 1
    
    full_signature = '\n'.join(signature_lines)
    
    # Extract parameters
    params_match = re.search(r'\(self,\s*(.*?)\)\s*->', full_signature, re.DOTALL)
    if params_match:
        params_str = params_match.group(1)
        # Split by comma, but be careful of nested structures
        params = []
        current_param = ''
        bracket_count = 0
        
        for char in params_str:
            if char in '[{(':
                bracket_count += 1
            elif char in ']})':
                bracket_count -= 1
            elif char == ',' and bracket_count == 0:
                if current_param.strip():
                    params.append(current_param.strip())
                current_param = ''
                continue
            current_param += char
        
        if current_param.strip():
            params.append(current_param.strip())
        
        return full_signature, params
    
    return full_signature, []


def generate_new_signature(method_name: str, old_params: List[str]) -> str:
    """Generate new method signature with **kwargs."""
    # Parse old parameters to extract names and defaults
    param_dict = {}
    for param in old_params:
        # Extract parameter name and default value
        match = re.match(r'(\w+)\s*:\s*([^=]+)(?:\s*=\s*(.+))?', param)
        if match:
            name = match.group(1)
            type_hint = match.group(2).strip()
            default = match.group(3).strip() if match.group(3) else None
            param_dict[name] = (type_hint, default)
    
    # Build new parameter list
    new_params = []
    
    # Add explicit parameters in order
    for param_name in EXPLICIT_PARAMS:
        if param_name in param_dict:
            type_hint, default = param_dict[param_name]
            if default:
                new_params.append(f"{param_name}: {type_hint} = {default}")
            else:
                new_params.append(f"{param_name}: {type_hint}")
    
    # Add **kwargs
    new_params.append("**kwargs")
    
    # Build signature
    params_str = ',\n            '.join(new_params)
    
    # Determine return type from old signature
    return_type = "list | str"  # default
    
    signature = f"""    async def {method_name}(
            self,
            {params_str}
    ) -> {return_type}:"""
    
    return signature


def generate_new_implementation(old_params: List[str]) -> str:
    """Generate new implementation with params dict."""
    # Extract parameter names
    param_names = []
    for param in old_params:
        match = re.match(r'(\w+)\s*:', param)
        if match:
            param_names.append(match.group(1))
    
    # Build params dict for explicit parameters
    explicit_dict_items = []
    for param_name in EXPLICIT_PARAMS:
        if param_name in param_names:
            explicit_dict_items.append(f"'{param_name}': {param_name}")
    
    params_dict = ',\n            '.join(explicit_dict_items)
    
    implementation = f"""        # Build params dict with explicit parameters
        params = {{
            {params_dict}
        }}
        # Merge with any additional kwargs, removing None values
        params.update(kwargs)
        params = {{k: v for k, v in params.items() if v is not None}}
        
        response = await self._async_find_request(
            url,
            _type=_type,
            _gen_output=_gen_output,
            **params
        )
        return response"""
    
    return implementation


def refactor_file(file_path: str, dry_run: bool = True) -> None:
    """Refactor a single file."""
    print(f"\n{'='*80}")
    print(f"Processing: {file_path}")
    print(f"{'='*80}")
    
    methods = find_async_find_methods(file_path)
    
    if not methods:
        print(f"No find methods found in {file_path}")
        return
    
    print(f"Found {len(methods)} find methods:")
    for line_num, method_name in methods:
        print(f"  - Line {line_num}: {method_name}")
    
    if dry_run:
        print("\n[DRY RUN] Would refactor these methods")
        for line_num, method_name in methods:
            signature, params = extract_method_signature(file_path, line_num)
            print(f"\n{method_name}:")
            print(f"  Current params: {len(params)}")
            print(f"  Would simplify to: {len(EXPLICIT_PARAMS)} explicit + **kwargs")
    else:
        print("\n[LIVE] Refactoring methods...")
        # Actual refactoring would go here
        print("  (Implementation pending - requires careful AST manipulation)")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Refactor find methods to use **kwargs pattern')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--file', type=str, help='Specific file to refactor')
    parser.add_argument('--module', type=str, help='Specific module directory to refactor')
    
    args = parser.parse_args()
    
    # Find all OMVS module files
    omvs_dir = Path('pyegeria/omvs')
    
    if args.file:
        files = [Path(args.file)]
    elif args.module:
        files = list(Path(args.module).glob('*.py'))
    else:
        files = list(omvs_dir.glob('*.py'))
    
    files = [f for f in files if f.name != '__init__.py']
    
    print(f"Found {len(files)} files to process")
    
    for file_path in sorted(files):
        refactor_file(str(file_path), dry_run=args.dry_run)
    
    print(f"\n{'='*80}")
    print("Summary:")
    print(f"  Files processed: {len(files)}")
    print(f"  Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"{'='*80}")


if __name__ == '__main__':
    main()