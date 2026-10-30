"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Run a coroutine to completion from synchronous code (ISSUE-168).

Every sync wrapper in the SDK calls `run_sync(self._async_x(...))`. This replaces the old
`asyncio.get_event_loop().run_until_complete(...)` pattern, which needed `nest_asyncio` to work
inside an already-running loop (Jupyter, Textual apps, async callers). `nest_asyncio` breaks
`asyncio.current_task()` on Python 3.14, and `get_event_loop()` no longer creates a loop there.

Each thread's `httpx.AsyncClient` (the client's per-thread `session`) is tied to the loop that first
used it, so every thread gets one persistent loop instead of a fresh loop per call:

- no loop running in this thread: run on this thread's own persistent loop;
- a loop is running: run on a shared background thread with its own persistent loop, and block
  until it finishes;
- already on that background loop (a sync call made from inside a coroutine it is running): run
  on a one-off thread, so the background loop never waits on itself.
"""

import asyncio
import contextvars
import threading
from typing import Any, Coroutine, TypeVar

T = TypeVar("T")

_thread_state = threading.local()
_background_loop: asyncio.AbstractEventLoop | None = None
_background_lock = threading.Lock()


def _loop_for_this_thread() -> asyncio.AbstractEventLoop:
    loop = getattr(_thread_state, "loop", None)
    if loop is None or loop.is_closed():
        loop = asyncio.new_event_loop()
        _thread_state.loop = loop
    return loop


def _get_background_loop() -> asyncio.AbstractEventLoop:
    global _background_loop
    with _background_lock:
        if _background_loop is None or _background_loop.is_closed():
            loop = asyncio.new_event_loop()
            threading.Thread(target=loop.run_forever, name="pyegeria-sync-runner", daemon=True).start()
            _background_loop = loop
        return _background_loop


def _run_on_new_thread(coro: Coroutine[Any, Any, T]) -> T:
    outcome: dict[str, Any] = {}

    def target() -> None:
        try:
            outcome["value"] = _loop_for_this_thread().run_until_complete(coro)
        except BaseException as exc:  # re-raised in the calling thread
            outcome["error"] = exc

    # A new thread starts with an empty context; carry the caller's (e.g. lineage_visible()).
    worker = threading.Thread(target=contextvars.copy_context().run, args=(target,),
                              name="pyegeria-sync-runner-nested")
    worker.start()
    worker.join()
    if "error" in outcome:
        raise outcome["error"]
    return outcome["value"]


def run_sync(coro: Coroutine[Any, Any, T]) -> T:
    """Run `coro` to completion and return its result, whether or not a loop is already running."""
    try:
        running = asyncio.get_running_loop()
    except RuntimeError:
        return _loop_for_this_thread().run_until_complete(coro)
    if running is _background_loop:
        return _run_on_new_thread(coro)
    return asyncio.run_coroutine_threadsafe(coro, _get_background_loop()).result()
