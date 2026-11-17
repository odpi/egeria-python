#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Re-capture tests/micro-tests/data/authoring/catalog_health_scratch.json from a live Egeria, READ-ONLY.

Runs `pyegeria.authoring.lifecycle.async_load_held("sheet", "catalog-health", ...)` through a recording proxy
around a real EgeriaTech, so the fixture holds exactly the calls load_held makes at this checkout -- including
the pager's probe pages past each null (pager step 4/5), which the 2026-11-12 capture predates -- and
Egeria's raw answers. Nothing is written: the proxy refuses any method whose name doesn't start with
_async_get_ / _async_find_ / get_ / find_.

The platform must already hold the catalog-health sheet (the fixture's `document`, processed once). The
original came from the round-trip probe's SCRATCH Egeria; laz's sheet differs (it also has the saved-query
tile, covered by test_authoring_laz_sheet.py), so capture where that document was processed.

    EGERIA_VIEW_SERVER=view-server EGERIA_VIEW_SERVER_URL=https://localhost:19443 \\
    EGERIA_USER=garygeeke EGERIA_USER_PASSWORD=... \\
      uv run python scripts/capture_catalog_health_fixture.py tests/micro-tests/data/authoring/catalog_health_scratch.json

EGERIA_VIEW_SERVER is required: the round-trip probe's scratch platform runs "view-server", laz runs
"qs-view-server". (The 2026-11-14 attempt used qs-view-server on scratch; that 404'd as "server not available",
which pyegeria then reported as "holds no dashboard sheet" -- fixed so it raises instead.)

The password is read from the environment and never printed.
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone

from pyegeria.authoring.lifecycle import async_load_held
from pyegeria.egeria_tech_client import EgeriaTech

READ_PREFIXES = ("_async_get_", "_async_find_", "get_", "find_")


class _Sub:
    def __init__(self, recorder, name, target):
        self._recorder, self._name, self._target = recorder, name, target

    def __getattr__(self, method):
        if not method.startswith(READ_PREFIXES):
            raise AttributeError(f"capture is read-only: {self._name}.{method} refused")
        fn = getattr(self._target, method)

        async def call(*args, **kwargs):
            record = {"sub": self._name, "method": method, "args": list(args), "kwargs": kwargs}
            result = fn(*args, **kwargs)
            if asyncio.iscoroutine(result):
                result = await result
            record["result"] = result
            self._recorder.calls.append(record)
            return result
        return call


class Recorder:
    def __init__(self, client):
        self._client, self.user_id, self.calls = client, client.user_id, []

    def __getattr__(self, name):
        return _Sub(self, name, getattr(self._client, name))


def main(out_path: str) -> None:
    with open(out_path, encoding="utf-8") as f:
        old = json.load(f)
    if not os.environ.get("EGERIA_VIEW_SERVER"):
        sys.exit("EGERIA_VIEW_SERVER is required (scratch: view-server; laz: qs-view-server)")
    client = EgeriaTech(os.environ["EGERIA_VIEW_SERVER"],
                        os.environ.get("EGERIA_VIEW_SERVER_URL", "https://localhost:19443"),
                        user_id=os.environ.get("EGERIA_USER", "garygeeke"),
                        user_pwd=os.environ.get("EGERIA_USER_PASSWORD", ""))
    client.create_egeria_bearer_token()
    rec = Recorder(client)
    sheet = asyncio.run(async_load_held("sheet", "catalog-health", rec))
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    fixture = {"_about": old.get("_about", "") + f" Re-captured {stamp} at "
                                                 f"{os.environ.get('EGERIA_VIEW_SERVER_URL', '')} with probe pages.",
               "document": old.get("document"), "user": rec.user_id, "calls": rec.calls}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(fixture, f, indent=1, sort_keys=True, default=str)
    print(f"{len(rec.calls)} calls; {len(sheet.placements)} placements")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "tests/micro-tests/data/authoring/catalog_health_scratch.json")
