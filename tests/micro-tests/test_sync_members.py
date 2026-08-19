import asyncio
from unittest.mock import AsyncMock, MagicMock

from md_processing.v2.glossary import TermProcessor
from md_processing.v2.extraction import DrECommand

async def test_glossary_term_processing():
    # Mock Egeria Client
    client = AsyncMock()
    
    # Mock get_related_elements to return nothing initially
    client._async_get_related_elements.return_value = []
    
    # Mock create/update calls
    client._async_create_glossary_term.return_value = "00000000-0000-0000-0000-000000000001"
    client._async_update_glossary_term.return_value = None
    
    # 1. Test Create with Multiple Glossaries and Folders
    cmd = DrECommand(
        verb="Create",
        object_type="Glossary Term",
        attributes={
            "Display Name": {"value": "TestTerm"},
            "Qualified Name": {"value": "QN123"},
            "Glossary Name": {"value": ["GlossaryA", "GlossaryB"], "guid_list": ["aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"]},
            "Folders": {"value": ["Folder1"], "guid_list": ["f0000000-0000-0000-0000-000000000001"]}
        },
        raw_block="Create Glossary Term..."
    )
    
    processor = TermProcessor(client, cmd)
    processor.parsed_output = {
        "attributes": cmd.attributes,
        "qualified_name": cmd.attributes["Qualified Name"]["value"],
        "valid": True
    }
    processor.render_result_markdown = AsyncMock(return_value="# Result")
    
    await processor.apply_changes()
    
    # Verify create called
    client._async_create_glossary_term.assert_called_once()
    
    # A brand-new term (known_new=True in _sync_term_memberships,
    # md_processing/v2/glossary.py) cannot have any existing
    # CollectionMembership relationships, so the expensive "what does this
    # element currently belong to" fetch is deliberately skipped entirely
    # for Create -- confirm the optimization actually skips it, not just
    # that sync still produces the right adds (below).
    client._async_get_related_elements.assert_not_called()

    # Verify add_to_collection called for each
    add_calls = [call.args for call in client._async_add_to_collection.call_args_list]
    assert ("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "00000000-0000-0000-0000-000000000001") in add_calls
    assert ("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb", "00000000-0000-0000-0000-000000000001") in add_calls
    assert ("f0000000-0000-0000-0000-000000000001", "00000000-0000-0000-0000-000000000001") in add_calls
    
    print("Test Create: PASSED")
    
    # 2. Test Update with Merge Update = False (Synchronize)
    client.reset_mock()
    # Now term is in A, B, 1
    client._async_get_related_elements.return_value = [
        {"elementHeader": {"guid": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"}},
        {"elementHeader": {"guid": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"}},
        {"elementHeader": {"guid": "f0000000-0000-0000-0000-000000000001"}}
    ]
    
    cmd_update = DrECommand(
        verb="Update",
        object_type="Glossary Term",
        attributes={
            "Display Name": {"value": "TestTerm"},
            "Qualified Name": {"value": "QN123"},
            "Glossary Name": {"value": ["GlossaryA", "GlossaryC"], "guid_list": ["aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "cccccccc-cccc-cccc-cccc-cccccccccccc"]},
            "Merge Update": {"value": False}
        },
        raw_block="Update Glossary Term..."
    )
    
    processor_update = TermProcessor(client, cmd_update)
    processor_update.parsed_output = {
        "attributes": cmd_update.attributes,
        "qualified_name": cmd_update.attributes["Qualified Name"]["value"],
        "guid": "00000000-0000-0000-0000-000000000001",
        "valid": True
    }
    processor_update.render_result_markdown = AsyncMock(return_value="# Result")
    
    await processor_update.apply_changes()
    
    # Verify update called with correct mergeUpdate flag
    client._async_update_glossary_term.assert_called_once()
    update_body = client._async_update_glossary_term.call_args.args[1]
    assert update_body["mergeUpdate"] is False
    
    # Should ADD C and REMOVE B and 1
    add_calls = [call.args for call in client._async_add_to_collection.call_args_list]
    remove_calls = [call.args for call in client._async_remove_from_collection.call_args_list]
    
    assert ("cccccccc-cccc-cccc-cccc-cccccccccccc", "00000000-0000-0000-0000-000000000001") in add_calls
    assert ("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb", "00000000-0000-0000-0000-000000000001") in remove_calls
    assert ("f0000000-0000-0000-0000-000000000001", "00000000-0000-0000-0000-000000000001") in remove_calls
    assert ("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "00000000-0000-0000-0000-000000000001") not in add_calls # Already there
    
    print("Test Update (Merge=False): PASSED")

    # 3. Test Update with Merge Update = True (Additive)
    client.reset_mock()
    client._async_get_related_elements.return_value = [
        {"elementHeader": {"guid": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"}}
    ]
    
    cmd_merge = DrECommand(
        verb="Update",
        object_type="Glossary Term",
        attributes={
            "Display Name": {"value": "TestTerm"},
            "Qualified Name": {"value": "QN123"},
            "Glossary Name": {"value": ["GlossaryB"], "guid_list": ["bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"]},
            "Merge Update": {"value": True}
        },
        raw_block="Update Glossary Term..."
    )
    
    processor_merge = TermProcessor(client, cmd_merge)
    processor_merge.parsed_output = {
        "attributes": cmd_merge.attributes,
        "qualified_name": cmd_merge.attributes["Qualified Name"]["value"],
        "guid": "00000000-0000-0000-0000-000000000001",
        "valid": True
    }
    processor_merge.render_result_markdown = AsyncMock(return_value="# Result")
    
    await processor_merge.apply_changes()
    
    # Verify update called with correct mergeUpdate flag
    client._async_update_glossary_term.assert_called_once()
    merge_body = client._async_update_glossary_term.call_args.args[1]
    assert merge_body["mergeUpdate"] is True
    
    # Check that properties NOT in the command (like abbreviation) are NOT in the body
    # while identification fields (class, typeName) are preserved.
    assert "abbreviation" not in merge_body["properties"]
    assert "class" in merge_body["properties"]
    assert "typeName" in merge_body["properties"]
    
    # Should ADD B and NOT remove A
    add_calls = [call.args for call in client._async_add_to_collection.call_args_list]
    remove_calls = [call.args for call in client._async_remove_from_collection.call_args_list]
    
    assert ("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb", "00000000-0000-0000-0000-000000000001") in add_calls
    assert len(remove_calls) == 0
    
    print("Test Update (Merge=True): PASSED")

if __name__ == "__main__":
    asyncio.run(test_glossary_term_processing())
