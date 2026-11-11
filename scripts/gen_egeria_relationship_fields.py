#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Regenerate pyegeria/view/egeria_relationship_fields.py from Egeria's element classes.

Reads every `RelatedMetadataElementSummary` / `RelatedMetadataHierarchySummary` field of
`AttributedMetadataElement.java` and `OpenMetadataRootElement.java` (open-metadata-framework,
metadataelements) with the relationship type names its trailing comment gives. Run it when Egeria adds
relationships, and say the egeria commit in the commit message.

    uv run -p 3.13 python scripts/gen_egeria_relationship_fields.py ~/localGit/egeria-v6/egeria
"""
import re
import subprocess
import sys
from pathlib import Path

REL = ("open-metadata-implementation/frameworks/open-metadata-framework/src/main/java/org/odpi/openmetadata/"
       "frameworks/openmetadata/metadataelements")
OUT = Path(__file__).resolve().parent.parent / "pyegeria" / "view" / "egeria_relationship_fields.py"


def fields(egeria: Path) -> dict:
    src = "".join((egeria / REL / f).read_text() for f in ("AttributedMetadataElement.java",
                                                         "OpenMetadataRootElement.java"))
    out = {}
    for m in re.finditer(r"private\s+(?:List<)?RelatedMetadata(?:Element|Hierarchy)Summary>?\s+(\w+)\s*=\s*null;"
                         r"\s*(?://|/\*)\s*([^\n]*)", src):
        types = re.findall(r"\b([A-Z][A-Za-z]+)\b(?=\s*(?:\(|,|/|$|\*))", m.group(2))
        out[m.group(1)] = sorted({t for t in types if t not in ("A", "The")})
    return out


def main(egeria_dir: str) -> None:
    egeria = Path(egeria_dir).expanduser()
    found = fields(egeria)
    commit = subprocess.run(["git", "-C", str(egeria), "log", "-1", "--format=%h, %cs", "--",
                             f"{REL}/AttributedMetadataElement.java", f"{REL}/OpenMetadataRootElement.java"],
                            capture_output=True, text=True).stdout.strip()
    lines = ['# SPDX-License-Identifier: Apache-2.0', '# Copyright Contributors to the ODPi Egeria project.',
             '"""The relationship lists an Egeria 6 element can carry, and the relationship type(s) each one reads.', '',
             "Generated from Egeria's `AttributedMetadataElement.java` and `OpenMetadataRootElement.java`",
             f"(open-metadata-framework, metadataelements; egeria commit {commit.replace(', ', ', ')}): every",
             '`RelatedMetadataElementSummary` field, with the relationship type names its comment gives. An empty tuple',
             'means the comment names none.', '',
             'Used by the structured TABLE and native DICT (R1) to tell a relationship that was read and is absent',
             '("none") from one that was not requested ("not read"): Egeria omits an empty relationship list.', '',
             'Do not edit by hand. Regenerate with `scripts/gen_egeria_relationship_fields.py <egeria checkout>`',
             'when Egeria adds relationships.', '"""', '', 'RELATIONSHIP_FIELDS = {']
    for name in sorted(found):
        types = found[name]
        lines.append(f'    "{name}": ({", ".join(repr(t) for t in types)}{"," if len(types) == 1 else ""}),')
    lines.append("}")
    OUT.write_text("\n".join(lines) + "\n")
    print(f"{len(found)} relationship fields written to {OUT} (egeria {commit})")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "~/localGit/egeria-v6/egeria")
