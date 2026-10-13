# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
ISSUE-141: ActionParameter.function was a required string, so an analytic-only
spec had to pass function="". It is now optional when analytic_function is set.
"""
import pytest
from pydantic import ValidationError

from pyegeria.view._output_format_models import ActionParameter


def test_analytic_only_action_needs_no_function():
    action = ActionParameter(analytic_function="pyegeria.view.overview_metrics.growth_series")
    assert action.function is None


def test_find_only_action_unchanged():
    assert ActionParameter(function="EgeriaTech.find_projects").analytic_function is None


def test_empty_string_function_still_accepted():
    assert ActionParameter(function="").function == ""


def test_action_with_neither_function_is_rejected():
    with pytest.raises(ValidationError):
        ActionParameter()


def test_analytic_demo_specs_build_without_function():
    from pyegeria.view.analytic_demo_specs import get_analytic_demo_specs

    specs = get_analytic_demo_specs()
    assert specs
    assert all(s.action.function is None and s.action.analytic_function for s in specs.values())
