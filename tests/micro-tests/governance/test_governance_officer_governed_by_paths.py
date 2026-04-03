import pytest

from pyegeria.omvs.governance_officer import GovernanceOfficer


@pytest.mark.asyncio
async def test_detach_governed_by_uses_definition_path_segment():
    client = GovernanceOfficer("view-server", "https://localhost:9443", "user", "pwd")
    captured = {}

    async def _fake_delete(url, body):
        captured["url"] = url
        captured["body"] = body

    client._async_delete_relationship_request = _fake_delete

    await client._async_detach_governed_by_definition("element-guid", "definition-guid", {"class": "DeleteRelationshipRequestBody"})

    assert "/governed-by/definition/definition-guid/detach" in captured["url"]


