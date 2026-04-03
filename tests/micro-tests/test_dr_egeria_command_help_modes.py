import os
import tempfile
from types import SimpleNamespace

import builtins

from commands.cat import dr_egeria_command_help as mod

class FakeClient:
    def __init__(self, *a, **kw):
        pass
    def create_egeria_bearer_token(self, *a, **kw):
        return "token"
    def find_glossary_terms(self, search_string, page_size=500, output_format=None, glossary_guid=None):
        # Return two fake terms with Markdown usage table
        term1 = {
            "elementHeader": {"guid": "g1"},
            "properties": {
                "displayName": "Create Widget",
                "description": "Create a widget.",
                "usage": "| ColA | ColB |\n|---|---|\n| a | b |"
            }
        }
        term2 = {
            "elementHeader": {"guid": "g2"},
            "properties": {
                "displayName": "Delete Widget",
                "description": "Delete a widget.",
                "usage": "| A | B |\n|---|---|\n| 1 | 2 |"
            }
        }
        return [term2, term1]  # out of order to test sorting
    def get_guid_for_name(self, name):
        return "guid123"
    def close_session(self):
        pass

def test_modes_md_and_mdhtml(tmp_path, monkeypatch):
    # Redirect outbox to temp dir
    monkeypatch.setenv("EGERIA_ROOT_PATH", str(tmp_path))
    monkeypatch.setenv("EGERIA_OUTBOX_PATH", ".")

    # Patch EgeriaTech with fake
    monkeypatch.setattr(mod, "EgeriaTech", FakeClient)

    # Run md mode
    mod.display_command_terms(search_string="*", output_format="TABLE", mode="md")

    # Verify an md file created
    files = list(tmp_path.glob("Command-Help-*-md.md"))
    assert files, "Expected an md file to be generated"
    content = files[0].read_text(encoding="utf-8")
    assert "# Dr.Egeria Commands" in content
    assert "## Create Widget" in content and "## Delete Widget" in content
    assert "| ColA | ColB |" in content

    # Run md-html mode
    mod.display_command_terms(search_string="*", output_format="TABLE", mode="md-html")
    files_html = list(tmp_path.glob("Command-Help-*-md-html.md"))
    assert files_html, "Expected an md-html file to be generated"
    html_content = files_html[-1].read_text(encoding="utf-8")
    assert "<table>" in html_content and "</table>" in html_content
    # Ensure usage converted to HTML (table rows present or pre fallback)
    assert ("<thead>" in html_content) or ("<pre>" in html_content)
