"""RS-W2-4 PR-0 (owner decision O1-a, 2026-11-08): a spec that still carries a non-empty
`analytic_binders` key reports it among the resolver's warnings, with a stable prefix the
Portal tags on. The PR-B shim still drops the key; an empty key stays silent.
"""
import warnings

import pytest

from pyegeria.view import spec_resolver as sr
from pyegeria.view._output_format_models import FormatSet

PREFIX = "deprecated: analytic_binders ignored (binders for: "


def _spec_dict(binders):
    return {"heading": "W24-Binder", "description": "probe", "target_type": "Referenceable",
            "action": {"analytic_function": "count_elements", "analytic_binders": binders},
            "formats": [{"types": ["DICT"], "attributes": []}]}


def _binder_warnings(result):
    return [w for w in result.warnings if w.startswith(sr.BINDERS_DEPRECATED_PREFIX)]


def test_the_prefix_is_the_stable_one_the_portal_matches():
    assert sr.BINDERS_DEPRECATED_PREFIX == "deprecated: analytic_binders ignored"


def test_a_loaded_spec_with_a_non_empty_binder_carries_the_warning():
    with pytest.warns(DeprecationWarning):
        spec = FormatSet.model_validate(_spec_dict({"reader": "x.Reader", "mgr": "os.getcwd"}))
    assert "analytic_binders" not in spec.model_dump()["action"]
    found = _binder_warnings(sr.resolve(spec, "W24-Binder", registry_names=set()))
    assert len(found) == 1
    assert found[0].startswith(PREFIX + "mgr, reader)")


def test_the_note_survives_a_copy_of_the_spec():
    with pytest.warns(DeprecationWarning):
        spec = FormatSet.model_validate(_spec_dict({"ods": "x.OdsReader"}))
    copied = spec.model_copy(deep=True)
    assert _binder_warnings(sr.resolve(copied, "W24-Binder", registry_names=set()))[0].startswith(
        PREFIX + "ods)")


def test_a_plain_dict_spec_with_a_binder_carries_the_warning():
    found = _binder_warnings(sr.resolve(_spec_dict({"ods": "x.OdsReader"}), "W24-Binder", registry_names=set()))
    assert len(found) == 1 and found[0].startswith(PREFIX + "ods)")


@pytest.mark.parametrize("empty", [{}, None, []])
def test_an_empty_binder_gives_no_warning(empty):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        spec = FormatSet.model_validate(_spec_dict(empty))
    assert spec.action._dropped_binders == []
    assert _binder_warnings(sr.resolve(spec, "W24-Binder", registry_names=set())) == []
    assert _binder_warnings(sr.resolve(_spec_dict(empty), "W24-Binder", registry_names=set())) == []


def test_no_registered_spec_carries_the_warning():
    """No built-in, demo or generated spec sets a non-empty binder (the 274 empty keys stay silent)."""
    results = sr.resolve_all(refresh=True)
    assert results
    assert {label for label, r in results.items() if _binder_warnings(r)} == set()
