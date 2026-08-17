# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Regression test for the attribute-name-pooling hazard b17f71e caught by hand.

load_compact_specs_from_dir() (compact_loader.py) merges attribute_definitions
from every compact_commands/*.json file into one global pool keyed by
attribute NAME -- not (family, name). A same-named-but-different-definition
attribute in a new family silently clobbers whichever earlier file's command
templates that name is used by, and the only trace is a `logger.debug` line
(easy to miss; not a warning, not a raised error).

b17f71e's own commit message documents this happening in practice: the
Lineage Linker family's original attribute defs briefly reused the names
"Relationship Type"/"Guard"/"Label"/"Description" with different
definitions than Glossary/Curation/Action Author already used those names
for, corrupting those unrelated families' rendered template output. It was
only caught by a human diffing synced templates afterward, not by a test.

This test reads every real compact_commands/*.json file directly (independent
of load_compact_specs_from_dir's own merge logic, so it isn't fooled if that
function's conflict handling itself regresses). It does NOT assert zero
collisions -- a handful of common attribute names (Identifier, Element Id,
Effective Time, ...) are already, legitimately, defined with slightly
different family-specific wording across many files, predating this test and
not the hazard being guarded against here. Instead it asserts the *set of
colliding names* doesn't grow beyond a known baseline -- so reusing an
EXISTING already-duplicated name is unaffected, but introducing a NEW name
that collides with a different family's definition (the actual failure mode
b17f71e hit) fails the test immediately instead of needing a human to notice
via a template diff.
"""
import json
import os

from md_processing.md_processing_utils.md_processing_constants import COMPACT_RESOURCE_DIR


# Fields _write_attr_block() (commands/tech/generate_md_cmd_templates.py) actually
# renders into a command's ### attribute block -- a difference in any other field
# (variable_name, property_name, existing_element, legacy_enum_type, generated,
# user_specified, unique, cardinality, level, inUpdate, examples, "Journal Entry")
# doesn't change what a user sees in the generated template, so isn't part of this
# specific hazard. Two files legitimately reusing the same attribute name with the
# same visible template content (just different internal bookkeeping/changelog) is
# fine and common in this codebase -- only a difference in one of these fields means
# one file's definition will silently win over the other's in rendered output.
_TEMPLATE_RENDERED_FIELDS = (
    "input_required", "data_type", "style", "description", "attr_labels",
    "valid_values", "default_value",
)


def _rendered_view(adef):
    return {k: adef.get(k) for k in _TEMPLATE_RENDERED_FIELDS}


def _load_all_attribute_definitions():
    """Returns {attr_name: [(fname, definition), ...]} across every compact JSON file."""
    by_name = {}
    for fname in sorted(os.listdir(COMPACT_RESOURCE_DIR)):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(COMPACT_RESOURCE_DIR, fname), "r", encoding="utf-8") as f:
            data = json.load(f)
        for aname, adef in data.get("attribute_definitions", {}).items():
            by_name.setdefault(aname, []).append((fname, adef))
    return by_name


def _is_documented_valid_values_completion(defs):
    """The one sanctioned case: an empty-valid_values def alongside earlier
    non-empty-valid_values def(s) for the same name -- compact_loader.py
    explicitly keeps the first (non-empty) one and skips the rest in this case."""
    have_valid_values = [d.get("valid_values") for _, d in defs]
    return any(have_valid_values) and not all(have_valid_values)


# Attribute names already known, as of this test's introduction (2026-08-17),
# to render differently across two or more compact_commands/*.json files --
# longstanding, accepted duplication of common family-agnostic names (each
# family wrote its own wording), not a regression. Confirmed by inspection
# that none of these came from the b17f71e incident (that incident's actual
# colliding names -- "Relationship Type"/"Guard"/"Label"/"Description" -- were
# fixed by renaming, and are correctly NOT in this baseline). Do not add a
# name here to silence a new collision without checking it isn't the same
# hazard: only add it if the duplication is a deliberate, reviewed choice.
_KNOWN_EXISTING_COLLISIONS = {
    "Effective Time", "Element Id", "Identifier", "Actor Name", "Organization",
    "Name Patterns", "Planned Completion Date", "Planned Start Date",
}


def test_no_new_cross_family_attribute_name_collisions():
    by_name = _load_all_attribute_definitions()

    collisions = {}
    for aname, defs in by_name.items():
        if len(defs) < 2:
            continue
        distinct = []
        for fname, adef in defs:
            rendered = _rendered_view(adef)
            if rendered not in distinct:
                distinct.append(rendered)
        if len(distinct) < 2:
            continue  # renders identically everywhere -- fine, however internal
            # bookkeeping fields differ
        if _is_documented_valid_values_completion(defs):
            continue  # sanctioned exception
        collisions[aname] = [fname for fname, _ in defs]

    new_collisions = {
        aname: files for aname, files in collisions.items()
        if aname not in _KNOWN_EXISTING_COLLISIONS
    }

    assert not new_collisions, (
        "New attribute name(s) defined differently across compact command "
        "files (silently pooled by name in compact_loader.py -- last file "
        "loaded wins, corrupting other families' template output). If this "
        "is intentional, either give the new attribute a distinct name, or "
        "add it to _KNOWN_EXISTING_COLLISIONS after confirming the "
        f"duplication is a deliberate, reviewed choice: {new_collisions}"
    )
