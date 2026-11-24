# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""PY-48 (Architect, FIX FIRST): a 6.4-gated command on a pre-6.4 platform is a FAILURE, never a success.

The gate refused with status "warning" (md_processing/v2/egeria_6_4.py), and the runner counted every status but
failure/error/unknown as succeeded: the Architect proved success True, commands_succeeded 1, nothing written. The
refusal now comes back as a failure whose words name the platform version, in the dispatcher result and in the runner.

No live server: the FakeEgeria harness answers /api/about as 6.3 and records every call.
"""
import importlib.util
import pathlib

import pytest

from pyegeria.authoring.runner import async_run_markdown

_spec = importlib.util.spec_from_file_location("e64_dre_harness",
                                               pathlib.Path(__file__).with_name("e64_dre_harness.py"))
h = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h)

DECISION = "d0000000-0000-4000-8000-000000000001"
OUTCOME = "f0000000-0000-4000-8000-000000000001"
DOC = f"## Link Decision Outcome\n### Decision\n{DECISION}\n### Outcome\n{OUTCOME}\n"

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
@pytest.mark.parametrize("directive", ["process", "validate"])
async def test_the_gate_refusal_is_a_failure_that_names_the_platform_version(monkeypatch, directive):
    fake = h.FakeEgeria(monkeypatch, about=h.ABOUT_6_3)
    [result] = await h.run_doc(fake, DOC, directive=directive)
    assert result["status"] == "failure"
    assert "runs Egeria 6.3" in result["message"] and "Nothing was sent" in result["message"]
    assert result["errors"] == [result["message"]]
    assert result["needs_egeria_6_4"] is True
    assert fake.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("directive", ["process", "validate"])
async def test_the_runner_does_not_count_the_gate_refusal_as_succeeded(monkeypatch, directive):
    fake = h.FakeEgeria(monkeypatch, about=h.ABOUT_6_3)
    out = await async_run_markdown(fake, DOC, directive)
    assert out["success"] is False
    assert out["commands_succeeded"] == 0 and out["commands_failed"] == 1
    key = "validation_errors" if directive == "validate" else "execution_errors"
    assert "runs Egeria 6.3" in out[key][0]["message"]
    assert fake.calls == []
