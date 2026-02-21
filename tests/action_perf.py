"""
Performance testing for `find_processes` in AssetMaker.
Systematically varies parameters and measures latency and response size.
"""

import time
import json
import os
from pyegeria.omvs.asset_maker import AssetMaker
from pyegeria import PyegeriaException, print_exception_table
from rich.console import Console
from rich.table import Table

def run_perf_tests():
    console = Console()
    
    # Connection details - Use erinoverview as it has data in this environment
    view_server = os.getenv("PYEG_SERVER_NAME", "qs-view-server")
    platform_url = os.getenv("PYEG_PLATFORM_URL", "https://127.0.0.1:9443")
    user_id = os.getenv("PYEG_USER_ID", "erinoverview")
    user_pwd = os.getenv("PYEG_USER_PWD", "secret")
    
    console.print(f"[bold blue]Starting Performance Tests[/bold blue]")
    console.print(f"Server: {view_server}")
    console.print(f"Platform: {platform_url}")
    console.print(f"User: {user_id}")
    
    try:
        console.print("  Initializing Client...")
        a_client = AssetMaker(
            view_server,
            platform_url,
            user_id=user_id,
            user_pwd=user_pwd,
        )
        
        # Create token
        console.print("  Creating Token...")
        a_client.create_egeria_bearer_token(user_id, user_pwd)
        console.print("  Token created.")
        
        # Check initial count - use activity_status_list=[] to find everything
        console.print("  Checking for existing processes...")
        initial_check = a_client.find_processes(search_string="*", activity_status_list=[], page_size=100)
        count = len(initial_check) if isinstance(initial_check, list) else 0
        if count == 0:
            msg = initial_check if isinstance(initial_check, str) else "No processes found"
            console.print(f"[warning]{msg}. Latency measurements will reflect empty result set performance.[/warning]")
        else:
            console.print(f"  Found {count} process(es) for testing.")

        results = []
        
        # 1. Varying include_only_relationships
        relationship_sets = [
            [],
            ["Actions"],
            ["AssignmentScope"],
            ["ActionRequestor"],
            ["Actions", "AssignmentScope"],
            ["Actions", "AssignmentScope", "ActionRequestor"]
        ]
        
        console.print("\n[yellow]Testing include_only_relationships...[/yellow]")
        for rel_set in relationship_sets:
            console.print(f"  Testing relationships: {rel_set}")
            start_time = time.perf_counter()
            try:
                response = a_client.find_processes(
                    search_string="*",
                    activity_status_list=[],
                    include_only_relationships=rel_set,
                    page_size=100,
                    output_format="JSON"
                )
                duration = time.perf_counter() - start_time
                size = len(json.dumps(response))
                res_count = len(response) if isinstance(response, list) else 0
                
                results.append({
                    "Parameter": "include_only_relationships",
                    "Value": str(rel_set),
                    "Latency (s)": round(duration, 4),
                    "Size (bytes)": size,
                    "Count": res_count
                })
            except Exception as e:
                console.print(f"[red]Error testing {rel_set}: {e}[/red]")
        
        # 2. Varying relationship_page_size
        page_sizes = [1, 2, 5]
        
        console.print("\n[yellow]Testing relationship_page_size...[/yellow]")
        for page_size in page_sizes:
            console.print(f"  Testing page_size: {page_size}")
            start_time = time.perf_counter()
            try:
                response = a_client.find_processes(
                    search_string="*",
                    activity_status_list=[],
                    relationship_page_size=page_size,
                    page_size=100,
                    output_format="JSON"
                )
                duration = time.perf_counter() - start_time
                size = len(json.dumps(response))
                res_count = len(response) if isinstance(response, list) else 0
                
                results.append({
                    "Parameter": "relationship_page_size",
                    "Value": str(page_size),
                    "Latency (s)": round(duration, 4),
                    "Size (bytes)": size,
                    "Count": res_count
                })
            except Exception as e:
                console.print(f"[red]Error testing page_size={page_size}: {e}[/red]")

        # 3. Varying graph_query_depth
        depths = [0, 1, 2, 3, 4, 5]
        console.print("\n[yellow]Testing graph_query_depth...[/yellow]")
        for depth in depths:
            console.print(f"  Testing depth: {depth}")
            start_time = time.perf_counter()
            try:
                response = a_client.find_processes(
                    search_string="*",
                    activity_status_list=[],
                    graph_query_depth=depth,
                    page_size=100,
                    output_format="JSON"
                )
                duration = time.perf_counter() - start_time
                size = len(json.dumps(response))
                res_count = len(response) if isinstance(response, list) else 0
                
                results.append({
                    "Parameter": "graph_query_depth",
                    "Value": str(depth),
                    "Latency (s)": round(duration, 4),
                    "Size (bytes)": size,
                    "Count": res_count
                })
            except Exception as e:
                console.print(f"[red]Error testing depth={depth}: {e}[/red]")

        # 4. Varying metadata_element_subtypes
        subtypes_sets = [
            ["Action"],
            ["ToDo"],
            ["Action", "ToDo"],
            [],
            ["Process"]
        ]
        console.print("\n[yellow]Testing metadata_element_subtypes...[/yellow]")
        for subtypes in subtypes_sets:
            console.print(f"  Testing subtypes: {subtypes}")
            start_time = time.perf_counter()
            try:
                response = a_client.find_processes(
                    search_string="*",
                    activity_status_list=[],
                    metadata_element_subtypes=subtypes,
                    page_size=100,
                    output_format="JSON"
                )
                duration = time.perf_counter() - start_time
                size = len(json.dumps(response))
                res_count = len(response) if isinstance(response, list) else 0
                
                results.append({
                    "Parameter": "metadata_element_subtypes",
                    "Value": str(subtypes),
                    "Latency (s)": round(duration, 4),
                    "Size (bytes)": size,
                    "Count": res_count
                })
            except Exception as e:
                console.print(f"[red]Error testing subtypes={subtypes}: {e}[/red]")
        
        # Print Table
        table = Table(title="Performance Impact Analysis - find_processes")
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_column("Latency (s)", justify="right", style="green")
        table.add_column("Size (bytes)", justify="right", style="blue")
        table.add_column("Count", justify="right", style="yellow")
        
        for res in results:
            table.add_row(
                res["Parameter"],
                res["Value"],
                f"{res['Latency (s)']:.4f}",
                str(res["Size (bytes)"]),
                str(res["Count"])
            )
        
        console.print("\n")
        console.print(table)
        
        # Summary for Vega-Lite visualization
        vega_lite_spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": "Performance Impact Analysis - find_processes",
            "title": "Performance Impact Analysis - find_processes",
            "data": {"values": results},
            "mark": "bar",
            "encoding": {
                "x": {"field": "Value", "type": "nominal", "axis": {"labelAngle": -45}},
                "y": {"field": "Latency (s)", "type": "quantitative"},
                "color": {"field": "Parameter", "type": "nominal"},
                "column": {"field": "Parameter", "type": "nominal"}
            }
        }
        
        console.print("\n[bold]Data Summary (Vega-Lite Markdown):[/bold]")
        console.print("```vega-lite")
        console.print(json.dumps(vega_lite_spec, indent=2))
        console.print("```")
            
    except PyegeriaException as e:
        print_exception_table(e)
    except Exception as e:
        console.print_exception(e)
    finally:
        if 'a_client' in locals():
            a_client.close_session()

if __name__ == "__main__":
    run_perf_tests()
