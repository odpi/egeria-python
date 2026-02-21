import json
from rich.console import Console

def verify_vega_lite_gen():
    console = Console()
    
    # Mock results
    results = [
        {"Parameter": "test", "Value": "val1", "Latency (s)": 0.1, "Size (bytes)": 100, "Count": 1},
        {"Parameter": "test", "Value": "val2", "Latency (s)": 0.2, "Size (bytes)": 200, "Count": 1}
    ]
    
    # Logic from action_perf.py
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
    
    print("\n[bold]Data Summary (Vega-Lite Markdown):[/bold]")
    print("```vega-lite")
    print(json.dumps(vega_lite_spec, indent=2))
    print("```")

if __name__ == "__main__":
    verify_vega_lite_gen()
