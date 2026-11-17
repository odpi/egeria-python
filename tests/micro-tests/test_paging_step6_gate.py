"""Pager step 6, the #9453 version gate (the Architect's step 6 ruling, 2026-11-14): find_metadata_elements and
by-property-value are trusted only on a platform whose /api/about shows the fix; get_relationships stays
NULL_NOT_END everywhere; the gate is best-effort, cached, fail-safe."""
import asyncio
import json

import pytest

from pyegeria.core import paging

pytestmark = pytest.mark.unit

NULL = "No elements found"
LAZ_5DEDA38D = {"name": "platform-chassis-spring", "time": "2026-11-14T19:55:39.317Z", "version": "6.3-SNAPSHOT",
                "group": "org.odpi.egeria", "artifact": "platform-chassis-spring"}   # laz after the upgrade
LAZ_002A3EF1 = {**LAZ_5DEDA38D, "time": "2026-11-10T08:00:00.000Z"}                  # before it


@pytest.fixture(autouse=True)
def _fresh_gate(monkeypatch):
    paging._GATE_CACHE.clear()
    monkeypatch.delenv(paging.GATE_OVERRIDE_ENV, raising=False)
    yield
    paging._GATE_CACHE.clear()


class _Platform:
    """A client on one platform whose /api/about answers `about` (a dict, a string, or an exception)."""

    def __init__(self, about, url="https://laz:9443"):
        self.about, self.platform_url, self.about_reads = about, url, 0

    def _answer(self):
        self.about_reads += 1
        if isinstance(self.about, BaseException):
            raise self.about
        return self.about if isinstance(self.about, str) else json.dumps(self.about)

    def get_platform_origin(self):
        return self._answer()

    async def async_get_platform_origin(self):
        return self._answer()


# ── each gate branch ──

@pytest.mark.parametrize("about, promoted", [
    (LAZ_5DEDA38D, True),                                   # 6.3-SNAPSHOT built after the #9453 merge
    ({"version": "6.3-SNAPSHOT", "time": "2026-11-14T19:52:00Z"}, True),   # exactly at it
    (LAZ_002A3EF1, False),                                  # 6.3-SNAPSHOT built before it
    ({"version": "6.3"}, True), ({"version": "6.4.1"}, True), ({"version": "7.0"}, True),   # releases > SNAPSHOT
    ({"version": "6.2"}, False), ({"version": "6.2.9"}, False),                             # older releases
    ({"version": "6.4-SNAPSHOT", "time": "2027-01-01T00:00:00Z"}, True),   # read-back R1: later SNAPSHOTs
    ({"version": "6.4-SNAPSHOT"}, True), ({"version": "7.0.1-SNAPSHOT"}, True),
    ({"version": "6.2-SNAPSHOT", "time": "2027-01-01T00:00:00Z"}, False),   # an earlier SNAPSHOT: never
    ({"version": "6.3-SNAPSHOT"}, False),                   # a SNAPSHOT with no time
    ({"version": "6.3-SNAPSHOT", "time": "yesterday"}, False),
    ({"version": "6.3-SNAPSHOT", "time": "2026-11-14T19:55:39"}, False),   # no timezone: not comparable
    ("not json", False), ({"name": "x"}, False), ([], False), (None, False),
])
def test_gate_from_about(about, promoted):
    assert paging.gate_from_about(about) is promoted


def test_about_failing_is_not_promoted_and_never_raises():
    client = _Platform(TimeoutError("unreachable"))
    assert paging.paging_for("find_metadata_elements", client)["end_policy"] == "suspect"
    assert asyncio.run(paging.async_platform_promoted(_Platform(ConnectionError("x"), url="https://b"))) is False


def test_the_override_forces_not_promoted(monkeypatch):
    monkeypatch.setenv(paging.GATE_OVERRIDE_ENV, "off")
    client = _Platform(LAZ_5DEDA38D)
    assert paging.platform_promoted(client) is False and client.about_reads == 0


# ── what is promoted, and what isn't ──

@pytest.mark.parametrize("method", sorted(m for m, needs in paging.METHOD_NEEDS.items() if needs == {"9453"}))
def test_a_gated_method_is_trusted_on_a_promoted_platform_only(method):
    assert paging.paging_for(method, _Platform(LAZ_5DEDA38D)) == {"end_policy": "trusted"}
    assert paging.paging_for(method, _Platform(LAZ_002A3EF1, url="https://old"))["null_not_end"] is True
    assert paging.paging_for(method)["null_not_end"] is True   # no client: not promoted


def test_get_elements_by_type_is_findmetadataelements_so_gated():
    """P3 (the Architect's ruling (c)): elements/by-type is getRootElementsByType -> findMetadataElements."""
    assert {"get_elements", "_async_get_elements"} <= paging.GATED_TRUSTED_METHODS
    assert paging.paging_for("get_elements", _Platform(LAZ_5DEDA38D)) == {"end_policy": "trusted"}
    assert paging.paging_for("get_elements")["null_not_end"] is True


def test_get_relationships_stays_null_not_end_while_promoted():
    p = paging.paging_for("get_relationships", _Platform(LAZ_5DEDA38D))
    assert p["null_not_end"] is True and p["probe_pages"] == paging.NULL_NOT_END_PROBE_PAGES


def test_a_promoted_find_reads_to_a_confirmed_end():
    rows = {0: [{"guid": "a"}], 100: []}   # a filtered page is [] on a fixed platform; null at 200 is the end
    r = paging.page_all(lambda s, n: rows.get(s, NULL),
                        **paging.paging_for("find_metadata_elements", _Platform(LAZ_5DEDA38D)))
    assert r.end == "confirmed" and r.reached_end and r.complete and len(r.items) == 1


def test_a_promoted_exists_can_answer_absent_at_a_confirmed_end():
    found = asyncio.run(paging.async_exists(lambda s, n: _async(NULL), lambda r: True,
                                            method="_async_get_elements_by_property_value",
                                            client=_Platform(LAZ_5DEDA38D)))
    assert found.answer == "absent" and found.read.end == "confirmed"


async def _async(value):
    return value


# ── the cache, and no needless about-read ──

def test_one_about_read_per_platform_within_the_ttl(monkeypatch):
    client = _Platform(LAZ_5DEDA38D)
    for _ in range(5):
        paging.paging_for("find_metadata_elements", client)
    asyncio.run(paging.async_paging_for("get_elements_by_property_value", client))
    assert client.about_reads == 1
    other = _Platform(LAZ_5DEDA38D, url="https://other:9443")
    paging.paging_for("find_metadata_elements", other)
    assert other.about_reads == 1                     # per platform URL
    import time
    real = time.monotonic
    monkeypatch.setattr(time, "monotonic", lambda: real() + paging.GATE_TTL_SECONDS + 1)
    paging.paging_for("find_metadata_elements", client)
    assert client.about_reads == 2                    # re-read after the TTL


def test_no_about_read_for_a_client_that_never_pages_a_gated_method():
    client = _Platform(LAZ_5DEDA38D)
    for method in ("get_collection_members", "find_authored_elements", "get_element_history", None):
        paging.paging_for(method, client)
        asyncio.run(paging.async_paging_for(method, client))
    assert client.about_reads == 0


# ── what a promoted read says ──

def test_a_promoted_overview_scan_is_plain_and_its_share_measured():
    from pyegeria.view import overview_metrics as om

    class Mgr(_Platform):
        def find_metadata_elements(self, body, *a, **kw):
            hits = [{"elementGUID": f"g{i}", "classifications": [{"classificationName": "Confidentiality"}]}
                    for i in range(3)]
            return hits[body["startFrom"]:body["startFrom"] + body["pageSize"]] or NULL

    mgr = Mgr(LAZ_5DEDA38D)
    with om.recording_unmeasured() as notes, om.recording_unconfirmed() as scans:
        r = om.governed_coverage(mgr)
    assert r["governedCount"] == 3 and "unconfirmed" not in r and scans == [] and notes == []


def test_a_promoted_single_display_match_is_linked_without_a_note():
    import importlib.util
    import pathlib

    from md_processing.v2.dashboard_sheet import DashboardSheetEgeriaWriter
    from pyegeria.view._output_dashboard_sheet_models import DashboardSheet, Placement
    spec = importlib.util.spec_from_file_location(
        "dashboard_fake_egeria", pathlib.Path(__file__).parent / "dashboard_fake_egeria.py")
    fake_egeria = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fake_egeria)
    egeria = fake_egeria.FakeEgeria()
    egeria.platform_url = "https://laz:9443"
    egeria.async_get_platform_origin = lambda: _async(json.dumps(LAZ_5DEDA38D))
    egeria.get_platform_origin = lambda: json.dumps(LAZ_5DEDA38D)
    report = egeria.add_entity("Report", "X::Report::One", "Only One")
    absent_name = "No Such Report Here"
    writer = DashboardSheetEgeriaWriter(egeria)
    asyncio.run(writer.write_sheet(DashboardSheet(name="s", heading="S",
                                                  placements=[Placement(ref="Only One"),
                                                              Placement(ref=absent_name)])))
    assert [r["end2"] for r in egeria.rels("DataSetContent")] == [report]
    assert not any("Egeria can't confirm" in n for n in writer.notes)
    assert any(f"There is no Report named '{absent_name}' in Egeria" in n for n in writer.notes)   # "none"


def test_a_failed_about_read_is_retried_after_a_short_ttl(monkeypatch):
    import time
    client = _Platform(TimeoutError("restarting"))
    assert paging.platform_promoted(client) is False and client.about_reads == 1
    real = time.monotonic
    monkeypatch.setattr(time, "monotonic", lambda: real() + paging.GATE_FAILED_TTL_SECONDS + 1)
    client.about = LAZ_5DEDA38D   # the platform is back
    assert paging.platform_promoted(client) is True and client.about_reads == 2


def test_a_slow_about_read_times_out_as_not_promoted(monkeypatch):
    monkeypatch.setattr(paging, "GATE_ABOUT_TIMEOUT_SECONDS", 0.05)

    class Slow(_Platform):
        async def async_get_platform_origin(self):
            await asyncio.sleep(1)
            return json.dumps(LAZ_5DEDA38D)

        def get_platform_origin(self):
            import time
            time.sleep(1)
            return json.dumps(LAZ_5DEDA38D)

    assert asyncio.run(paging.async_platform_promoted(Slow(None, url="https://slow-a"))) is False
    assert paging.platform_promoted(Slow(None, url="https://slow-b")) is False


def test_the_sync_about_read_closes_its_worker_threads_session():
    """Step 6 gate read-back advisory: the worker thread's thread-local session (and its run_sync loop) is
    closed after the read, so none is left open per platform per TTL."""
    import threading

    closed = []

    class Session:
        async def aclose(self):
            closed.append(threading.current_thread().name)

    class Client(_Platform):
        def __init__(self):
            super().__init__(LAZ_5DEDA38D)
            self._thread_local = threading.local()

        def get_platform_origin(self):
            from pyegeria.core.async_runner import _loop_for_this_thread
            _loop_for_this_thread()                 # the read's run_sync loop on this thread
            self._thread_local.session = Session()  # what a real read opens on this thread
            return super().get_platform_origin()

    c = Client()
    assert paging.platform_promoted(c) is True
    assert len(closed) == 1 and closed[0].startswith("pyegeria-about")
