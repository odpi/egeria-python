# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""PY-8: no new unpaged by-name read slips in without a disposition.

get_collections_by_name (and the communities / note-logs by-name family) is a findMetadataElements search on the
server, so a single page proves nothing: an exact qualified name goes through Egeria's unique-name read
(pyegeria.core.unique_name), a label is paged with paging_for. test_by_name_dispositions.py proves each
existing call site's behaviour; this test pins WHICH modules may call them, so a new call site fails here until
someone gives it a disposition and adds it to the table.
"""
import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]
CALL = re.compile(r"\b_?(?:async_)?get_(?:collections|communities)_by_name\s*\(|\b_async_get_note_logs_by_name\s*\(")

#: module -> disposition. The definitions and their sync/async wrappers live in omvs/ and core/.
ALLOWED = {
    "pyegeria/omvs/collection_manager.py": "definition and its sync wrapper",
    "pyegeria/omvs/community_matters_omvs.py": "definition and its sync wrapper",
    "pyegeria/core/_server_client.py": "note-log by-name wrapper (definition side)",
    "pyegeria/view/egeria_spec_cache.py": "label lookup: paged with paging_for; 'not found' only on a confirmed end",
}
#: Prototype screens that don't use the SDK's by-name read at all (they pass a GUID to a manager stub); not a
#: get-or-create guard and not a display of a name lookup, so no disposition applies. Revisit if they are finished.
PROTOTYPES = {
    "my_egeria/my_egeria/services/governance_officer_service.py",
    "my_egeria/my_egeria/screens/GovernanceOfficer/governance_officer_browser.py",
}


def _callers():
    found = {}
    for top in ("pyegeria", "md_processing", "commands", "my_egeria"):
        for path in (ROOT / top).rglob("*.py"):
            rel = path.relative_to(ROOT).as_posix()
            text = path.read_text(encoding="utf-8", errors="ignore")
            hits = [i + 1 for i, line in enumerate(text.splitlines())
                    if CALL.search(line) and not line.lstrip().startswith(("#", "def ", "async def "))]
            if hits:
                found[rel] = hits
    return found


def test_every_unpaged_by_name_call_site_has_a_disposition():
    unexpected = {m: lines for m, lines in _callers().items() if m not in ALLOWED and m not in PROTOTYPES}
    assert not unexpected, (
        "a get_*_by_name call with no disposition (an exact qualified name -> pyegeria.core.unique_name; a label "
        f"-> paging_for, 'not found' only on a confirmed end): {unexpected}")


def test_the_table_has_no_stale_rows():
    seen = _callers()
    stale = [m for m in list(ALLOWED) + sorted(PROTOTYPES) if m not in seen]
    assert not stale, f"in the disposition table but no longer calling a by-name read: {stale}"
