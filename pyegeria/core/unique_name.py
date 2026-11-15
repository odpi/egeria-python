"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

"Which element has this qualified name?" answered by Egeria's exact unique-name read, three ways.

A qualified name is unique in Egeria, and Egeria answers it server-side and exactly
(classification-explorer ``elements/by-unique-name`` -> getMetadataElementByUniqueName): no client paging, so
neither a filtered page nor the B5 null-mid-set can make it read as "absent". A paged ``get_*_by_name`` search
(findMetadataElements underneath, NULL_NOT_END before odpi/egeria #9453) must never decide create-versus-reuse
or "not found" for an exact qualified name (the exists-lookups / publish ruling; MyEgeria read-back R2).

- found: the element (of ``type_name``, when given);
- absent: Egeria's specific not-found (``NO_ELEMENTS_FOUND`` or ``PyegeriaNotFoundException``), or an element of
  another type holds the name (``wrong_type``: then no element of ``type_name`` can hold it). wrong_type ->
  absent is right for READERS only: a write guard must REFUSE on wrong_type, because Egeria rejects a second
  element with the same qualified name;
- unknown: any other answer or error. A write guard refuses on unknown and writes nothing; a reader says it
  couldn't tell (``words``), never "not found".
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pyegeria.core._exceptions import PyegeriaNotFoundException
from pyegeria.core._globals import NO_ELEMENTS_FOUND

ANSWERS = ("found", "absent", "unknown")


@dataclass(frozen=True)
class UniqueName:
    answer: str
    qualified_name: str
    element: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
    wrong_type: Optional[str] = None   # absent because an element of this other type holds the name

    @property
    def found(self) -> bool:
        return self.answer == "found"

    @property
    def guid(self) -> str:
        return str(((self.element or {}).get("elementHeader") or {}).get("guid") or "")

    def words(self, what: str) -> str:
        if self.answer == "found":
            return f"{what} {self.qualified_name}: found"
        if self.answer == "absent":
            held = f" (a {self.wrong_type} holds that qualified name)" if self.wrong_type else ""
            return f"{what} {self.qualified_name}: not found{held}"
        return (f"Couldn't tell whether Egeria holds {what} {self.qualified_name}: "
                f"{self.reason or 'no clear answer'}")


class UniqueNameUnknown(RuntimeError):
    """Raised by readers that turn "unknown" into an error (never into "not found"); the message is the words."""

    def __init__(self, found: UniqueName, what: str):
        super().__init__(found.words(what))
        self.found = found


def type_names(element: Dict[str, Any]) -> List[str]:
    t = (element.get("elementHeader") or {}).get("type") or {}
    return [n for n in (t.get("typeName"), *(t.get("superTypeNames") or [])) if n]


def _element_of(result: Any) -> Optional[Dict[str, Any]]:
    if isinstance(result, dict) and result.get("elementHeader"):
        return result
    if isinstance(result, dict) and isinstance(result.get("element"), dict):
        return result["element"]
    return None


def answer_for(result: Any, qualified_name: str, type_name: Optional[str] = None) -> UniqueName:
    """Classify what the unique-name read returned."""
    if result == NO_ELEMENTS_FOUND:
        return UniqueName("absent", qualified_name)
    element = _element_of(result)
    if element is None or not (element.get("elementHeader") or {}).get("guid"):
        return UniqueName("unknown", qualified_name, reason="Egeria's answer wasn't an element or 'not found'")
    if type_name and type_name not in type_names(element):
        held = (type_names(element) or ["different element"])[0]
        return UniqueName("absent", qualified_name, element, wrong_type=held)
    return UniqueName("found", qualified_name, element)


def answer_for_error(exc: BaseException, qualified_name: str) -> UniqueName:
    """Classify an error from the unique-name read: only Egeria's specific not-found is "absent"."""
    if isinstance(exc, PyegeriaNotFoundException):
        return UniqueName("absent", qualified_name)
    try:
        detail = " ".join(str(exc).split())[:200]
    except Exception:  # noqa: BLE001 -- an exception that can't say itself still has a class name
        detail = ""
    return UniqueName("unknown", qualified_name,
                      reason=f"the unique-name read failed: {type(exc).__name__}" + (f": {detail}" if detail else ""))


def _text(value: Any) -> Optional[str]:
    return (value.strip() or None) if isinstance(value, str) else None


def _caller_token(client: Any) -> Optional[str]:
    """The caller's own bearer token, bare (``get_token`` may return the "Bearer ..." header value), or None."""
    try:
        token = _text(client.get_token())
    except Exception:  # noqa: BLE001 -- no Authorization header: the caller holds no token
        return None
    if token and token.lower().startswith("bearer "):
        token = _text(token[7:])
    return token


@dataclass
class _Read:
    """How to make the unique-name read: `fn`, plus the explorer built for it (closed after), or `unknown`."""
    fn: Any = None
    explorer: Any = None
    unknown: Optional[str] = None


def _reader(client: Any, name: str) -> _Read:
    """The unique-name read on `client`, its classification_manager, or a ClassificationExplorer made on the
    same platform AS THE SAME CALLER (CollectionManager has no unique-name read of its own; READBACK U1):

    - the caller's token, built with ``user_pwd=NO_PASSWORD``: the explorer never holds the settings default
      password, so a 401 auto-retry can't sign in again with it (C2);
    - with no token, ``carried_password(client)``: the password the caller holds, or its NO_PASSWORD opt-out
      (then, with no token either, unknown); never a settings default;
    - with neither, or no real ``view_server``/``platform_url`` strings (a fake, a non-client): unknown, with no
      client built and no call to Egeria.
    """
    fn = getattr(client, name, None)
    if callable(fn):
        return _Read(fn)
    sub = getattr(client, "classification_manager", None)
    fn = getattr(sub, name, None) if sub is not None else None
    if callable(fn):
        return _Read(fn)
    view_server = _text(getattr(client, "view_server", None))
    platform_url = _text(getattr(client, "platform_url", None))
    if not (view_server and platform_url):
        return _Read(unknown="the caller isn't a client on an Egeria platform, so no unique-name read was made")
    from pyegeria.core._helper_client import bare_token, helper_client, helper_password
    from pyegeria.core._no_password import NO_PASSWORD
    token = bare_token(client)
    user_id = _text(getattr(client, "user_id", None))
    if not token:
        password = helper_password(client, None)
        if not (user_id and password is not NO_PASSWORD and _text(password)):
            return _Read(unknown="the caller holds neither a token nor its own password, so no unique-name read "
                                 "was made")
    from pyegeria.omvs.classification_explorer import ClassificationExplorer
    explorer = helper_client(ClassificationExplorer, client, view_server=view_server)   # C3: the one helper
    return _Read(getattr(explorer, name), explorer)


def _close(explorer: Any) -> None:
    try:
        explorer.close_session()
    except Exception:  # noqa: BLE001 -- closing is best-effort; the answer stands
        pass


async def _async_close(explorer: Any) -> None:
    try:
        await explorer._async_close_session()
    except Exception:  # noqa: BLE001 -- closing is best-effort; the answer stands
        pass


def by_unique_name(client: Any, qualified_name: str, type_name: Optional[str] = None) -> UniqueName:
    """Egeria's exact unique-name read of `qualified_name` (optionally of `type_name` or a subtype). Never raises:
    an error is "unknown" (or "absent" for Egeria's specific not-found)."""
    try:
        read = _reader(client, "get_element_by_unique_name")
    except Exception as exc:  # noqa: BLE001 -- couldn't even build the read: unknown, never absent
        return UniqueName("unknown", qualified_name, reason=f"the unique-name read failed: {type(exc).__name__}")
    if read.unknown:
        return UniqueName("unknown", qualified_name, reason=read.unknown)
    try:
        result = read.fn(qualified_name)
    except Exception as exc:  # noqa: BLE001 -- only Egeria's specific not-found is "absent"
        return answer_for_error(exc, qualified_name)
    finally:
        if read.explorer is not None:
            _close(read.explorer)
    return answer_for(result, qualified_name, type_name)


async def async_by_unique_name(client: Any, qualified_name: str, type_name: Optional[str] = None) -> UniqueName:
    """``by_unique_name`` for async code."""
    try:
        read = _reader(client, "_async_get_element_by_unique_name")
    except Exception as exc:  # noqa: BLE001 -- couldn't even build the read: unknown, never absent
        return UniqueName("unknown", qualified_name, reason=f"the unique-name read failed: {type(exc).__name__}")
    if read.unknown:
        return UniqueName("unknown", qualified_name, reason=read.unknown)
    try:
        result = await read.fn(qualified_name)
    except Exception as exc:  # noqa: BLE001 -- only Egeria's specific not-found is "absent"
        return answer_for_error(exc, qualified_name)
    finally:
        if read.explorer is not None:
            await _async_close(read.explorer)
    return answer_for(result, qualified_name, type_name)


def element_by_unique_name(client: Any, qualified_name: str, type_name: Optional[str] = None,
                           what: str = "the element") -> Optional[Dict[str, Any]]:
    """For a reader: the element, None when Egeria says there is none (of `type_name`), and
    UniqueNameUnknown (never None) when it can't tell."""
    found = by_unique_name(client, qualified_name, type_name)
    if found.answer == "unknown":
        raise UniqueNameUnknown(found, what)
    return found.element if found.found else None
