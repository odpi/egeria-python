import pytest

from md_processing.md_processing_utils.tests.command_parsing_helpers import (
    FakeEgeriaClient,
    build_command_block,
    commands_for_family,
    parse_command,
    resolve_command_spec,
    required_attribute_keys,
)

FAMILY = "Glossary"


@pytest.mark.parametrize("command", commands_for_family(FAMILY))
def test_glossary_command_parsing(command, skip_reporter, missing_spec_reporter):
    _, status = resolve_command_spec(command)
    if status == "missing_spec":
        missing_spec_reporter(command)
        pytest.fail(f"Missing command spec for {command}")
    if status != "ok":
        skip_reporter(command, status)
    txt = build_command_block(command)
    parsed = parse_command(command, txt, FakeEgeriaClient())
    assert parsed is not None
    assert parsed["valid"] is True
    for key in required_attribute_keys(command):
        assert parsed["attributes"][key]["value"] is not None
