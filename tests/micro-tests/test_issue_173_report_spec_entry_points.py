"""ISSUE-173: installed packages contribute report specs through the
`pyegeria.report_specs` entry-point group, and other code through
`register_report_specs()`. The env-var and config.json sources and the
`trellis.report_specs` alias warned in 6.2.18 and are removed in 6.2.19: a
refresh no longer reads them, and logs a warning if one is still set."""
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
def log_lines():
    from loguru import logger
    lines = []
    sink = logger.add(lambda m: lines.append(m.record["message"]), level="WARNING")
    yield lines
    logger.remove(sink)


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
    brf.clear_runtime_report_specs()
    yield monkeypatch
    brf.clear_runtime_report_specs()


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
                  _ep("object", f"{mod}:TILE_OBJECT"))
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


def test_only_the_pyegeria_group_is_read(monkeypatch):
    asked = []
    monkeypatch.setattr(brf, "entry_points", lambda group: asked.append(group) or [])
    assert brf._report_spec_entry_points() == []
    assert asked == [brf.REPORT_SPEC_ENTRY_POINT_GROUP]  # no trellis.report_specs alias


@pytest.mark.parametrize("source", [
    "PYEGERIA_REPORT_SPEC_MODULES", "PYEGERIA_REPORT_FORMATS_MODULES", "PYEGERIA_REPORT_FORMATS_JSON", "config.json"])
def test_each_removed_source_is_not_read_and_logs_a_warning(isolated, tmp_path, log_lines, source):
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
    assert _refresh_no_deprecation() == []
    assert "EP-Tile" not in brf.get_report_registry()
    warned = [m for m in log_lines if "no longer read" in m]
    assert len(warned) == 1 and name in warned[0] and "register_report_specs()" in warned[0]


def test_no_warning_when_no_removed_source_is_set(isolated, log_lines):
    _refresh_no_deprecation()
    assert not [m for m in log_lines if "no longer read" in m]


def test_runtime_registration_survives_a_refresh(isolated):
    brf.register_report_specs(tile_specs(), source="portal")
    _refresh_no_deprecation()
    assert "EP-Tile" in brf.get_report_registry()


def test_registering_again_from_the_same_source_is_a_no_op(isolated):
    brf.register_report_specs(tile_specs(), source="portal")
    brf.register_report_specs(tile_specs(), source="portal")  # e.g. a reloaded handler
    assert "EP-Tile" in brf.get_report_registry()


def test_registering_a_label_from_another_source_raises(isolated):
    brf.register_report_specs(tile_specs(), source="portal")
    with pytest.raises(brf.ReportFormatCollision):
        brf.register_report_specs(tile_specs(), source="someone-else")


def test_registering_a_builtin_label_raises_and_registers_nothing(isolated):
    specs = FormatSetDict({"EP-New": _spec("EP-New"), "Referenceable": _spec("clash")})
    with pytest.raises(brf.ReportFormatCollision):
        brf.register_report_specs(specs, source="portal")
    assert "EP-New" not in brf.get_report_registry()


def test_unregister_lets_another_source_take_the_label(isolated):
    brf.register_report_specs(tile_specs(), source="portal")
    assert brf.unregister_report_spec("EP-Tile")
    brf.register_report_specs(tile_specs(), source="someone-else")
    assert "EP-Tile" in brf.get_report_registry()


def test_pyegeria_ships_its_demo_specs_as_an_entry_point():
    eps = [ep for _, ep in brf._report_spec_entry_points() if ep.value == DEMO_LOADER]
    assert eps, "run `uv sync` so the installed metadata carries pyegeria's own entry points"
