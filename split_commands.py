import json
import os
import re

# Configuration
INPUT_FILE = "md_processing/data/commands.json"
OUTPUT_DIR = "md_processing/data/commands"

FAMILY_MAP = {
    "Data Designer": "commands_data_designer.json",
    "Digital Product Manager": "commands_product_manager.json",
    "External Reference": "commands_external_reference.json",
    "Feedback Manager": "commands_feedback.json",
    "General": "commands_general.json",
    "Glossary": "commands_glossary.json",
    "Governance Officer": "commands_governance.json",
    "Project": "commands_project.json",
    "Solution Architect": "commands_solution_architect.json"
}

# Defaults to remove
CMD_DEFAULTS = {
    "alternate_names": "",
    "find_constraints": "",
    "extra_find": "",
    "extra_constraints": "",
    "Journal Entry": "",
    "ReferenceURL": "",
    "attach": False,
    "upsert": True,
    "level": "Basic",
}

ATTR_DEFAULTS = {
    "examples": "",
    "default_value": "",
    "valid_values": "",
    "existing_element": "",
    "generated": False,
    "style": "Simple",
    "user_specified": True,
    "unique": False,
    "input_required": False,
    "min_cardinality": 0,
    "max_cardinality": 1,
    "level": "Basic",
    "Journal Entry": "",
    "inUpdate": True
}

def clean_dict(d, defaults):
    """Remove keys that match default values."""
    new_d = d.copy()
    for k, v in defaults.items():
        if k in new_d and new_d[k] == v:
            del new_d[k]
    return new_d

def main():
    print(f"Reading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)

    specs = data.get("Command Specifications", {})
    
    # Store commands by filename
    files_content = {v: {} for v in FAMILY_MAP.values()}
    # Catch-all for unknown families
    files_content["commands_misc.json"] = {}

    for cmd_name, cmd_data in specs.items():
        if not isinstance(cmd_data, dict):
             # Handle metadata keys like "exported"
            continue

        family = cmd_data.get("family", "General")
        filename = FAMILY_MAP.get(family, "commands_misc.json")
        
        # Clean Command
        cleaned_cmd = clean_dict(cmd_data, CMD_DEFAULTS)
        
        # Clean Attributes
        if "Attributes" in cleaned_cmd:
            new_attrs = []
            for attr_entry in cleaned_cmd["Attributes"]:
                # attr_entry is typically { "Display Name": { ... } }
                new_entry = {}
                for attr_name, attr_data in attr_entry.items():
                    new_entry[attr_name] = clean_dict(attr_data, ATTR_DEFAULTS)
                new_attrs.append(new_entry)
            cleaned_cmd["Attributes"] = new_attrs

        files_content[filename][cmd_name] = cleaned_cmd

    # Write files
    print(f"Writing to {OUTPUT_DIR}...")
    for filename, content in files_content.items():
        if not content:
            continue
            
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Wrap in "Command Specifications" to maintain similar structure for now, 
        # or simplified? The plan implies simple merging.
        # Let's keep it simple: { "CommandName": { ... } }
        # But the loader needs to know. Let's stick closer to original structure 
        # but maybe without the top level key if we change loader? 
        # The plan says "Function load_commands should scan... and merge".
        # Let's just output the dict of commands. The loader will put them into the global dict.
        
        output_data = {"Command Specifications": content}
        
        with open(filepath, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"  -> {filename}: {len(content)} commands")

if __name__ == "__main__":
    main()
