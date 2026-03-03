import os
import sys

# Add the repository root to sys.path to ensure local pyegeria is used
# matches structure: [repo_root]/examples/surveys/survey_crawler.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import argparse
import csv
from typing import Dict, Any, Optional, List
host_name = os.uname()[1]
# Try to import rich for beautiful output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# Import Egeria clients
try:
    from pyegeria import AssetMaker, PyegeriaException, print_basic_exception
    from pyegeria.omvs.data_discovery import DataDiscovery
    from pyegeria.models import NewElementRequestBody
    HAS_PYEGERIA = True
except ImportError:
    HAS_PYEGERIA = False

# Import the inspector from the local directory
from json_inspector import identify_file

import json
from datetime import datetime

def scan_directory(root_path: str) -> Dict[str, Any]:
    """Recursively scan the directory for JSON files and identify them."""
    full_root = os.path.abspath(root_path)
    if not os.path.isdir(full_root):
        print(f"Error: {root_path} is not a valid directory.")
        return {"results": [], "total_files": 0, "json_files": 0}

    results = []
    total_files = 0
    json_files = 0
    
    for dirpath, _, filenames in os.walk(full_root):
        for filename in filenames:
            total_files += 1
            if filename.lower().endswith('.json'):
                json_files += 1
                filepath = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(filepath, full_root)
                
                try:
                    summary = identify_file(filepath)
                    if summary:
                        results.append({
                            "name": filename,
                            "path": rel_path,
                            "full_path": filepath,
                            "type": summary.get("artifact_type", "Unknown"),
                            "label": summary.get("display_label", "N/A"),
                            "details": summary
                        })
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

    return {
        "results": results,
        "total_files": total_files,
        "json_files": json_files
    }

def get_markdown_table(results: List[Dict[str, Any]]) -> str:
    """Generate a markdown table from the results."""
    if not results:
        return "No matching JSON files found."
    
    lines = ["| File Name | Relative Path | Artifact Type | Display Label |",
             "| :--- | :--- | :--- | :--- |"]
    
    for res in results:
        lines.append(f"| {res['name']} | {res['path']} | {res['type']} | {res['label']} |")
    
    return "\n".join(lines)

def get_breakdown_vega(json_count: int, total_count: int) -> str:
    """Generate a Vega-Lite spec for the file breakdown."""
    other_count = total_count - json_count
    data = [
        {"Category": "Identified JSON", "Count": json_count},
        {"Category": "Other Files", "Count": other_count}
    ]
    
    spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "description": "File Breakdown: Identified JSON vs Other Files",
        "data": {"values": data},
        "mark": {"type": "arc", "innerRadius": 50},
        "encoding": {
            "theta": {"field": "Count", "type": "quantitative"},
            "color": {"field": "Category", "type": "nominal", "scale": {"range": ["#673ab7", "#e0e0e0"]}}
        },
        "title": "File Structure Breakdown"
    }
    return json.dumps(spec, indent=2)

def get_histogram_vega(results: List[Dict[str, Any]]) -> str:
    """Generate a Vega-Lite spec for the artifact type histogram."""
    type_counts = {}
    for res in results:
        atype = res["type"]
        type_counts[atype] = type_counts.get(atype, 0) + 1
    
    data = [{"Type": k, "Count": v} for k, v in type_counts.items()]
    
    spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "description": "Histogram of Identified JSON Artifact Types",
        "data": {"values": data},
        "mark": "bar",
        "encoding": {
            "y": {"field": "Type", "type": "nominal", "sort": "-x", "title": "Artifact Type"},
            "x": {"field": "Count", "type": "quantitative", "title": "Count"},
            "color": {"field": "Type", "type": "nominal", "legend": None}
        },
        "title": "JSON Artifact Type Distribution"
    }
    return json.dumps(spec, indent=2)

def generate_full_report(scan_data: Dict[str, Any], root_path: str) -> str:
    """Generate a complete markdown report with table and charts."""
    results = scan_data["results"]
    total = scan_data["total_files"]
    json_count = len(results)
    
    md_table = get_markdown_table(results)
    breakdown_vega = get_breakdown_vega(json_count, total)
    histogram_vega = get_histogram_vega(results)
    
    report = f"""# Egeria Survey Scan Report
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Root Path: `{root_path}`

## Summary
- **Total Files Scanned:** {total}
- **JSON Files Identified:** {json_count}

## File Breakdown
```vega-lite
{breakdown_vega}
```

## Artifact Type Distribution
```vega-lite
{histogram_vega}
```

## Detailed Findings
{md_table}
"""
    return report

def save_to_csv(results: List[Dict[str, Any]], csv_path: str):
    """Save the scan results to a CSV file."""
    if not results:
        print("No results to save.")
        return

    try:
        with open(csv_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["name", "path", "type", "label"])
            writer.writeheader()
            for res in results:
                writer.writerow({
                    "name": res["name"],
                    "path": res["path"],
                    "type": res["type"],
                    "label": res["label"]
                })
        print(f"Successfully wrote results to {csv_path}")
    except Exception as e:
        if HAS_PYEGERIA and isinstance(e, PyegeriaException):
            print_basic_exception(e)
        else:
            print(f"Error saving to CSV: {e}")

def integrate_with_egeria(results: List[Dict[str, Any]], root_path: str, egeria_config: Dict[str, str]):
    """Find directory GUID and create SurveyReports for MCP configs."""
    if not HAS_PYEGERIA:
        print("Error: pyegeria not installed. Cannot perform Egeria integration.")
        return

    full_root = os.path.abspath(root_path)
    view_server = egeria_config.get("server")
    platform_url = egeria_config.get("url")
    user_id = "peterprofile"
    user_password = "secret"

    client = AssetMaker(view_server, platform_url, user_id)
    discovery = DataDiscovery(view_server, platform_url, user_id)
    
    client.create_egeria_bearer_token(user_id, user_password)
    discovery.create_egeria_bearer_token(user_id, user_password)
    print(f"user: {user_id}, pwd: {user_password}")
    print(f"Connecting to Egeria at {platform_url} as {user_id}...")
    
    # 1. Find the GUID of the root directory (as a FileFolder)
    try:
        # Search for the directory by pathName or qualifiedName
        # We specify the type to narrow it down
        folder_assets = client.find_assets(search_string=full_root, metadata_element_type="FileFolder", output_format="DICT",report_spec="Referenceable")
        
        if not folder_assets or (isinstance(folder_assets, str) and "not found" in folder_assets.lower()):
            print(f"Warning: Root directory {full_root} not found as a FileFolder in Egeria.")
            return

        # Assuming find_assets returns a list of DICTs when output_format is DICT (default)
        if isinstance(folder_assets, list) and len(folder_assets) > 0:
            parent_guid = folder_assets[0].get("guid")
        else:
            print("Could not retrieve a valid GUID for the root directory.")
            folder_body={
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "FileFolderProperties",
                    "qualifiedName": f"FileFolder::{host_name}-{full_root}",
                    "displayName": f"{host_name}-{full_root}",
                    "description": f"Catalog entry for root directory: {host_name}-{full_root}"
                
                }
            }
            parent_guid = client.create_asset(body=folder_body)
            

        print(f"Found parent FileFolder GUID: {parent_guid}")
        qualified_name = f"SurveyReport::JSON-File::{parent_guid}::{datetime.now().isoformat()}"
        display_name = f"JSON File Survey Report for {full_root}"
        description = f"Automated JSON Filesurvey report for {full_root}"
        print(f"Creating SurveyReport for {full_root}...")
                
        body = {
            "class": "NewElementRequestBody",
            "parentGUID": parent_guid,
            "parentRelationshipTypeName": "ReportSubject",
            "properties": {
                "class": "SurveyReportProperties",
                "qualifiedName": qualified_name,
                "displayName": display_name,
                "description": description
            }
        }
        
        report_guid = client.create_asset(body=body)
        print(f"Created SurveyReport with GUID: {report_guid}")

        # 3. Create annotations for each identified file
        for res in results:
            print(f"Creating annotation for {res['name']}...")
            annotation_qualified_name = f"{qualified_name}::annotation::{res['path']}"
            
            annotation_body = {
                "class": "NewElementRequestBody",
                "parentGUID": report_guid,
                "parentRelationshipTypeName": "ReportedAnnotation",
                "properties": {
                    "class": "AnnotationProperties",
                    "qualifiedName": annotation_qualified_name,
                    "displayName": f"Annotation for {res['name']}",
                    "summary": f"Identified as {res['type']}",
                    "annotationType": res["type"],
                    "jsonProperties": json.dumps(res["details"])
                }
            }
            
            try:
                annotation_guid = discovery.create_annotation(body=annotation_body)
                print(f"Created Annotation with GUID: {annotation_guid}")
            except Exception as e:
                print(f"Failed to create annotation for {res['name']}: {e}")

    except Exception as e:
        if HAS_PYEGERIA and isinstance(e, PyegeriaException):
            print_basic_exception(e)
        else:
            print(f"Error in Egeria integration: {e}")

        # 2. For each identified MCP configuration, create a SurveyReport
        # for res in results:
        #     if "MCP" in res["type"]:
        #         qualified_name = f"SurveyReport::JSON-File::{res['path']}"
        #         display_name = f"Survey Report for {res['name']}"
        #         description = f"Automated survey report for {res['type']} located at {res['path']}"
                
        #         print(f"Creating SurveyReport for {res['name']}...")
                
        #         body = {
        #             "class": "NewElementRequestBody",
        #             "parentGUID": parent_guid,
        #             "parentRelationshipTypeName": "ReportSubject",
        #             "properties": {
        #                 "class": "AssetProperties",
        #                 "typeName": "SurveyReport",
        #                 "qualifiedName": qualified_name,
        #                 "displayName": display_name,
        #                 "description": description
        #             }
        #         }
                
                # try:
                #     report_guid = client.create_asset(body=body)
                #     print(f"Created SurveyReport with GUID: {report_guid}")
                # except Exception as e:
                #     print(f"Failed to create SurveyReport for {res['name']}: {e}")

    

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
    parser.add_argument("--csv", help="Optional path to write results to a CSV file.")
    parser.add_argument("--markdown", action="store_true", help="Display results as a markdown table.")
    parser.add_argument("--report", help="Optional path to write a full markdown report with Vega-Lite charts.")
    parser.add_argument("--egeria", action="store_true", help="Enable Egeria integration to create SurveyReports.")
    parser.add_argument("--server", default=os.environ.get("EGERIA_VIEW_SERVER", "view-server"), help="Egeria View Server name.")
    parser.add_argument("--url", default=os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443"), help="Egeria Platform URL.")
    parser.add_argument("--user", default=os.environ.get("EGERIA_USER_ID", "pete"), help="Egeria User ID.")
    
    args = parser.parse_args()
    
    if HAS_RICH:
        Console().print(Panel(f"Scanning [bold]{args.path}[/bold]...", style="blue"))
    else:
        print(f"Scanning {args.path}...")
        
    scan_data = scan_directory(args.path)
    results = scan_data["results"]
    
    if args.markdown:
        print("\n" + get_markdown_table(results))
    else:
        print_results(results, args.path)
    
    if args.csv:
        save_to_csv(results, args.csv)
        
    if args.report:
        try:
            report_content = generate_full_report(scan_data, args.path)
            with open(args.report, "w", encoding="utf-8") as f:
                f.write(report_content)
            print(f"Successfully wrote full report to {args.report}")
        except Exception as e:
            print(f"Error generating report: {e}")

    if args.egeria:
        egeria_config = {
            "server": args.server,
            "url": args.url,
            "user": args.user
        }
        integrate_with_egeria(results, args.path, egeria_config)

if __name__ == "__main__":
    main()
