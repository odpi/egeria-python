# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
A repository relationship count needs MetadataExpert's native `count_relationships_between_elements`.
A ClassificationExplorer has only `get_relationships`, and the Portal's supply builds exactly the
class a routine declares. So a routine that counts repository relationships through its `ce` slot
must declare a client that has the native method (EgeriaTech), or on the Portal every count is None:
"no native relationship count is available" (O-cap-1 read-back P1-1, 2026-11-08).

These tests run the routines through a RoleSupply that, like the Portal's, hands out a client shaped
like the class it is asked for, and check the declared class is the one used.
"""
import pytest

import pyegeria.view.base_report_formats as brf
import pyegeria.view.overview_metrics as om
from pyegeria.view import format_set_executor as fse
from pyegeria.view._output_format_models import ActionParameter, Format, FormatSet
from pyegeria.view.analytic_demo_specs import get_analytic_demo_specs
from pyegeria.view.analytic_registry import get_analytic_registry
from pyegeria.view.role_supply import Subject, Viewer

NO_NATIVE = "no native relationship count is available"


class _CE:
    """ClassificationExplorer-shaped: get_relationships only (checked live: no native count)."""

    def __init__(self, calls):
        self.calls = calls

    def get_relationships(self, relationship_type=None, **kw):
        self.calls.append(("ClassificationExplorer.get_relationships", relationship_type))
        return [{"relationshipHeader": {"guid": "r1"}}]


class _Tech(_CE):
    """EgeriaTech/MetadataExpert-shaped: the native counts as well as get_relationships."""

    def count_relationships_between_elements(self, body, **kw):
        self.calls.append(("count_relationships_between_elements", body["relationshipTypeName"], kw))
        return 12

    def count_metadata_elements(self, body, **kw):
        self.calls.append(("count_metadata_elements", body.get("metadataElementTypeName"), kw))
        return 100

    def find_metadata_elements(self, body, *a, **kw):
        return []


class _PortalShapedSupply:
    """Hands out a distinct client per declared class, shaped like that class, as the Portal does."""

    def __init__(self):
        self.asked, self.calls = [], []

    def client(self, cls):
        self.asked.append(cls.__name__)
        return _CE(self.calls) if cls.__name__ == "ClassificationExplorer" else _Tech(self.calls)

    def viewer(self):
        return Viewer(user_id="u", is_admin=False, display_name="U")

    def reader(self, source):
        return None

    def subject(self):
        return Subject(guid="g", type_name="Asset")

    def refusal_words(self, kind):
        return f"cannot supply {kind}"


@pytest.fixture(autouse=True)
def _clean():
    om._count_caps.clear()
    om._native_server_ok.clear()
    yield
    om._count_caps.clear()
    om._native_server_ok.clear()
    brf.clear_runtime_report_specs()


def _run(label, supply, **params):
    return fse.exec_report_spec(label, output_format="DICT", params=params, view_server="vs",
                                view_url="https://x", user="u", user_pass="p", supply=supply)


def test_feedback_summary_on_a_portal_shaped_supply_counts_the_repository():
    supply = _PortalShapedSupply()
    out = _run("Analytic Demo - Feedback Summary", supply)
    assert supply.asked == ["EgeriaTech"]   # the declared class is the one used
    assert out["kind"] == "json" and "unmeasured" not in out
    assert out["data"]["total"] == 5 * 12
    rel = [c for c in supply.calls if c[0] == "count_relationships_between_elements"]
    assert len(rel) == 5 and all(c[2] == {"push_down": True} for c in rel)


def test_count_relationships_on_a_portal_shaped_supply_counts_the_repository():
    brf.register_report_specs({"P1-1 Count Relationships": FormatSet(
        heading="P1-1", description="probe", target_type="Referenceable",
        action=ActionParameter(analytic_function="count_relationships"),
        formats=[Format(types=["DICT"], attributes=[])])}, source="test")
    supply = _PortalShapedSupply()
    out = _run("P1-1 Count Relationships", supply, relationship_type="SemanticAssignment")
    assert supply.asked == ["EgeriaTech"]
    assert out == {"kind": "json", "data": 12}


def test_a_classification_explorer_alone_cannot_count_the_repository():
    # Why the declaration matters: handed a ClassificationExplorer, the count is not measured.
    with om.recording_unmeasured() as notes:
        assert om.feedback_summary(_CE([]))["total"] is None
    assert notes and all(n["reason"].startswith(NO_NATIVE) for n in notes)


@pytest.mark.parametrize("name", ["feedback_summary", "count_relationships"])
def test_routines_counting_repository_relationships_through_ce_do_not_declare_a_classification_explorer(name):
    assert get_analytic_registry()[name].inputs == ["egeria_client:EgeriaTech"]


def test_a_metric_trend_of_feedback_gives_its_egeria_tech_to_the_ce_slot():
    # metric_trend declares [EgeriaTech, ClassificationExplorer] (an input may be declared once only);
    # a target that declares EgeriaTech for its ce slot gets metric_trend's EgeriaTech there.
    calls = []
    series = om.metric_trend(_Tech(calls), _CE(calls), "feedback_summary", window="7d", points=2)
    assert [p["total"] for p in series] == [60, 60]
    assert not any(c[0] == "ClassificationExplorer.get_relationships" for c in calls)


def test_sweep_no_demo_spec_lacks_a_native_relationship_count_on_a_portal_shaped_supply():
    """Every demo spec, run through a supply that builds exactly the declared classes: none may come
    back 'not measured' because its declared client lacks the native relationship count."""
    lacking = []
    for label in get_analytic_demo_specs():
        supply = _PortalShapedSupply()
        try:
            out = _run(label, supply)
        except Exception:  # noqa: BLE001 -- a spec that needs params it lacks is not this check's subject
            continue
        reasons = [n["reason"] for n in (out.get("unmeasured") or [])] if isinstance(out, dict) else []
        if any(r.startswith(NO_NATIVE) for r in reasons):
            lacking.append(label)
    assert lacking == []
