#!/usr/bin/env python3
"""
Dr.Egeria Markdown Syntax Migration Script

This script migrates Dr.Egeria Markdown files from the old syntax to the new syntax:
- Commands: # Verb Object  ->  ## Verb Object
- Attributes: ## Label      ->  ### Label

It supports processing a single file or a directory recursively.
It is designed to be idempotent and avoid double-bumping already migrated files.
"""

import os
import re
import sys
import argparse
from pathlib import Path

# Standard Dr.Egeria / OMAG verbs
STANDARD_VERBS = {
    "Create", "Update", "Delete", "Link", "Attach", "Add",
    "Unlink", "Detach", "Remove", "Display", "Run", "View",
    "Search", "Find", "Provenance", "Validate", "Process"
}

# Attributes that might be mistaken for commands because they start with a verb
KNOWN_ATTRIBUTES = {
    "Display Name", "Search Keywords", "Search String", "Create Time", "Update Time",
    "Qualified Name", "Category Name"
}

VERBS_PATTERN = "|".join(STANDARD_VERBS)

# Regex to match OLD Command: # Verb Object
OLD_CMD_RX = re.compile(rf"^#\s+(?P<verb>{VERBS_PATTERN})(?:\s+(?P<object>[^#\n]+))?$", re.IGNORECASE)

# Regex to match NEW Command: ## Verb Object
NEW_CMD_RX = re.compile(rf"^##\s+(?P<verb>{VERBS_PATTERN})(?:\s+(?P<object>[^#\n]+))?$", re.IGNORECASE)

# Regex to match NEW Attribute: ### Label
NEW_ATTR_RX = re.compile(r"^###\s+[^#\n]+$")

def migrate_content(content: str) -> str:
    """
    Migrates the content of a markdown file to the new Dr.Egeria syntax.
    """
    lines = content.splitlines(keepends=True)
    
    KNOWN_ATTRIBUTES_LOWER = {a.lower() for a in KNOWN_ATTRIBUTES}

    def is_old_attr(line_stripped):
        if not line_stripped.startswith("## "):
            return False
        text = line_stripped[3:].strip()
        # It's an old attribute if it's a KNOWN_ATTRIBUTE or NOT a NEW_CMD
        return (text.lower() in KNOWN_ATTRIBUTES_LOWER or 
                not NEW_CMD_RX.match(line_stripped))

    # 1. Detect if the file needs migration
    has_old_cmd = any(OLD_CMD_RX.match(line.strip()) for line in lines)
    has_old_attr = any(is_old_attr(line.strip()) for line in lines)
    
    # If it has neither old cmd nor old attr, skip it
    if not has_old_cmd and not has_old_attr:
        return content

    # 2. Perform migration
    new_lines = []
    for line in lines:
        stripped = line.strip()
        
        # Convert OLD Command: # Verb Object -> ## Verb Object
        cmd_match = OLD_CMD_RX.match(stripped)
        if cmd_match:
            new_lines.append("#" + line)
            continue
            
        # Convert OLD Attribute: ## Label -> ### Label
        if is_old_attr(stripped):
            new_lines.append("#" + line)
            continue
            
        # If it's a NEW command (## Verb Object), leave it alone
        # If it's a NEW attribute (### Label), leave it alone
        
        new_lines.append(line)
        
    return "".join(new_lines)

def process_path(target_path: Path, recursive: bool = False):
    if target_path.is_file():
        files = [target_path]
    elif target_path.is_dir():
        if recursive:
            files = list(target_path.glob("**/*.md"))
        else:
            files = list(target_path.glob("*.md"))
    else:
        print(f"Error: {target_path} is not a valid file or directory.")
        return

    migrated_count = 0
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = migrate_content(content)
            
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Migrated: {file_path}")
                migrated_count += 1
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print(f"Migration complete. Total files migrated: {migrated_count}")

def main():
    parser = argparse.ArgumentParser(description="Migrate Dr.Egeria Markdown files to new syntax.")
    parser.add_argument("path", help="Path to a single markdown file or a directory.")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively process directories.")
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
        
    args = parser.parse_args()
    process_path(Path(args.path), args.recursive)

if __name__ == "__main__":
    main()
