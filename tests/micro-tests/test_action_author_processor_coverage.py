# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Dispatcher-registration coverage for the "Action Author" family, mirroring
test_governance_processor_coverage.py's check for "Governance Officer".

register_governance_processors() is family-name-gated (see CLAUDE.md's
"register_governance_processors() is family-name-gated, not automatic" note) --
a compact-spec command whose family is "Action Author" is only wired up if that
family name is explicitly checked for in dr_egeria.py. This test walks the real
compact command specs and asserts every "Action Author" command variant lands in
the dispatcher registry, and that the OM_TYPE-routed / bespoke commands land on
their expected processor classes.
"""
from md_processing.dr_egeria import register_governance_processors
from md_processing.v2 import (
    GovernanceProcessor,
    GovernanceLinkProcessor,
    ActionProcessStepLinkProcessor,
    ActionExecutorTargetLinkProcessor,
    EmbeddedProcessProcessor,
    InitiateEngineActionProcessor,
    CancelEngineActionProcessor,
)
import md_processing.md_processing_utils.md_processing_constants as md_constants
from md_processing.md_processing_utils.md_processing_constants import (
    build_command_variants,
    get_command_spec,
    load_commands,
)


def _build_registry():
    load_commands()
    registry = {}

    def register_processor(base_command, processor_cls):
        spec = get_command_spec(base_command)
        variants = build_command_variants(base_command, spec) if spec else {base_command}
        for variant in variants:
            registry[variant] = processor_cls

    register_governance_processors(register_processor)
    return registry


def test_action_author_compact_commands_are_registered_to_processors():
    registry = _build_registry()

    specs = md_constants.COMMAND_DEFINITIONS.get("Command Specifications", {})
    expected = set()
    for command_name, spec in specs.items():
        if not isinstance(spec, dict):
            continue
        if spec.get("family") != "Action Author":
            continue
        expected.update(build_command_variants(command_name, spec))

    missing = sorted(expected - set(registry.keys()))
    assert not missing, f"Missing Action Author processor registrations: {missing}"


def test_action_author_om_type_routed_commands_resolve_to_bespoke_processors():
    registry = _build_registry()

    specs = md_constants.COMMAND_DEFINITIONS.get("Command Specifications", {})
    for command_name, spec in specs.items():
        if not isinstance(spec, dict) or spec.get("family") != "Action Author":
            continue
        om_type = spec.get("OM_TYPE")
        if om_type in ("GovernanceActionProcessFlow", "NextGovernanceActionProcessStep"):
            for variant in build_command_variants(command_name, spec):
                assert registry.get(variant) is ActionProcessStepLinkProcessor, (
                    f"Expected ActionProcessStepLinkProcessor for {variant}"
                )
        elif om_type in ("GovernanceActionExecutor", "TargetForGovernanceAction"):
            for variant in build_command_variants(command_name, spec):
                assert registry.get(variant) is ActionExecutorTargetLinkProcessor, (
                    f"Expected ActionExecutorTargetLinkProcessor for {variant}"
                )


def test_embedded_process_and_engine_action_resolve_to_their_own_processors():
    # These three commands are re-registered explicitly after the generic
    # family walk (same pattern as "Create Report" overriding its family's
    # generic walker) -- confirm the override actually wins, not the
    # GovernanceProcessor/GovernanceLinkProcessor the generic walk would
    # otherwise assign them.
    registry = _build_registry()

    assert registry.get("Create Embedded Process") is EmbeddedProcessProcessor
    assert registry.get("Initiate Engine Action") is InitiateEngineActionProcessor
    assert registry.get("Cancel Engine Action") is CancelEngineActionProcessor
