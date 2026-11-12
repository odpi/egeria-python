# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""A Report's stored params reach its spec in the spec's own names (6.2.35, the Architect's LD-2 read-back).

A Report element keeps its params in additionalProperties, camelCase (searchString, pageSize, collectionQname,
collectionGuid ...), all strings, as Egeria stores a map of strings; its analytic params are a JSON string under
analyticParams. exec_report_spec keeps only the names the spec declares, which are snake_case, so the stored ones
were all dropped ("'collectionQname' ignored -- it takes: collection_qname") and a collection-scoped tile failed
with "Give collection_guid, collection_qname or collection_name". With snake_case keys the same specs work.
"""
import json
from types import SimpleNamespace

import pytest

import pyegeria.view.format_set_executor as fse
from pyegeria.view import dashboard_resolver as dr

pytestmark = pytest.mark.unit


def _report_element(**additional):
    return {"elementHeader": {"guid": "rep-1", "type": {"typeName": "Report"}},
            "properties": {"typeName": "Report", "qualifiedName": "DeployedReport::Assets with No Lineage",
                           "displayName": "Assets with No Lineage", "additionalProperties": additional}}


def _run(element, *, analytic: bool, monkeypatch):
    sent = {}
    monkeypatch.setattr(fse, "exec_report_spec", lambda name, **kw: sent.update(name=name, **kw) or {"kind": "x"})
    report = dr.report_from_element(element)
    action = SimpleNamespace(analytic_function="trellis_curation_coverage" if analytic else None)
    placement = dr.ResolvedPlacement(position=1, ref="Assets with No Lineage", kind="report", title="t",
                                     report=report, spec=report.report_spec, format_set=SimpleNamespace(action=action))
    dr._run_report(SimpleNamespace(user_id="erinoverview"), placement)
    return sent["params"], report


def test_stored_camel_case_params_reach_the_spec_in_snake_case(monkeypatch):
    el = _report_element(reportSpec="Assets-No-Lineage", outputFormat="DICT", collectionQname="Collection::Catalog Health",
                         collectionGuid="c0ffee00-0000-0000-0000-000000000001", searchString="*", pageSize="50")
    params, report = _run(el, analytic=False, monkeypatch=monkeypatch)
    assert params == {"collection_qname": "Collection::Catalog Health",
                      "collection_guid": "c0ffee00-0000-0000-0000-000000000001",
                      "search_string": "*", "page_size": "50"}
    assert report.params["collectionQname"] == "Collection::Catalog Health"   # the stored record is unchanged


def test_analytic_params_are_mapped_too(monkeypatch):
    el = _report_element(reportSpec="Tasks", outputFormat="DICT",
                         analyticParams=json.dumps({"collectionQname": "Collection::Next Steps", "top": 5}))
    params, _ = _run(el, analytic=True, monkeypatch=monkeypatch)
    assert params == {"collection_qname": "Collection::Next Steps", "top": 5}


def test_snake_case_keys_are_left_alone_and_win_over_a_converted_one(monkeypatch):
    el = _report_element(reportSpec="Tasks", outputFormat="DICT", collection_qname="Collection::Explicit",
                         collectionQname="Collection::Converted", metric_path="trellis_x")
    params, _ = _run(el, analytic=False, monkeypatch=monkeypatch)
    assert params == {"collection_qname": "Collection::Explicit", "metric_path": "trellis_x"}


@pytest.mark.parametrize(("key", "snake"), [("collectionQname", "collection_qname"),
                                            ("collectionGUID", "collection_guid"), ("pageSize", "page_size"),
                                            ("asOfTime", "as_of_time"), ("top", "top"), ("search_string", "search_string")])
def test_the_name_mapping(key, snake):
    assert dr._snake(key) == snake
