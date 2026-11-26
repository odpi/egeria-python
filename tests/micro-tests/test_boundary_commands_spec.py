# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Dr.Egeria commands for the solution boundaries of odpi/egeria#9465: `Create Solution Boundary` and `Create Design Model Boundary`.

What these pin: the compact-spec entries (names, verb, OM_TYPE, find method and constraint), that they use the Collection Base bundle ONLY (exactly
the attributes `Create Concept Model` has: nothing invented, because both Java types add no property to a collection), that the strict spec
validator has no finding about them, that the generated report specs and seed carry them, and that the generated Basic templates exist.
Nothing here talks to a platform. The processor routing and the get/update branches belong to the processor change (not here).
"""
import json
from pathlib import Path

import pytest

from md_processing.md_processing_utils import md_processing_constants as consts
from md_processing.v2.extraction import STANDARD_VERBS

ROOT = Path(__file__).resolve().parents[2]
COMPACT = ROOT / "md_processing" / "data" / "compact_commands"
NAMES = ("Create Solution Boundary", "Create Design Model Boundary")


@pytest.fixture(scope="module")
def spec():
    consts.load_commands()
    return consts.COMMAND_DEFINITIONS["Command Specifications"]


@pytest.fixture(scope="module")
def raw():
    return json.loads((COMPACT / "commands_solution_architect_compact.json").read_text())["commands"]


def _attrs(entry):
    return sorted(a if isinstance(a, str) else a.get("name", str(a)) for a in entry["Attributes"])


def test_create_is_a_standard_verb():
    assert "Create" in STANDARD_VERBS            # a new command's verb must be one, or the block silently fails to parse


def test_solution_boundary_command(spec):
    c = spec["Create Solution Boundary"]
    assert (c["verb"], c["OM_TYPE"], c["family"], c["upsert"]) == ("Create", "SolutionBoundary", "Solution Architect", True)
    assert c["find_method"] == "SolutionArchitect.find_solution_boundaries"
    assert c["qn_prefix"] == "SolutionBoundary" and c["bundle"] == "Collection Base"


def test_design_model_boundary_command(spec):
    c = spec["Create Design Model Boundary"]
    assert (c["verb"], c["OM_TYPE"], c["family"], c["upsert"]) == ("Create", "DesignModelBoundary", "Solution Architect", True)
    # the view service has no request for this type; the generic collection find, constrained to the type (the same pattern as Create Concept Model)
    assert c["find_method"] == "CollectionManager.find_collections"
    assert json.loads(c["find_constraints"]) == {"metadata_element_type": "DesignModelBoundary"}
    assert c["qn_prefix"] == "DesignModelBoundary" and c["bundle"] == "Collection Base"


def test_the_attributes_are_a_collection_s_and_nothing_else(spec):
    base = _attrs(spec["Create Concept Model"])        # the existing command on the same bundle
    assert base and "Purpose" in base
    for name in NAMES:
        assert _attrs(spec[name]) == base, name
        assert spec[name]["custom_attributes"] == []


def test_the_find_method_is_not_shared_between_the_two(raw):
    assert raw["Create Solution Boundary"]["find_method"] != raw["Create Design Model Boundary"]["find_method"]
    assert raw["Create Solution Boundary"]["find_constraints"] == ""


def test_the_strict_validator_has_no_finding_about_them():
    from md_processing.md_processing_utils.compact_spec_validator import validate_compact_specs
    findings = validate_compact_specs(COMPACT, valid_om_types=None)
    assert [f for f in findings if f.command_name in NAMES] == []


def test_the_processing_type_is_derived_from_the_constraint():
    from md_processing.md_processing_utils.compact_spec_validator import derive_processing_type_name
    assert derive_processing_type_name("Create Design Model Boundary", {"metadata_element_type": "DesignModelBoundary"}) == "DesignModelBoundary"


@pytest.mark.parametrize("label", ["Solution-Boundary-DrE-Basic", "Solution-Boundary-DrE-Advanced",
                                   "Design-Model-Boundary-DrE-Basic", "Design-Model-Boundary-DrE-Advanced"])
def test_the_generated_report_specs_exist(label):
    from pyegeria.view.base_report_formats import get_report_registry
    spec = get_report_registry()[label]
    assert spec.family == "Solution Architect"


def test_the_seed_carries_the_generated_specs():
    seed = json.loads((ROOT / "pyegeria" / "view" / "seed" / "Solution Architect.json").read_text())
    labels = {e["label"] for e in seed["specs"]}
    assert {"Solution-Boundary-DrE-Basic", "Solution-Boundary-DrE-Advanced", "Design-Model-Boundary-DrE-Basic",
            "Design-Model-Boundary-DrE-Advanced", "Solution-Boundary", "Solution-Boundary-Mermaid"} <= labels


@pytest.mark.parametrize("level", ["basic", "advanced"])
@pytest.mark.parametrize("name", ["Create_Solution_Boundary.md", "Create_Design_Model_Boundary.md"])
def test_the_generated_templates_exist(level, name):
    text = (ROOT / "sample-data" / "templates" / level / "Solution Architect" / name).read_text()
    assert "## " + name[:-3].replace("_", " ") in text
    assert "valid values not read" not in text      # an offline generation leaves this marker; it must never be committed


def test_the_generated_update_names_keep_boundary(spec):
    # B5 routes by the command name; the Update variant is generated from the Create name and must still say "Boundary"
    for name in NAMES:
        variants = consts.build_command_variants(name, spec[name])
        updates = [v for v in variants if v.startswith("Update")]
        assert updates and all("Boundary" in v for v in updates), name


def test_the_design_model_boundary_description_says_it_returns_solution_boundaries_too(spec):
    assert "also returns solution boundaries" in spec["Create Design Model Boundary"]["description"]
