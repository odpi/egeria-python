
import json
import asyncio
from md_processing.v2.extraction import UniversalExtractor, DrECommand
from md_processing.v2.parsing import AttributeFirstParser
from md_processing.md_processing_utils.md_processing_constants import get_command_spec

async def test_resource_use_validation():
    print("\n--- TEST: RESOURCE USE VALIDATION ---")
    
    # Use the spec for "Attach Collection to Resource" which contains "Resource Use"
    spec = get_command_spec("Attach Collection to Resource")
    if not spec:
        print("Error: Spec for 'Attach Collection to Resource' not found")
        return
        
    raw_block = "# Link Collection to Resource\n\n## Collection Id\ncoll-123\n\n## Element Id\nelem-456\n\n## Resource Use\nCatalog Resource"
    
    # Use UniversalExtractor to populate the command object
    extractor = UniversalExtractor(raw_block)
    commands = extractor.extract_commands()
    if not commands:
        print("Error: No commands extracted")
        return
    cmd = commands[0]
    print(f"Extracted Command: Verb='{cmd.verb}', Object='{cmd.object_type}'")
    print(f"Extracted Attributes: {cmd.attributes}")
    
    if not cmd.verb:
        print("Skipping as it's not a command block")
        return
        
    # 1. Create parser with "process" directive (should be lenient)
    parser = AttributeFirstParser(cmd, directive="process")
    result = await parser.parse()
    
    print(f"Parsed Attributes: {json.dumps(result.get('attributes', {}), indent=2)}")
    print(f"Errors: {result.get('errors', [])}")
    print(f"Warnings: {result.get('warnings', [])}")
    
    # Assertions
    attrs = result.get('attributes', {})
    resource_use = attrs.get('Resource Use', {}).get('value')
    
    assert resource_use == "Catalog Resource", f"Expected 'Catalog Resource', got '{resource_use}'"
    assert not result.get('errors'), f"Expected no errors, got {result.get('errors')}"
    # Now it should NOT have a warning if it's in the spec
    assert len(result.get('warnings')) == 0, f"Expected no warnings, got {result.get('warnings')}"
    print("\nSUCCESS: Resource Use parsed correctly without errors or warnings!")

if __name__ == "__main__":
    asyncio.run(test_resource_use_validation())
