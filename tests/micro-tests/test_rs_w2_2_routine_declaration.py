# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""RS-W2-2 PR-A: a registry entry is a routine declaration plus bindings, and
`AnalyticFunctionSpec` is its compatibility view (`function` is the one python binding).
No behaviour change: every entry converts mechanically and round-trips, and a report spec
still names routines by registered name only (ISSUE-173)."""
import pytest

from pyegeria.view import format_set_executor as fse
from pyegeria.view.analytic_registry import (
    _BUILTINS,
    ROW_SHAPES,
    Admission,
    AnalyticDeclaration,
    AnalyticFunctionSpec,
    AnalyticParam,
    Binding,
    FieldDeclaration,
    ParamDeclaration,
    RoutineDeclaration,
    TileSafety,
    clear_runtime_analytic_functions,
    get_analytic_registry,
    get_routine_registry,
    register_analytic_functions,
    routine_declaration_errors,
)

FN = "pyegeria.view.overview_metrics.count_elements"


def _view_of(spec: AnalyticFunctionSpec) -> AnalyticFunctionSpec:
    return AnalyticFunctionSpec.from_routine(spec.routine(), returns=spec.returns, action=spec.action,
                                             envelope=spec.envelope)


# ── Every entry converts, and the view round-trips ──

def test_every_registry_entry_reads_as_a_routine_declaration():
    assert routine_declaration_errors() == {}
    assert set(get_routine_registry()) == set(get_analytic_registry())


@pytest.mark.parametrize("name", sorted(_BUILTINS))
def test_builtin_round_trips_through_the_routine_declaration(name):
    spec = _BUILTINS[name]
    routine = spec.routine()
    assert routine.python_target() == spec.function
    assert [b.kind for b in routine.bindings] == ["python"]
    assert routine.declaration == spec.declaration
    assert _view_of(spec).model_dump() == spec.model_dump()


def _full_routine() -> RoutineDeclaration:
    return RoutineDeclaration(
        name="type_census", kind="processor", description="Counts rows by type.", version="1.0",
        source="egeria", family="Census", tags=["census"], generic=True,
        inputs=["egeria_client:MetadataExpert", "viewer"],
        params=[ParamDeclaration(name="type_name", required=True, description="what to count"),
                ParamDeclaration(name="page_size", type="int", default=100, category="performance"),
                ParamDeclaration(name="layout", default="wide", category="shape")],
        constants={"metadata_element_type": "Asset"},
        **{"in": "TypeCount"},
        declaration=_BUILTINS["count_elements"].declaration,
        pushdown=["count by the repository"],
        tile_safe=TileSafety(safe=True, cap={"page_size": 100}, reason="0.2-0.8 s measured"),
        admission=Admission(resource_types=["database"], test_only=True),
        bindings=[Binding(kind="egeria_query", target="Type census"), Binding(kind="python", target=FN)],
    )


def test_a_full_declaration_round_trips_through_the_view():
    routine = _full_routine()
    view = AnalyticFunctionSpec.from_routine(routine)
    assert view.function == FN
    assert view.resource_types == ["database"] and view.test_only is True
    assert [p.category for p in view.params] == ["content", "performance", "shape"]
    assert view.routine() == routine
    assert view.routine().model_dump(by_alias=True)["in"] == "TypeCount"


def test_the_view_dumps_and_reloads():
    view = AnalyticFunctionSpec.from_routine(_full_routine())
    assert AnalyticFunctionSpec.model_validate(view.model_dump()).routine() == view.routine()
    assert AnalyticFunctionSpec.model_validate(view.model_dump(by_alias=True)).routine() == view.routine()


# ── function <-> the one python binding ──

def test_function_alone_becomes_the_python_binding():
    spec = AnalyticFunctionSpec(name="n", function=FN)
    assert [(b.kind, b.target) for b in spec.bindings] == [("python", FN)]


def test_a_python_binding_alone_fills_function():
    spec = AnalyticFunctionSpec(name="n", bindings=[{"kind": "python", "target": FN}])
    assert spec.function == FN


@pytest.mark.parametrize("data, words", [
    ({"function": FN, "bindings": [{"kind": "python", "target": FN + "_other"}]}, "they are one value"),
    ({"bindings": [{"kind": "python", "target": FN}, {"kind": "python", "target": FN + "2"}]},
     "more than one python binding"),
    ({}, "declares no binding"),
    ({"bindings": [{"kind": "python", "target": "count_elements"}]}, "not a dotted import path"),
    ({"bindings": [{"kind": "sql", "target": "  "}]}, "names no target"),
])
def test_binding_refusals_say_why(data, words):
    with pytest.raises(ValueError, match=words):
        AnalyticFunctionSpec(name="n", **data)


def test_an_entry_with_no_python_binding_is_refused_by_name_when_run():
    register_analytic_functions({"saved_census": AnalyticFunctionSpec(
        name="saved_census", bindings=[Binding(kind="egeria_query", target="Census query")])})
    try:
        assert get_routine_registry()["saved_census"].python_target() == ""
        with pytest.raises(fse.AnalyticFunctionRefused,
                           match=r"'saved_census' has no python binding \(its bindings: egeria_query 'Census "
                                 r"query'\); this pyegeria runs python bindings only"):
            fse.resolve_report_spec_function("saved_census")
    finally:
        clear_runtime_analytic_functions()


# ── Declaration rules, mirrored from trellis-analytics 0.4 ──

@pytest.mark.parametrize("change, words", [
    ({"params": [ParamDeclaration(name="x")], "constants": {"x": 1}}, "as a parameter and a constant"),
    ({"params": [ParamDeclaration(name="x"), ParamDeclaration(name="x")]}, "parameter x more than once"),
    ({"inputs": ["client"]}, "is not a role word"),
    ({"inputs": ["viewer", "viewer"]}, "an input more than once"),
    ({"generic": True, "binding_note": "fixed to Asset"}, "a generic routine fixes nothing"),
    ({"in": "TypeCount"}, "only a processor reads"),
    ({"name": "type census"}, "not an identifier"),
    ({"bindings": [Binding(kind="python", target=FN), Binding(kind="python", target=FN + "2")]},
     "more than one python binding"),
    ({"surprise": 1}, "Extra inputs are not permitted"),
])
def test_routine_refusals_say_why(change, words):
    with pytest.raises(ValueError, match=words):
        RoutineDeclaration(**{"name": "r", **change})


@pytest.mark.parametrize("make, words", [
    (lambda: ParamDeclaration(name="x", required=True, default=1), "required and has a default"),
    (lambda: ParamDeclaration(name="x", category="speed"), "content"),
    (lambda: TileSafety(safe=True, reason=" "), "declares no reason"),
    (lambda: TileSafety(safe=False, cap={"n": 1}, reason="slow"), "a cap says within what it IS safe"),
])
def test_part_refusals_say_why(make, words):
    with pytest.raises(ValueError, match=words):
        make()


def test_a_breaking_entry_is_named_not_raised():
    """An entry that runs today but breaks a declaration rule is listed with the rule's words;
    the registry and the run path are unchanged (PR-A: no behaviour change)."""
    register_analytic_functions({"noted_generic": AnalyticFunctionSpec(
        name="noted_generic", function=FN, generic=True, binding_note="fixed to Asset")})
    try:
        assert "noted_generic" in get_analytic_registry()
        assert "noted_generic" not in get_routine_registry()
        assert "a generic routine fixes nothing" in routine_declaration_errors()["noted_generic"]
        assert callable(fse.resolve_report_spec_function("noted_generic"))
    finally:
        clear_runtime_analytic_functions()


def test_param_category_defaults_to_content():
    assert AnalyticParam(name="x").category == "content"


# ── declaration.out in the library's three forms (RS-W2-1a read-back F2) ──

def test_out_reads_a_field_list_a_shape_name_and_an_inline_shape():
    base = _BUILTINS["count_elements"].declaration.model_dump()
    as_list = AnalyticDeclaration.model_validate(base)
    assert [f.name for f in as_list.out_fields()] == ["value"]
    named = AnalyticDeclaration.model_validate({**base, "out": "TypeCount"})
    assert named.out_fields() == ROW_SHAPES["TypeCount"]
    library_only = AnalyticDeclaration.model_validate({**base, "out": "CoverageResult"})
    assert library_only.out_fields() == []
    inline = AnalyticDeclaration.model_validate(
        {**base, "out": {"fields": [{"name": "n", "label": "N", "type": "int"}, {"include": "TypeCount.count"}]}})
    assert inline.out_fields() == [FieldDeclaration(name="n", label="N", type="int")]


def test_a_routine_reads_its_out_fields_through_its_declaration():
    assert _BUILTINS["counts_by_type"].routine().out_fields() == ROW_SHAPES["TypeCount"]
    assert RoutineDeclaration(name="r").out_fields() == []


# ── The allow-list applies to binding targets only (ISSUE-173) ──

@pytest.mark.parametrize("name", sorted(_BUILTINS))
def test_every_builtin_python_binding_is_allowed(name):
    assert fse.python_binding_allowed(_BUILTINS[name].routine().python_target())


def test_a_report_spec_path_is_refused_even_under_an_allowed_prefix():
    assert fse.python_binding_allowed(FN)
    with pytest.raises(fse.AnalyticFunctionRefused, match="use its registered name 'count_elements'"):
        fse.resolve_report_spec_function(FN)


def test_an_undeclared_out_reads_as_no_fields():
    """The library writes an undeclared `out` as None; pyegeria's built-ins as []."""
    base = _BUILTINS["count_elements"].declaration.model_dump()
    assert AnalyticDeclaration.model_validate({**base, "out": None}).out_fields() == []
