from md_processing.dr_egeria import register_governance_processors
from md_processing.v2.governance import GovernanceProcessor, GovernanceLinkProcessor, GovernanceContextProcessor
import md_processing.md_processing_utils.md_processing_constants as md_constants
from md_processing.md_processing_utils.md_processing_constants import (
    build_command_variants,
    get_command_spec,
    load_commands,
)


def test_governance_compact_commands_are_registered_to_processors():
    load_commands()

    registry = {}

    def register_processor(base_command, processor_cls):
        spec = get_command_spec(base_command)
        variants = build_command_variants(base_command, spec) if spec else {base_command}
        for variant in variants:
            registry[variant] = processor_cls

    register_governance_processors(register_processor)

    specs = md_constants.COMMAND_DEFINITIONS.get("Command Specifications", {})
    expected = set()
    for command_name, spec in specs.items():
        if not isinstance(spec, dict):
            continue
        if spec.get("family") != "Governance Officer":
            continue
        expected.update(build_command_variants(command_name, spec))

    missing = sorted(expected - set(registry.keys()))
    assert not missing, f"Missing governance processor registrations: {missing}"

    assert registry.get("Create Governance Driver") is GovernanceProcessor
    assert registry.get("View Governance Definition Context") is GovernanceContextProcessor



def test_governance_link_variants_resolve_to_link_processor():
    load_commands()

    registry = {}

    def register_processor(base_command, processor_cls):
        spec = get_command_spec(base_command)
        variants = build_command_variants(base_command, spec) if spec else {base_command}
        for variant in variants:
            registry[variant] = processor_cls

    register_governance_processors(register_processor)

    specs = md_constants.COMMAND_DEFINITIONS.get("Command Specifications", {})
    for command_name, spec in specs.items():
        if not isinstance(spec, dict):
            continue
        if spec.get("family") != "Governance Officer":
            continue
        if command_name.split(" ", 1)[0] != "Link":
            continue
        for variant in build_command_variants(command_name, spec):
            assert registry.get(variant) is GovernanceLinkProcessor, f"Expected GovernanceLinkProcessor for {variant}"


