#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

`pyegeria report-specs sync`: sync report specs held in Egeria into the local cache that the
registry's EGERIA tier reads (report-spec pipeline model §7a "Sync"; RS-EGERIA-TIER stage 1).

    pyegeria report-specs sync [--folder QN]... [--spec LABEL]... [--include-drafts]
                               [--cache-dir D] [--shared]

With no --folder and no --spec it takes the folders configured in "Pyegeria Report Spec Folders"
(config.json) or PYEGERIA_REPORT_SPEC_FOLDERS; with none configured it says so and syncs nothing.
It prints the sync report as it is. Credentials come from the usual pyegeria settings
(EGERIA_VIEW_SERVER, EGERIA_VIEW_SERVER_URL, EGERIA_USER, EGERIA_USER_PASSWORD) or the options.
"""
from __future__ import annotations

import argparse
import json
import sys


def _sync(args) -> int:
    from pyegeria.core.config import settings
    from pyegeria.omvs.collection_manager import CollectionManager
    from pyegeria.view.egeria_spec_cache import SyncAlreadyRunning, sync_report_specs

    client = CollectionManager(args.server or settings.Environment.egeria_view_server,
                               args.url or settings.Environment.egeria_view_server_url,
                               user_id=args.userid or settings.User_Profile.user_name,
                               user_pwd=args.password or settings.User_Profile.user_pwd)
    try:
        client.create_egeria_bearer_token()
        report = sync_report_specs(client, folders=args.folder or None, specs=args.spec or None,
                                   include_drafts=args.include_drafts, cache_dir=args.cache_dir,
                                   shared=True if args.shared else None)
    except SyncAlreadyRunning as exc:
        print(str(exc), file=sys.stderr)
        return 2
    finally:
        try:
            client.close_session()
        except Exception:  # noqa: BLE001
            pass
    print(json.dumps(report.to_dict(), indent=2) if args.json else report.render())
    return 1 if report.skipped and not (report.added or report.updated or report.unchanged) else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="pyegeria", description="pyegeria command line tools.")
    groups = parser.add_subparsers(dest="group", required=True)
    rs = groups.add_parser("report-specs", help="Report specs held in Egeria.")
    cmds = rs.add_subparsers(dest="command", required=True)
    sync = cmds.add_parser("sync", help="Sync report specs held in Egeria into the local cache.")
    sync.add_argument("--folder", action="append", metavar="QN",
                      help="CollectionFolder qualified name (repeatable). Default: the configured folders.")
    sync.add_argument("--spec", action="append", metavar="LABEL",
                      help="Sync only this spec label (repeatable); prunes nothing else.")
    sync.add_argument("--include-drafts", action="store_true",
                      help="Also take DRAFT and PROPOSED specs, into the separate drafts/ cache.")
    sync.add_argument("--cache-dir", metavar="D", help="Cache directory (default: PYEGERIA_REPORT_SPEC_CACHE_DIR, "
                                                        "else ~/.pyegeria/cache/report_specs/<platform>/<server>).")
    sync.add_argument("--shared", action="store_true",
                      help="Mark the cache shared: a fetch-on-call never writes into it.")
    sync.add_argument("--json", action="store_true", help="Print the report as JSON.")
    sync.add_argument("--server", help="View server name.")
    sync.add_argument("--url", help="View server platform URL.")
    sync.add_argument("--userid", help="User id.")
    sync.add_argument("--password", help="Password (prefer the environment).")
    args = parser.parse_args(argv)
    if args.group == "report-specs" and args.command == "sync":
        return _sync(args)
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    sys.exit(main())
