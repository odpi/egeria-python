# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""RS-W2-1a: pyegeria's declaration model mirrors trellis-analytics' (decision D2: the library
authors the vocabulary, pyegeria mirrors it). Every built-in declaration must load as a library
`Declaration`, its `out` fields as a library `Shape`, and every row shape it names as a library
shape. This is the only coupling: pyegeria never imports the library at run time, and this test is
skipped when the library is not installed.

Run it against a release with, for example:
    uv run -p 3.13 --with egeria-trellis-analytics==0.3.1 pytest tests/micro-tests/test_declarations_match_library.py
"""
import warnings

import pytest

library = pytest.importorskip("trellis_analytics.declaration")

from pyegeria.view.analytic_registry import _BUILTINS, ROW_SHAPES  # noqa: E402

#: Keys pyegeria declares that a library release may not know yet, by where they sit. Each is
#: dropped before validation only when the installed library's model has no such field, so a newer
#: library that adds them checks them too.
PYEGERIA_AHEAD = {"measure": {"population"}, "declaration": {"out"}}


def _known(model, data: dict, where: str) -> dict:
    ahead = {k for k in PYEGERIA_AHEAD[where] if k not in model.model_fields}
    return {k: v for k, v in data.items() if k not in ahead}


def _for_library(decl) -> dict:
    data = decl.model_dump(exclude_defaults=True)
    data["absence"] = decl.absence.model_dump()
    data["measures"] = [_known(library.MeasureDeclaration, m, "measure") for m in data.get("measures", [])]
    return _known(library.Declaration, data, "declaration")


def _fields(fields) -> list:
    return [f.model_dump(exclude_defaults=True) for f in fields]


#: pyegeria's own routines; entry points from the library declare in the library's own models.
DECLARED = sorted((name, spec.declaration) for name, spec in _BUILTINS.items()
                  if spec.declaration is not None)


@pytest.fixture(scope="module", autouse=True)
def _row_shapes_registered():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        for name, fields in ROW_SHAPES.items():
            library.register_shape(name, {"fields": _fields(fields)})


@pytest.mark.parametrize("name, decl", DECLARED, ids=[n for n, _ in DECLARED])
def test_declaration_loads_in_the_library(name, decl):
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)  # no legacy word reaches the library
        library.Declaration.model_validate(_for_library(decl))


@pytest.mark.parametrize("name, decl", DECLARED, ids=[n for n, _ in DECLARED])
def test_out_loads_as_a_library_shape(name, decl):
    shape = library.Shape.model_validate({"fields": _fields(decl.out)})
    for f in shape.declared():
        if f.kind == "dataset":
            assert f.shape in library.SHAPES, f"{name}.{f.name} names shape {f.shape}, not registered"


@pytest.mark.parametrize("shape", sorted(ROW_SHAPES))
def test_row_shapes_load_in_the_library(shape):
    library.Shape.model_validate({"fields": _fields(ROW_SHAPES[shape])})
