"""AuthoringRefused.answer: callers branch on "absent" / "unknown" / "refused", never on the words
(the Architect's S2 advisory and the Studio builder's request, 2026-11-14)."""
import asyncio
import json

import pytest

from pyegeria.authoring import (
    ANSWER_ABSENT, ANSWER_REFUSED, ANSWER_UNKNOWN, ANSWERS, AuthoringRefused, async_load_held,
)
from pyegeria.core import paging

pytestmark = pytest.mark.unit

NULL = "No elements found"
GATED = json.dumps({"version": "6.3-SNAPSHOT", "time": "2026-11-14T19:55:39.317Z"})
OLD = json.dumps({"version": "6.3-SNAPSHOT", "time": "2026-11-10T08:00:00Z"})


@pytest.fixture(autouse=True)
def _fresh_gate():
    paging._GATE_CACHE.clear()
    yield
    paging._GATE_CACHE.clear()


class _Client:
    """Nothing held: the unique-name read says not found; the display-name read is empty."""
    user_id = "peterprofile"

    def __init__(self, about=OLD):
        self.about, self.platform_url = about, "https://p:9443"

        class CM:
            async def _async_get_element_by_unique_name(self, qn):
                return NULL

            async def _async_get_elements_by_property_value(self, *a, **kw):
                return NULL

        self.classification_manager = CM()

    def get_platform_origin(self):
        return self.about

    async def async_get_platform_origin(self):
        return self.about


def _refusal(kind, label, client):
    with pytest.raises(AuthoringRefused) as ei:
        asyncio.run(async_load_held(kind, label, client))
    return ei.value


def test_default_is_refused_and_the_words_are_kept():
    exc = AuthoringRefused("no")
    assert exc.answer == ANSWER_REFUSED and str(exc) == "no" and isinstance(exc, ValueError)
    assert set(ANSWERS) == {"absent", "unknown", "refused"}


def test_an_answer_outside_the_three_is_an_error():
    with pytest.raises(ValueError):
        AuthoringRefused("x", answer="maybe")


def test_spec_not_held_is_absent():
    exc = _refusal("spec", "Nope", _Client())
    assert exc.answer == ANSWER_ABSENT and str(exc).startswith("Egeria holds no")


def test_report_on_a_gated_platform_is_absent():
    exc = _refusal("report", "Nope", _Client(about=GATED))
    assert exc.answer == ANSWER_ABSENT and str(exc).startswith("Egeria holds no")


def test_report_on_an_older_platform_is_unknown_never_absent():
    exc = _refusal("report", "Nope", _Client(about=OLD))
    assert exc.answer == ANSWER_UNKNOWN and str(exc).startswith("Couldn't confirm")


def test_no_client_and_a_bad_kind_are_refused():
    with pytest.raises(AuthoringRefused) as ei:
        asyncio.run(async_load_held("spec", "X", None))
    assert ei.value.answer == ANSWER_REFUSED
    with pytest.raises(AuthoringRefused) as ei:
        asyncio.run(async_load_held("table", "X", _Client()))
    assert ei.value.answer == ANSWER_REFUSED


def test_publish_unique_name_read_failure_is_unknown():
    from pyegeria.authoring.publication import _find_exact

    class Failing(_Client):
        def __init__(self):
            super().__init__()

            class CM:
                async def _async_get_element_by_unique_name(self, qn):
                    raise RuntimeError("connection reset")

            self.classification_manager = CM()

    with pytest.raises(AuthoringRefused) as ei:
        asyncio.run(_find_exact(Failing(), "ReportSpec", "qualifiedName", "ReportSpec::X"))
    assert ei.value.answer == ANSWER_UNKNOWN


@pytest.fixture
def reworded(monkeypatch):
    """Every raise site in the three-way reads, with different words: the answer must not depend on them."""
    import pyegeria.authoring.drafts as drafts
    import pyegeria.authoring.lifecycle as lifecycle
    import pyegeria.authoring.publication as publication
    import pyegeria.authoring.versions as versions

    class Reworded(AuthoringRefused):
        def __init__(self, *args, **kw):
            super().__init__("Something else entirely.", **kw)

    for mod in (drafts, lifecycle, publication, versions):
        monkeypatch.setattr(mod, "AuthoringRefused", Reworded)


@pytest.mark.parametrize("kind,about,expected", [
    ("spec", OLD, ANSWER_ABSENT),
    ("sheet", OLD, ANSWER_ABSENT),
    ("report", GATED, ANSWER_ABSENT),
    ("report", OLD, ANSWER_UNKNOWN),
])
def test_the_answer_holds_when_the_words_change(reworded, kind, about, expected):
    exc = _refusal(kind, "Nope", _Client(about=about))
    assert str(exc) == "Something else entirely."
    assert not str(exc).startswith(("Egeria holds no", "Couldn't confirm"))
    assert exc.answer == expected
