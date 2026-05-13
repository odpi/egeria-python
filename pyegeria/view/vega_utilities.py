"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Utilities for generating Vega-Lite chart specifications from Egeria data structures.
"""

from typing import Dict, Any, Optional

def generate_vega_bar_chart(
    data: Dict[str, Any],
    title: str,
    x_label: str = "Count",
    y_label: str = "Category",
    orientation: str = "horizontal"
) -> Optional[Dict[str, Any]]:
    """
    Generate a Vega-Lite bar chart specification from a dictionary of category-to-value counts.

    Parameters
    ----------
    data : dict
        A dictionary where keys are categories and values are numeric counts.
    title : str
        The title of the chart.
    x_label : str
        The label for the X axis.
    y_label : str
        The label for the Y axis.
    orientation : str
        'horizontal' or 'vertical'. Default is 'horizontal'.

    Returns
    -------
    dict
        A Vega-Lite JSON specification, or None if the input data is invalid/empty.
    """
    if not isinstance(data, dict) or not data:
        return None

    # Filter out empty or non-numeric values
    plot_data = [{"category": k, "count": v} for k, v in data.items() if isinstance(v, (int, float))]
    if not plot_data:
        return None

    spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": title,
        "description": title,
        "data": {"values": plot_data},
        "mark": {"type": "bar", "tooltip": True},
        "encoding": {
            "color": {"field": "category", "type": "nominal", "legend": None},
            "tooltip": [
                {"field": "category", "type": "nominal", "title": y_label},
                {"field": "count", "type": "quantitative", "title": x_label}
            ]
        }
    }

    if orientation == "horizontal":
        spec["encoding"]["y"] = {"field": "category", "type": "nominal", "sort": "-x", "title": y_label}
        spec["encoding"]["x"] = {"field": "count", "type": "quantitative", "title": x_label}
    else:
        spec["encoding"]["x"] = {"field": "category", "type": "nominal", "axis": {"labelAngle": -45}, "title": x_label}
        spec["encoding"]["y"] = {"field": "count", "type": "quantitative", "title": y_label}

    return spec


def generate_vega_pie_chart(
    data: Dict[str, Any],
    title: str,
    category_label: str = "Category",
    value_label: str = "Count",
    donut: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Generate a Vega-Lite pie or donut chart specification from a dictionary of category-to-value counts.

    Parameters
    ----------
    data : dict
        A dictionary where keys are categories and values are numeric counts.
    title : str
        The title of the chart.
    category_label : str
        The label for the categorical data in tooltips.
    value_label : str
        The label for the quantitative data in tooltips.
    donut : bool
        If True, renders as a donut chart (innerRadius > 0). If False, renders as a standard pie chart.

    Returns
    -------
    dict
        A Vega-Lite JSON specification, or None if the input data is invalid/empty.
    """
    if not isinstance(data, dict) or not data:
        return None

    plot_data = [{"category": k, "count": v} for k, v in data.items() if isinstance(v, (int, float))]
    if not plot_data:
        return None

    mark = {"type": "arc", "tooltip": True}
    if donut:
        mark["innerRadius"] = 50

    spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": title,
        "description": title,
        "data": {"values": plot_data},
        "mark": mark,
        "encoding": {
            "theta": {"field": "count", "type": "quantitative"},
            "color": {"field": "category", "type": "nominal"},
            "tooltip": [
                {"field": "category", "type": "nominal", "title": category_label},
                {"field": "count", "type": "quantitative", "title": value_label}
            ]
        }
    }

    return spec

def vega_to_html(vega_spec: Dict[str, Any]) -> str:
    """
    Wrap a Vega-Lite specification in a standalone HTML page with the vega-embed library.

    Parameters
    ----------
    vega_spec : dict
        The Vega-Lite JSON specification.

    Returns
    -------
    str
        A standalone HTML string that renders the chart.
    """
    import json
    spec_json = json.dumps(vega_spec)
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Vega-Lite Chart</title>
    <!-- Import Vega & Vega-Lite (does not have to be from CDN) -->
    <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f8f9fa;
        }}
        #vis {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div id="vis"></div>

    <script type="text/javascript">
        var spec = {spec_json};
        vegaEmbed('#vis', spec).then(function(result) {{
            // Access the Vega view instance as result.view
        }}).catch(console.error);
    </script>
</body>
</html>'''
    return html
