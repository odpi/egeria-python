import json
import os
from collections import Counter
from rich.console import Console
from rich.table import Table

console = Console()

def analyze_json(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)

    specs = data.get("Command Specifications", {})
    total_commands = len(specs)
    
    # Analyze common fields in commands
    command_fields = Counter()
    command_defaults = {
        "alternate_names": "",
        "find_constraints": "",
        "extra_find": "",
        "extra_constraints": "",
        "Journal Entry": "",
        "ReferenceURL": "",
        "attach": False,
        "upsert": True,
        "level": "Basic",
        # "find_method": ""  # Varies too much
    }
    
    savings_count = Counter()
    
    # Analyze attributes
    total_attributes = 0
    attr_fields = Counter()
    attr_defaults = {
        "examples": "",
        "default_value": "",
        "valid_values": "",
        "existing_element": "",
        "generated": False,
        "style": "Simple",
        "user_specified": True,
        "unique": False,
        "input_required": False, # careful
        "min_cardinality": 0,
        "max_cardinality": 1,
        "level": "Basic",
        "Journal Entry": "",
        "inUpdate": True
    }
    
    for cmd_name, cmd_data in specs.items():
        if not isinstance(cmd_data, dict): continue
        
        for field, default in command_defaults.items():
            if cmd_data.get(field) == default:
                savings_count[f"Command.{field}"] += 1
        
        attributes = cmd_data.get("Attributes", [])
        for attr_item in attributes:
            # key is the display name
            for attr_name, attr_data in attr_item.items():
                total_attributes += 1
                for field, default in attr_defaults.items():
                    if attr_data.get(field) == default:
                        savings_count[f"Attribute.{field}"] += 1

    # Display results
    table = Table(title="Redundancy Analysis")
    table.add_column("Field", style="cyan")
    table.add_column("Redundant Count", justify="right")
    table.add_column("Total Objects", justify="right")
    table.add_column("Percentage", justify="right")
    
    for key, count in savings_count.items():
        total = total_commands if key.startswith("Command") else total_attributes
        pct = (count / total * 100) if total else 0
        table.add_row(key, str(count), str(total), f"{pct:.1f}%")
        
    console.print(table)
    
    # Estimate size reduction
    # Rough estimate: 20 bytes per line removal?
    lines_saved = sum(savings_count.values())
    console.print(f"\nTotal potential lines removed: {lines_saved}")
    console.print(f"Total commands: {total_commands}")
    console.print(f"Total attributes: {total_attributes}")

# Run analysis
analyze_json("md_processing/data/commands.json")
