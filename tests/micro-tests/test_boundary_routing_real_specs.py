# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""The boundary commands route to SolutionArchitectProcessor with the REAL compact specs (B4 + B5 together).

test_b5_boundary_routing.py uses synthetic specs, because B5 was built before B4's specs existed. This runs the real
dispatcher on the real Solution Architect specs, for the Create command and the Update variant generated from it, and
checks that no other Solution Architect command name contains "Boundary" (B5 routes such names by the word).
No platform is contacted.
"""
import pytest

import md_processing.md_processing_utils.md_processing_constants as mpc
from md_processing.dr_egeria import setup_dispatcher
from md_processing.v2.extraction import DrECommand
from md_processing.v2.solution_architect import SolutionArchitectProcessor

pytestmark = pytest.mark.unit

BOUNDARY_COMMANDS = ("Create Solution Boundary", "Create Design Model Boundary")


@pytest.mark.parametrize("verb", ["Create", "Update"])
@pytest.mark.parametrize("object_type", ["Solution Boundary", "Design Model Boundary"])
def test_real_boundary_commands_resolve_to_the_solution_architect_processor(verb, object_type):
    dispatcher = setup_dispatcher(object())  # registration only; the client is never called
    command = DrECommand(verb=verb, object_type=object_type, attributes={}, raw_block=f"## {verb} {object_type}\n")
    assert dispatcher.resolve_processor_class(command) is SolutionArchitectProcessor


def test_the_two_boundary_commands_are_the_only_solution_architect_names_with_boundary():
    mpc.load_commands()
    specs = mpc.COMMAND_DEFINITIONS["Command Specifications"]
    names = {name for name, spec in specs.items()
             if isinstance(spec, dict) and spec.get("family") == "Solution Architect" and "Boundary" in name}
    assert names == set(BOUNDARY_COMMANDS)
    assert {specs[n]["OM_TYPE"] for n in BOUNDARY_COMMANDS} == {"SolutionBoundary", "DesignModelBoundary"}
