# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""md_processing.templates: the rendered Dr.Egeria templates shipped as package data."""
from pathlib import Path

import pytest

from md_processing import templates as tpl

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _clear_caches():
    tpl._root_and_source.cache_clear()
    tpl._index.cache_clear()
    yield
    tpl._root_and_source.cache_clear()
    tpl._index.cache_clear()


@pytest.mark.unit
@pytest.mark.parametrize("level", tpl.LEVELS)
def test_levels_have_templates(level):
    assert tpl.templates_source(level) in ("package", "checkout")
    items = tpl.list_templates(level)
    assert len(items) > 100
    assert "Glossary" in tpl.list_families(level)
    # every entry points at a readable file whose heading is its command
    for t in items[:25]:
        text = tpl.read_template(t.command, level, family=t.family)
        assert f"## {t.command}" in text


@pytest.mark.unit
def test_views_and_reports_family_present():
    # The family the 2026-08-17 EA clone lacked (brief §1).
    cmds = {t.command for t in tpl.list_templates("basic", family="Views & Reports")}
    assert {"Create Dashboard Sheet", "Link Report to Dashboard Sheet"} <= cmds


@pytest.mark.unit
def test_basic_create_templates_carry_zone_membership():
    text = tpl.read_template("Create Glossary", "basic")
    assert "### Zone Membership" in text


@pytest.mark.unit
def test_advanced_is_superset_of_basic():
    basic = {(t.family, t.command) for t in tpl.list_templates("basic")}
    advanced = {(t.family, t.command) for t in tpl.list_templates("advanced")}
    assert basic <= advanced


@pytest.mark.unit
@pytest.mark.parametrize("name", ["Create Glossary", "create_glossary", "Create_Glossary.md", "  CREATE   glossary "])
def test_lookup_is_name_tolerant(name):
    info = tpl.find_template(name, "basic")
    assert info.command == "Create Glossary"
    assert info.family == "Glossary"
    assert info.resource == "Glossary/Create_Glossary.md"


@pytest.mark.unit
def test_lookup_by_heading_name_with_punctuation():
    # file is Link_Term-Term_Relationship.md; heading keeps the hyphen
    info = tpl.find_template("Link Term-Term Relationship", "advanced")
    assert info.file_name == "Link_Term-Term_Relationship.md"


@pytest.mark.unit
def test_unknown_command_and_level():
    with pytest.raises(tpl.TemplateNotFound):
        tpl.read_template("Create No Such Thing", "basic")
    with pytest.raises(tpl.TemplateNotFound):
        tpl.read_template("Create Glossary", "basic", family="Projects")
    with pytest.raises(ValueError):
        tpl.list_templates("expert")


@pytest.mark.unit
def test_packaged_copy_wins_over_checkout(tmp_path, monkeypatch):
    fam = tmp_path / "basic" / "Fam"
    fam.mkdir(parents=True)
    (fam / "Do_Thing.md").write_text("___\n\n## Do Thing\n> x\n", encoding="utf-8")
    monkeypatch.setattr(tpl, "_packaged_root", lambda: tmp_path)
    assert tpl.templates_source("basic") == "package"
    assert [t.command for t in tpl.list_templates("basic")] == ["Do Thing"]
    # advanced isn't in the fake package, so it falls back to the checkout
    assert tpl.templates_source("advanced") == "checkout"


@pytest.mark.unit
def test_missing_everywhere(tmp_path, monkeypatch):
    monkeypatch.setattr(tpl, "_packaged_root", lambda: tmp_path / "none")
    monkeypatch.setattr(tpl, "_checkout_root", lambda: tmp_path / "none")
    assert tpl.templates_source("basic") == "missing"
    with pytest.raises(FileNotFoundError):
        tpl.list_templates("basic")


@pytest.mark.unit
def test_build_config_ships_templates():
    # The wheel gets them from setup.py's build_py hook; the sdist must carry
    # the source tree and package-data must admit the copied files.
    manifest = (REPO / "MANIFEST.in").read_text()
    assert "recursive-include sample-data/templates/basic *.md" in manifest
    assert "recursive-include sample-data/templates/advanced *.md" in manifest
    assert '"data/templates/**/*.md"' in (REPO / "pyproject.toml").read_text()
    assert "BuildPyWithTemplates" in (REPO / "setup.py").read_text()

