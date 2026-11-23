"""
Digital Products family commands (md_processing/v2/product_manager.py) through the real
dispatcher with a fake client: Import / Publish Data Contract and
Data Product -- plus the extractor recognising the new Import / Publish verbs.
"""
from typing import Any, Dict, List

import pytest

from pyegeria import NO_ELEMENTS_FOUND

from md_processing.dr_egeria import setup_dispatcher
from md_processing.v2.extraction import DrECommand, UniversalExtractor

ELEMENTS = {
    "Hospital Data": "product-1",
    "Hospital Asset": "asset-1",
    "Hospital Feed": "asset-2",
    "Bitol Daemon": "daemon-1",
    "Baudot Manager": "manager-1",
}
CONTRACT = "apiVersion: v3.1.0\nkind: DataContract\nid: 6d0f\nname: Weekly measurements\nversion: 1.0.0\n"


class _FakeProductManager:
    def __init__(self, import_guid="agreement-1"):
        self.calls: List[tuple] = []
        self.import_guid = import_guid

    async def _async_create_one_time_subscription(self, guid, body=None):
        self.calls.append(("one-time", guid, body)); return "gap-one-time"

    async def _async_create_periodic_subscription(self, guid, body=None):
        self.calls.append(("periodic", guid, body)); return "gap-periodic"

    async def _async_create_ongoing_update_subscription(self, guid, body=None):
        self.calls.append(("ongoing-update", guid, body)); return "gap-ongoing"

    async def _async_import_data_contract_string(self, document):
        self.calls.append(("import-contract", document)); return self.import_guid

    async def _async_import_data_product_string(self, document):
        self.calls.append(("import-product", document)); return self.import_guid

    async def _async_publish_data_contract_string(self, daemon_guid, document):
        self.calls.append(("publish-contract", daemon_guid, document))

    async def _async_publish_data_product_string(self, daemon_guid, document):
        self.calls.append(("publish-product", daemon_guid, document))


class _FakeClient:
    def __init__(self, **kwargs):
        self.product_manager = _FakeProductManager(**kwargs)

    async def __async_get_guid__(self, qualified_name=None, display_name=None, property_name="qualifiedName",
                                 tech_type=None, **kwargs):
        guid = ELEMENTS.get(qualified_name or display_name)
        return guid or NO_ELEMENTS_FOUND


def _cmd(verb: str, object_type: str, attributes: Dict[str, Any]) -> DrECommand:
    raw = f"## {verb} {object_type}\n" + "".join(f"### {k}\n{v}\n" for k, v in attributes.items())
    return DrECommand(verb=verb, object_type=object_type, attributes=attributes, raw_block=raw)


async def _run(command: DrECommand, context=None, **client_kwargs):
    client = _FakeClient(**client_kwargs)
    ctx = {"directive": "process", **(context or {})}
    results = await setup_dispatcher(client).dispatch_batch([command], ctx)
    return results[0], client.product_manager.calls


# PY-49: the Create Subscription Type command no longer exists (Egeria 6.4 has no subscription type), so its tests
# are gone with it.


# --- Import / Publish documents --------------------------------------------------------------

def _doc(tmp_path, name="contract.yaml", text=CONTRACT):
    (tmp_path / name).write_text(text)
    return {"input_path": str(tmp_path / "doc.md")}


@pytest.mark.asyncio
@pytest.mark.parametrize("object_type, call", [("Data Contract", "import-contract"), ("Data Product", "import-product")])
async def test_import_reads_the_file_relative_to_the_markdown_document(tmp_path, object_type, call):
    context = _doc(tmp_path)
    result, calls = await _run(_cmd("Import", object_type, {"Document File": "contract.yaml"}), context)

    assert result["status"] == "success", result
    assert calls == [(call, CONTRACT)]
    assert "agreement-1" in result["output"]


@pytest.mark.asyncio
async def test_import_that_egeria_skips_is_reported_not_swallowed(tmp_path):
    context = _doc(tmp_path)
    result, calls = await _run(_cmd("Import", "Data Contract", {"Document File": "contract.yaml"}), context,
                               import_guid=None)

    assert result["status"] != "success"
    assert "skipped" in result["message"]


@pytest.mark.asyncio
@pytest.mark.parametrize("object_type, call", [("Data Contract", "publish-contract"), ("Data Product", "publish-product")])
async def test_publish_sends_the_document_to_the_resolved_daemon(tmp_path, object_type, call):
    context = _doc(tmp_path)
    result, calls = await _run(_cmd("Publish", object_type, {
        "Integration Daemon": "Bitol Daemon", "Document File": "contract.yaml"}), context)

    assert result["status"] == "success", result
    assert calls == [(call, "daemon-1", CONTRACT)]


@pytest.mark.asyncio
@pytest.mark.parametrize("verb, extra", [("Import", {}), ("Publish", {"Integration Daemon": "Bitol Daemon"})])
async def test_missing_or_empty_document_file_fails_before_calling_egeria(tmp_path, verb, extra):
    context = _doc(tmp_path, "empty.yaml", "   \n")
    for name in ("does-not-exist.yaml", "empty.yaml"):
        result, calls = await _run(_cmd(verb, "Data Contract", {"Document File": name, **extra}), context)
        assert result["status"] != "success"
        assert calls == []


@pytest.mark.asyncio
async def test_absolute_document_path_is_used_as_given(tmp_path):
    (tmp_path / "abs.yaml").write_text(CONTRACT)
    result, calls = await _run(_cmd("Import", "Data Contract", {"Document File": str(tmp_path / "abs.yaml")}),
                               {"input_path": "/somewhere/else/doc.md"})

    assert result["status"] == "success", result
    assert calls == [("import-contract", CONTRACT)]


# --- the new verbs must be recognised as commands, not prose --------------------------------

@pytest.mark.parametrize("heading, verb, object_type", [
    ("## Import Data Contract", "Import", "Data Contract"),
    ("## Import Data Product", "Import", "Data Product"),
    ("## Publish Data Contract", "Publish", "Data Contract"),
    ("## Publish Data Product", "Publish", "Data Product"),
])
def test_new_headings_are_extracted_as_commands(heading, verb, object_type):
    text = f"\n___\n\n{heading}\n\n### Document File\nc.yaml\n\n___\n"
    commands = [c for c in UniversalExtractor(text).extract_commands() if c.is_command]

    assert [(c.verb, c.object_type) for c in commands] == [(verb, object_type)]
