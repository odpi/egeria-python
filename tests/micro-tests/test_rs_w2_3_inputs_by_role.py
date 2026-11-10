# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""RS-W2-3 PR-A: the executor supplies a routine's DECLARED inputs from the environment's role
supply, in declared order; it never reads parameter names to decide what to pass. A role the
supply cannot provide, or a declaration that does not match its binding (check 5), refuses the
run before any stage, in words. Plain pyegeria's PlainSupply hands back the caller's EgeriaTech
for every class it proxies to, so Wave 2 is byte-identical."""

import pytest

import pyegeria.view.base_report_formats as brf
import pyegeria.view.overview_metrics as om
from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.omvs.classification_explorer import ClassificationExplorer
from pyegeria.omvs.metadata_expert import MetadataExpert
from pyegeria.view import format_set_executor as fse
from pyegeria.view import spec_resolver as sr
from pyegeria.view._output_format_models import ActionParameter, Format, FormatSet
from pyegeria.view.analytic_demo_specs import get_analytic_demo_specs
from pyegeria.view.analytic_registry import (AnalyticFunctionSpec, _BUILTINS as BUILTIN_ANALYTIC_FUNCTIONS,
                                             clear_runtime_analytic_functions, register_analytic_functions)
from pyegeria.view.role_supply import (CallerTokenExpired, NoSuchReader, PlainSupply, RoleRefused, Subject,
                                       Viewer, egeria_tech_classes, supply_inputs)

MOD = "pyegeria.view.overview_metrics"


# ── A fake Egeria client: the only thing faked in the end-to-end tests ──

class _FakeTech:
    """Stands in for EgeriaTech inside format_set_executor; records construction and auth."""
    made = []

    def __init__(self, view_server=None, view_url=None, user_id=None, user_pwd=None, **kw):
        self.view_server, self.platform_url, self.user_id = view_server, view_url, user_id
        self.minted = 0
        self.tokens = []
        self.calls = []
        _FakeTech.made.append(self)

    def set_bearer_token(self, token):
        self.tokens.append(token)

    def create_egeria_bearer_token(self):
        self.minted += 1

    def find_metadata_elements(self, body):
        self.calls.append(("find_metadata_elements", body.get("metadataElementTypeName")))
        return [{"elementHeader": {"guid": "g1", "classifications": []}, "elementProperties": {}}]

    def count_metadata_elements(self, body, **kw):
        self.calls.append(("count_metadata_elements", body.get("metadataElementTypeName")))
        return 7

    def count_relationships_between_elements(self, body, **kw):
        self.calls.append(("count_relationships_between_elements", body.get("relationshipTypeName")))
        return 3

    def get_relationships(self, relationship_type=None, **kw):
        self.calls.append(("get_relationships", relationship_type))
        return [{"relationshipHeader": {"guid": "r1"}, "end1": {"guid": "g1"}, "end2": {"guid": "g2"}}]


@pytest.fixture
def fake_tech(monkeypatch):
    _FakeTech.made = []
    monkeypatch.setattr(fse, "EgeriaTech", _FakeTech)
    om._count_caps.clear()
    om._native_server_ok.clear()
    yield _FakeTech.made
    om._count_caps.clear()
    om._native_server_ok.clear()


@pytest.fixture(autouse=True)
def _clean():
    yield
    clear_runtime_analytic_functions()
    brf.clear_runtime_report_specs()


def _routine(monkeypatch, name, func, inputs):
    """Register `func` as routine `name` (bound under overview_metrics, an allowed module)."""
    monkeypatch.setattr(om, f"_w23_{name}", func, raising=False)
    register_analytic_functions({name: AnalyticFunctionSpec(name=name, function=f"{MOD}._w23_{name}",
                                                            inputs=list(inputs))})


def _spec_for(routine, label="W23-Probe"):
    brf.register_report_specs({label: FormatSet(
        heading=label, description="probe", target_type="Referenceable",
        action=ActionParameter(analytic_function=routine), formats=[Format(types=["DICT"], attributes=[])])},
        source="test")
    return label


def _run(label, **kw):
    return fse.exec_report_spec(label, output_format="DICT", view_server="vs", view_url="https://x",
                                user="u", user_pass="p", **kw)


class _Supply:
    """An environment's supply with a distinct object per client class, a viewer and a subject."""

    def __init__(self, fail_client=None):
        self.asked = []
        self.fail_client = fail_client

    def client(self, cls):
        self.asked.append(cls.__name__)
        if self.fail_client:
            raise self.fail_client
        return f"client<{cls.__name__}>"

    def viewer(self):
        return Viewer(user_id="peterprofile", is_admin=False, display_name="Peter")

    def reader(self, source):
        return f"reader<{source}>"

    def subject(self):
        return Subject(guid="g-subject", type_name="Asset")

    def refusal_words(self, kind):
        return f"the test environment cannot supply {kind}"


# ── The 28 built-in declarations ──

def test_every_builtin_declares_its_client_inputs_and_they_match_its_binding():
    assert len(BUILTIN_ANALYTIC_FUNCTIONS) == 28
    served = {c.__name__ for c in egeria_tech_classes()}
    for name, entry in BUILTIN_ANALYTIC_FUNCTIONS.items():
        assert entry.inputs, f"{name} declares no inputs"
        for role in entry.inputs:
            kind, _, cls = role.partition(":")
            assert kind == "egeria_client" and cls in served, f"{name}: {role}"
        assert sr.declared_inputs(name) == entry.inputs  # check 5 passes for every built-in
        entry.routine()  # a valid RoutineDeclaration (no repeated input)


def test_two_client_slots_are_declared_by_the_class_each_one_calls():
    assert BUILTIN_ANALYTIC_FUNCTIONS["semantic_grounding"].inputs == [
        "egeria_client:MetadataExpert", "egeria_client:ClassificationExplorer"]
    assert BUILTIN_ANALYTIC_FUNCTIONS["certifications_summary"].inputs == ["egeria_client:ClassificationExplorer"]
    assert BUILTIN_ANALYTIC_FUNCTIONS["control_implementation_summary"].inputs == ["egeria_client:SecurityOfficer"]
    # Calls across several classes -> EgeriaTech (asset_composition also reads ValidMetadata; metric_trend
    # forwards its first client to any target routine).
    assert BUILTIN_ANALYTIC_FUNCTIONS["asset_composition"].inputs == ["egeria_client:EgeriaTech"]
    assert BUILTIN_ANALYTIC_FUNCTIONS["metric_trend"].inputs == [
        "egeria_client:EgeriaTech", "egeria_client:ClassificationExplorer"]


# ── PlainSupply ──

def test_plain_supply_hands_back_the_callers_egeria_tech_for_every_class_it_proxies():
    tech = EgeriaTech("vs", "https://localhost:9443", user_id="u", user_pwd="p")
    supply = PlainSupply(tech)
    for cls in egeria_tech_classes():
        assert supply.client(cls) is tech  # never a subclient in Wave 2
    assert tech._instantiated_clients == {}


def test_plain_supply_builds_the_client_once_and_only_when_asked():
    built = []
    supply = PlainSupply(client_factory=lambda: built.append(1) or "THE-CLIENT")
    assert built == []
    assert supply.client(MetadataExpert) == supply.client(ClassificationExplorer) == "THE-CLIENT"
    assert built == [1]


def test_plain_supply_supplies_no_reader_viewer_or_subject():
    supply = PlainSupply("C")
    with pytest.raises(NoSuchReader, match="no reader 'ods': Plain pyegeria supplies no readers"):
        supply.reader("ods")
    with pytest.raises(RoleRefused, match="Plain pyegeria does not know who is viewing"):
        supply.viewer()
    assert supply.subject() is None
    with pytest.raises(RoleRefused, match="no Egeria client was given"):
        PlainSupply().client(MetadataExpert)


def test_inputs_are_supplied_in_declared_order():
    supply = _Supply()
    args = supply_inputs("r", ["egeria_client:ClassificationExplorer", "egeria_client:MetadataExpert",
                               "viewer", "subject", "reader:ods"], supply)
    assert args[:2] == ["client<ClassificationExplorer>", "client<MetadataExpert>"]
    assert args[2].user_id == "peterprofile" and args[3].guid == "g-subject" and args[4] == "reader<ods>"


# ── Refusals, each with its words, before any stage runs ──

def test_refusal_a_missing_role(monkeypatch, fake_tech):
    """The routine declares a role (viewer) plain pyegeria does not supply."""
    called = []
    _routine(monkeypatch, "who_is_looking", lambda mgr, viewer, **kw: called.append(1),
             ["egeria_client:MetadataExpert", "viewer"])
    with pytest.raises(RoleRefused) as info:
        _run(_spec_for("who_is_looking"))
    assert str(info.value) == (
        "Routine 'who_is_looking' cannot run: its declared input 'viewer' is not supplied (Plain pyegeria "
        "does not know who is viewing; run this routine where the viewer is supplied (Resource Explorer or "
        "the Portal).)")
    assert info.value.role == "viewer"
    assert called == []  # no stage ran


def test_refusal_an_undeclared_client_slot_at_load_and_at_run_with_the_same_words(monkeypatch, fake_tech):
    """The routine's binding takes a client argument its declaration does not list (check 5)."""
    called = []
    _routine(monkeypatch, "takes_a_client", lambda mgr, as_of=None: called.append(1), [])
    words = ("routine takes_a_client's binding takes 1 leading client argument(s) and its declaration lists "
             "0 egeria_client input(s)")
    label = _spec_for("takes_a_client")
    resolved = sr.resolve_all(refresh=True)[label]
    assert not resolved.runnable and resolved.checks == [5]
    assert resolved.unrunnable_reason == f"Spec '{label}' cannot run (check 5): {words}."
    with pytest.raises(RoleRefused) as info:
        _run(label)
    assert str(info.value) == f"Routine 'takes_a_client' cannot run: {words}."
    assert called == [] and fake_tech == []  # refused before connecting, before any stage


def test_refusal_a_declared_input_the_supply_lacks(monkeypatch, fake_tech):
    """The environment's supply cannot mint a client for the caller (e.g. an expired token)."""
    called = []
    _routine(monkeypatch, "counts", lambda mgr, ce, **kw: called.append(1),
             ["egeria_client:MetadataExpert", "egeria_client:ClassificationExplorer"])
    expired = CallerTokenExpired("Your Egeria session has expired; sign in again.")
    with pytest.raises(CallerTokenExpired) as info:
        _run(_spec_for("counts"), supply=_Supply(fail_client=expired))
    assert str(info.value) == (
        "Routine 'counts' cannot run: its declared input 'egeria_client:MetadataExpert' is not supplied "
        "(Your Egeria session has expired; sign in again.)")
    assert called == [] and fake_tech == []


def test_refusal_a_client_class_plain_pyegeria_does_not_serve(monkeypatch, fake_tech):
    _routine(monkeypatch, "odd_client", lambda client: 1, ["egeria_client:NotAPyegeriaClient"])
    with pytest.raises(RoleRefused, match="no client class named NotAPyegeriaClient is known to pyegeria"):
        _run(_spec_for("odd_client"))


def test_a_fetch_step_must_be_a_registered_routine(monkeypatch):
    from pyegeria.view.analytic_registry import AnalyticActionSpec
    monkeypatch.setattr(om, "_w23_unregistered_fetch", lambda mgr: [], raising=False)
    with pytest.raises(RoleRefused, match="is not a registered routine, so it declares no inputs"):
        fse.run_analytic_action(AnalyticActionSpec(fetch=f"{MOD}._w23_unregistered_fetch"), "C")


# ── End to end through the real executor, only the Egeria client faked ──

def test_end_to_end_a_two_client_routine_gets_the_callers_one_client_in_both_slots(fake_tech):
    seen = {}
    real = om.semantic_grounding

    def spy(mgr, ce, **kw):
        seen["mgr"], seen["ce"] = mgr, ce
        return real(mgr, ce, **kw)

    om_spy = pytest.MonkeyPatch()
    om_spy.setattr(om, "semantic_grounding", spy)
    try:
        result = _run("Analytic Demo - Semantic Grounding", token="caller-token")
    finally:
        om_spy.undo()
    assert result["kind"] == "json" and set(result["data"]) == {
        "groundedAssets", "groundedAssetTotal", "groundedAssetPct", "groundedAssetNote", "groundingLinksScanned", "groundingLinksNotOnAsset",
        "groundingLinks", "groundingPct"}
    assert len(fake_tech) == 1 and fake_tech[0].tokens == ["caller-token"] and fake_tech[0].minted == 0
    assert seen["mgr"] is seen["ce"] is fake_tech[0]
    # native counts through mgr (R4), and the SemanticAssignment scan for distinct grounded Assets (6.2.31)
    assert {c[0] for c in fake_tech[0].calls} == {"count_metadata_elements", "count_relationships_between_elements",
                                                  "get_relationships"}


def test_end_to_end_an_environment_supply_is_asked_by_declared_class_in_order(fake_tech):
    supply = _Supply()
    seen = {}

    def spy(mgr, ce, **kw):
        seen["args"] = (mgr, ce)
        return {"groundingLinks": 1, "groundingPct": 1}

    mp = pytest.MonkeyPatch()
    mp.setattr(om, "semantic_grounding", spy)
    try:
        result = _run("Analytic Demo - Semantic Grounding", supply=supply)
    finally:
        mp.undo()
    assert supply.asked == ["MetadataExpert", "ClassificationExplorer"]
    assert seen["args"] == ("client<MetadataExpert>", "client<ClassificationExplorer>")
    assert fake_tech == []  # the environment's supply, not a client built from user/password
    result.pop("spec_source", None)  # RS-EGERIA-TIER: provenance beside kind, not in data
    assert result == {"kind": "json", "data": {"groundingLinks": 1, "groundingPct": 1}}


def test_the_run_and_the_resolver_read_inputs_through_one_function(monkeypatch, fake_tech):
    """Rule 1: what the resolver shows (check 5) and what the run binds come from declared_inputs."""
    calls = []
    real = sr.declared_inputs
    monkeypatch.setattr(sr, "declared_inputs", lambda *a, **k: calls.append(a[0]) or real(*a, **k))
    _run("Analytic Demo - Element Count by Type")
    sr.resolve(get_analytic_demo_specs()["Analytic Demo - Element Count by Type"])
    assert calls == ["count_elements", "count_elements"]


def test_every_demo_spec_lists_its_declared_inputs_at_load():
    results = sr.resolve_all(refresh=True)
    for label, spec in get_analytic_demo_specs().items():
        result = results[label]
        assert result.runnable, result.unrunnable_reason
        entry = BUILTIN_ANALYTIC_FUNCTIONS[spec.action.analytic_function]
        assert result.role_inputs == entry.inputs


# ── PR-B: the binder is gone; the key is accepted and ignored for one release ──

def test_a_spec_still_carrying_analytic_binders_loads_with_a_deprecation_warning():
    with pytest.warns(DeprecationWarning, match=r"analytic_binders is no longer supported .*binders for: ods"):
        action = ActionParameter(analytic_function="count_elements",
                                 analytic_binders={"ods": "trellis_analytics.readers.ods.OdsReader"})
    assert "analytic_binders" not in action.model_dump()


def test_an_empty_analytic_binders_key_is_dropped_silently():
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        action = ActionParameter.model_validate({"analytic_function": "count_elements", "analytic_binders": {}})
    assert "analytic_binders" not in action.model_dump()


def test_a_spec_with_a_binder_runs_on_declared_inputs_alone(monkeypatch, fake_tech):
    """The ignored binder neither builds nor replaces anything: the routine gets its declared inputs."""
    seen = {}

    def probe(mgr, type_name="x"):
        seen["args"] = (mgr, type_name)
        return {"count": 1}

    _routine(monkeypatch, "binder_probe", probe, ["egeria_client:MetadataExpert"])
    with pytest.warns(DeprecationWarning):
        action = ActionParameter(analytic_function="binder_probe", analytic_binders={"mgr": "os.getcwd"})
    brf.register_report_specs({"W23-Binder": FormatSet(
        heading="W23-Binder", description="probe", target_type="Referenceable", action=action,
        formats=[Format(types=["DICT"], attributes=[])])}, source="test")
    assert sr.resolve(brf.get_report_registry()["W23-Binder"], "W23-Binder").runnable
    result = _run("W23-Binder", params={"type_name": "Asset"})
    result.pop("spec_source", None)  # RS-EGERIA-TIER: provenance beside kind, not in data
    assert result == {"kind": "json", "data": {"count": 1}}
    assert len(fake_tech) == 1 and seen["args"] == (fake_tech[0], "Asset")  # the caller's client, not os.getcwd()
    assert not hasattr(fse, "_apply_analytic_binders")
