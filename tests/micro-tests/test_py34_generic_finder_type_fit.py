"""
PY-34: a generic finder's type fit is checked against the type the spec asks it for.

ClassificationExplorer.find_authored_elements returns whatever `metadata_element_type` it is asked for, so
pyegeria had "no record of its element type" and the fit check warned and checked nothing (EA's U3 B05/B15,
2026-11-18). Now the check reads the value the spec fixes in `action.spec_params`:
- fixed to the target type (or a supertype of it): the fit is checked and passes;
- fixed to an unrelated type: refused;
- not fixed: warned in words (the method can return any type), and recorded as not checked.
No live server: the super-type read is replaced.
"""
import asyncio
from types import SimpleNamespace

import pytest

import md_processing.md_processing_utils.typed_properties as tp
from pyegeria.authoring.models import ValidationResult
from pyegeria.authoring.validate import GENERIC_FIND_TYPE_PARAMS, _check_find_fit

FIND = "ClassificationExplorer.find_authored_elements"


def _fs(target, spec_params=None, function=FIND):
    return SimpleNamespace(target_type=target,
                           action=SimpleNamespace(function=function, analytic_function=None,
                                                  spec_params=spec_params or {}))


def _run(fs, client=object()):
    result = ValidationResult()
    asyncio.run(_check_find_fit(fs, client, result))
    return result


@pytest.fixture
def chain(monkeypatch):
    chains = {"GlossaryTerm": ["GlossaryTerm", "Referenceable", "OpenMetadataRoot"],
              "GovernancePolicy": ["GovernancePolicy", "GovernanceDefinition", "Referenceable", "OpenMetadataRoot"]}

    async def fake_chain(client, target):
        return chains.get(target)

    monkeypatch.setattr(tp, "type_super_chain", fake_chain)
    return chains


def test_find_authored_elements_is_registered_as_generic():
    assert GENERIC_FIND_TYPE_PARAMS[FIND][0] == "metadata_element_type"


@pytest.mark.parametrize("target", ["GlossaryTerm", "GovernancePolicy"])
def test_fixed_to_the_target_type_fits(chain, target):
    r = _run(_fs(target, {"metadata_element_type": target}))
    assert "find method fits the target type" in r.checked
    assert not r.warnings and not r.errors and not r.not_checked


def test_fixed_to_a_supertype_fits_through_the_super_chain(chain):
    r = _run(_fs("GovernancePolicy", {"metadata_element_type": "GovernanceDefinition"}))
    assert "find method fits the target type" in r.checked and not r.errors


def test_fixed_to_an_unrelated_type_is_refused(chain):
    r = _run(_fs("GlossaryTerm", {"metadata_element_type": "Project"}))
    assert r.errors and "returns Project elements" in r.errors[0]
    assert "find method fits the target type" not in r.checked


def test_the_name_variant_of_the_parameter_is_read_too(chain):
    r = _run(_fs("GlossaryTerm", {"metadata_element_type_name": "GlossaryTerm"}))
    assert "find method fits the target type" in r.checked


def test_not_fixed_warns_in_words_and_is_not_checked(chain):
    r = _run(_fs("GlossaryTerm", {}))
    assert r.warnings and "doesn't fix one, so it can return elements of any type" in r.warnings[0]
    assert r.not_checked and "metadata_element_type not fixed" in r.not_checked[0]
    assert "find method fits the target type" not in r.checked


def test_an_unregistered_method_still_says_it_cant_tell(chain):
    r = _run(_fs("GlossaryTerm", {}, function="SomeManager.find_something"))
    assert r.warnings and "pyegeria has no record of its element type" in r.warnings[0]
