"""pyegeria.view.report_spec_publish: the shared report-spec publish/withdraw helper (stage 1a).

Golden: tests/micro-tests/data/report_spec_publish/ea_goldens_2026_11_12.json holds Egeria Advisor's
own output (trellis 82340b58, advisor/egeria_spec_publish.py) for fixed inputs, captured with this
branch's pyegeria. The helper must produce the same documents, digests, steps and refusal words. EA's
`also_portal=True` is `folders=[ADVISOR, PORTAL]` here, and its env-var proof is `restricted=`.
Offline: the runner is a fake; nothing talks to Egeria.
"""
import ast
import json
from pathlib import Path

import pytest

from pyegeria.view import report_spec_publish as rsp
from pyegeria.view._output_format_models import FormatSet

GOLD = json.loads((Path(__file__).parent / "data" / "report_spec_publish" / "ea_goldens_2026_11_12.json").read_text())
PROVEN = rsp.restricted_publish_status("READBACK-zone-proof")
EA_ALLOWED_WORDS = "EA's and the Portal's consumer folders"


def _fs(case):
    d = json.loads(json.dumps(GOLD["specs"][case["spec"]]))
    if case.get("alias"):
        d["aliases"] = case["alias"]
    return FormatSet.model_validate(d)


def _build(case):
    kw = dict(case["kw"])
    folders = [rsp.ADVISOR_FOLDER] + ([rsp.PORTAL_FOLDER] if kw.pop("also_portal", False) else [])
    return rsp.build_publish_document(case["label"], _fs(case), folders=folders,
                                      restricted=PROVEN if case.get("proven") else None, **kw)


# ── Golden: the same as EA ────────────────────────────────────────────────────

@pytest.mark.parametrize("case", GOLD["publish"], ids=[c["id"] for c in GOLD["publish"]])
def test_publish_document_is_byte_identical_to_eas(case):
    plan = _build(case)
    for key, want in case["expect"].items():
        assert plan[key] == want, key


@pytest.mark.parametrize("case", GOLD["refusals"], ids=[c["id"] for c in GOLD["refusals"]])
def test_refusal_words_are_eas(case):
    with pytest.raises(rsp.PublishRefused) as exc:
        _build(case)
    assert str(exc.value) == case["words"]


@pytest.mark.parametrize("case", GOLD["withdraw"], ids=[c["id"] for c in GOLD["withdraw"]])
def test_withdraw_document_is_byte_identical_to_eas(case):
    plan = rsp.build_withdraw_document(case["label"], case["folders"] or [rsp.ADVISOR_FOLDER],
                                       allowed=rsp.CONSUMER_FOLDERS, allowed_words=EA_ALLOWED_WORDS)
    assert {k: plan[k] for k in case["expect"]} == case["expect"]


def test_withdraw_refusal_words_are_eas():
    r = GOLD["withdraw_refusal"]
    with pytest.raises(rsp.PublishRefused) as exc:
        rsp.build_withdraw_document("X", r["folders"], allowed=rsp.CONSUMER_FOLDERS, allowed_words=EA_ALLOWED_WORDS)
    assert str(exc.value) == r["words"]


def test_not_proven_status_is_eas():
    assert rsp.restricted_publish_status(None) == GOLD["not_proven"]
    assert rsp.restricted_publish_status("  ") == GOLD["not_proven"]
    assert rsp.restricted_publish_status(" proof.md ") == {"enabled": True, "message": None, "proof": "proof.md"}


# ── Folders are the app's ─────────────────────────────────────────────────────

def test_portal_folders_in_its_own_order():
    case = GOLD["publish"][0]
    plan = rsp.build_publish_document(case["label"], _fs(case), folders=[rsp.PORTAL_FOLDER, rsp.ADVISOR_FOLDER,
                                                                         rsp.PORTAL_FOLDER])
    assert plan["folders"] == [rsp.PORTAL_FOLDER, rsp.ADVISOR_FOLDER]
    md = plan["markdown"]
    assert md.index(rsp.PORTAL_FOLDER) < md.index(rsp.ADVISOR_FOLDER) and md.count("## Add Member to Collection") == 2


@pytest.mark.parametrize("folders,words", [
    ([], "Publish needs at least one consumer folder."),
    (["ReportSpecFolder::Consumer::A, B"], "A consumer folder cannot contain a comma (it would become two entries): "
                                            "'ReportSpecFolder::Consumer::A, B'."),
    (["X\n## Create Report Spec"], "A consumer folder must be a single line of text (line breaks of any kind are refused)."),
])
def test_bad_folders_are_refused(folders, words):
    case = GOLD["publish"][0]
    with pytest.raises(rsp.PublishRefused) as exc:
        rsp.build_publish_document(case["label"], _fs(case), folders=folders)
    assert str(exc.value) == words


def test_withdraw_without_an_allow_list_takes_any_one_line_folder():
    plan = rsp.build_withdraw_document("S", ["ReportSpecFolder::Consumer::Other"])
    assert plan["markdown"].count("## Remove Member from Collection") == 1


# ── Zones ─────────────────────────────────────────────────────────────────────

def test_zone_rules():
    assert rsp.check_zones("public", None) == []
    assert rsp.check_zones("restricted", ["b", " a ", "b"], restricted=PROVEN) == ["a", "b"]
    with pytest.raises(rsp.PublishRefused, match="not yet proven"):
        rsp.check_zones("restricted", ["a"])                     # no status = not proven
    with pytest.raises(rsp.PublishRefused, match="not yet proven"):
        rsp.check_zones("restricted", ["a"], restricted=rsp.restricted_publish_status(""))


# ── Never a Parent ID ─────────────────────────────────────────────────────────

def test_no_document_ever_has_a_parent_id():
    for case in GOLD["publish"]:
        assert "Parent ID" not in _build(case)["markdown"]
    for case in GOLD["withdraw"]:
        assert "Parent" not in case["expect"]["markdown"]


def test_the_module_writes_no_parent_id():
    """Only the docstrings and comments may name it: no string the code builds contains it."""
    tree = ast.parse(Path(rsp.__file__).read_text())
    docstrings = {id(n.body[0].value) for n in ast.walk(tree)
                  if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and n.body
                  and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant)}
    strings = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)
               and id(n) not in docstrings]
    assert not [s for s in strings if "Parent" in s]


def test_no_credentials_and_no_io():
    tree = ast.parse(Path(rsp.__file__).read_text())
    imported = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    imported |= {(n.module or "").split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert imported <= {"__future__", "hashlib", "json", "re", "typing", "pyegeria"}, imported
    args = {a.arg for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) for a in n.args.args + n.args.kwonlyargs}
    assert not args & {"creds", "token", "password", "user_pwd", "user_id", "egeria_credentials"}


# ── held_in_egeria ────────────────────────────────────────────────────────────

def test_held_in_the_shared_tier():
    got = rsp.held_in_egeria("S", shared_tier=lambda label: {"tier": "egeria"}, app="EA")
    assert got == {"held": True, "zones": [], "how": "held in Egeria (EA's shared tier)"}


def test_held_restricted_for_this_user():
    got = rsp.held_in_egeria("S", shared_tier=lambda label: None,
                             restricted_reader=lambda: {"specs": [{"label": "S", "zones": ["finance"]}]})
    assert got == {"held": True, "zones": ["finance"], "how": "held in Egeria, restricted"}


def test_not_held_says_what_was_read():
    got = rsp.held_in_egeria("S", shared_tier=lambda label: None, restricted_reader=lambda: {"specs": []}, app="EA")
    assert got == {"held": False, "zones": [], "how": "not held in Egeria as far as EA can see"}


def test_unreadable_tier_and_reader_are_not_known():
    def boom(*_):
        raise ConnectionError("platform down")
    got = rsp.held_in_egeria("S", shared_tier=boom, restricted_reader=boom, app="EA")
    assert got["held"] is False
    assert got["how"] == ("not known: restricted specs not read (platform down); "
                          "EA's shared tier could not be read (platform down)")


def test_no_restricted_reader_is_not_known_never_not_held():
    got = rsp.held_in_egeria("S", shared_tier=lambda label: None, app="the Portal")
    assert got == {"held": False, "zones": [], "how": "not known: restricted specs not read (the Portal reads none)"}


# ── run_document: steps, confirm, the digest refusal ──────────────────────────

class FakeRun:
    def __init__(self, answer):
        self.answer, self.calls = answer, []

    def __call__(self, markdown, directive):
        self.calls.append((directive, markdown))
        return self.answer


def _plan(description="Projects of a team."):
    case = GOLD["publish"][0]
    fs = _fs(case).model_copy(update={"description": description})
    return rsp.build_publish_document(case["label"], fs, folders=[rsp.PORTAL_FOLDER])


def test_preview_runs_nothing():
    run = FakeRun({"success": True})
    out = rsp.run_document(_plan(), step="preview", run=run)
    assert out["step"] == "preview" and out["result"] is None and run.calls == []


def test_validate_runs_validate():
    run = FakeRun(json.dumps({"success": True, "validation_errors": [], "secret": "x"}))
    out = rsp.run_document(_plan(), step="validate", run=run)
    assert run.calls[0][0] == "validate" and out["result"] == {"success": True, "validation_errors": []}
    assert "after" not in out


def test_process_needs_a_confirm():
    run = FakeRun({"success": True})
    with pytest.raises(rsp.PublishRefused) as exc:
        rsp.run_document(_plan(), step="process", run=run, digest=_plan()["digest"])
    assert str(exc.value) == "Confirm first: the document runs as you, and writes to Egeria." and run.calls == []


def test_process_refuses_a_document_that_changed_since_the_preview():
    previewed = rsp.run_document(_plan(), step="preview")["digest"]
    rebuilt = _plan(description="Someone edited the spec meanwhile.")
    run = FakeRun({"success": True})
    with pytest.raises(rsp.PublishRefused) as exc:
        rsp.run_document(rebuilt, step="process", run=run, confirmed=True, digest=previewed)
    assert str(exc.value) == ("The document changed since you previewed it (the spec, or what Egeria holds); "
                              "preview it again before confirming.")
    assert run.calls == []
    with pytest.raises(rsp.PublishRefused):
        rsp.check_unchanged(previewed, rebuilt["markdown"])
    rsp.check_unchanged(previewed, _plan()["markdown"])           # unchanged: no refusal


def test_process_runs_the_previewed_document_and_says_what_the_app_must_do():
    plan = _plan()
    run = FakeRun({"success": True, "commands_total": 2, "commands_succeeded": 2})
    out = rsp.run_document(plan, step="process", run=run, confirmed=True, digest=plan["digest"])
    assert run.calls == [("process", plan["markdown"])]
    assert out["result"] == {"success": True, "commands_total": 2, "commands_succeeded": 2}
    assert out["after"] == {"invalidate": ["Team Projects"], "sync": True,
                            "why": "ReportSpec::Team Projects changed in Egeria; refresh this app's copy of its report specs."}


def test_a_failed_process_asks_for_nothing():
    plan = _plan()
    out = rsp.run_document(plan, step="process", run=FakeRun({"success": False, "execution_errors": ["403"]}),
                           confirmed=True, digest=plan["digest"])
    assert "after" not in out and out["result"]["success"] is False


def test_unreadable_runner_answer_is_a_failure_in_words():
    plan = _plan()
    out = rsp.run_document(plan, step="process", run=FakeRun("<html>gateway timeout</html>"),
                           confirmed=True, digest=plan["digest"])
    assert out["result"] == {"success": False, "output": "<html>gateway timeout</html>",
                             "execution_errors": [{"message": "unreadable result"}]}


@pytest.mark.parametrize("step,kw,words", [
    ("apply", {}, "Step must be one of preview, validate, process, not 'apply'."),
    ("validate", {"run": None}, "The validate step needs a runner (the app runs the document as the signed-in user)."),
])
def test_step_refusals(step, kw, words):
    with pytest.raises(rsp.PublishRefused) as exc:
        rsp.run_document(_plan(), step=step, **kw)
    assert str(exc.value) == words


def test_withdraw_runs_through_the_same_steps():
    plan = rsp.build_withdraw_document("Team Projects", [rsp.PORTAL_FOLDER])
    run = FakeRun({"success": True})
    out = rsp.run_document(plan, step="process", run=run, confirmed=True, digest=plan["digest"])
    assert run.calls[0] == ("process", plan["markdown"]) and out["after"]["invalidate"] == ["Team Projects"]
