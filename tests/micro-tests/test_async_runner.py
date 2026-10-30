"""
ISSUE-168: run_sync replaces get_event_loop().run_until_complete + nest_asyncio, so sync wrappers
work with no running loop, inside a running loop (Jupyter, Textual), and nested, on Python 3.12-3.14.
"""
import asyncio
import threading

import pytest

from pyegeria.core.async_runner import run_sync


async def _whoami():
    await asyncio.sleep(0)
    assert asyncio.current_task() is not None
    return threading.current_thread().name, id(asyncio.get_running_loop())


def test_no_running_loop_reuses_one_loop_per_thread():
    name1, loop1 = run_sync(_whoami())
    name2, loop2 = run_sync(_whoami())
    assert name1 == name2 == threading.current_thread().name
    assert loop1 == loop2  # the per-thread httpx session stays on one loop


def test_each_thread_gets_its_own_loop():
    loops = []
    workers = [threading.Thread(target=lambda: loops.append(run_sync(_whoami())[1])) for _ in range(2)]
    for w in workers:
        w.start()
    for w in workers:
        w.join()
    assert len(set(loops)) == 2


async def test_inside_running_loop_uses_background_loop():
    # What a notebook cell or a Textual app does: call a sync wrapper while a loop is running.
    name, loop = run_sync(_whoami())
    assert name == "pyegeria-sync-runner"
    assert loop != id(asyncio.get_running_loop())
    assert run_sync(_whoami())[1] == loop  # the same background loop every time


async def test_nested_sync_call_from_the_background_loop_does_not_deadlock():
    async def outer():
        return run_sync(_whoami())  # a sync wrapper called from a coroutine running on the background loop

    name, _ = run_sync(outer())
    assert name == "pyegeria-sync-runner-nested"


def test_exceptions_propagate():
    async def boom():
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        run_sync(boom())


async def test_exceptions_propagate_from_background_loop():
    async def boom():
        raise KeyError("x")

    with pytest.raises(KeyError):
        run_sync(boom())


# --- context variables (lineage_visible) reach the coroutine on every path --------------------

async def _lineage_flag():
    from pyegeria.core._base_platform_client import _for_lineage_default
    await asyncio.sleep(0)
    return _for_lineage_default.get()


def test_lineage_visible_reaches_the_no_loop_path():
    from pyegeria import lineage_visible
    with lineage_visible():
        assert run_sync(_lineage_flag()) is True


async def test_lineage_visible_reaches_the_background_and_nested_paths():
    from pyegeria import lineage_visible

    async def outer():
        return run_sync(_lineage_flag())  # nested: a sync call from a coroutine on the background loop

    with lineage_visible():
        assert run_sync(_lineage_flag()) is True
        assert run_sync(outer()) is True
    assert run_sync(_lineage_flag()) is False

# --- the per-thread httpx session follows the event loop -------------------------------------

def _client(monkeypatch):
    from pyegeria.core._base_server_client import BaseServerClient
    monkeypatch.setattr(BaseServerClient, "check_connection", lambda self: "test")
    return BaseServerClient("view-server", "https://localhost:1", user_id="u", user_pwd="p")


def test_session_is_renewed_when_the_thread_switches_loops(monkeypatch):
    client = _client(monkeypatch)

    async def current():
        return client.session

    first = run_sync(current())
    assert run_sync(current()) is first          # same thread, same runner loop: reused
    assert asyncio.run(current()) is not first   # asyncio.run is a different loop: new session


def test_explicitly_set_session_is_kept(monkeypatch):
    client = _client(monkeypatch)
    sentinel = object()
    client.session = sentinel

    async def current():
        return client.session

    assert run_sync(current()) is sentinel
    assert asyncio.run(current()) is sentinel


# --- no sync wrapper bypasses run_sync ---------------------------------------------------------

def test_library_code_does_not_start_its_own_event_loop():
    # asyncio.run() and get_event_loop() fail inside a running loop (Jupyter, Textual) unless
    # nest_asyncio is applied, which pyegeria no longer does. CLI entry points under
    # `if __name__ == "__main__":` may still use asyncio.run().
    import ast
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    banned = {"run", "get_event_loop", "new_event_loop"}
    found = []
    for package in ("pyegeria", "md_processing"):
        for path in (root / package).rglob("*.py"):
            if path.name == "async_runner.py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            main_blocks = [n for n in ast.walk(tree) if isinstance(n, ast.If) and "__main__" in ast.unparse(n.test)]
            skip = {id(n) for block in main_blocks for n in ast.walk(block)}
            for node in ast.walk(tree):
                if (isinstance(node, ast.Call) and id(node) not in skip and isinstance(node.func, ast.Attribute)
                        and node.func.attr in banned and isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "asyncio"):
                    found.append(f"{path.relative_to(root)}:{node.lineno} asyncio.{node.func.attr}")
    assert not found, "use pyegeria.core.async_runner.run_sync instead:\n" + "\n".join(found)
