import json

from commands.tech.gen_report_specs import build_format_sets_from_commands
from pyegeria.view.base_report_formats import get_report_spec_match


def _make_compact_payload():
    return {
        "attribute_definitions": {
            "Description": {
                "variable_name": "description",
                "level": "Basic",
            },
            "Status": {
                "variable_name": "status",
                "level": "Basic",
            },
            "Version Identifier": {
                "variable_name": "version_identifier",
                "level": "Basic",
            },
            "Journal Entry": {
                "variable_name": "journal_entry",
                "level": "Basic",
            },
            "Search Keywords": {
                "variable_name": "search_keywords",
                "level": "Basic",
            },
            "Request ID": {
                "variable_name": "request_id",
                "level": "Basic",
            },
            "Category": {
                "variable_name": "category",
                "level": "Basic",
            },
            "URL": {
                "variable_name": "url",
                "level": "Basic",
            },
            "Qualified Name": {
                "variable_name": "qualified_name",
                "level": "Basic",
            },
            "GUID": {
                "variable_name": "guid",
                "level": "Basic",
            },
            "Display Name": {
                "variable_name": "display_name",
                "level": "Basic",
            },
        },
        "bundles": {
            "Test Bundle": {
                "inherits": None,
                "own_attributes": [
                    "Description",
                    "Status",
                    "Version Identifier",
                    "Journal Entry",
                    "Search Keywords",
                    "Request ID",
                    "Category",
                    "URL",
                    "Qualified Name",
                    "GUID",
                    "Display Name",
                ],
            }
        },
        "commands": {
            "Create Widget": {
                "display_name": "Create Widget",
                "family": "Testing",
                "verb": "Create",
                "find_method": "WidgetManager.find_widgets",
                "find_constraints": "",
                "bundle": "Test Bundle",
                "custom_attributes": [],
            }
        },
    }


def _get_format(fs, output_type: str):
    matched = get_report_spec_match(fs, output_type)
    return matched["formats"]


def test_generated_report_specs_emit_list_and_all_with_curated_columns(tmp_path):
    file_path = tmp_path / "commands_testing_compact.json"
    file_path.write_text(json.dumps(_make_compact_payload()), encoding="utf-8")

    sets = build_format_sets_from_commands(file_path)
    fs = sets["Widget-DrE-Basic"]

    list_format = _get_format(fs, "LIST")
    all_format = _get_format(fs, "REPORT")

    list_keys = [col["key"] for col in list_format["attributes"]]
    all_keys = [col["key"] for col in all_format["attributes"]]

    assert list_format["types"] == ["LIST"]
    assert all_format["types"] == ["ALL"]

    for removed_key in ("journal_entry", "search_keywords", "request_id"):
        assert removed_key not in list_keys
        assert removed_key not in all_keys

    # url excluded from LIST only; still present in ALL
    assert "url" not in list_keys
    assert "url" in all_keys

    assert list_keys[:3] == ["display_name", "qualified_name", "guid"]
    assert list_keys[-3:] == ["version_identifier", "status", "category"]
    assert all_keys == [
        "description",
        "status",
        "version_identifier",
        "category",
        "url",
        "qualified_name",
        "guid",
        "display_name",
    ]


def test_generated_report_specs_preserve_explicit_default_types_override(tmp_path):
    file_path = tmp_path / "commands_testing_compact.json"
    file_path.write_text(json.dumps(_make_compact_payload()), encoding="utf-8")

    sets = build_format_sets_from_commands(file_path, default_types=["FORM"])
    fs = sets["Widget-DrE-Basic"]

    assert len(fs.formats) == 1
    assert fs.formats[0].types == ["FORM"]
    assert [col.key for col in fs.formats[0].attributes] == [
        "description",
        "status",
        "version_identifier",
        "category",
        "url",
        "qualified_name",
        "guid",
        "display_name",
    ]

