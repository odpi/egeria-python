"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Role supply (RS-W2-3; report-spec pipeline model §7): the executor builds a routine's call from
the inputs the routine DECLARES, asking a `RoleSupply` for each one. It never reads parameter
names to decide what to pass.

A routine declares its inputs as role words (`analytic_registry.INPUT_ROLES`):

  - ``egeria_client:<Class>`` -> ``supply.client(<Class>)``: a client whose methods the routine calls
  - ``reader:<name>``         -> ``supply.reader(<name>)``: a reader the environment owns
  - ``viewer``                -> ``supply.viewer()``: who is looking (identity words)
  - ``subject``               -> ``supply.subject()``: the resource in view

The inputs are bound to the routine's leading positional parameters in declared order (each
input's position is its index in ``inputs``); declared parameters follow by name.

Every input is obtained before the routine's first stage runs, so a role the environment cannot
provide refuses the run before anything is called, in the environment's own words
(`RoleSupply.refusal_words`). Each environment provides its own supply: `PlainSupply` (here) is
plain pyegeria's and supplies the caller's Egeria client only; the Portal and Resource Explorer
provide theirs.

Wave 2 boundary: `PlainSupply.client(cls)` hands back the caller's `EgeriaTech` itself for
EgeriaTech and for every class it proxies to, never a separate subclient, so behaviour is
byte-identical with the name-introspecting executor it replaces. Handing out per-class clients,
and the call indirection around them, are Wave 3.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Protocol, Sequence, runtime_checkable

__all__ = [
    "RoleRefused",
    "NoSuchReader",
    "CallerTokenExpired",
    "Viewer",
    "Subject",
    "RoleSupply",
    "PlainSupply",
    "egeria_tech_classes",
    "role_kind",
    "supply_inputs",
]


class RoleRefused(ValueError):
    """A declared input the environment cannot supply. Raised before any stage runs. `words` is
    the whole sentence a person is shown; `role` the input that could not be supplied."""

    def __init__(self, words: str, *, role: str = "", routine: str = "", reason: str = ""):
        super().__init__(words)
        self.words = words
        self.role = role
        self.routine = routine
        self.reason = reason or words


class NoSuchReader(RoleRefused):
    """The environment has no reader of the declared name."""


class CallerTokenExpired(RoleRefused):
    """The environment cannot mint or refresh a client for the caller (e.g. an expired token).
    Raised by an environment's supply; plain pyegeria never raises it."""


@dataclass(frozen=True)
class Viewer:
    """Who is looking. A field the environment does not know is None, never a guessed value."""
    user_id: str
    is_admin: Optional[bool] = None
    display_name: Optional[str] = None


@dataclass(frozen=True)
class Subject:
    """The resource in view."""
    guid: str
    type_name: Optional[str] = None
    display_name: Optional[str] = None


@runtime_checkable
class RoleSupply(Protocol):
    """What an environment supplies a routine. Each method returns the role or raises
    `RoleRefused` (or a subclass) whose words say why, in the environment's own terms."""

    def client(self, cls: type) -> Any: ...

    def viewer(self) -> Viewer: ...

    def reader(self, source: str) -> Any: ...

    def subject(self) -> Optional[Subject]: ...

    def refusal_words(self, kind: str) -> str: ...


# ── EgeriaTech and the classes it proxies to ──

_EGERIA_TECH_CLASSES: Optional[List[type]] = None


def egeria_tech_classes() -> List[type]:
    """EgeriaTech plus every subclient class it proxies to (its `__getattr__` looks there).
    The resolver and `PlainSupply` both read this list, so "a class EgeriaTech serves" means the
    same thing at load and at run."""
    global _EGERIA_TECH_CLASSES
    if _EGERIA_TECH_CLASSES is None:
        from pyegeria.egeria_tech_client import EgeriaTech
        # Construction sets attributes only; nothing connects.
        probe = EgeriaTech("role-supply", "https://localhost:9443", user_id="role-supply", user_pwd="")
        _EGERIA_TECH_CLASSES = [EgeriaTech] + list(dict.fromkeys(probe._subclient_map.values()))
    return _EGERIA_TECH_CLASSES


def _client_class(name: str) -> Optional[type]:
    return next((c for c in egeria_tech_classes() if c.__name__ == name), None)


# ── Plain pyegeria's supply ──

_PLAIN_WORDS = {
    "egeria_client": "Plain pyegeria supplies one Egeria client, the caller's EgeriaTech, for EgeriaTech "
                     "and the clients it proxies to; it supplies no other client class.",
    "reader": "Plain pyegeria supplies no readers; run this routine where its reader is supplied "
              "(Resource Explorer or the Portal).",
    "viewer": "Plain pyegeria does not know who is viewing; run this routine where the viewer is supplied "
              "(Resource Explorer or the Portal).",
    "subject": "Plain pyegeria has no resource in view; run this routine where a subject is supplied "
               "(Resource Explorer or the Portal).",
}


class PlainSupply:
    """Plain pyegeria's supply: the caller's EgeriaTech, nothing else.

    Give it the client (`egeria_client`) or a factory that builds an authenticated one
    (`client_factory`, called at most once, on the first `client()` request, so a routine that
    declares no client never connects or mints a token, ISSUE-137).

    `client(cls)` returns that one EgeriaTech when `cls` is EgeriaTech or a class EgeriaTech
    proxies to (Wave 2: byte-identical, no subclients), or when the client already is a `cls`.
    Any other class, and every reader, viewer and subject, is refused with `refusal_words`."""

    def __init__(self, egeria_client: Any = None, *, client_factory: Optional[Callable[[], Any]] = None):
        self._client = egeria_client
        self._factory = client_factory

    def _the_client(self) -> Any:
        if self._client is None:
            if self._factory is None:
                raise RoleRefused("no Egeria client was given to plain pyegeria's supply", role="egeria_client")
            self._client = self._factory()
        return self._client

    def client(self, cls: type) -> Any:
        if cls in egeria_tech_classes():
            return self._the_client()
        if self._client is not None and isinstance(self._client, cls):
            return self._client
        raise RoleRefused(f"no {getattr(cls, '__name__', cls)} client: " + self.refusal_words("egeria_client"),
                          role=f"egeria_client:{getattr(cls, '__name__', cls)}")

    def viewer(self) -> Viewer:
        raise RoleRefused(self.refusal_words("viewer"), role="viewer")

    def reader(self, source: str) -> Any:
        raise NoSuchReader(f"no reader '{source}': " + self.refusal_words("reader"), role=f"reader:{source}")

    def subject(self) -> Optional[Subject]:
        return None

    def refusal_words(self, kind: str) -> str:
        return _PLAIN_WORDS.get(kind, f"Plain pyegeria does not supply '{kind}'.")


# ── Supplying a routine's declared inputs ──

def role_kind(role: str) -> str:
    """The role word without its qualifier: egeria_client, reader, viewer or subject."""
    return role.split(":", 1)[0]


def supply_inputs(routine: str, inputs: Sequence[str], supply: RoleSupply) -> List[Any]:
    """The positional arguments for a routine's declared `inputs`, in declared order, each asked of
    `supply`. Every input is obtained before this returns, so a role the supply cannot provide
    raises `RoleRefused` before the routine's first stage runs. The words name the routine, the
    input and the environment's reason."""
    args: List[Any] = []
    for role in inputs:
        kind, _, qualifier = role.partition(":")
        try:
            if kind == "egeria_client":
                cls = _client_class(qualifier)
                if cls is None:
                    raise RoleRefused(f"no client class named {qualifier} is known to pyegeria: "
                                      + supply.refusal_words("egeria_client"), role=role)
                value = supply.client(cls)
            elif kind == "reader":
                value = supply.reader(qualifier)
            elif kind == "viewer":
                value = supply.viewer()
            elif kind == "subject":
                value = supply.subject()
                if value is None:
                    raise RoleRefused(supply.refusal_words("subject"), role=role)
            else:
                raise RoleRefused(f"'{role}' is not a role word", role=role)
        except RoleRefused as exc:
            reason = f"its declared input '{role}' is not supplied ({exc.words})"
            raise type(exc)(f"Routine '{routine}' cannot run: {reason}", role=role, routine=routine,
                            reason=reason) from exc
        args.append(value)
    return args
