import json

from md_processing.md_processing_utils.compact_loader import load_compact_specs_from_dir


def test_load_compact_specs_preserves_custom_attributes_and_attribute_definitions(tmp_path):
    compact_payload = {
        "attribute_definitions": {
            "Blueprint": {
                "variable_name": "blueprint",
                "style": "Reference Name",
                "existing_element": "SolutionBlueprint",
            },
            "Component1": {
                "variable_name": "component1",
                "style": "Reference Name",
                "existing_element": "SolutionComponent",
            },
        },
        "bundles": {
            "Collection Membership": {
                "inherits": "",
                "own_attributes": [],
            }
        },
        "commands": {
            "Link Solution Component to Blueprint": {
                "display_name": "Link Solution Component to Blueprint",
                "family": "Solution Architect",
                "verb": "Link",
                "upsert": False,
                "attach": False,
                "find_method": "",
                "find_constraints": "",
                "extra_find": "",
                "extra_constraints": "",
                "OM_TYPE": "CollectionMembership",
                "bundle": "Collection Membership",
                "custom_attributes": ["Blueprint", "Component1"],
            }
        },
    }

    file_path = tmp_path / "commands_solution_architect_compact.json"
    file_path.write_text(json.dumps(compact_payload), encoding="utf-8")

    specs = load_compact_specs_from_dir(str(tmp_path))
    spec = specs["Link Solution Component to Blueprint"]

    assert spec["custom_attributes"] == ["Blueprint", "Component1"]
    assert "Blueprint" in spec["attribute_definitions"]
    assert "Component1" in spec["attribute_definitions"]
    assert spec["attribute_definitions"]["Blueprint"]["existing_element"] == "SolutionBlueprint"

