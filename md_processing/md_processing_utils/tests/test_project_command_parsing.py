import pytest

from md_processing.md_processing_utils.common_md_proc_utils import parse_upsert_command, parse_view_command
from md_processing.md_processing_utils.tests.command_parsing_helpers import FakeEgeriaClient


@pytest.mark.parametrize(
    "command, object_type, action, exists",
    [
        ("Create Project", "Project", "Create", False),
        ("Update Project", "Project", "Update", True),
        ("Create Campaign", "Campaign", "Create", False),
        ("Update Campaign", "Campaign", "Update", True),
        ("Create Task", "Task", "Create", False),
        ("Update Task", "Task", "Update", True),
        ("Create Study Project", "Study Project", "Create", False),
        ("Update Study Project", "Study Project", "Update", True),
        ("Create Personal Project", "Personal Project", "Create", False),
        ("Update Personal Project", "Personal Project", "Update", True),
    ],
)
def test_project_upsert_parsing_skips_optional_attrs(command, object_type, action, exists):
    txt = f"# {command}\n## Display Name\nExample {object_type}\n___"
    parsed = parse_upsert_command(FakeEgeriaClient(exists), object_type, action, txt)

    assert parsed["valid"] is True
    attributes = parsed["attributes"]
    assert attributes["Display Name"]["value"] == f"Example {object_type}"
    assert attributes["Status"]["value"] == "ACTIVE"
    assert "Description" not in attributes


@pytest.mark.parametrize(
    "command, object_type",
    [
        ("Link Parent Project", "Parent Project"),
        ("Link Project Dependency", "Project Dependency"),
    ],
)
def test_project_link_parsing_skips_optional_attrs(command, object_type):
    txt = "# {command}\n## Parent Project\nParent A\n## Child Project\nChild B\n___".format(
        command=command
        )
    parsed = parse_view_command(FakeEgeriaClient(True), object_type, "Link", txt)

    assert parsed["valid"] is True
    attributes = parsed["attributes"]
    assert attributes["Parent Project"]["value"] == "Parent A"
    assert attributes["Child Project"]["value"] == "Child B"
    assert "Description" not in attributes
    assert "Label" not in attributes
