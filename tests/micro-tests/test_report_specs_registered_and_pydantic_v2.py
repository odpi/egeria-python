# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
6.2.19 release checks for the report-spec registry.

- Every function a registered report spec names (an action's
  `analytic_function`, or a `metric_path` anywhere in its params) is a
  registered analytic-function name. Dotted paths are refused from 6.2.19
  (ISSUE-173), so a spec that still used one would fail at run time, not at
  load. This is the Trellis Coordinator's specs_check.py as a test.
- The report-spec models load and serialise without Pydantic V1 deprecation
  warnings (they would break on Pydantic V3), and `Format.dict()` still emits
  the legacy `columns` key that callers read.
"""
import pathlib
import re
import warnings

import pytest
from pydantic.warnings import PydanticDeprecatedSince20

from pyegeria.view.analytic_registry import get_analytic_registry
from pyegeria.view.base_report_formats import get_report_registry

pytestmark = pytest.mark.unit

VIEW_DIR = pathlib.Path(__file__).resolve().parents[2] / "pyegeria" / "view"
MODEL_FILES = ["_output_format_models.py", "_output_dashboard_sheet_models.py", "base_report_formats.py"]


def _function_refs(obj, label, refs):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in ("analytic_function", "metric_path") and isinstance(value, str) and value:
                refs.append((label, key, value))
            else:
                _function_refs(value, label, refs)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            _function_refs(item, label, refs)


def test_every_report_spec_names_registered_functions_only():
    analytics = get_analytic_registry()
    registry = get_report_registry()
    assert len(registry) > 300, "the report-spec registry lost specs"
    refs = []
    for label, fs in registry.items():
        _function_refs(fs.model_dump(), label, refs)
    assert refs, "expected shipped report specs that name analytic functions"
    bad = [r for r in refs if "." in r[2] or r[2] not in analytics]
    assert bad == []


def test_report_spec_models_raise_no_pydantic_v1_deprecation():
    with warnings.catch_warnings():
        warnings.simplefilter("error", PydanticDeprecatedSince20)
        registry = get_report_registry()
        for fs in registry.values():
            fs.dict()
            fs.model_dump()


def test_format_dict_keeps_the_legacy_columns_key():
    fs = next(fs for fs in get_report_registry().values() if fs.formats)
    fmt = fs.dict()["formats"][0]
    assert fmt["columns"] == fmt["attributes"]


@pytest.mark.parametrize("name", MODEL_FILES)
def test_no_pydantic_v1_validators_in_report_spec_models(name):
    src = (VIEW_DIR / name).read_text()
    assert not re.search(r"@(root_)?validator\b", src)
    assert "super().dict(" not in src
