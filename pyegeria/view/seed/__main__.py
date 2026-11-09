"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

`python -m pyegeria.view.seed build` writes the report-spec seed from the Python constants;
`python -m pyegeria.view.seed check` exits 1 when the seed files differ from what `build` would write.
"""

from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m pyegeria.view.seed",
                                     description="Build or check pyegeria's report-spec seed (packaged JSON).")
    parser.add_argument("command", choices=["build", "check"])
    parser.add_argument("--dir", default=None, help="the seed directory (default: the packaged one)")
    args = parser.parse_args(argv)

    from pyegeria.view import seed
    directory = Path(args.dir) if args.dir else seed.SEED_DIR
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        if args.command == "build":
            files = seed.write_seed(directory)
            import json
            census = json.loads(files[seed.MANIFEST])["census"]
            print(f"Report spec seed written to {directory}: {len(files) - 1} family files, census {census}")
            return 0
        diffs = seed.check_seed(directory)
    if diffs:
        print("The report spec seed is stale; run `python -m pyegeria.view.seed build`:", file=sys.stderr)
        for d in diffs:
            print(f"  {d}", file=sys.stderr)
        return 1
    print(f"The report spec seed in {directory} is current.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
