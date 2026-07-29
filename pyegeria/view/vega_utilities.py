"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Utilities for generating Vega-Lite chart specifications from Egeria data structures.

Deliberately favors Vega-Lite over Mermaid for anything chart-like (Vega-Lite
renders visually richer output and covers far more chart types than Mermaid's
handful of text-DSL diagram kinds; Mermaid stays the right choice only for
structural graphs it already owns — entity/relationship diagrams, mind maps).
Named generators below cover the chart shapes known to be needed today
(bar/pie/line/area/scatter/funnel); `generate_vega_chart` is a low-level
escape hatch for anything else a caller needs that doesn't have a named
helper yet — future chart-type needs aren't fully known in advance, so callers
are not blocked waiting for a dedicated function to be added here.
"""

from typing import Dict, List, Any, Optional, Union

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


def _multiseries_spec(
    records: List[Dict[str, Any]],
    x_field: str,
    y_fields: Union[str, List[str]],
    mark: Union[str, Dict[str, Any]],
    title: str,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    x_type: str = "nominal",
) -> Optional[Dict[str, Any]]:
    """Shared spec builder for line/area charts. Accepts wide-format records
    (one dict per x-value, with one or more numeric y fields) and uses
    Vega-Lite's `fold` transform to plot each y field as its own series —
    callers don't need to reshape their data into long format first."""
    if not isinstance(records, list) or not records:
        return None
    fields = [y_fields] if isinstance(y_fields, str) else list(y_fields)
    if not fields:
        return None

    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": title,
        "description": title,
        "data": {"values": records},
        "transform": [{"fold": fields, "as": ["series", "value"]}],
        "mark": mark,
        "encoding": {
            "x": {"field": x_field, "type": x_type, "title": x_label or x_field},
            "y": {"field": "value", "type": "quantitative", "title": y_label or "Value"},
            "color": {"field": "series", "type": "nominal", "title": "Series"},
            "tooltip": [
                {"field": x_field, "type": x_type, "title": x_label or x_field},
                {"field": "series", "type": "nominal"},
                {"field": "value", "type": "quantitative"},
            ],
        },
    }


def generate_vega_line_chart(
    records: List[Dict[str, Any]],
    x_field: str,
    y_fields: Union[str, List[str]],
    title: str,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    x_type: str = "nominal",
) -> Optional[Dict[str, Any]]:
    """
    Generate a Vega-Lite line chart specification, plotting one or more numeric
    fields as separate series over a shared x-axis (e.g. an asOfTime trend).

    Parameters
    ----------
    records : list[dict]
        Wide-format rows, e.g. [{"date": "2026-01", "assets": 100, "terms": 40}, ...].
    x_field : str
        The key in each record to use as the x-axis (e.g. "date").
    y_fields : str | list[str]
        One or more keys to plot as separate lines (e.g. ["assets", "terms"]).
    title : str
        The title of the chart.
    x_label, y_label : str, optional
        Axis titles; default to x_field / "Value".
    x_type : str
        Vega-Lite type for the x field — "temporal" for real dates, "nominal"
        (default) for pre-formatted labels like asOfTime snapshot labels.

    Returns
    -------
    dict
        A Vega-Lite JSON specification, or None if the input data is invalid/empty.
    """
    return _multiseries_spec(records, x_field, y_fields, "line", title, x_label, y_label, x_type)


def generate_vega_area_chart(
    records: List[Dict[str, Any]],
    x_field: str,
    y_fields: Union[str, List[str]],
    title: str,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    x_type: str = "nominal",
    stacked: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    Generate a Vega-Lite area chart specification — the same shape as
    generate_vega_line_chart, useful for showing composition changing over
    time (e.g. governed vs ungoverned share of the catalog by snapshot).

    Parameters
    ----------
    stacked : bool
        If True (default), series are stacked. If False, areas overlap
        (each drawn from 0), useful when series should be compared directly
        rather than summed.
    """
    mark = {"type": "area", "opacity": 0.85 if stacked else 0.6}
    spec = _multiseries_spec(records, x_field, y_fields, mark, title, x_label, y_label, x_type)
    if spec and not stacked:
        spec["encoding"]["y"]["stack"] = None
    return spec


def generate_vega_scatter_chart(
    records: List[Dict[str, Any]],
    x_field: str,
    y_field: str,
    title: str,
    color_field: Optional[str] = None,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Generate a Vega-Lite scatter plot specification for exploring a
    relationship between two numeric fields (e.g. asset count vs. governance
    coverage, one point per snapshot or per zone).

    Parameters
    ----------
    records : list[dict]
        Rows containing at least x_field and y_field (numeric), and
        color_field if given.
    color_field : str, optional
        A field (numeric or categorical) to color points by.

    Returns
    -------
    dict
        A Vega-Lite JSON specification, or None if the input data is invalid/empty.
    """
    if not isinstance(records, list) or not records:
        return None

    encoding = {
        "x": {"field": x_field, "type": "quantitative", "title": x_label or x_field},
        "y": {"field": y_field, "type": "quantitative", "title": y_label or y_field},
        "tooltip": [
            {"field": x_field, "type": "quantitative"},
            {"field": y_field, "type": "quantitative"},
        ],
    }
    if color_field:
        encoding["color"] = {"field": color_field, "type": "nominal"}
        encoding["tooltip"].append({"field": color_field, "type": "nominal"})

    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": title,
        "description": title,
        "data": {"values": records},
        "mark": {"type": "point", "filled": True, "tooltip": True},
        "encoding": encoding,
    }


def generate_vega_funnel_chart(
    stages: Dict[str, Any],
    title: str,
    stage_label: str = "Stage",
    value_label: str = "Count",
) -> Optional[Dict[str, Any]]:
    """
    Generate a Vega-Lite funnel-style chart from ordered stage counts (e.g.
    Cataloged -> Documented -> Classified -> Lineage-traced -> AI-Ready).

    Vega-Lite has no native funnel mark; this renders the standard practical
    substitute — ordered horizontal bars, widest-first, each annotated with
    its percentage of the first stage — rather than a true trapezoid funnel
    shape. Stage order is preserved exactly as given (not sorted by value).

    Parameters
    ----------
    stages : dict
        Ordered {stage_name: count}, first stage is the funnel's base (100%).

    Returns
    -------
    dict
        A Vega-Lite JSON specification, or None if the input data is invalid/empty.
    """
    if not isinstance(stages, dict) or not stages:
        return None

    stage_names = list(stages.keys())
    base = None
    plot_data = []
    for name in stage_names:
        val = stages[name]
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            continue
        if base is None:
            base = val
        pct = round(100 * val / base, 1) if base else 0
        plot_data.append({"stage": name, "count": val, "pctOfFirst": pct})
    if not plot_data:
        return None

    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": title,
        "description": title,
        "data": {"values": plot_data},
        "mark": {"type": "bar", "tooltip": True},
        "encoding": {
            "y": {"field": "stage", "type": "nominal", "sort": stage_names, "title": stage_label},
            "x": {"field": "count", "type": "quantitative", "title": value_label},
            "color": {"field": "stage", "type": "nominal", "sort": stage_names, "legend": None},
            "tooltip": [
                {"field": "stage", "type": "nominal", "title": stage_label},
                {"field": "count", "type": "quantitative", "title": value_label},
                {"field": "pctOfFirst", "type": "quantitative", "title": "% of first stage"},
            ],
        },
    }


def generate_vega_chart(
    values: List[Dict[str, Any]],
    mark: Union[str, Dict[str, Any]],
    encoding: Dict[str, Any],
    title: str,
    description: Optional[str] = None,
    transform: Optional[List[Dict[str, Any]]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Low-level escape hatch: assemble a Vega-Lite spec envelope around a
    caller-supplied mark and encoding, for chart shapes that don't have a
    named generator above. No validation of Vega-Lite mark/encoding
    semantics is performed — that's on the caller; this only assembles the
    envelope ($schema/data/title) consistently with the named generators.

    Parameters
    ----------
    values : list[dict]
        The data rows (becomes data.values).
    mark : str | dict
        A Vega-Lite mark type (e.g. "bar") or mark definition object.
    encoding : dict
        A Vega-Lite encoding object (x/y/color/tooltip/... channels).
    transform : list[dict], optional
        Vega-Lite transform steps (e.g. a fold/aggregate/filter), if needed.

    Returns
    -------
    dict
        A Vega-Lite JSON specification, or None if values is empty/invalid.
    """
    if not isinstance(values, list) or not values:
        return None
    if not mark or not isinstance(encoding, dict) or not encoding:
        return None

    spec: Dict[str, Any] = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": title,
        "description": description or title,
        "data": {"values": values},
        "mark": mark,
        "encoding": encoding,
    }
    if transform:
        spec["transform"] = transform
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
