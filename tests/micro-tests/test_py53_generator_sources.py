"""PY-53: the generator emits `source` columns for classification payloads; the specs that show related info."""
import pytest

import commands.tech.gen_report_specs as _gen

CLASSIFICATION_PAYLOAD_KEYS = _gen.CLASSIFICATION_PAYLOAD_KEYS
CLASSIFICATION_SOURCES = getattr(_gen, "CLASSIFICATION_SOURCES", {})
from pyegeria.view.base_report_formats import get_report_registry
try:
    from pyegeria.view.column_source import check_source
except ImportError:  # pragma: no cover
    check_source = None


def test_every_generator_source_is_in_the_6_4_tables():
    assert len(CLASSIFICATION_SOURCES) == 13
    assert {k: check_source(v) for k, v in CLASSIFICATION_SOURCES.items() if check_source(v)} == {}


def test_only_payload_keys_are_mapped_and_unmappable_ones_stay_skipped():
    assert set(CLASSIFICATION_SOURCES) <= CLASSIFICATION_PAYLOAD_KEYS
    assert {"is_data_value", "supplementary_properties"} == CLASSIFICATION_PAYLOAD_KEYS - set(CLASSIFICATION_SOURCES)


def _sources(label):
    fs = get_report_registry()[label]
    return {c.key: c.source for f in fs.formats for c in f.attributes if c.source}


def test_a_generated_spec_carries_the_classification_source_column():
    found = {label: _sources(label) for label in get_report_registry()
             if label.endswith("-DrE-Advanced") or label.endswith("-DrE-Basic")}
    emitted = {s for d in found.values() for s in d.values()}
    assert emitted & set(CLASSIFICATION_SOURCES.values())


def test_projects_shows_kind_and_target_label():
    assert _sources("Projects") == {"project_kind": "class:Campaign,Task,StudyProject,PersonalProject,GlossaryProject,GovernanceProject",
                                    "project_target_labels": "rel:projectTargets.label"}


def test_file_folders_shows_branch():
    src = _sources("File-Folders")
    assert src["branch_name"] == "class:Branch.displayName" and src["branch_scope"] == "class:Branch.scope"
    assert get_report_registry()["File-Folders"].target_type == "FileFolder"


def test_every_source_in_the_registry_validates():
    bad = {}
    for label, fs in get_report_registry().items():
        for f in fs.formats:
            for c in f.attributes:
                if c.source and check_source(c.source):
                    bad[(label, c.key)] = check_source(c.source)
    assert bad == {}


SIX_PROJECT_KINDS = ["Campaign", "Task", "StudyProject", "PersonalProject", "GlossaryProject", "GovernanceProject"]


def test_project_kind_names_all_six_6_4_project_kind_classifications():
    from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS
    for name in SIX_PROJECT_KINDS:
        assert PROPERTIES_CLASS_FIELDS[f"{name}Properties"][0] == "classification", name
    assert _sources("Projects")["project_kind"] == "class:" + ",".join(SIX_PROJECT_KINDS)


def test_every_project_kind_shows_in_the_project_kind_column():
    from pyegeria.view.column_source import resolve_source
    source = _sources("Projects")["project_kind"]
    for name in SIX_PROJECT_KINDS:
        element = {"elementHeader": {"classifications": [{"classificationName": name}]}}
        assert resolve_source(element, source)[1] == name, name
