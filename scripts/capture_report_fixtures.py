#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Capture the report-spec rendering fixtures (fix-now, R1-R3) from a live Egeria, READ-ONLY.

Runs each CDO-sheet tile's report spec through `exec_report_spec` with a recorder around the HTTP
layer (`_async_make_request`), and stores each request (method, path, body) with Egeria's raw JSON
answer -- the raw element JSON, never pyegeria's output. `tests/micro-tests/report_fixture_replay.py`
answers the same requests from the file, so every output format can be rendered offline.

Read-only: the recorder refuses any request whose path is not a find/get/by-search/by-name read.

    EGERIA_USER=erinoverview EGERIA_USER_PASSWORD=... \\
      uv run -p 3.13 python scripts/capture_report_fixtures.py tests/micro-tests/data/report_specs
"""
import json
import os
import re
import sys
from datetime import datetime, timezone
from urllib.parse import urlparse

from pyegeria.core._base_platform_client import BasePlatformClient
from pyegeria.core._base_server_client import BaseServerClient
from pyegeria.view.format_set_executor import exec_report_spec

#: The tiles of the CDO sheet "How the Data Governance Program is Going" (Chief Data Officer Dashboard).
TILES = [
    ("risk_register", "Risk-DrE-Basic", {"search_string": "CocoPharma::Risk::"}, ["LIST", "DICT"]),
    ("governance_metrics", "Governance-Metric-DrE-Basic", {"search_string": "CocoPharma::GovernanceMetric::"},
     ["LIST", "DICT"]),
    ("ninety_day_plan", "Project-DrE-Basic", {"search_string": "JulesKeeper::"}, ["LIST", "DICT"]),
    ("digital_products", "Digital-Products", {"search_string": "*"}, ["DICT", "REPORT"]),
    ("isc_register", "Collections", {"search_string": "Strategic Information Supply Chains"}, ["MERMAID", "DICT"]),
]

_READ_PATH = re.compile(r"(/by-search-string|/by-name|/by-type|/by-guid|/elements/|/members|/find|/retrieve|"
                        r"/collections/[^/]+$|/token|/users/|/api/about|/platform/origin)", re.I)
_RECORDS = []


def _path(endpoint: str) -> str:
    p = urlparse(endpoint)
    return p.path + (f"?{p.query}" if p.query else "")


def _wrap(cls):
    original = cls._async_make_request

    async def recording(self, request_type, endpoint, payload=None, *args, **kwargs):
        path = _path(endpoint)
        if request_type.upper() not in ("GET", "POST") or not _READ_PATH.search(path) or "delete" in path or \
                "update" in path or "attach" in path or "detach" in path:
            raise RuntimeError(f"capture is read-only: {request_type} {path} refused")
        response = await original(self, request_type, endpoint, payload, *args, **kwargs)
        body = payload if not isinstance(payload, str) else _maybe_json(payload)
        try:
            answer = response.json()
        except Exception:  # noqa: BLE001 -- a text answer is kept as text
            answer = {"__text__": getattr(response, "text", str(response))}
        _RECORDS.append({"method": request_type.upper(), "path": path, "body": body,
                         "status": getattr(response, "status_code", 200), "answer": answer})
        return response

    cls._async_make_request = recording


def _maybe_json(text):
    try:
        return json.loads(text)
    except Exception:  # noqa: BLE001
        return text


def main(out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    _wrap(BaseServerClient)
    _wrap(BasePlatformClient)
    user = os.environ.get("EGERIA_USER", "erinoverview")
    kw = dict(view_server=os.environ.get("EGERIA_VIEW_SERVER", "qs-view-server"),
              view_url=os.environ.get("EGERIA_VIEW_SERVER_URL", "https://localhost:9443"),
              user=user, user_pass=os.environ.get("EGERIA_USER_PASSWORD", ""))
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for name, spec, params, formats in TILES:
        _RECORDS.clear()
        for fmt in formats:
            out = exec_report_spec(spec, output_format=fmt, params=dict(params), **kw)
            print(f"{name} {fmt}: kind {out.get('kind')}")
        seen, calls = set(), []
        for r in _RECORDS:
            if "/token" in r["path"] or "/users/" in r["path"]:
                continue  # authentication: not replayed (tests pass a token)
            key = json.dumps([r["method"], r["path"], r["body"]], sort_keys=True, default=str)
            if key not in seen:
                seen.add(key)
                calls.append(r)
        fixture = {"captured": stamp, "server": "laz qs-view-server", "user": user, "spec": spec,
                   "params": params, "formats": formats, "calls": calls}
        with open(os.path.join(out_dir, f"{name}.json"), "w", encoding="utf-8") as f:
            json.dump(fixture, f, indent=1, sort_keys=True, default=str)
        print(f"{name}: {len(calls)} distinct requests")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "tests/micro-tests/data/report_specs")
