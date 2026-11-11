#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Capture the SD-2 export_dcat fixtures from a live Egeria, READ-ONLY.

Runs `export_dcat` through a recording proxy around a real EgeriaTech, so each fixture holds
exactly the calls the exporter made and Egeria's raw answers (or, for a refused read, the raw
Egeria error body). Nothing is written to Egeria: the exporter only reads, and the proxy refuses
any method whose name does not start with get_/find_.

    EGERIA_USER=erinoverview EGERIA_USER_PASSWORD=... \\
      uv run -p 3.13 python scripts/capture_dcat_fixtures.py tests/micro-tests/data/dcat

Scopes captured (laz, 2026-11-11) are listed in SCOPES below; the zone-refused Report is read by
GUID only, to record a real OPEN-METADATA-SECURITY-403-020 answer.
"""
import json
import os
import sys
from datetime import datetime, timezone

from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.view.export_dcat import export_dcat

SCOPES = [
    ("portal_dashboards", {"scope": "DashboardFolder::Consumer::Portal"}),
    ("org_structure_products", {"scope": "DigitalProductFamily::Jacquard::ORGANIZATION-STRUCTURE-FAMILY::Organization Structure"}),
    ("clinical_trial_files", {"search_string": "DataLake::PROJ-CT-TBDF::WeeklyMeasurements::Oak Dene Hospital::PROJ-CT-TBDF_00002"}),
    ("coco_data_hub", {"search_string": "PostgreSQL Relational Database::Coco PostgreSQL Server 1::coco_data_hub"}),
]
#: A Report zoned ['peterprofile'] (B4 scratch-restricted-demo); erinoverview's read by GUID is refused.
NOT_VISIBLE_GUID = "eccbf12f-d1df-48db-b2b6-dcfb2e30504b"


class Recorder:
    def __init__(self, client):
        self._client = client
        self.user_id = client.user_id
        self.calls = []

    def __getattr__(self, name):
        if not (name.startswith("get_") or name.startswith("find_")):
            raise AttributeError(f"capture is read-only: {name} refused")
        method = getattr(self._client, name)

        def call(*args, **kwargs):
            record = {"method": name, "args": list(args), "kwargs": kwargs}
            try:
                result = method(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001 -- recorded, then re-raised
                record["error"] = {"class": type(exc).__name__,
                                   "related_http_code": getattr(exc, "related_http_code", None),
                                   "additional_info": getattr(exc, "additional_info", None),
                                   "message": str(getattr(exc, "message", "") or exc)}
                self.calls.append(record)
                raise
            record["result"] = result
            self.calls.append(record)
            return result
        return call


def main(out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    client = EgeriaTech(os.environ.get("EGERIA_VIEW_SERVER", "qs-view-server"),
                        os.environ.get("EGERIA_VIEW_SERVER_URL", "https://localhost:9443"),
                        user_id=os.environ.get("EGERIA_USER", "erinoverview"),
                        user_pwd=os.environ.get("EGERIA_USER_PASSWORD", ""))
    client.create_egeria_bearer_token()
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for name, params in SCOPES:
        rec = Recorder(client)
        out = export_dcat(rec, **params)
        fixture = {"captured": stamp, "server": "laz qs-view-server", "user": rec.user_id, "params": params,
                   "calls": rec.calls}
        with open(os.path.join(out_dir, f"{name}.json"), "w", encoding="utf-8") as f:
            json.dump(fixture, f, indent=1, sort_keys=True, default=str)
        print(f"{name}: {len(rec.calls)} calls; notes:")
        for n in out["notes"]:
            print("   ", n)
    rec = Recorder(client)
    try:
        rec.get_element_by_guid(NOT_VISIBLE_GUID, output_format="JSON")
        print("WARNING: the zone-refused Report was readable; no 403 captured")
    except Exception:  # noqa: BLE001
        pass
    with open(os.path.join(out_dir, "not_visible_report.json"), "w", encoding="utf-8") as f:
        json.dump({"captured": stamp, "server": "laz qs-view-server", "user": rec.user_id, "calls": rec.calls},
                  f, indent=1, sort_keys=True, default=str)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "tests/micro-tests/data/dcat")
