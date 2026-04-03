import json

from click.testing import CliRunner

from commands.tech.validate_compact_specs import main as validate_compact_specs_cli
from md_processing.md_processing_utils.compact_spec_validator import (
    collect_derived_processing_types,
    derive_processing_type_name,
    validate_compact_spec_file,
    validate_compact_specs,
)


def test_derive_processing_type_name_prefers_metadata_element_type():
    derived = derive_processing_type_name(
        "Create Governance Strategy",
        {"metadata_element_type": "GovernanceStrategy", "metadata_element_types": ["Threat"]},
    )
    assert derived == "GovernanceStrategy"


def test_validate_compact_spec_file_warns_on_ignored_find_constraints_keys(tmp_path):
    payload = {
        "commands": {
            "Create Threat": {
                "find_constraints": json.dumps(
                    {
                        "metadata_element_type": "Threat",
                        "classification_name": "GovernanceDefinitionStatus",
                    }
                )
            }
        }
    }
    file_path = tmp_path / "compact.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    findings = validate_compact_spec_file(file_path)
    codes = {f.code for f in findings}
    assert "FIND_CONSTRAINTS_KEYS_IGNORED_BY_PROCESSING" in codes


def test_validate_compact_spec_file_errors_on_bad_find_constraints_json(tmp_path):
    payload = {
        "commands": {
            "Create Threat": {
                "find_constraints": "{bad-json"
            }
        }
    }
    file_path = tmp_path / "compact_bad.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    findings = validate_compact_spec_file(file_path)
    codes = {f.code for f in findings}
    assert "FIND_CONSTRAINTS_JSON_INVALID" in codes


def test_validate_compact_spec_file_singleton_metadata_element_types_is_warning(tmp_path):
    payload = {
        "commands": {
            "Create Threat": {
                "find_constraints": json.dumps({"metadata_element_types": ["Threat"]})
            }
        }
    }
    file_path = tmp_path / "compact_singleton.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    findings = validate_compact_spec_file(file_path)
    severities = {f.code: f.severity for f in findings}
    assert severities.get("METADATA_ELEMENT_TYPES_SINGLETON") == "WARNING"


def test_validate_compact_spec_file_accepts_resolvable_find_method(tmp_path):
    payload = {
        "commands": {
            "Create Threat": {
                "find_method": "GovernanceOfficer.find_governance_definitions",
                "find_constraints": json.dumps({"metadata_element_type": "Threat"}),
            }
        }
    }
    file_path = tmp_path / "compact_find_method_valid.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    findings = validate_compact_spec_file(file_path)
    codes = {f.code for f in findings}
    assert "FIND_METHOD_CLASS_NOT_FOUND" not in codes
    assert "FIND_METHOD_METHOD_NOT_FOUND" not in codes


def test_validate_compact_spec_file_errors_on_unresolvable_find_method_class(tmp_path):
    payload = {
        "commands": {
            "Create Threat": {
                "find_method": "NoSuchClass.find_governance_definitions",
                "find_constraints": json.dumps({"metadata_element_type": "Threat"}),
            }
        }
    }
    file_path = tmp_path / "compact_find_method_bad_class.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    findings = validate_compact_spec_file(file_path)
    codes = {f.code for f in findings}
    assert "FIND_METHOD_CLASS_NOT_FOUND" in codes


def test_collect_derived_processing_types_includes_command_rows(tmp_path):
    payload = {
        "commands": {
            "Create Governance Strategy": {
                "find_constraints": json.dumps({"metadata_element_type": "GovernanceStrategy"})
            }
        }
    }
    file_path = tmp_path / "compact_types.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    rows = collect_derived_processing_types(tmp_path)
    assert rows
    assert rows[0]["derived_processing_type"] == "GovernanceStrategy"


def test_validate_compact_specs_warns_on_duplicate_command_names(tmp_path):
    one = tmp_path / "a.json"
    two = tmp_path / "b.json"
    one.write_text(json.dumps({"commands": {"Create Threat": {}}}), encoding="utf-8")
    two.write_text(json.dumps({"commands": {"Create Threat": {}}}), encoding="utf-8")

    findings = validate_compact_specs(tmp_path)
    codes = {f.code for f in findings}
    assert "DUPLICATE_COMMAND_NAME" in codes


def test_validate_compact_specs_cli_supports_both_output_format(tmp_path):
    file_path = tmp_path / "compact.json"
    file_path.write_text(json.dumps({"commands": {"Create Threat": {"find_constraints": ""}}}), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(validate_compact_specs_cli, [str(tmp_path), "--format", "both"])

    assert result.exit_code == 0
    assert "Errors:" in result.output
    assert '"findings"' in result.output
    assert '"derived_processing_types"' in result.output

