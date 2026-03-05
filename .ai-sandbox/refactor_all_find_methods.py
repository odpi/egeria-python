#!/usr/bin/env python3
"""
Script to refactor all find methods in OMVS modules to use **kwargs pattern.
This applies the pattern consistently across all files that use _async_find_request.
"""

import re
import os
from pathlib import Path

# Files and their find method counts based on search results
FILES_TO_REFACTOR = {
    'pyegeria/omvs/classification_manager.py': 7,
    'pyegeria/omvs/schema_maker.py': 1,
    'pyegeria/omvs/solution_architect.py': 4,
    'pyegeria/omvs/reference_data.py': 1,
    'pyegeria/omvs/subject_area.py': 1,
    'pyegeria/omvs/project_manager.py': 1,
    'pyegeria/omvs/time_keeper.py': 1,
    'pyegeria/omvs/valid_metadata.py': 1,
    'pyegeria/omvs/location_arena.py': 1,
    'pyegeria/omvs/product_manager.py': 2,
    'pyegeria/omvs/metadata_explorer_omvs.py': 4,
    'pyegeria/omvs/data_designer.py': 1,  # find_data_classes method
}

def find_async_find_methods(file_path):
    """Find all async methods that call _async_find_request."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to find async methods that use _async_find_request
    pattern = r'(async def (_async_find_\w+)\([^)]+\)[^:]*:.*?(?=\n    (?:async )?def |$))'
    matches = re.findall(pattern, content, re.DOTALL)
    
    methods = []
    for match in matches:
        method_text = match[0]
        method_name = match[1]
        if 'await self._async_find_request(' in method_text:
            methods.append((method_name, method_text))
    
    return methods

def analyze_method_signature(method_text):
    """Extract the method signature and parameters."""
    # Find the method definition line(s)
    sig_match = re.search(r'async def (\w+)\((.*?)\):', method_text, re.DOTALL)
    if not sig_match:
        return None
    
    method_name = sig_match.group(1)
    params_text = sig_match.group(2)
    
    # Parse parameters
    params = []
    for param in params_text.split(','):
        param = param.strip()
        if param and param != 'self':
            params.append(param)
    
    return {
        'name': method_name,
        'params': params,
        'full_text': method_text
    }

def main():
    """Main function to analyze all files."""
    print("Analyzing find methods across OMVS modules...")
    print("=" * 80)
    
    total_methods = 0
    for file_path, expected_count in FILES_TO_REFACTOR.items():
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue
        
        print(f"\n📄 {file_path}")
        print(f"   Expected methods: {expected_count}")
        
        methods = find_async_find_methods(file_path)
        print(f"   Found methods: {len(methods)}")
        
        for method_name, method_text in methods:
            print(f"   - {method_name}")
            total_methods += 1
    
    print("\n" + "=" * 80)
    print(f"Total methods found: {total_methods}")
    print(f"Total expected: {sum(FILES_TO_REFACTOR.values())}")
    
    print("\n✅ Analysis complete!")
    print("\nTo refactor these methods, they should follow this pattern:")
    print("""
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
        report_spec: str | dict = None,
        **kwargs
    ) -> list | str:
        url = f"..."
        
        # Merge explicit parameters with kwargs
        params = {
            'search_string': search_string,
            'body': body,
            'starts_with': starts_with,
            'ends_with': ends_with,
            'ignore_case': ignore_case,
            'start_from': start_from,
            'page_size': page_size,
            'output_format': output_format,
            'report_spec': report_spec
        }
        params.update(kwargs)
        
        # Filter out None values, but keep search_string even if None (it's required)
        params = {k: v for k, v in params.items() if v is not None or k == 'search_string'}
        
        response = await self._async_find_request(
            url,
            _type="...",
            _gen_output=self._generate_xxx_output,
            **params
        )
        return response
    """)

if __name__ == '__main__':
    main()