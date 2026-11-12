# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""6.2.39: a bulleted list attribute keeps one item per bullet; a comma inside a bullet stays in it.

Dr.Egeria used to split every list value on commas, semicolons and newlines, so the CDO workbook's
"Recovery Objective Coverage and Achievement" metric (4 bullets, two with commas) was stored in Egeria
with 6 implications (see the governance_metrics capture). The commands below are copied verbatim from
egeria-workspaces coco-workbooks/4. keeping-safe/it-governance-program.md."""
import asyncio
import gzip
import json
from pathlib import Path

import pytest

from md_processing.md_processing_utils.common_md_proc_utils import split_list_value
from md_processing.md_processing_utils.common_md_utils import split_tb_string
from md_processing.md_processing_utils.md_processing_constants import load_commands
from md_processing.v2.parsing import parse_dr_egeria_content

pytestmark = pytest.mark.unit

DATA = Path(__file__).parent / "data"
EXCERPT = (DATA / "dr_egeria" / "it_governance_program_excerpt.md").read_text()

METRIC_IMPLICATIONS = [
    "Coverage and achievement are distinct measures and both are required",
    "Results go to the Service Owner and the depending domain, not only to IT",
    "Services supporting regulatory deadlines are reported separately",
    "Persistent shortfall is evidence for renegotiating the objective, not for repeated failure reporting",
]
IMPERATIVE_FIRST = "Service characteristics must be agreed with the depending domain, not set by IT alone"


def _parsed():
    load_commands()
    return asyncio.run(parse_dr_egeria_content(EXCERPT))


def test_the_workbook_metric_has_four_implications():
    metric = next(c for c in _parsed() if c["object_type"] == "Governance Metric")
    assert metric["attributes"]["Implications"]["value"] == METRIC_IMPLICATIONS


def test_the_workbook_imperative_keeps_its_comma():
    imperative = next(c for c in _parsed() if c["object_type"] == "Business Imperative")
    implications = imperative["attributes"]["Implications"]["value"]
    assert implications[0] == IMPERATIVE_FIRST and len(implications) == 4


def test_egeria_holds_the_split_value_today():
    """The bug as captured read-only on laz (2026-11-11): the same metric stored with 6 implications."""
    capture = json.loads(gzip.open(DATA / "report_specs" / "governance_metrics.json.gz").read())
    stored = next(e["properties"]["implications"] for c in capture["calls"]
                  for e in (c["answer"].get("elements") or [])
                  if "Coverage and achievement are distinct measures" in " ".join(e["properties"].get("implications") or []))
    assert len(stored) == 6 and "not only to IT" in stored


@pytest.mark.parametrize("text, expected", [
    ("a, b", ["a", "b"]),                                         # a single line still splits
    ("a; b", ["a", "b"]),
    ("- one, with a comma", ["one, with a comma"]),               # one bullet stays one item
    ("- a, b\n- c", ["a, b", "c"]),
    ("* a, b\n+ c", ["a, b", "c"]),
    ("First line, with comma\nSecond", ["First line, with comma", "Second"]),  # a line list: a line is an item
    ("first line, with comma\nsecond", ["first line, with comma", "second"]),  # short lines: a line list
    ("\n- a\n\n- b\n", ["a", "b"]),
    ("", []),
    (None, None),
    (["x", " y "], ["x", "y"]),
    ("-5, 6", ["-5", "6"]),                                       # "-5" is not a bullet
    ("- Item 1; - Item 2, Item 3", ["Item 1", "Item 2", "Item 3"]),  # an inline bulleted list on one line
])
def test_split_list_value(text, expected):
    assert split_list_value(text) == expected


def test_spec_metadata_splitting_is_unchanged():
    assert split_tb_string("Display Name; Name, Title") == ["Display Name", "Name", "Title"]


# ── n1: mixed blocks and wrapped prose (real blocks from egeria-workspaces, copied verbatim) ──
# glossary_usage.txt        <- coco-workbooks/1. coco-data-hub/data-field-naming/glossary.md:32-34 (Usage)
# samples_examples.txt      <- exchange-quickstart/loading-bay/dr-egeria-samples/dr_egeria_intro_part1.md (Examples)
# samples_mixed_examples.txt <- exchange-quickstart/loading-bay/dr-egeria-samples/dr_egeria_intro_part3.md:83-89

def _block(name):
    return (DATA / "dr_egeria" / name).read_text()


def test_wrapped_prose_is_one_item():
    items = split_list_value(_block("glossary_usage.txt"))
    assert len(items) == 1
    assert items[0].startswith("This glossary is used by data architects") and "by combining a prime word" in items[0]
    assert items[0].endswith("Common Class Words folder).") and "\n" not in items[0]


def test_a_plain_line_list_is_one_item_per_line():
    assert split_list_value(_block("samples_examples.txt")) == [
        "Create Glossary or", "Update Glossary or", "Create Term or", "Update Term"]


def test_a_mixed_block_keeps_intro_bullets_and_closing_line_apart():
    items = split_list_value(_block("samples_mixed_examples.txt"))
    assert items[0] == "Default values for key environment variables in the **Egeria Workspaces** environment:"
    assert items[1:5] == ["EGERIA_ROOT_PATH=/home/jovyan", "EGERIA_INBOX_PATH=loading-bay/dr-egeria-inbox",
                          "EGERIA_OUTBOX_PATH=distribution-hub/dr-egeria-outbox", "EGERIA_LOCAL_QUALIFIER=EGERIA"]
    assert items[5].startswith("So place input files") and len(items) == 6   # a closing sentence stands alone


@pytest.mark.parametrize("text, expected", [
    ("- a bullet that wraps onto\n  an indented next line\n- second", ["a bullet that wraps onto an indented next line", "second"]),
    ("- a bullet that wraps and\ncontinues in lower case\n- second", ["a bullet that wraps and continues in lower case", "second"]),
    ("- a finished bullet.\nlower case after a full stop\n- b", ["a finished bullet.", "lower case after a full stop", "b"]),
    ("Intro line\n- a, b\n- c", ["Intro line", "a, b", "c"]),
    ("Short one\nShort two", ["Short one", "Short two"]),
])
def test_continuation_rules(text, expected):
    assert split_list_value(text) == expected


def test_a_short_lower_case_keyword_list_stays_a_list():
    """n2: lower case alone never makes a wrap in a block without bullets."""
    assert split_list_value("crm\nerp\ndata quality") == ["crm", "erp", "data quality"]


def test_a_short_lower_case_line_after_a_bullet_continues_it():
    """Pinned: inside a bulleted block, a non-bullet line in lower case after a bullet that did not end its
    sentence is that bullet's wrapped continuation, however short; after a finished bullet it stands alone."""
    from md_processing.md_processing_utils.common_md_utils import _continues
    assert _continues("- Service characteristics must be agreed", "erp") is True
    assert split_list_value("- crm and\nerp\n- data quality") == ["crm and erp", "data quality"]
    assert _continues("- Service characteristics are agreed.", "erp") is False
    assert _continues("- crm", "Data Quality") is False
