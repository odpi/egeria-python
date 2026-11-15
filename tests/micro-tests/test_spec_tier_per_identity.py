"""T4 (READBACK-STUDIO-FIXES 2026-11-15, flag (b)): the EGERIA tier is cached per identity, never in one shared
slot. Each entry is built whole and swapped in atomically, so a reload for one identity never hands a concurrent
read for another the previous identity's specs or meta. The cache is LRU-bounded. ``spec_identity(None)`` is
explicitly no one, declared multi-user or not. Hermetic: EGERIA_* identity vars are cleared."""
import threading
import time

import pytest

from pyegeria.view import egeria_spec_cache as esc

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def tier(tmp_path, monkeypatch):
    for var in ("EGERIA_USER", "EGERIA_USER_PASSWORD", "EGERIA_PASSWORD", "PYEGERIA_MULTI_USER", esc.DRAFTS_ENV):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv(esc.CACHE_DIR_ENV, str(tmp_path))
    monkeypatch.setattr(esc, "_RELOAD_INTERVAL_S", 0.0)    # every read re-checks: widest window for the race
    loads = []
    state = {"delay": 0.0, "stamp": (1, None)}

    def _stamp(directory, with_drafts):
        return state["stamp"]

    def _load_dir(directory, tier_label, specs, meta, skipped, shared):
        who = esc.current_spec_identity()
        loads.append(who)
        time.sleep(state["delay"])                          # a slow disk load, mid-reload
        specs[f"Spec-{who}"] = object()
        meta[f"Spec-{who}"] = {"tier": "egeria", "label": f"Spec-{who}", "owner": who}

    monkeypatch.setattr(esc, "_stamp", _stamp)
    monkeypatch.setattr(esc, "_read_manifest", lambda d: {"entries": {}, "shared": False})
    monkeypatch.setattr(esc, "_manifest_loads_for", lambda d, m, identity: identity is not None)
    monkeypatch.setattr(esc, "_load_dir", _load_dir)
    esc._invalidate_tier()
    yield {"loads": loads, "state": state}
    esc._invalidate_tier()


def _read_as(identity):
    with esc.spec_identity(identity):
        specs = dict(esc.egeria_tier())
        info = esc.egeria_tier_info(f"Spec-{identity}")
        return set(specs), info


def test_a_read_during_another_identitys_slow_reload_gets_its_own_tier(tier, monkeypatch):
    """The 8dd9e087 race, deterministically: b's reload is inside its slow load (a's specs still in the old
    slot, b's key and check time already set) when a second request for b arrives. It must not get a's tier."""
    monkeypatch.setattr(esc, "_RELOAD_INTERVAL_S", 60.0)   # the freshness check passes for the second request
    _read_as("a@p/v")
    inside, release = threading.Event(), threading.Event()
    real = esc._load_dir

    def gated(*args, **kw):
        if esc.current_spec_identity() == "b@p/v" and not inside.is_set():
            inside.set()
            release.wait(5)
        return real(*args, **kw)

    monkeypatch.setattr(esc, "_load_dir", gated)
    out = {}
    first = threading.Thread(target=lambda: out.__setitem__("first", _read_as("b@p/v")))
    first.start()
    assert inside.wait(5)
    second = threading.Thread(target=lambda: out.__setitem__("second", _read_as("b@p/v")))
    second.start()
    second.join(0.5)                                     # the old slot answered at once; the fix loads b's own
    release.set()
    first.join(5)
    second.join(5)
    for name in ("first", "second"):
        specs, info = out[name]
        assert specs == {"Spec-b@p/v"} and info["owner"] == "b@p/v", (name, specs, info)


def test_two_threads_alternating_identities_with_a_slow_load_never_cross(tier, monkeypatch):
    monkeypatch.setattr(esc, "_RELOAD_INTERVAL_S", 60.0)
    tier["state"]["delay"] = 0.01
    seen, errors = {"a@p/v": [], "b@p/v": []}, []

    def run(identity, n):
        try:
            for i in range(n):
                if i % 3 == 0:
                    tier["state"]["stamp"] = (i, None)
                    esc._invalidate_tier()                 # everyone reloads
                specs, info = _read_as(identity)
                seen[identity].append((specs, info))
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=run, args=(who, 12)) for who in ("a@p/v", "b@p/v", "a@p/v", "b@p/v")]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors
    for who, reads in seen.items():
        assert len(reads) == 24
        for specs, info in reads:
            assert specs == {f"Spec-{who}"}, (who, specs)            # never the other identity's specs
            assert info and info["owner"] == who                     # never the other identity's meta


def test_tier_info_reads_the_callers_own_entry(tier):
    _read_as("a@p/v")
    with esc.spec_identity("b@p/v"):
        assert esc.egeria_tier_info("Spec-a@p/v") is None            # a's meta isn't b's
        assert esc.egeria_tier_info("Spec-b@p/v")["owner"] == "b@p/v"


def test_known_names_peeks_only_the_callers_entry_and_never_loads(tier):
    _read_as("a@p/v")
    n = len(tier["loads"])
    with esc.spec_identity("b@p/v"):
        assert "Spec-a@p/v" not in esc._known_names()
    assert len(tier["loads"]) == n
    with esc.spec_identity("a@p/v"):
        assert "Spec-a@p/v" in esc._known_names()


def test_an_entry_is_replaced_whole_never_mutated(tier):
    _read_as("a@p/v")
    first = next(iter(esc._TIERS.values()))
    tier["state"]["stamp"] = (2, None)
    _read_as("a@p/v")
    second = next(iter(esc._TIERS.values()))
    assert first is not second and first.stamp == (1, None) and second.stamp == (2, None)
    with pytest.raises(Exception):
        first.specs = {}                                               # frozen


def test_lru_eviction(tier, monkeypatch):
    monkeypatch.setattr(esc, "TIER_CACHE_SIZE", 3)
    for who in ("a", "b", "c"):
        _read_as(f"{who}@p/v")
    _read_as("a@p/v")                                                  # a is now most recent
    _read_as("d@p/v")                                                  # evicts b, the least recent
    held = {key[-1] for key in esc._TIERS}
    assert held == {"a@p/v", "c@p/v", "d@p/v"} and len(esc._TIERS) == 3


@pytest.mark.parametrize("declared", [False, True])
def test_explicit_none_is_no_one_declared_or_not(tier, monkeypatch, declared):
    monkeypatch.setenv("EGERIA_USER", "erinoverview")                  # a fallback that must NOT be used
    if declared:
        monkeypatch.setenv("PYEGERIA_MULTI_USER", "1")
    with esc.spec_identity(None):
        assert esc.current_spec_identity() is None
        assert dict(esc.egeria_tier()) == {}                           # no private manifest loads for no one
    with esc.spec_identity(""):
        assert esc.current_spec_identity() is None
    if not declared:
        assert esc.current_spec_identity() is not None                 # outside a block: the fallback applies


def test_an_inner_identity_overrides_an_outer_none_and_restores_it(tier):
    with esc.spec_identity(None):
        with esc.spec_identity("a@p/v"):
            assert esc.current_spec_identity() == "a@p/v"
        assert esc.current_spec_identity() is None
