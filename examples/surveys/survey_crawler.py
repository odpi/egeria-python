"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Recursive survey crawler to identify JSON file types in a directory structure.
"""

import os
import sys
import argparse
from typing import Dict, Any, Optional

# Try to import rich for beautiful output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# Import the inspector from the local directory
from json_inspector import identify_file

def scan_directory(root_path: str):
    """Recursively scan the directory for JSON files and identify them."""
    full_root = os.path.abspath(root_path)
    if not os.path.isdir(full_root):
        print(f"Error: {root_path} is not a valid directory.")
        return

    results = []
    
    for dirpath, _, filenames in os.walk(full_root):
        for filename in filenames:
            if filename.lower().endswith('.json'):
                filepath = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(filepath, full_root)
                
                try:
                    summary = identify_file(filepath)
                    if summary:
                        results.append({
                            "name": filename,
                            "path": rel_path,
                            "type": summary.get("artifact_type", "Unknown"),
                            "label": summary.get("display_label", "N/A"),
                            "details": summary
                        })
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

    return results

def print_results(results: list, root_path: str):
    """Nicely print the results using Rich or standard print."""
    if not results:
        if HAS_RICH:
            Console().print(Panel(f"No matching JSON structures found in [bold]{root_path}[/bold]", style="yellow"))
        else:
            print(f"No matching JSON structures found in {root_path}")
        return

    if HAS_RICH:
        console = Console()
        table = Table(title=f"Survey Identification Results for: {root_path}")
        
        table.add_column("File Name", style="cyan")
        table.add_column("Relative Path", style="green")
        table.add_column("Artifact Type", style="magenta")
        table.add_column("Display Label", style="yellow")
        
        for res in results:
            table.add_row(
                res["name"],
                res["path"],
                res["type"],
                res["label"]
            )
        
        console.print(table)
    else:
        print(f"\nSurvey Identification Results for: {root_path}")
        print("-" * 80)
        print(f"{'File Name':<25} | {'Relative Path':<30} | {'Artifact Type':<20}")
        print("-" * 80)
        for res in results:
            print(f"{res['name']:<25} | {res['path']:<30} | {res['type']:<20}")

def main():
    parser = argparse.ArgumentParser(description="Recursively scan and identify JSON file types for Egeria surveys.")
    parser.add_argument("path", help="The root directory path to scan.")
    
    args = parser.parse_args()
    
    if HAS_RICH:
        Console().print(Panel(f"Scanning [bold]{args.path}[/bold]...", style="blue"))
    else:
        print(f"Scanning {args.path}...")
        
    results = scan_directory(args.path)
    print_results(results, args.path)

if __name__ == "__main__":
    main()
