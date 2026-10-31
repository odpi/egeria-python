"""ISSUE-173: installed packages contribute report specs through the
`pyegeria.report_specs` entry-point group (alias `trellis.report_specs`). The
env-var and config.json sources still load this release, with one
DeprecationWarning per refresh."""
import warnings
from importlib.metadata import EntryPoint

import pytest

import pyegeria.view.base_report_formats as brf
from pyegeria.core.config import settings
from pyegeria.view._output_format_models import Column, Format, FormatSet, FormatSetDict

pytestmark = pytest.mark.unit

DEMO_LOADER = "pyegeria.view.analytic_demo_specs:get_analytic_demo_specs"


def _spec(heading: str) -> FormatSet:
    return FormatSet(heading=heading, description=heading,
                     formats=[Format(types=["DICT"], attributes=[Column(name="Display Name", key="displayName")])])


def tile_specs():
    return FormatSetDict({"EP-Tile": _spec("EP-Tile")})


def tile_specs_plain_dict():
    return {"EP-Plain": _spec("EP-Plain")}


TILE_OBJECT = FormatSetDict({"EP-Object": _spec("EP-Object")})


def clashing_specs():
    return FormatSetDict({"Referenceable": _spec("clash")})


def broken_specs():
    raise RuntimeError("cannot build specs")


def _ep(name: str, value: str, group: str = brf.REPORT_SPEC_ENTRY_POINT_GROUP) -> tuple:
    return group, EntryPoint(name=name, value=value, group=group)


@pytest.fixture
def isolated(monkeypatch, tmp_path):
    monkeypatch.setattr(settings.Environment, "pyegeria_report_spec_modules", [])
    for var in ("PYEGERIA_REPORT_SPEC_MODULES", "PYEGERIA_REPORT_FORMATS_JSON", "PYEGERIA_REPORT_FORMATS_MODULES",
                "PYEGERIA_USER_FORMAT_SETS_DIR"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("PYEGERIA_USER_REPORT_SPECS_DIR", str(tmp_path))
    monkeypatch.setattr(brf, "_CONFIG_REPORT_FORMATS", FormatSetDict())
    monkeypatch.setattr(brf, "_config_report_specs_loaded", True)
    monkeypatch.setattr(brf, "_report_spec_entry_points", lambda: [])
    return monkeypatch


def _entry_points(isolated, *eps):
    isolated.setattr(brf, "_report_spec_entry_points", lambda: list(eps))


def _refresh_no_deprecation():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        skipped = brf.refresh_report_specs()
    assert not [w for w in caught if w.category is DeprecationWarning]
    return skipped


def test_entry_point_specs_load_in_each_shape(isolated):
    mod = __name__
    _entry_points(isolated, _ep("tile", f"{mod}:tile_specs"), _ep("plain", f"{mod}:tile_specs_plain_dict"),
                  _ep("object", f"{mod}:TILE_OBJECT", group="trellis.report_specs"))
    assert _refresh_no_deprecation() == []
    registry = brf.get_report_registry()
    assert {"EP-Tile", "EP-Plain", "EP-Object"} <= set(registry)


def test_broken_or_clashing_entry_point_is_skipped_and_the_rest_load(isolated):
    mod = __name__
    _entry_points(isolated, _ep("broken", f"{mod}:broken_specs"), _ep("clash", f"{mod}:clashing_specs"),
                  _ep("tile", f"{mod}:tile_specs"))
    skipped = dict(_refresh_no_deprecation())
    assert "cannot build specs" in skipped[f"ENTRY_POINT:{brf.REPORT_SPEC_ENTRY_POINT_GROUP}:broken"]
    assert "Referenceable" in skipped[f"ENTRY_POINT:{brf.REPORT_SPEC_ENTRY_POINT_GROUP}:clash"]
    assert "EP-Tile" in brf.get_report_registry()


@pytest.mark.parametrize("source", [
    "PYEGERIA_REPORT_SPEC_MODULES", "PYEGERIA_REPORT_FORMATS_MODULES", "PYEGERIA_REPORT_FORMATS_JSON", "config.json"])
def test_each_deprecated_source_still_loads_and_warns(isolated, tmp_path, source):
    if source == "PYEGERIA_REPORT_FORMATS_JSON":
        path = tmp_path / "legacy" / "specs.json"
        path.parent.mkdir()
        tile_specs().save_to_json(str(path))
        isolated.setenv(source, str(path))
    elif source == "config.json":
        isolated.setattr(settings.Environment, "pyegeria_report_spec_modules", [f"{__name__}:tile_specs"])
    else:
        isolated.setenv(source, f"{__name__}:tile_specs")
    name = 'config.json "Pyegeria Report Spec Modules"' if source == "config.json" else source
    with pytest.warns(DeprecationWarning, match=f"{name}.*'pyegeria.report_specs' entry-point group"):
        assert brf.refresh_report_specs() == []
    assert "EP-Tile" in brf.get_report_registry()


def test_config_entry_naming_an_entry_point_loader_is_the_same_source(isolated):
    _entry_points(isolated, _ep("tile", f"{__name__}:tile_specs"))
    isolated.setattr(settings.Environment, "pyegeria_report_spec_modules", [f"{__name__}:tile_specs"])
    with pytest.warns(DeprecationWarning):  # still told to drop the key...
        skipped = brf.refresh_report_specs()
    assert skipped == []  # ...but it is not reported as a clash with itself
    assert "EP-Tile" in brf.get_report_registry()


def test_pyegeria_ships_its_demo_specs_as_an_entry_point():
    eps = [ep for _, ep in brf._report_spec_entry_points() if ep.value == DEMO_LOADER]
    assert eps, "run `uv sync` so the installed metadata carries pyegeria's own entry points"
