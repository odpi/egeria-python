#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Interactive Textual TUI to view Egeria Report Spec Schemas as a collapsible tree.
"""

import click
from textual.app import App, ComposeResult
from textual.widgets import Tree, Header, Footer
from rich.text import Text

from pyegeria.core.config import settings
from pyegeria.egeria_tech_client import EgeriaTech

class SchemaTreeApp(App):
    """A Textual App to display the schema attributes as an interactive tree."""
    
    TITLE = "Egeria Report Schema Explorer"
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("e", "expand_all", "Expand All"),
        ("c", "collapse_all", "Collapse All")
    ]
    
    def __init__(self, schema_data: list[dict], report_spec_name: str, **kwargs):
        super().__init__(**kwargs)
        self.schema_data = schema_data
        self.report_spec_name = report_spec_name
        self.tree_widget = None

    def compose(self) -> ComposeResult:
        yield Header()
        self.tree_widget = Tree(f"Schema for '{self.report_spec_name}'")
        self.tree_widget.root.expand()
        
        nodes = {"": self.tree_widget.root}
        
        for item in self.schema_data:
            path = item.get("attribute_path", "")
            data_type = item.get("data_type", "unknown")
            
            parts = path.split('.')
            current_path = ""
            
            for i, part in enumerate(parts):
                parent_path = current_path
                current_path = f"{current_path}.{part}" if current_path else part
                
                if current_path not in nodes:
                    is_leaf = (i == len(parts) - 1)
                    if is_leaf:
                        label = Text.assemble((f"{part}: ", ""), (f"{data_type}", "cyan"))
                        nodes[current_path] = nodes[parent_path].add_leaf(label)
                    else:
                        label = Text(part, style="bold")
                        nodes[current_path] = nodes[parent_path].add(label, expand=True)
                        
        yield self.tree_widget
        yield Footer()
        
    def action_expand_all(self) -> None:
        """Expand all nodes in the tree."""
        for node in self.tree_widget.root.children:
            self._expand_node(node)
            
    def _expand_node(self, node) -> None:
        if node.allow_expand:
            node.expand()
        for child in node.children:
            self._expand_node(child)
            
    def action_collapse_all(self) -> None:
        """Collapse all nodes in the tree."""
        for node in self.tree_widget.root.children:
            self._collapse_node(node)
            
    def _collapse_node(self, node) -> None:
        if node.allow_expand:
            node.collapse()
        for child in node.children:
            self._collapse_node(child)

@click.command(name="report-schema-tree", help="View a report spec schema as an interactive tree.")
@click.option("--report", "-r", "report_spec_name", required=True, help="Name of the Report Spec to inspect.")
@click.option("--search-string", "-s", default="*", help="Search string to use to fetch the sample element.")
@click.option("--exclude-system/--no-exclude-system", default=True, help="Exclude boilerplate system properties.")
def schema_tree_cmd(report_spec_name: str, search_string: str, exclude_system: bool):
    """Fetch the schema using get_report_spec_schema and display the Textual tree."""
    import os
    user = os.environ.get("EGERIA_USER", "erinoverview")
    password = os.environ.get("EGERIA_USER_PASSWORD", "secret")
    server = settings.Environment.egeria_view_server
    url = settings.Environment.egeria_view_server_url
    
    print(f"Fetching schema for '{report_spec_name}' from {server} @ {url}...")
    try:
        client = EgeriaTech(server, url, user_id=user, user_pwd=password)
        client.create_egeria_bearer_token()
        schema_data = client.get_report_spec_schema(
            report_spec_name=report_spec_name, 
            search_string=search_string, 
            exclude_system_properties=exclude_system
        )
        if not schema_data:
            print("No schema attributes discovered.")
            return
            
        if len(schema_data) == 1 and schema_data[0].get("attribute_path") == "Error":
            print(schema_data[0].get("data_type", "Unknown execution error."))
            return
            
        app = SchemaTreeApp(schema_data=schema_data, report_spec_name=report_spec_name)
        app.run()
    except Exception as e:
        print(f"Error fetching schema: {e}")

if __name__ == "__main__":
    schema_tree_cmd()
