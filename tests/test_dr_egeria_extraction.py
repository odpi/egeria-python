import pytest
from md_processing.v2.extraction import UniversalExtractor, DrECommand
from md_processing.v2.parsing import AttributeFirstParser, parse_dr_egeria_content
from md_processing.v2.utils import parse_key_value

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
    
    assert len(commands) == 1
    assert commands[0].verb == "Create"
    assert commands[0].object_type == "Glossary"
    assert commands[0].attributes["Display Name"] == "My New Glossary"
    assert commands[0].attributes["Description"] == "A glossary for testing."

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
    
    assert len(commands) == 2
    assert commands[0].verb == "Create"
    assert commands[0].object_type == "Term"
    assert commands[1].verb == "Update"
    assert commands[1].object_type == "Glossary"

def test_headless_command_extraction():
    # Headless command (no leading #)
    text = "Create Project\n## Display Name\nHeadless Project"
    extractor = UniversalExtractor(text)
    commands = extractor.extract_commands()
    
    assert len(commands) == 1
    assert commands[0].verb == "Create"
    assert commands[0].object_type == "Project"

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
    
    desc = commands[0].attributes["Description"]
    assert "Line 1" in desc
    assert "Line 2" in desc
    assert "provenance" not in desc

def test_parse_key_value():
    text = "| Key | Value |\n| --- | --- |\n| a | 1 |\n| b | 2 |"
    kv = parse_key_value(text)
    assert kv == {"a": "1", "b": "2"}
    
    text_list = "* x: y\n* z = 10"
    kv = parse_key_value(text_list)
    assert kv == {"x": "y", "z": "10"}

def test_extract_and_parse_integration():
    text = """
# Create Glossary
## Display Name
Integrated Glossary
## Description
Testing integration.
"""
    results = parse_dr_egeria_content(text)
    assert len(results) == 1
    attrs = results[0]["attributes"]
    # Looking for 'Display Name' (canonical) or 'display_name' (variable name)
    assert "Display Name" in attrs or "display_name" in attrs
    assert results[0]["verb"] == "Create"
