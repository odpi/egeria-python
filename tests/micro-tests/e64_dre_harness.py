# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""A fake Egeria for the Dr.Egeria Egeria 6.4 command tests (Phase B), loaded by file path from the tests.

A markdown document goes through the real path: UniversalExtractor -> setup_dispatcher -> the command's processor
-> the REAL pyegeria 6.4 wrapper (GovernanceOfficer, DataEngineer, ProjectManager, SchemaMaker, DevopsPipeline),
whose ``_async_make_request`` is patched to record what it would send. So a test sees the exact body the A6
wrapper produced, after its own checks (properties class, unread keys, int positions) passed.

No live server.
"""
from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional

from pyegeria import NO_ELEMENTS_FOUND
from pyegeria.core import egeria_6_4_gate
from pyegeria.omvs.data_engineer import DataEngineer
from pyegeria.omvs.devops_pipeline import DevopsPipeline
from pyegeria.omvs.governance_officer import GovernanceOfficer
from pyegeria.omvs.project_manager import ProjectManager
from pyegeria.omvs.schema_maker import SchemaMaker

from md_processing.dr_egeria import setup_dispatcher
from md_processing.v2.extraction import UniversalExtractor

PLATFORM = "https://localhost:1"
SERVER = "view-server"
ROOT = f"{PLATFORM}/servers/{SERVER}/api/open-metadata/"
NEW_GUID = "0a9e9a52-0000-4000-8000-00000000c0de"

#: about answers for the gate
ABOUT_6_3 = json.dumps({"class": "AboutPlatform", "version": "6.3", "time": "2026-11-20T10:00:00Z"})
ABOUT_6_4 = json.dumps({"class": "AboutPlatform", "version": "6.4-SNAPSHOT", "time": "2026-11-21T20:30:00Z"})


class _Response:
    def __init__(self, payload: Any, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code
        self.text = json.dumps(payload)

    def json(self):
        return self._payload


class FakeEgeria:
    """Stands in for EgeriaTech: name lookups, the five 6.4 subclients (real wrappers, request recorded)."""

    def __init__(self, monkeypatch, names: Optional[Dict[str, str]] = None, about: Optional[str] = None,
                 respond: Optional[Callable[[str, str, Any], Any]] = None):
        self.calls: List[Dict[str, Any]] = []
        self.names = names or {}
        self._respond = respond
        egeria_6_4_gate.clear_cache()
        if about is not None:
            self.platform_url = PLATFORM

            async def origin():
                return about
            self.async_get_platform_origin = origin
        for cls in (GovernanceOfficer, DataEngineer, ProjectManager, SchemaMaker, DevopsPipeline):
            monkeypatch.setattr(cls, "check_connection", lambda self: "test")
        self.governance_officer = self._wrap(GovernanceOfficer(SERVER, PLATFORM, "user", "pwd"))
        self.data_engineer = self._wrap(DataEngineer(SERVER, PLATFORM, "user", "pwd"))
        self.project_manager = self._wrap(ProjectManager(SERVER, PLATFORM, "user", "pwd"))
        self.schema_maker = self._wrap(SchemaMaker(SERVER, PLATFORM, "user", "pwd"))
        self.devops_pipeline = self._wrap(DevopsPipeline(SERVER, PLATFORM, "user", "pwd"))

    def _wrap(self, client):
        async def fake_make_request(method, url, payload=None, *args, **kwargs):
            body = json.loads(payload) if isinstance(payload, str) else payload
            path = url[len(ROOT):] if url.startswith(ROOT) else url
            self.calls.append({"method": method, "path": path, "body": body})
            answer = self._respond(method, path, body) if self._respond else None
            if isinstance(answer, BaseException):
                raise answer
            if answer is None:
                answer = {"class": "GUIDResponse", "relatedHTTPCode": 200, "guid": NEW_GUID}
            return _Response(answer)
        client._async_make_request = fake_make_request
        return client

    async def __async_get_guid__(self, qualified_name=None, display_name=None, property_name="qualifiedName",
                                 tech_type=None, **kwargs):
        return self.names.get(qualified_name or display_name, NO_ELEMENTS_FOUND)

    async def _async_get_element_by_guid_(self, guid, *args, **kwargs):
        return NO_ELEMENTS_FOUND

    async def _async_get_metadata_element_by_guid(self, guid, *args, **kwargs):
        return None

    def writes(self, path_part: str) -> List[Dict[str, Any]]:
        """The recorded requests whose path contains `path_part`."""
        return [c for c in self.calls if path_part in c["path"]]


async def run_doc(fake: FakeEgeria, text: str, directive: str = "process") -> List[Dict[str, Any]]:
    """Run a Dr.Egeria document through the real extractor and dispatcher; the command results, in order."""
    commands = [c for c in UniversalExtractor(text).extract_commands() if c.is_command]
    assert commands, "the document has no command"
    return await setup_dispatcher(fake).dispatch_batch(commands, {"directive": directive})
