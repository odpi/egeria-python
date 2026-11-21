# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""scripts/audit_properties_class_bodies.py: finds built request bodies whose `properties.class`
silently drops keys (TR-89), names a parent class, or has no class at all.

Every test plants a tiny source file in tmp_path and audits only that, so no repo, Egeria checkout
or server is needed. The parent map is passed in, so the hierarchy is fixed by the test.
"""
import importlib.util
import os
import sys
import textwrap

import pytest

_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "audit_properties_class_bodies.py")


@pytest.fixture(scope="module")
def audit():
    spec = importlib.util.spec_from_file_location("audit_properties_class_bodies", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # dataclasses look the module up by name
    spec.loader.exec_module(mod)
    return mod


PARENTS = {
    "SourceControlLibraryProperties": "SoftwareCapabilityProperties",
    "SoftwareCapabilityProperties": "ReferenceableProperties",
    "ReferenceableProperties": "EntityProperties",
    "EntityProperties": None,  # a complete chain: every superclass was scanned
}


def _run(audit, tmp_path, source, parents=PARENTS):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "planted.py").write_text(textwrap.dedent(source))
    return audit.audit_repo(str(repo), parents=parents)


def _kinds(result):
    return sorted(f.kind for f in result.findings)


def test_finds_tr89_library_type_dropped(audit, tmp_path):
    result = _run(audit, tmp_path, """
        def publish(client, qn):
            body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "SoftwareCapabilityProperties",
                    "qualifiedName": qn,
                    "libraryType": "git",
                },
            }
            return client.create(body)
    """)
    unread = [f for f in result.findings if f.kind == audit.UNREAD_KEYS]
    assert len(unread) == 1
    assert unread[0].cls == "SoftwareCapabilityProperties"
    assert unread[0].keys == ("libraryType",)
    assert unread[0].line == 5  # the line of the properties dict literal
    assert "SourceControlLibraryProperties" in unread[0].fix  # the one class that reads libraryType


def test_key_added_after_the_literal_is_seen(audit, tmp_path):
    result = _run(audit, tmp_path, """
        def publish(client, qn):
            props = {"class": "SoftwareCapabilityProperties", "qualifiedName": qn}
            props["libraryType"] = "git"
            client.create({"class": "NewElementRequestBody", "properties": props})
    """)
    unread = [f for f in result.findings if f.kind == audit.UNREAD_KEYS]
    assert [f.keys for f in unread] == [("libraryType",)]


def test_clean_body_finds_nothing(audit, tmp_path):
    result = _run(audit, tmp_path, """
        def publish(client, qn):
            body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "SourceControlLibraryProperties",
                    "qualifiedName": qn,
                    "libraryType": "git",
                },
            }
            return client.create(body)
    """)
    assert result.findings == []
    assert result.unclassified == []
    assert result.bodies_checked == 1


def test_finds_properties_with_no_class(audit, tmp_path):
    result = _run(audit, tmp_path, """
        def publish(client, qn):
            return client.create({"class": "NewElementRequestBody",
                                  "properties": {"qualifiedName": qn, "displayName": "x"}})
    """)
    assert _kinds(result) == [audit.NO_CLASS]
    assert result.findings[0].keys == ("displayName", "qualifiedName")


def test_reports_parent_class_from_type_name(audit, tmp_path):
    result = _run(audit, tmp_path, """
        def publish(client, qn):
            return client.create({"class": "NewElementRequestBody",
                                  "properties": {"class": "SoftwareCapabilityProperties",
                                                 "typeName": "SourceControlLibrary",
                                                 "qualifiedName": qn}})
    """)
    assert _kinds(result) == [audit.PARENT_CLASS]
    f = result.findings[0]
    assert f.cls == "SoftwareCapabilityProperties"
    assert "SourceControlLibraryProperties" in f.fix


def test_reports_parent_class_from_function_name(audit, tmp_path):
    result = _run(audit, tmp_path, """
        def create_source_control_library(client, qn):
            return client.create({"class": "NewElementRequestBody",
                                  "properties": {"class": "SoftwareCapabilityProperties", "qualifiedName": qn}})
    """)
    assert _kinds(result) == [audit.PARENT_CLASS]


def test_pass_through_properties_are_skipped_not_guessed(audit, tmp_path):
    result = _run(audit, tmp_path, """
        def create_thing(client, properties):
            return client.create({"class": "NewElementRequestBody", "properties": properties})
    """)
    assert result.findings == []
    assert result.pass_through == 1


def test_unresolved_class_is_unclassified(audit, tmp_path):
    result = _run(audit, tmp_path, """
        def create_thing(client, type_name, qn):
            return client.create({"class": "NewElementRequestBody",
                                  "properties": {"class": f"{type_name}Properties", "qualifiedName": qn}})
    """)
    assert result.findings == []
    assert len(result.unclassified) == 1
    assert "type_name" in result.unclassified[0].reason


def test_string_class_bound_in_scope_is_resolved(audit, tmp_path):
    result = _run(audit, tmp_path, """
        def publish(client, qn):
            cls = "SoftwareCapabilityProperties"
            return client.create({"class": "NewElementRequestBody",
                                  "properties": {"class": cls, "qualifiedName": qn, "libraryType": "git"}})
    """)
    assert [f.keys for f in result.findings if f.kind == audit.UNREAD_KEYS] == [("libraryType",)]


def test_parent_inference_without_a_parent_map(audit, tmp_path):
    """No Egeria checkout: a strict superset of fields of the same kind stands in for 'subclass'."""
    result = _run(audit, tmp_path, """
        def create_source_control_library(client, qn):
            return client.create({"class": "NewElementRequestBody",
                                  "properties": {"class": "SoftwareCapabilityProperties", "qualifiedName": qn}})
    """, parents=None)
    assert _kinds(result) == [audit.PARENT_CLASS]
    assert "inferred" in result.findings[0].detail


def test_class_from_a_spread_literal_counts(audit, tmp_path):
    result = _run(audit, tmp_path, """
        def publish(client, qn):
            base = {"class": "SourceControlLibraryProperties", "qualifiedName": qn}
            return client.create({"class": "NewElementRequestBody",
                                  "properties": {**base, "libraryType": "git"}})
    """)
    assert result.findings == []


def test_literal_type_name_overrides_function_name(audit, tmp_path):
    """typeName names a type with no Properties class of its own: not a parent-class case."""
    result = _run(audit, tmp_path, """
        def create_source_control_library(client, qn):
            return client.create({"class": "NewElementRequestBody",
                                  "properties": {"class": "SoftwareCapabilityProperties",
                                                 "typeName": "SoftwareCapability", "qualifiedName": qn}})
    """)
    assert result.findings == []


def test_class_with_unscanned_superclass_is_unclassified(audit, tmp_path):
    """FindPropertyNameProperties inherits from GetOptions, which the table generator doesn't scan."""
    result = _run(audit, tmp_path, """
        def find(client, v):
            return client.find({"class": "FindPropertyNameProperties", "propertyValue": v,
                                "propertyName": "qualifiedName", "forLineage": True})
    """, parents={"FindPropertyNameProperties": "GetOptions"})
    assert result.findings == []
    assert "GetOptions" in result.unclassified[0].reason


def test_class_maybe_in_an_opaque_spread_is_not_no_class(audit, tmp_path):
    result = _run(audit, tmp_path, """
        def fix_class(body):
            return {**body, "properties": {**body["properties"], "class": "SourceControlLibraryProperties"}}
    """)
    assert [f for f in result.findings if f.kind == audit.NO_CLASS] == []


def test_self_spread_of_a_parameter_is_opaque(audit, tmp_path):
    result = _run(audit, tmp_path, """
        def fix_class(body):
            if body.get("properties"):
                body = {**body, "properties": {**body["properties"], "class": "SourceControlLibraryProperties"}}
            return body
    """)
    assert [f for f in result.findings if f.kind == audit.NO_CLASS] == []


def test_relationship_properties_built_without_class(audit, tmp_path):
    result = _run(audit, tmp_path, """
        def link(client, label):
            props = {}
            if label:
                props["label"] = label
            body = {"class": "NewRelationshipRequestBody", "properties": props}
            client.link(body)
    """)
    assert [(f.kind, f.keys) for f in result.findings] == [(audit.NO_CLASS, ("label",))]


def test_name_reused_across_branches_keeps_keys_apart(audit, tmp_path):
    result = _run(audit, tmp_path, """
        def apply(client, kind, qn, lib):
            if kind == "plain":
                props = {"class": "SoftwareCapabilityProperties", "qualifiedName": qn}
                client.create({"class": "NewElementRequestBody", "properties": props})
            elif kind == "scl":
                props = {"class": "SourceControlLibraryProperties", "qualifiedName": qn}
                props["libraryType"] = lib
                client.create({"class": "NewElementRequestBody", "properties": props})
    """)
    assert result.findings == []
    assert result.bodies_checked == 2


def test_setter_known_key_is_not_a_finding_but_a_table_gap(audit, tmp_path):
    """ResourceListProperties' fields are package-private, so the table misses them; Jackson binds setters."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "planted.py").write_text(textwrap.dedent("""
        def link(client, use):
            client.link({"class": "NewRelationshipRequestBody",
                         "properties": {"class": "ResourceListProperties", "resourceUse": use}})
    """))
    h = audit.Hierarchy({"ResourceListProperties": "RelationshipBeanProperties", "RelationshipBeanProperties": None},
                        {"ResourceListProperties": {"resourceUse", "label"}})
    result = audit.audit_repo(str(repo), hierarchy=h)
    assert result.findings == []
    assert h.gaps == {"ResourceListProperties": {"resourceUse"}}


def test_alternate_table_is_used(audit, tmp_path):
    """--table: audit against another generated table (A0's regeneration), not this checkout's."""
    table = tmp_path / "alt_fields.py"
    table.write_text('"""GENERATED by x from Egeria abc at 1234567 2026-11-21"""\n'
                     "PROPERTIES_CLASS_FIELDS = {'SoftwareCapabilityProperties': "
                     "('entity', ('qualifiedName', 'libraryType'))}\n")
    saved = (audit.PROPERTIES_CLASS_FIELDS, audit._TABLE_PATH)
    try:
        audit.load_table(str(table))
        assert audit.table_source_ref() == "1234567"
        result = _run(audit, tmp_path, """
            def publish(client, qn):
                client.create({"class": "NewElementRequestBody",
                               "properties": {"class": "SoftwareCapabilityProperties", "qualifiedName": qn,
                                              "libraryType": "git"}})
        """)
        assert result.findings == []
    finally:
        audit.PROPERTIES_CLASS_FIELDS, audit._TABLE_PATH = saved
