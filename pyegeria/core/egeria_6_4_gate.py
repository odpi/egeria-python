# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""The version gate for the Egeria 6.4 additions (odpi/egeria#9463): "needs Egeria 6.4", in words.

An Egeria before 6.4 has none of the 6.4 requests (decisions, data values, project targets, supported variable
types, Branch): they 404, and the lists they fill are absent. Anything that offers a 6.4 request (Dr.Egeria
commands now, the Egeria Explorer cards later) asks here first, and says the same words when the answer is no.
It is never reported as an error, and never as "none".

How the answer is reached, in order:

1. The platform's ``/api/about`` version, read once per platform URL per GATE_TTL_SECONDS:
   - a release (no ``-SNAPSHOT``) carries the additions from 6.4.0 on;
   - a ``6.4-SNAPSHOT`` carries them when built at or after the #9463 merge (2026-11-21T19:51:36Z, 90232870b2);
     one built before it is a 6.4 line without the additions;
   - a SNAPSHOT of a later line (6.5-SNAPSHOT, ...) carries them; an earlier line, never.
2. If the version can't be read or parsed, the answer is unknown (None), never "no": the request is sent, and a
   bare HTTP 404 from it (the endpoint is not served, as opposed to Egeria's own not-found, which is a 200 with
   relatedHTTPCode 404) is read as "needs Egeria 6.4" with :func:`is_missing_6_4_endpoint`.
"""
from __future__ import annotations

import json
import re
import time
from datetime import datetime
from typing import Any, Optional

from loguru import logger

#: The #9463 merge into odpi/egeria main: a 6.4-SNAPSHOT built at or after it carries the additions.
EGERIA_6_4_MERGE_SHA = "90232870b2955ea33a1e791c331b4d085cc9da3e"
EGERIA_6_4_SNAPSHOT_CUTOFF = "2026-11-21T19:51:36Z"

GATE_TTL_SECONDS = 3600          # a parsed /api/about answer
GATE_FAILED_TTL_SECONDS = 60     # a failed about-read is retried soon
GATE_ABOUT_TIMEOUT_SECONDS = 5

_CACHE: dict[str, tuple[float, Optional[bool], str]] = {}   # platform URL -> (expires, carries, version)


def carries_6_4(about: Any) -> tuple[Optional[bool], str]:
    """Whether a platform's /api/about answer shows the 6.4 additions: (True | False | None, version seen).

    None means the answer couldn't be read or parsed: unknown, not "no"."""
    try:
        if isinstance(about, (str, bytes)):
            about = json.loads(about)
        if not isinstance(about, dict):
            return None, ""
        version = str(about.get("version") or "").strip()
        m = re.fullmatch(r"(\d+)\.(\d+)(?:\.(\d+))?(-SNAPSHOT)?", version)
        if not m:
            return None, version
        numbers = tuple(int(g or 0) for g in m.groups()[:3])
        if not m.group(4):                              # a release
            return numbers >= (6, 4, 0), version
        if numbers[:2] > (6, 4):                        # a later line's SNAPSHOT
            return True, version
        if numbers[:2] < (6, 4):                        # an earlier line's SNAPSHOT
            return False, version
        built = about.get("time")                       # a 6.4 SNAPSHOT: built after the merge?
        if not built:
            return None, version
        when = datetime.fromisoformat(str(built).replace("Z", "+00:00"))
        cutoff = datetime.fromisoformat(EGERIA_6_4_SNAPSHOT_CUTOFF.replace("Z", "+00:00"))
        if when.tzinfo is None:
            return None, version
        return when >= cutoff, f"{version} built {built}"
    except Exception:  # noqa: BLE001 -- an unreadable answer is unknown, never "no"
        return None, ""


def needs_6_4_words(what: str, platform_url: str = "", version: str = "") -> str:
    """The one sentence every 6.4 refusal uses.

    With a version (read from /api/about), the request was never sent. Without one, the request was sent and the
    platform answered HTTP 404 (it doesn't serve the request), so the words say that instead."""
    where = f"the platform at {platform_url}" if platform_url else "this platform"
    lead = f"{what} needs Egeria 6.4 (odpi/egeria#9463, process variables and decisions): {where}"
    if version:
        return f"{lead} runs Egeria {version}. Nothing was sent to Egeria."
    return f"{lead} does not serve this request (HTTP 404), so nothing was changed."


def is_missing_6_4_endpoint(exc: BaseException) -> bool:
    """A bare HTTP 404 on a 6.4 request: the endpoint isn't served (an Egeria before 6.4).

    Egeria's own "element not found" comes back as HTTP 200 with relatedHTTPCode 404 and is a
    PyegeriaNotFoundException; only the transport-level 404 (a PyegeriaClientException) means the URL is unknown."""
    from pyegeria.core._exceptions import PyegeriaClientException
    return isinstance(exc, PyegeriaClientException) and getattr(exc, "http_status_code", None) == 404


def _about_reader(client: Any):
    reader = getattr(client, "async_get_platform_origin", None)
    if reader is None:
        for sub in ("classification_manager", "metadata_expert"):
            inner = getattr(client, sub, None)
            reader = getattr(inner, "async_get_platform_origin", None) if inner is not None else None
            if reader is not None:
                break
    return reader


async def async_egeria_6_4_status(client: Any) -> tuple[Optional[bool], str, str]:
    """(carries the 6.4 additions: True | False | None, the version seen, the platform URL). Never raises."""
    url = getattr(client, "platform_url", None)
    if not isinstance(url, str) or not url:
        return None, "", ""
    hit = _CACHE.get(url)
    if hit is not None and hit[0] > time.monotonic():
        return hit[1], hit[2], url
    about = None
    try:
        reader = _about_reader(client)
        if reader is not None:
            import asyncio
            about = await asyncio.wait_for(reader(), timeout=GATE_ABOUT_TIMEOUT_SECONDS)
    except Exception as e:  # noqa: BLE001 -- a failed about-read is "unknown"
        logger.debug(f"Egeria 6.4 gate: could not read {url}/api/about: {e}")
    carries, version = carries_6_4(about) if about else (None, "")
    ttl = GATE_TTL_SECONDS if about else GATE_FAILED_TTL_SECONDS
    _CACHE[url] = (time.monotonic() + ttl, carries, version)
    return carries, version, url


def clear_cache() -> None:
    """Forget every platform's answer (tests; a platform upgraded in place)."""
    _CACHE.clear()
