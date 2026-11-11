# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Replay the report-spec rendering fixtures (data/report_specs/*.json.gz) through the real pyegeria
stack: every request a report spec makes is answered from Egeria's raw JSON recorded on laz by
scripts/capture_report_fixtures.py, so each output format renders offline exactly as it would live.

    replay = ReportReplay(monkeypatch, "risk_register")
    out = replay.run("LIST")        # exec_report_spec with the tile's own spec and params

A request the fixture does not hold fails the test with its method, path and body.
"""
import copy
import gzip
import json
from pathlib import Path
from urllib.parse import urlparse

import httpx

from pyegeria.core._base_platform_client import BasePlatformClient
from pyegeria.core._base_server_client import BaseServerClient
from pyegeria.view.format_set_executor import exec_report_spec

DATA = Path(__file__).parent / "data" / "report_specs"
TILES = ("risk_register", "governance_metrics", "ninety_day_plan", "digital_products", "isc_register")


def load_fixture(name):
    with gzip.open(DATA / f"{name}.json.gz", "rt", encoding="utf-8") as f:
        return json.load(f)


def _key(method, path, body):
    return json.dumps([method.upper(), path, body], sort_keys=True, default=str)


class ReportReplay:
    def __init__(self, monkeypatch, name, *, answer_override=None):
        self.fixture = load_fixture(name)
        self.answers = {_key(c["method"], c["path"], c["body"]): c for c in self.fixture["calls"]}
        self.override = answer_override
        self.requests = []

        async def replay(client, request_type, endpoint, payload=None, *args, **kwargs):
            p = urlparse(endpoint)
            path = p.path + (f"?{p.query}" if p.query else "")
            body = json.loads(payload) if isinstance(payload, str) and payload.strip().startswith("{") else payload
            self.requests.append((request_type.upper(), path, body))
            call = self.answers.get(_key(request_type, path, body))
            if call is None:
                raise AssertionError(f"no recorded answer for {request_type} {path} {json.dumps(body, default=str)}")
            answer = copy.deepcopy(call["answer"])
            if self.override:
                answer = self.override(path, body, answer)
            request = (httpx.Request(request_type.upper(), endpoint, json=body) if isinstance(body, dict)
                       else httpx.Request(request_type.upper(), endpoint))
            return httpx.Response(call.get("status", 200), json=answer, request=request)

        for cls in (BaseServerClient, BasePlatformClient):
            monkeypatch.setattr(cls, "_async_make_request", replay)
            if hasattr(cls, "check_connection"):
                monkeypatch.setattr(cls, "check_connection", lambda self: "replay", raising=False)

    def run(self, output_format, **params):
        return exec_report_spec(self.fixture["spec"], output_format=output_format,
                                params={**self.fixture["params"], **params},
                                view_server="qs-view-server", view_url="https://localhost:9443",
                                user=self.fixture["user"], user_pass="", token="replay-token")
