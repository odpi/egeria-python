import pytest
from typing import Any, cast
from md_processing.v2.extraction import UniversalExtractor, DrECommand
from md_processing.v2.parsing import AttributeFirstParser, parse_dr_egeria_content
from md_processing.v2.utils import parse_key_value
from md_processing.v2.view import ViewProcessor

def test_standard_command_extraction():
    text = """
# Create Glossary
## Display Name
My New Glossary
## Description
A glossary for testing.
"""
    extractor = UniversalExtractor(text)
    commands = extractor.extract_commands()
    
    # Filter only actual commands
    actual_commands = [c for c in commands if c.is_command]
    
    assert len(actual_commands) == 1
    assert actual_commands[0].verb == "Create"
    assert actual_commands[0].object_type == "Glossary"
    assert actual_commands[0].attributes["Display Name"] == "My New Glossary"
    assert actual_commands[0].attributes["Description"] == "A glossary for testing."

def test_mixed_markdown_extraction():
    text = """
Some introductory text.

# Create Term
## Display Name
Test Term

Some more text in between.

# Update Glossary
## Description
Updated description.

Footer text.
"""
    extractor = UniversalExtractor(text)
    commands = extractor.extract_commands()
    
    # Filter only actual commands
    actual_commands = [c for c in commands if c.is_command]
    
    assert len(actual_commands) == 2
    assert actual_commands[0].verb == "Create"
    assert actual_commands[0].object_type == "Term"
    assert actual_commands[1].verb == "Update"
    assert actual_commands[1].object_type == "Glossary"
    
    # Check that non-command text is preserved as blocks
    assert any(not c.is_command and "introductory text" in c.raw_block for c in commands)
    # Note: 'Footer text' is part of the previous command block unless separated by ---
    assert any("Footer text" in c.raw_block for c in commands)

def test_headless_command_extraction():
    # Headless command (no leading #)
    text = "Create Project\n## Display Name\nHeadless Project"
    extractor = UniversalExtractor(text)
    commands = extractor.extract_commands()
    
    # Filter only actual commands
    actual_commands = [c for c in commands if c.is_command]
    
    assert len(actual_commands) == 1
    assert actual_commands[0].verb == "Create"
    assert actual_commands[0].object_type == "Project"

def test_attribute_preservation():
    # Test that provenance lines (>) are filtered out but newlines are preserved
    text = """
# Create Glossary
## Description
Line 1
> This is a provenance line to ignore
Line 2
"""
    extractor = UniversalExtractor(text)
    commands = extractor.extract_commands()
    
    # Filter only actual commands
    actual_commands = [c for c in commands if c.is_command]
    
    desc = actual_commands[0].attributes["Description"]
    assert "Line 1" in desc
    assert "Line 2" in desc
    assert "provenance" not in desc


def test_prose_with_command_words_is_not_treated_as_command():
    text = """
# Governance Officer FAQ
In this section we explain how to create governance definitions safely.
Do not run anything from this paragraph directly.
"""
    extractor = UniversalExtractor(text)
    commands = extractor.extract_commands()

    actual_commands = [c for c in commands if c.is_command]
    assert len(actual_commands) == 0
    assert any("Governance Officer FAQ" in c.raw_block for c in commands)

def test_parse_key_value():
    text = "| Key | Value |\n| --- | --- |\n| a | 1 |\n| b | 2 |"
    kv = parse_key_value(text)
    assert kv == {"a": "1", "b": "2"}
    
    text_list = "* x: y\n* z = 10"
    kv = parse_key_value(text_list)
    assert kv == {"x": "y", "z": "10"}

@pytest.mark.asyncio
async def test_extract_and_parse_integration():
    text = """
# Create Glossary
## Display Name
Integrated Glossary
## Description
Testing integration.
"""
    results = await parse_dr_egeria_content(text)
    assert len(results) == 1
    attrs = results[0]["attributes"]
    # Looking for 'Display Name' (canonical) or 'display_name' (variable name)
    assert "Display Name" in attrs or "display_name" in attrs
    assert results[0]["verb"] == "Create"


@pytest.mark.asyncio
async def test_view_report_keeps_metadata_name_filters_as_simple_attributes():
    cmd = DrECommand(
        verb="View",
        object_type="Report",
        attributes={
            "Report Spec": "Digital-Products",
            "Metadata Element Type Name": "DigitalProduct",
            "Metadata Element Subtype Names": "RootCollection\nCollectionFolder",
            "Output Format": "LIST",
        },
        raw_block="# View Report",
    )

    parser = AttributeFirstParser(cmd)
    parsed = await parser.parse()

    assert parsed["attributes"]["Metadata Element Type Name"]["style"] == "Simple"
    assert parsed["attributes"]["Metadata Element Type Name"]["value"] == "DigitalProduct"
    assert parsed["attributes"]["Metadata Element Subtype Names"]["style"] == "Simple List"
    assert parsed["attributes"]["Metadata Element Subtype Names"]["value"] == ["RootCollection", "CollectionFolder"]


@pytest.mark.asyncio
async def test_view_report_validation_output_uses_report_context_not_qualified_name(monkeypatch):
    async def _fake_run_report(**kwargs):
        return {"kind": "text", "content": "ok"}

    # Keep report execution local/offline for tests.
    monkeypatch.setattr("md_processing.v2.view._async_run_report", _fake_run_report)

    cmd = DrECommand(
        verb="View",
        object_type="Report",
        attributes={
            "Report Spec": "Digital-Products",
            "Output Format": "LIST",
            "Metadata Element Type Name": "DigitalProduct",
        },
        raw_block="# View Report",
    )

    processor = ViewProcessor(client=cast(Any, object()), command=cmd, context={"directive": "validate"})
    result = await processor.execute()

    assert result["status"] == "success"
    assert "**Action**: View" in result["analysis"]
    assert "**Report Spec**: `Digital-Products`" in result["analysis"]
    assert "**Output Format**: `LIST`" in result["analysis"]
    assert "**Qualified Name**" not in result["analysis"]
    assert result.get("qualified_name") in (None, "")


@pytest.mark.asyncio
async def test_view_report_anchor_scope_id_resolves_when_declared_reference_style(monkeypatch):
    async def _fake_run_report(**kwargs):
        return {"kind": "text", "content": "ok"}

    monkeypatch.setattr("md_processing.v2.view._async_run_report", _fake_run_report)

    cmd = DrECommand(
        verb="View",
        object_type="Report",
        attributes={
            "Report Spec": "Collections",
            "Search String": "*",
            "Output Format": "LIST",
            "Anchor Scope ID": "Collection::SalesForecast::Root::1.0",
        },
        raw_block="# View Report",
    )

    processor = ViewProcessor(client=cast(Any, object()), command=cmd, context={"directive": "validate"})
    result = await processor.execute()

    # If the command spec marks Anchor Scope ID as a reference-style attribute,
    # unresolved values should fail validation.
    assert result["status"] == "failure"
    assert "Referenced element" in result.get("analysis", "")


