#!/usr/bin/env python3
"""
Improved script to fix Python built-in shadowing issues.
Handles function parameters in signatures more carefully.
"""

import re
from pathlib import Path
from typing import Tuple

def fix_filter_in_function_params(content: str) -> Tuple[str, int]:
    """Fix filter parameter in function signatures."""
    changes = 0
    lines = content.split('\n')
    modified_lines = []
    
    for i, line in enumerate(lines):
        original_line = line
        
        # Check if this is a function parameter line with 'filter'
        # Pattern: "filter: type" or "filter=" in function context
        if 'def ' in line or (i > 0 and '(' in lines[i-1] and 'def ' in lines[i-1]):
            # Replace filter: with filter_string:
            line = re.sub(r'\bfilter\s*:', 'filter_string:', line)
            # Replace filter= with filter_string=
            line = re.sub(r'\bfilter\s*=', 'filter_string=', line)
            
            if line != original_line:
                changes += 1
        
        modified_lines.append(line)
    
    return '\n'.join(modified_lines), changes

def fix_type_in_function_params(content: str) -> Tuple[str, int]:
    """Fix type parameter in function signatures."""
    changes = 0
    lines = content.split('\n')
    modified_lines = []
    
    for i, line in enumerate(lines):
        original_line = line
        
        # Check if this is a function parameter line with 'type'
        if 'def ' in line or (i > 0 and '(' in lines[i-1] and 'def ' in lines[i-1]):
            # Replace type: str with type_name: str
            line = re.sub(r'\btype\s*:\s*str', 'type_name: str', line)
            # Replace type= with type_name=
            line = re.sub(r'\btype\s*=', 'type_name=', line)
            
            if line != original_line:
                changes += 1
        
        modified_lines.append(line)
    
    return '\n'.join(modified_lines), changes

def fix_filter_usage(content: str) -> Tuple[str, int]:
    """Fix filter variable usage in function bodies."""
    changes = 0
    
    # Fix: "filter": filter -> "filter": filter_string
    pattern1 = r'"filter"\s*:\s*filter\b'
    content, count1 = re.subn(pattern1, '"filter": filter_string', content)
    changes += count1
    
    # Fix: if filter is/== -> if filter_string is/==
    pattern2 = r'\bif filter (is|==)'
    content, count2 = re.subn(pattern2, r'if filter_string \1', content)
    changes += count2
    
    # Fix: elif filter is/== -> elif filter_string is/==
    pattern3 = r'\belif filter (is|==)'
    content, count3 = re.subn(pattern3, r'elif filter_string \1', content)
    changes += count3
    
    # Fix: filter = "value" assignments in function bodies (but not parameters)
    # This is tricky - only fix if it's an assignment, not a parameter
    pattern4 = r'(\n\s+)filter = '
    content, count4 = re.subn(pattern4, r'\1filter_string = ', content)
    changes += count4
    
    return content, changes

def fix_docstrings(content: str) -> Tuple[str, int]:
    """Fix parameter names in docstrings."""
    changes = 0
    
    # Fix: filter : str in docstrings
    pattern1 = r'(\n\s+)filter\s*:\s*str'
    content, count1 = re.subn(pattern1, r'\1filter_string : str', content)
    changes += count1
    
    # Fix: type : str in docstrings
    pattern2 = r'(\n\s+)type\s*:\s*str'
    content, count2 = re.subn(pattern2, r'\1type_name : str', content)
    changes += count2
    
    return content, changes

def process_file(filepath: Path) -> Tuple[int, int]:
    """Process a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        total_filter_changes = 0
        total_type_changes = 0
        
        # Fix filter in function parameters
        content, changes = fix_filter_in_function_params(content)
        total_filter_changes += changes
        
        # Fix type in function parameters
        content, changes = fix_type_in_function_params(content)
        total_type_changes += changes
        
        # Fix filter usage in bodies
        content, changes = fix_filter_usage(content)
        total_filter_changes += changes
        
        # Fix docstrings
        content, changes = fix_docstrings(content)
        # Count filter vs type changes in docstrings
        if 'filter_string' in content and 'filter_string' not in original_content:
            total_filter_changes += 1
        if 'type_name' in content and 'type_name' not in original_content:
            total_type_changes += 1
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ {filepath}: {total_filter_changes} filter, {total_type_changes} type")
            return total_filter_changes, total_type_changes
        
        return 0, 0
        
    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")
        return 0, 0

def main():
    """Main execution."""
    print("=" * 70)
    print("Python Built-in Shadowing Fix Script v2")
    print("=" * 70)
    print()
    
    total_filter = 0
    total_type = 0
    files_modified = 0
    
    dirs = ["pyegeria", "tests", "commands", "md_processing"]
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            continue
        
        print(f"Processing directory: {dir_name}")
        print("-" * 70)
        
        for filepath in dir_path.rglob("*.py"):
            if "__pycache__" in str(filepath):
                continue
            
            filter_changes, type_changes = process_file(filepath)
            if filter_changes > 0 or type_changes > 0:
                total_filter += filter_changes
                total_type += type_changes
                files_modified += 1
    
    print()
    print("=" * 70)
    print(f"Files modified: {files_modified}")
    print(f"Total filter fixes: {total_filter}")
    print(f"Total type fixes: {total_type}")
    print("=" * 70)

if __name__ == "__main__":
    main()