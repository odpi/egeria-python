# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""RS-W2-2 PR-A: pyegeria's RoutineDeclaration mirrors trellis-analytics 0.4's (decision D2: the
library authors the schema, pyegeria mirrors it). Every built-in, read as a routine declaration,
must load as a library `RoutineDeclaration`, and the library's own reading of a pyegeria entry
(`routine_declaration(spec)`) must agree with pyegeria's (`spec.routine()`). Skipped when the
library (0.4 or later) is not installed.

    uv run -p 3.13 --with 'egeria-trellis-analytics>=0.4' pytest tests/micro-tests/test_routine_declarations_match_library.py
"""
import warnings

import pytest

routine_lib = pytest.importorskip("trellis_analytics.routine")
library = pytest.importorskip("trellis_analytics.declaration")

from pyegeria.view.analytic_registry import _BUILTINS, ROW_SHAPES  # noqa: E402

#: Declaration keys pyegeria may carry that an installed library release lacks: dropped only then.
PYEGERIA_AHEAD = {"measure": {"population"}, "declaration": {"out"}}


def _known(model, data: dict, where: str) -> dict:
    ahead = {k for k in PYEGERIA_AHEAD[where] if k not in model.model_fields}
    return {k: v for k, v in data.items() if k not in ahead}


def _for_library(routine) -> dict:
    data = routine.model_dump(by_alias=True, exclude_defaults=True)
    decl = routine.declaration
    if decl is not None:
        d = decl.model_dump(exclude_defaults=True)
        d["absence"] = decl.absence.model_dump()
        d["measures"] = [_known(library.MeasureDeclaration, m, "measure") for m in d.get("measures", [])]
        data["declaration"] = _known(library.Declaration, d, "declaration")
    return data


@pytest.fixture(scope="module", autouse=True)
def _row_shapes_registered():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        for name, fields in ROW_SHAPES.items():
            library.register_shape(name, {"fields": [f.model_dump(exclude_defaults=True) for f in fields]})


@pytest.mark.parametrize("name", sorted(_BUILTINS))
def test_builtin_routine_loads_in_the_library(name):
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)  # no legacy word reaches the library
        routine_lib.RoutineDeclaration.model_validate(_for_library(_BUILTINS[name].routine()))


@pytest.mark.parametrize("name", sorted(_BUILTINS))
def test_the_library_reads_a_pyegeria_entry_as_pyegeria_does(name):
    spec = _BUILTINS[name]
    theirs = routine_lib.routine_declaration(spec).model_dump(by_alias=True, exclude={"declaration"})
    ours = spec.routine().model_dump(by_alias=True, exclude={"declaration"})
    assert theirs == ours


@pytest.mark.parametrize("model", ["RoutineDeclaration", "ParamDeclaration", "Binding", "TileSafety", "Admission"])
def test_field_names_match(model):
    from pyegeria.view import analytic_registry as ours
    assert set(getattr(ours, model).model_fields) == set(getattr(routine_lib, model).model_fields)


@pytest.mark.parametrize("words", ["ROUTINE_KINDS", "BINDING_KINDS", "PARAM_CATEGORIES", "INPUT_ROLES"])
def test_vocabularies_match(words):
    from pyegeria.view import analytic_registry as ours
    assert tuple(getattr(ours, words)) == tuple(getattr(routine_lib, words))
