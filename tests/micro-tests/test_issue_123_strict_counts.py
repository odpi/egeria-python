# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
ISSUE-123: count_elements turns a failed query into 0, so an outage looks like
an empty catalog. strict=True returns None whenever the count is not known;
the default keeps the old behaviour for existing callers.
"""
from unittest.mock import MagicMock

import pytest

from pyegeria.view import analytic_registry
from pyegeria.view import overview_metrics as om


def _mgr(native=None, find_result=None, find_error=None):
    attrs = ["platform_url", "view_server", "find_metadata_elements"]
    if native is not None:
        attrs.append("count_metadata_elements")
    m = MagicMock(spec=attrs)
    m.platform_url, m.view_server = "https://localhost:9443", "test-server"
    if native is not None:
        m.count_metadata_elements = native
    if find_error is not None:
        m.find_metadata_elements.side_effect = find_error
    else:
        m.find_metadata_elements.return_value = find_result
    return m


@pytest.fixture(autouse=True)
def _reset_seam_caches():
    om._count_caps.clear()
    om._native_server_ok.clear()
    yield
    om._count_caps.clear()
    om._native_server_ok.clear()


def test_default_still_returns_zero_on_failure():
    assert om.count_elements(_mgr(find_error=RuntimeError("401")), "Asset") == 0


def test_strict_returns_none_when_the_query_fails():
    assert om.count_elements(_mgr(find_error=RuntimeError("401")), "Asset", strict=True) is None


def test_strict_returns_none_when_native_and_fallback_both_fail():
    mgr = _mgr(native=MagicMock(side_effect=RuntimeError("timeout")), find_error=RuntimeError("timeout"))
    assert om.count_elements(mgr, "Asset", strict=True) is None


def test_strict_real_zero_is_zero():
    # pyegeria answers a miss with its sentinel string, not an empty list.
    assert om.count_elements(_mgr(find_result="No elements found"), "Asset", strict=True) == 0
    assert om.count_elements(_mgr(find_result=[]), "Asset", strict=True) == 0


def test_strict_returns_none_for_a_capped_fallback():
    full_page = [{"i": i} for i in range(om.DEFAULT_CAP)]
    assert om.count_elements(_mgr(find_result=full_page), "Asset") == om.DEFAULT_CAP
    assert om.count_elements(_mgr(find_result=full_page), "Asset", strict=True) is None


def test_strict_returns_none_for_an_unexpected_result():
    assert om.count_elements(_mgr(find_result={"weird": True}), "Asset", strict=True) is None


def test_strict_native_count_is_trusted_even_above_the_cap():
    mgr = _mgr(native=MagicMock(return_value={"count": om.DEFAULT_CAP + 5}))
    assert om.count_elements(mgr, "Asset", strict=True) == om.DEFAULT_CAP + 5


def test_strict_by_property():
    mgr = _mgr(find_error=RuntimeError("500"))
    assert om.count_elements_by_property(mgr, "DigitalProduct", "deploymentStatus", "ACTIVE") == 0
    assert om.count_elements_by_property(mgr, "DigitalProduct", "deploymentStatus", "ACTIVE",
                                         strict=True) is None


def test_strict_propagates_through_the_composite_counts():
    mgr = _mgr(find_error=RuntimeError("down"))
    assert om.counts_by_type(mgr, [("Stores", "DataStore")], strict=True)[0]["count"] is None
    assert set(om.people_counts(mgr, strict=True).values()) == {None}
    assert set(om.usage_context_counts(mgr, strict=True).values()) == {None}
    assert set(om.people_counts(mgr).values()) == {0}


@pytest.mark.parametrize("name", ["count_elements", "count_elements_by_property", "counts_by_type",
                                  "people_counts", "usage_context_counts"])
def test_strict_is_declared_for_report_specs(name):
    spec = analytic_registry.get_analytic_registry()[name]
    assert any(p.name == "strict" and p.type == "bool" for p in spec.params)
