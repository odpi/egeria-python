"""What two Overview metrics count, as their specs and registry entries say (6.2.31).

governed_coverage counts elements of any type the caller can see -- not a share of Assets (the
Portal's Governed tile is an Asset share across the repository, so the two differ by definition).
"""
from __future__ import annotations

import pytest

from pyegeria.view.analytic_registry import get_analytic_registry
from pyegeria.view.base_report_formats import get_report_registry

pytestmark = pytest.mark.unit


def _spec_description(label: str) -> str:
    spec = get_report_registry()[label]
    return spec.description if hasattr(spec, "description") else spec["description"]


def test_governance_coverage_spec_says_any_type_not_a_share_of_assets():
    text = _spec_description("Analytic Demo - Governance Coverage")
    assert "ANY type that you can see" in text
    assert "not a share of Assets" in text
    assert "Governed tile" in text  # says why the Overview tile differs


def test_governed_coverage_registry_entry_is_not_a_share_of_assets():
    text = get_analytic_registry()["governed_coverage"].description
    assert "Share of assets" not in text
    assert "any type" in text and "not a share of Assets" in text


def test_semantic_grounding_spec_names_distinct_assets_and_keeps_links_apart():
    text = _spec_description("Analytic Demo - Semantic Grounding")
    assert "DISTINCT Assets" in text and "groundedAssetPct" in text
    assert "links, not Assets" in text
    returns = get_analytic_registry()["semantic_grounding"].returns
    for field in ("groundedAssets", "groundedAssetTotal", "groundedAssetPct", "groundingLinks", "groundingPct"):
        assert field in returns
