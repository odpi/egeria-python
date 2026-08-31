"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a generic data view screen to display sample data (up to 10 rows)
   for a selected data element from Shop for Data in My Profile App.
"""

import json
from typing import Any, List, Dict, Union, Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Container
from textual.screen import ModalScreen
from textual.widgets import DataTable, Header, Footer, Static, Label, Button


class GenericDataViewScreen(ModalScreen):
    """Generic Data View Modal Screen for displaying sample data (max 10 rows)
    with Key and Value columns for a selected data source or data element.
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("b", "back", "Go back"),
        ("escape", "back", "Back"),
        ("return", "back", "Back"),
        ("s", "subscribe", "Subscribe to Data Source"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(
        self,
        sample_data: Any = None,
        data_element_name: str = "",
        data_element_qualified_name: str = "",
        view_server: str = "",
        platform_url: str = "",
        user_name: str = "",
        user_password: str = "",
        max_rows: int = 10,
        *args,
        **kwargs,
    ):
        """Initialize the GenericDataViewScreen.

        Parameters
        ----------
        sample_data : Any
            Sample data to display. Accepts a list of dicts or a dict.
        data_element_name : str
            Display name of the data element / data source being sampled.
        data_element_qualified_name : str
            Qualified name of the data element / data source.
        view_server : str
            Egeria view server name.
        platform_url : str
            Egeria platform URL.
        user_name : str
            User name.
        user_password : str
            User password.
        max_rows : int
            Maximum number of rows to display (default 10).
        """
        super().__init__(id="generic_data_view_screen", *args, **kwargs)
        self.sample_data = sample_data
        self.data_element_name = data_element_name or "Selected Data Element"
        self.data_element_qualified_name = data_element_qualified_name or ""
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_name = user_name
        self.user_password = user_password
        self.max_rows = max_rows
        self.data_table: DataTable = DataTable(id="generic_data_view_table")

    def compose(self) -> ComposeResult:
        """Compose UI components for the Generic Data View screen."""
        self.title = "Shop for Data - Sample Data View"
        self.sub_title = self.data_element_name

        yield Header(show_clock=True)
        yield Static(
            f"Sample Data View: {self.data_element_name} (Max {self.max_rows} Rows)",
            id="generic_data_view_title",
            classes="span-3",
        )
        yield Static(
            f"Qualified Name: {self.data_element_qualified_name}" if self.data_element_qualified_name else "",
            id="generic_data_view_subtitle",
        )
        yield ScrollableContainer(
            self.data_table,
            id="generic_data_view_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Populate the data table with Key and Value rows up to max_rows."""
        self.data_table.cursor_type = "row"
        self.data_table.zebra_stripes = True
        self.data_table.add_columns("Key", "Value")

        parsed_rows = self.parse_sample_data(self.sample_data, self.max_rows)
        if not parsed_rows:
            self.data_table.add_row("No data", "No sample data available for this data element")
        else:
            for key, val in parsed_rows:
                self.data_table.add_row(str(key), str(val))

    @staticmethod
    def parse_sample_data(raw_data: Any, max_rows: int = 10) -> List[tuple]:
        """Format raw sample data into a list of (Key, Value) tuples up to max_rows.

        Supports:
        - dict: key-value pairs (or wrapped {"data": [...]})
        - list of dicts: each dict converted to key/value representation
        - other fallback types (strings, lists, etc.)
        """
        if raw_data is None:
            return []

        rows: List[tuple] = []

        # Check if dict wraps a list in standard response format e.g. {"data": [...], "kind": ...}
        if isinstance(raw_data, dict) and "data" in raw_data and isinstance(raw_data["data"], list):
            raw_data = raw_data["data"]

        if isinstance(raw_data, dict):
            # Format: dict -> Key / Value pairs up to max_rows
            items = list(raw_data.items())[:max_rows]
            for key, value in items:
                formatted_val = GenericDataViewScreen._format_value(value)
                rows.append((str(key), formatted_val))

        elif isinstance(raw_data, list):
            # Format: list with dicts (or other items) within list elements up to max_rows
            items = raw_data[:max_rows]
            for idx, item in enumerate(items):
                if isinstance(item, dict):
                    # Check for explicit Key/Value keys
                    if "Key" in item and "Value" in item:
                        rows.append((str(item["Key"]), GenericDataViewScreen._format_value(item["Value"])))
                    elif "key" in item and "value" in item:
                        rows.append((str(item["key"]), GenericDataViewScreen._format_value(item["value"])))
                    elif len(item) == 1:
                        # Single key-value pair in dict
                        k, v = next(iter(item.items()))
                        rows.append((str(k), GenericDataViewScreen._format_value(v)))
                    else:
                        # Multi-key dictionary record
                        # Look for common key identifiers
                        key_candidate = None
                        for cand in ["Display Name", "display_name", "Qualified Name", "qualified_name", "Name", "name", "ID", "id", "Key", "key"]:
                            if cand in item and item[cand]:
                                key_candidate = cand
                                break

                        if key_candidate:
                            row_key = str(item[key_candidate])
                            other_fields = {k: v for k, v in item.items() if k != key_candidate}
                            if other_fields:
                                row_val = ", ".join(f"{k}: {GenericDataViewScreen._format_value(v)}" for k, v in other_fields.items())
                            else:
                                row_val = str(item[key_candidate])
                            rows.append((row_key, row_val))
                        else:
                            row_key = f"Row {idx + 1}"
                            row_val = ", ".join(f"{k}: {GenericDataViewScreen._format_value(v)}" for k, v in item.items())
                            rows.append((row_key, row_val))
                elif isinstance(item, (tuple, list)):
                    if len(item) >= 2:
                        rows.append((str(item[0]), GenericDataViewScreen._format_value(item[1])))
                    elif len(item) == 1:
                        rows.append((f"Row {idx + 1}", GenericDataViewScreen._format_value(item[0])))
                    else:
                        rows.append((f"Row {idx + 1}", ""))
                else:
                    rows.append((f"Row {idx + 1}", str(item)))

        elif isinstance(raw_data, str):
            rows.append(("Sample Data", raw_data))
        else:
            rows.append(("Sample Data", str(raw_data)))

        return rows[:max_rows]

    @staticmethod
    def _format_value(val: Any) -> str:
        """Format a single value for display in DataTable."""
        if val is None:
            return ""
        if isinstance(val, (dict, list)):
            try:
                return json.dumps(val)
            except Exception:
                return str(val)
        return str(val)

    def action_quit(self) -> None:
        """Quit action handler."""
        self.dismiss(210)

    def action_back(self) -> None:
        """Back action handler."""
        self.dismiss(200)

    def action_subscribe(self) -> None:
        """Subscribe action handler. Returns 211 with element details."""
        self.dismiss([211, self.data_element_name, self.data_element_qualified_name])


# Alias DataViewScreen for convenience
DataViewScreen = GenericDataViewScreen
