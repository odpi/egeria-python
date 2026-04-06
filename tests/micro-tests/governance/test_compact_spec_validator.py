import json

from click.testing import CliRunner

from commands.tech.validate_compact_specs import main as validate_compact_specs_cli
from md_processing.md_processing_utils.compact_spec_validator import (
    _extract_typedef_names_by_category,
    collect_derived_processing_types,
    derive_processing_type_name,
    _extract_typedef_names,
    _normalize_bearer_token,
    fetch_valid_om_types,
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
                        "some_unknown_filter": "GovernanceDefinitionStatus",
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


def test_validate_compact_spec_file_does_not_warn_for_intentional_classification_names_key(tmp_path):
    payload = {
        "commands": {
            "Create Data Sharing Agreement": {
                "find_constraints": json.dumps(
                    {
                        "metadata_element_type": "Agreement",
                        "classification_names": ["DataSharingAgreement"],
                    }
                )
            }
        }
    }
    file_path = tmp_path / "compact_classification_names.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    findings = validate_compact_spec_file(file_path)
    codes = {f.code for f in findings}
    assert "FIND_CONSTRAINTS_KEYS_IGNORED_BY_PROCESSING" not in codes


def test_validate_compact_spec_file_does_not_warn_for_intentional_classification_name_key(tmp_path):
    payload = {
        "commands": {
            "Create Data Sharing Agreement": {
                "find_constraints": json.dumps(
                    {
                        "metadata_element_type": "Agreement",
                        "classification_name": "DataSharingAgreement",
                    }
                )
            }
        }
    }
    file_path = tmp_path / "compact_classification_name.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    findings = validate_compact_spec_file(file_path)
    codes = {f.code for f in findings}
    assert "FIND_CONSTRAINTS_KEYS_IGNORED_BY_PROCESSING" not in codes


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


def test_validate_compact_spec_file_accepts_serverclient_find_method(tmp_path):
    payload = {
        "commands": {
            "Create Comment": {
                "find_method": "ServerClient.find_comments",
                "find_constraints": json.dumps({"metadata_element_type": "Comment"}),
            }
        }
    }
    file_path = tmp_path / "compact_find_method_serverclient_valid.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    findings = validate_compact_spec_file(file_path)
    codes = {f.code for f in findings}
    assert "FIND_METHOD_CLASS_NOT_FOUND" not in codes


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


def test_validate_compact_spec_file_warns_when_om_type_missing(tmp_path):
    payload = {
        "commands": {
            "Create Governance Strategy": {
                "find_constraints": json.dumps({"metadata_element_type": "GovernanceStrategy"})
            }
        }
    }
    file_path = tmp_path / "compact_missing_om_type.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    findings = validate_compact_spec_file(file_path)
    severities = {f.code: f.severity for f in findings}
    assert severities.get("OM_TYPE_MISSING") == "WARNING"


def test_validate_compact_spec_file_does_not_flag_mismatch_by_default(tmp_path):
    payload = {
        "commands": {
            "Create Governance Strategy": {
                "OM_TYPE": "Threat",
                "find_constraints": json.dumps({"metadata_element_type": "GovernanceStrategy"}),
            }
        }
    }
    file_path = tmp_path / "compact_mismatch_om_type.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    findings = validate_compact_spec_file(file_path)
    codes = {f.code for f in findings}
    assert "OM_TYPE_MISMATCH" not in codes


def test_validate_compact_spec_file_flags_mismatch_when_enabled(tmp_path):
    payload = {
        "commands": {
            "Create Governance Strategy": {
                "OM_TYPE": "Threat",
                "find_constraints": json.dumps({"metadata_element_type": "GovernanceStrategy"}),
            }
        }
    }
    file_path = tmp_path / "compact_mismatch_om_type_enabled.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    findings = validate_compact_spec_file(file_path, validate_derived_match=True)
    severities = {f.code: f.severity for f in findings}
    assert severities.get("OM_TYPE_MISMATCH") == "ERROR"


def test_validate_compact_spec_file_errors_when_om_type_not_in_valid_typedefs(tmp_path):
    payload = {
        "commands": {
            "Create Governance Strategy": {
                "OM_TYPE": "NotARealType",
                "find_constraints": json.dumps({"metadata_element_type": "NotARealType"}),
            }
        }
    }
    file_path = tmp_path / "compact_invalid_om_type.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    findings = validate_compact_spec_file(file_path, valid_om_types={"GovernanceStrategy", "Threat"})
    severities = {f.code: f.severity for f in findings}
    assert severities.get("OM_TYPE_INVALID") == "ERROR"


def test_collect_derived_processing_types_includes_command_rows(tmp_path):
    payload = {
        "commands": {
            "Create Governance Strategy": {
                "OM_TYPE": "GovernanceStrategy",
                "find_constraints": json.dumps({"metadata_element_type": "GovernanceStrategy"})
            }
        }
    }
    file_path = tmp_path / "compact_types.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    rows = collect_derived_processing_types(tmp_path)
    assert rows
    assert rows[0]["om_type"] == "GovernanceStrategy"
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
    result = runner.invoke(validate_compact_specs_cli, [str(tmp_path), "--format", "both", "--no-validate-om-types"])

    assert result.exit_code == 0
    assert "Errors:" in result.output
    assert '"findings"' in result.output
    assert '"derived_processing_types"' in result.output


def test_validate_compact_specs_cli_only_checks_mismatch_when_enabled(tmp_path):
    file_path = tmp_path / "compact.json"
    file_path.write_text(
        json.dumps(
            {
                "commands": {
                    "Create Governance Strategy": {
                        "OM_TYPE": "Threat",
                        "find_constraints": json.dumps({"metadata_element_type": "GovernanceStrategy"}),
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    runner = CliRunner()
    default_result = runner.invoke(
        validate_compact_specs_cli,
        [str(tmp_path), "--format", "json", "--no-validate-om-types"],
    )
    assert default_result.exit_code == 0
    assert "OM_TYPE_MISMATCH" not in default_result.output

    strict_result = runner.invoke(
        validate_compact_specs_cli,
        [
            str(tmp_path),
            "--format",
            "json",
            "--no-validate-om-types",
            "--validate-derived-match",
        ],
    )
    assert strict_result.exit_code != 0
    assert "OM_TYPE_MISMATCH" in strict_result.output


def test_fetch_valid_om_types_creates_bearer_token_before_typedef_calls(monkeypatch):
    class DummyValidMetadataManager:
        def __init__(self, server, url, user_id=None, user_pwd=None):
            self.calls = []

        def create_egeria_bearer_token(self, user_id, user_pwd):
            self.calls.append(("token", user_id, user_pwd))
            return "\n\"abc123\"\n"

        def set_bearer_token(self, token):
            self.calls.append(("set_token", token))

        def get_all_entity_defs(self, output_format="JSON"):
            self.calls.append(("entity", output_format))
            return [{"name": "Asset"}]

        def get_all_relationship_defs(self, output_format="JSON"):
            self.calls.append(("relationship", output_format))
            return [{"name": "SemanticAssignment"}]

        def get_all_classification_defs(self, output_format="JSON"):
            self.calls.append(("classification", output_format))
            return [{"name": "DataSharingAgreement"}]

        def close_session(self):
            self.calls.append(("close",))

    dummy_holder = {}

    def _factory(*args, **kwargs):
        inst = DummyValidMetadataManager(*args, **kwargs)
        dummy_holder["instance"] = inst
        return inst

    monkeypatch.setattr(
        "md_processing.md_processing_utils.compact_spec_validator.ValidMetadataManager",
        _factory,
    )

    types = fetch_valid_om_types("qs-view-server", "https://localhost:9443", "erinoverview", "secret")

    assert types == {"Asset", "SemanticAssignment", "DataSharingAgreement"}
    assert dummy_holder["instance"].calls[:5] == [
        ("token", "erinoverview", "secret"),
        ("set_token", "abc123"),
        ("entity", "JSON"),
        ("relationship", "JSON"),
        ("classification", "JSON"),
    ]


def test_normalize_bearer_token_strips_whitespace_and_quotes():
    assert _normalize_bearer_token("\n  \"token-value\" \t") == "token-value"


def test_fetch_valid_om_types_raises_for_failed_token(monkeypatch):
    class DummyValidMetadataManager:
        def __init__(self, server, url, user_id=None, user_pwd=None):
            self.calls = []

        def create_egeria_bearer_token(self, user_id, user_pwd):
            self.calls.append(("token", user_id, user_pwd))
            return "FAILED"

        def close_session(self):
            self.calls.append(("close",))

    monkeypatch.setattr(
        "md_processing.md_processing_utils.compact_spec_validator.ValidMetadataManager",
        DummyValidMetadataManager,
    )

    try:
        fetch_valid_om_types("qs-view-server", "https://localhost:9443", "erinoverview", "secret")
        assert False, "Expected RuntimeError for unusable token"
    except RuntimeError as exc:
        assert "usable bearer token" in str(exc)


def test_extract_typedef_names_supports_wrapped_payload_shapes():
    entity_payload = {"typeDefList": [{"name": "Asset"}]}
    rel_payload = {"typeDefs": [{"name": "SemanticAssignment"}]}
    elem_payload = {"elements": [{"name": "Project"}]}

    names = set()
    names |= _extract_typedef_names(entity_payload)
    names |= _extract_typedef_names(rel_payload)
    names |= _extract_typedef_names(elem_payload)

    assert names == {"Asset", "SemanticAssignment", "Project"}


def test_fetch_valid_om_types_handles_wrapped_typedef_responses(monkeypatch):
    class DummyValidMetadataManager:
        def __init__(self, server, url, user_id=None, user_pwd=None):
            self.calls = []

        def create_egeria_bearer_token(self, user_id, user_pwd):
            self.calls.append(("token", user_id, user_pwd))
            return "abc123"

        def set_bearer_token(self, token):
            self.calls.append(("set_token", token))

        def get_all_entity_defs(self, output_format="JSON"):
            self.calls.append(("entity", output_format))
            return {"typeDefList": [{"name": "Asset"}]}

        def get_all_relationship_defs(self, output_format="JSON"):
            self.calls.append(("relationship", output_format))
            return {"typeDefs": [{"name": "SemanticAssignment"}]}

        def get_all_classification_defs(self, output_format="JSON"):
            self.calls.append(("classification", output_format))
            return {"elements": [{"name": "DataSharingAgreement"}]}

        def close_session(self):
            self.calls.append(("close",))

    monkeypatch.setattr(
        "md_processing.md_processing_utils.compact_spec_validator.ValidMetadataManager",
        DummyValidMetadataManager,
    )

    types = fetch_valid_om_types("qs-view-server", "https://localhost:9443", "erinoverview", "secret")
    assert types == {"Asset", "SemanticAssignment", "DataSharingAgreement"}


def test_extract_typedef_names_by_category_filters_entity_and_relationship_defs():
    payload = {
        "typeDefs": [
            {"class": "OpenMetadataEntityDef", "category": "ENTITY_DEF", "name": "Asset"},
            {"class": "OpenMetadataRelationshipDef", "category": "RELATIONSHIP_DEF", "name": "SemanticAssignment"},
            {"class": "OpenMetadataClassificationDef", "category": "CLASSIFICATION_DEF", "name": "Confidentiality"},
        ]
    }

    names = _extract_typedef_names_by_category(payload, {"ENTITY_DEF", "RELATIONSHIP_DEF"})
    assert names == {"Asset", "SemanticAssignment"}


def test_fetch_valid_om_types_falls_back_to_get_all_entity_types_when_split_defs_empty(monkeypatch):
    class DummyValidMetadataManager:
        def __init__(self, server, url, user_id=None, user_pwd=None):
            self.calls = []

        def create_egeria_bearer_token(self, user_id, user_pwd):
            self.calls.append(("token", user_id, user_pwd))
            return "abc123"

        def set_bearer_token(self, token):
            self.calls.append(("set_token", token))

        def get_all_entity_defs(self, output_format="JSON"):
            self.calls.append(("entity_defs", output_format))
            return []

        def get_all_relationship_defs(self, output_format="JSON"):
            self.calls.append(("relationship_defs", output_format))
            return []

        def get_all_classification_defs(self, output_format="JSON"):
            self.calls.append(("classification_defs", output_format))
            return []

        def get_all_entity_types(self, output_format="JSON"):
            self.calls.append(("all_types", output_format))
            return [
                {"class": "OpenMetadataEntityDef", "category": "ENTITY_DEF", "name": "Asset"},
                {"class": "OpenMetadataRelationshipDef", "category": "RELATIONSHIP_DEF", "name": "SemanticAssignment"},
                {"class": "OpenMetadataClassificationDef", "category": "CLASSIFICATION_DEF", "name": "Confidentiality"},
            ]

        def close_session(self):
            self.calls.append(("close",))

    monkeypatch.setattr(
        "md_processing.md_processing_utils.compact_spec_validator.ValidMetadataManager",
        DummyValidMetadataManager,
    )

    types = fetch_valid_om_types("qs-view-server", "https://localhost:9443", "erinoverview", "secret")
    assert types == {"Asset", "SemanticAssignment", "Confidentiality"}


def test_fetch_valid_om_types_retries_with_alternate_loopback_host_when_empty(monkeypatch):
    class DummyValidMetadataManager:
        def __init__(self, server, url, user_id=None, user_pwd=None):
            self.url = url

        def create_egeria_bearer_token(self, user_id, user_pwd):
            return "abc123"

        def set_bearer_token(self, token):
            return None

        def get_all_entity_defs(self, output_format="JSON"):
            return []

        def get_all_relationship_defs(self, output_format="JSON"):
            return []

        def get_all_classification_defs(self, output_format="JSON"):
            return []

        def get_all_entity_types(self, output_format="JSON"):
            if "127.0.0.1" in self.url:
                return [
                    {"class": "OpenMetadataEntityDef", "category": "ENTITY_DEF", "name": "Asset"},
                    {"class": "OpenMetadataRelationshipDef", "category": "RELATIONSHIP_DEF", "name": "SemanticAssignment"},
                    {"class": "OpenMetadataClassificationDef", "category": "CLASSIFICATION_DEF", "name": "DataSharingAgreement"},
                ]
            return []

        def close_session(self):
            return None

    monkeypatch.setattr(
        "md_processing.md_processing_utils.compact_spec_validator.ValidMetadataManager",
        DummyValidMetadataManager,
    )

    types = fetch_valid_om_types("qs-view-server", "https://localhost:9443", "erinoverview", "secret")
    assert types == {"Asset", "SemanticAssignment", "DataSharingAgreement"}


def test_extract_typedef_names_by_category_supports_nested_wrapped_payload():
    payload = {
        "elements": [
            {
                "typeDefs": [
                    {"class": "OpenMetadataEntityDef", "category": "EntityDef", "name": "Asset"},
                    {"class": "OpenMetadataRelationshipDef", "category": "relationship def", "name": "SemanticAssignment"},
                ]
            }
        ]
    }

    names = _extract_typedef_names_by_category(payload, {"ENTITY_DEF", "RELATIONSHIP_DEF"})
    assert names == {"Asset", "SemanticAssignment"}


def test_fetch_valid_om_types_raises_when_no_types_discovered(monkeypatch):
    class DummyValidMetadataManager:
        def __init__(self, server, url, user_id=None, user_pwd=None):
            self.url = url

        def create_egeria_bearer_token(self, user_id, user_pwd):
            return "abc123"

        def set_bearer_token(self, token):
            return None

        def get_all_entity_defs(self, output_format="JSON"):
            return []

        def get_all_relationship_defs(self, output_format="JSON"):
            return []

        def get_all_classification_defs(self, output_format="JSON"):
            return []

        def get_all_entity_types(self, output_format="JSON"):
            return []

        def close_session(self):
            return None

    monkeypatch.setattr(
        "md_processing.md_processing_utils.compact_spec_validator.ValidMetadataManager",
        DummyValidMetadataManager,
    )

    try:
        fetch_valid_om_types("qs-view-server", "https://example.org:9443", "erinoverview", "secret")
        assert False, "Expected RuntimeError for zero discovered OM types"
    except RuntimeError as exc:
        assert "Zero OM types discovered" in str(exc)


def test_validate_compact_spec_file_allows_classification_placeholder(tmp_path):
    payload = {
        "commands": {
            "Create Study Project": {
                "OM_TYPE": "CLASSIFICATION",
                "find_constraints": json.dumps({"metadata_element_type": "Project"}),
            }
        }
    }
    file_path = tmp_path / "compact_classification_placeholder.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    findings = validate_compact_spec_file(file_path, valid_om_types={"Project", "Campaign"})
    codes = {f.code for f in findings}
    assert "OM_TYPE_INVALID" not in codes
    assert "OM_TYPE_CLASSIFICATION_PLACEHOLDER" in codes


def test_validate_compact_spec_file_does_not_warn_missing_om_type_for_report_family(tmp_path):
    payload = {
        "commands": {
            "Report": {
                "family": "Report",
                "find_constraints": "",
            }
        }
    }
    file_path = tmp_path / "compact_report_missing_om_type.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    findings = validate_compact_spec_file(file_path)
    codes = {f.code for f in findings}
    assert "OM_TYPE_MISSING" not in codes


def test_validate_compact_spec_file_does_not_warn_missing_om_type_for_dynamic_name_lookup(tmp_path):
    payload = {
        "commands": {
            "Link Term-Term Relationship": {
                "find_method": "name",
                "find_constraints": "",
            }
        }
    }
    file_path = tmp_path / "compact_dynamic_missing_om_type.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    findings = validate_compact_spec_file(file_path)
    codes = {f.code for f in findings}
    assert "OM_TYPE_MISSING" not in codes


