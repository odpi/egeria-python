import json
import os
import collections
from pathlib import Path

def validate_compact_json(compact_dir):
    all_files = list(Path(compact_dir).glob('*.json'))
    
    global_attribute_definitions = {}
    global_bundle_definitions = {}
    
    all_errors = []
    all_warnings = []

    # Phase 1: Check for duplicate keys in each file and build global maps
    for file_path in all_files:
        with open(file_path, 'r') as f:
            content = f.read()

        def collect_duplicates(ordered_pairs):
            keys = [p[0] for p in ordered_pairs]
            counts = collections.Counter(keys)
            duplicates = [k for k, count in counts.items() if count > 1]
            if duplicates:
                all_errors.append(f"[{file_path.name}] Found duplicate keys: {duplicates}")
            return dict(ordered_pairs)

        try:
            data = json.loads(content, object_pairs_hook=collect_duplicates)
            
            # Update global maps
            attrs = data.get('attribute_definitions', {})
            for attr_name, attr_def in attrs.items():
                if attr_name in global_attribute_definitions:
                    # Optional: check for consistency if defined in multiple files
                    pass
                global_attribute_definitions[attr_name] = attr_def
                
                # Check for basic attribute properties
                if not attr_def.get('style'):
                    all_errors.append(f"[{file_path.name}] Attribute '{attr_name}' has missing or empty style.")
                if not attr_def.get('variable_name'):
                    all_errors.append(f"[{file_path.name}] Attribute '{attr_name}' has missing or empty variable_name.")
                if not attr_def.get('description'):
                    all_warnings.append(f"[{file_path.name}] Attribute '{attr_name}' has empty description.")

            bundles = data.get('bundles', {})
            for bundle_name, bundle_def in bundles.items():
                global_bundle_definitions[bundle_name] = bundle_def

        except json.JSONDecodeError as e:
            all_errors.append(f"[{file_path.name}] JSON Decode Error: {e}")

    # Phase 2: Check for cross-references
    for file_path in all_files:
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except:
                continue # Already reported
                
            # Check bundles
            bundles = data.get('bundles', {})
            for bundle_name, bundle_def in bundles.items():
                inherits = bundle_def.get('inherits')
                if inherits and inherits not in global_bundle_definitions:
                    all_errors.append(f"[{file_path.name}] Bundle '{bundle_name}' inherits from unknown bundle '{inherits}'.")
                
                own_attrs = bundle_def.get('own_attributes', [])
                for attr_name in own_attrs:
                    # Strip extra quotes if present (some files have them)
                    clean_attr = attr_name.strip('"')
                    if clean_attr not in global_attribute_definitions:
                        all_errors.append(f"[{file_path.name}] Bundle '{bundle_name}' references unknown attribute '{attr_name}'.")

            # Check commands
            commands = data.get('commands', {})
            for cmd_name, cmd_def in commands.items():
                bundle = cmd_def.get('bundle')
                if bundle and bundle not in global_bundle_definitions:
                    all_errors.append(f"[{file_path.name}] Command '{cmd_name}' references unknown bundle '{bundle}'.")
                
                custom_attrs = cmd_def.get('custom_attributes', [])
                for attr_name in custom_attrs:
                    clean_attr = attr_name.strip('"')
                    if clean_attr not in global_attribute_definitions:
                        all_errors.append(f"[{file_path.name}] Command '{cmd_name}' references unknown attribute '{attr_name}'.")

    # Output results
    if all_errors:
        print("\nERRORS found:")
        for err in all_errors:
            print(f"  ❌ {err}")
    else:
        print("\n✅ No critical errors found.")

    if all_warnings:
        print("\nWARNINGS found:")
        for warn in all_warnings:
            print(f"  ⚠️ {warn}")
    else:
        print("\n✅ No warnings found.")

    return len(all_errors) == 0

if __name__ == '__main__':
    compact_dir = 'md_processing/data/compact_commands/'
    success = validate_compact_json(compact_dir)
    exit(0 if success else 1)
