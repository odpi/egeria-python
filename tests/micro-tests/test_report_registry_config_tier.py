"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Tests for the CONFIG tier of the report-spec registry: each configured entry
loads independently, so one bad entry is skipped without dropping the others.
"""

import pytest

import pyegeria.view.base_report_formats as brf
from pyegeria.core.config import settings
from pyegeria.view._output_format_models import Column, Format, FormatSet, FormatSetDict

pytestmark = pytest.mark.unit


def _spec(heading: str) -> FormatSet:
    return FormatSet(
        heading=heading,
        description=heading,
        formats=[Format(types=["DICT"], attributes=[Column(name="Display Name", key="displayName")])],
    )


def _write_specs(path, *labels) -> str:
    FormatSetDict({label: _spec(label) for label in labels}).save_to_json(str(path))
    return str(path)


@pytest.fixture
def user_dir(tmp_path):
    d = tmp_path / "user_specs"
    d.mkdir()
    return d


@pytest.fixture
def isolated(monkeypatch, user_dir):
    monkeypatch.setattr(settings.Environment, "pyegeria_report_spec_modules", [])
    for var in ("PYEGERIA_REPORT_SPEC_MODULES", "PYEGERIA_REPORT_FORMATS_JSON", "PYEGERIA_REPORT_FORMATS_MODULES",
                "PYEGERIA_USER_FORMAT_SETS_DIR"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("PYEGERIA_USER_REPORT_SPECS_DIR", str(user_dir))
    monkeypatch.setattr(brf, "_CONFIG_REPORT_FORMATS", FormatSetDict())
    monkeypatch.setattr(brf, "_config_report_specs_loaded", True)
    monkeypatch.setattr(brf, "report_specs", FormatSetDict(dict(brf.report_specs)))
    return monkeypatch


def test_bad_entry_does_not_skip_later_entries(isolated, tmp_path):
    good_a = _write_specs(tmp_path / "a.json", "ConfigTier-A")
    good_b = _write_specs(tmp_path / "b.json", "ConfigTier-B")
    missing = str(tmp_path / "missing.json")
    isolated.setenv("PYEGERIA_REPORT_SPEC_MODULES", ",".join([good_a, missing, "no.such.module:loader", good_b]))

    skipped = brf.refresh_report_specs()

    assert [s for s, _ in skipped] == [f"JSON:{missing}", "MODULE:no.such.module:loader"]
    registry = brf.get_report_registry()
    assert "ConfigTier-A" in registry
    assert "ConfigTier-B" in registry


def test_colliding_entry_skipped_whole_others_kept(isolated, tmp_path):
    first = _write_specs(tmp_path / "first.json", "ConfigTier-Shared", "ConfigTier-OnlyFirst")
    second = _write_specs(tmp_path / "second.json", "ConfigTier-Shared", "ConfigTier-OnlySecond")
    third = _write_specs(tmp_path / "third.json", "ConfigTier-Third")
    isolated.setattr(settings.Environment, "pyegeria_report_spec_modules", [first, second, third])

    skipped = brf.refresh_report_specs()

    assert [s for s, _ in skipped] == [f"JSON:{second}"]
    registry = brf.get_report_registry()
    assert "ConfigTier-OnlyFirst" in registry
    assert "ConfigTier-Third" in registry
    assert "ConfigTier-OnlySecond" not in registry


def test_entry_duplicating_builtin_is_skipped_and_registry_still_works(isolated, tmp_path):
    builtin_label = next(iter(brf.base_report_specs.keys()))
    clash = _write_specs(tmp_path / "clash.json", builtin_label, "ConfigTier-WithClash")
    ok = _write_specs(tmp_path / "ok.json", "ConfigTier-Ok")
    isolated.setenv("PYEGERIA_REPORT_SPEC_MODULES", f"{clash},{ok}")

    skipped = brf.refresh_report_specs()

    assert [s for s, _ in skipped] == [f"JSON:{clash}"]
    registry = brf.get_report_registry()
    assert "ConfigTier-Ok" in registry
    assert "ConfigTier-WithClash" not in registry


def test_all_entries_good_returns_no_skips(isolated, tmp_path):
    good = _write_specs(tmp_path / "good.json", "ConfigTier-Good")
    isolated.setenv("PYEGERIA_REPORT_FORMATS_JSON", good)
    isolated.setenv("PYEGERIA_REPORT_FORMATS_MODULES", "pyegeria.view.analytic_demo_specs:get_analytic_demo_specs")

    assert brf.refresh_report_specs() == []
    assert "ConfigTier-Good" in brf.get_report_registry()


def test_user_dir_specs_reach_registry_and_select(isolated, user_dir):
    _write_specs(user_dir / "b.json", "UserDir-B")
    _write_specs(user_dir / "a.json", "UserDir-A")
    (user_dir / "broken.json").write_text("{ not json")
    (user_dir / "notes.txt").write_text("ignored")

    skipped = brf.refresh_report_specs()

    assert [s for s, _ in skipped] == [f"JSON:{user_dir / 'broken.json'}"]
    assert "UserDir-A" in brf.get_report_registry()
    assert brf.select_report_spec("UserDir-B", "DICT") is not None


def test_load_user_report_specs_refreshes_registry(isolated, user_dir):
    assert "UserDir-Late" not in brf.get_report_registry()
    _write_specs(user_dir / "late.json", "UserDir-Late")

    assert brf.load_user_report_specs() == []
    assert "UserDir-Late" in brf.get_report_registry()
    assert "UserDir-Late" in brf.report_specs


def test_user_dir_falls_back_to_config_setting(isolated, user_dir):
    isolated.delenv("PYEGERIA_USER_REPORT_SPECS_DIR")
    isolated.setattr(settings.Environment, "pyegeria_user_report_specs_dir", str(user_dir))
    _write_specs(user_dir / "cfg.json", "UserDir-FromConfig")

    assert brf.refresh_report_specs() == []
    assert "UserDir-FromConfig" in brf.get_report_registry()


def test_file_both_listed_and_in_user_dir_loads_once(isolated, user_dir):
    path = _write_specs(user_dir / "both.json", "UserDir-Both")
    isolated.setenv("PYEGERIA_REPORT_SPEC_MODULES", path)

    assert brf.refresh_report_specs() == []
    assert "UserDir-Both" in brf.get_report_registry()
