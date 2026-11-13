# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""The authoring API as MCP tools (D5: MCP first). Plain functions, registered by pyegeria's MCP server.

**Identity.** Every Egeria read and write acts as the user: the MCP client passes an as-user credential,
`as_user={"user_id": ..., "token": <the user's Egeria bearer token>}`. The server's own (service)
credentials are never used for authoring:
- read-only tools work without a credential where they can (new draft, diff, validate without Egeria
  checks, publish plan); a tool that must read Egeria (preview, history, a held prototype) needs one;
- `authoring_apply` needs one, plus `confirmed=True` and the plan's digest, and refuses otherwise, in words.

**Drafts** live in a local DraftStore (D16) keyed by the caller's user id, under the directory the server
is configured with (`PYEGERIA_AUTHORING_DRAFTS_DIR`, default `~/.pyegeria/authoring-drafts`).
"""
from __future__ import annotations

import os
from typing import Any, Callable, Dict, List, Optional

from pyegeria.authoring import diff as _diff
from pyegeria.authoring.drafts import LocalDraftStore, async_new_from, new_draft
from pyegeria.authoring.lifecycle import apply, async_history, async_load_held, publish_plan, withdraw_plan
from pyegeria.authoring.models import AuthoringRefused, as_draft, draft_key
from pyegeria.authoring.preview import async_preview
from pyegeria.authoring.runner import inprocess_runner
from pyegeria.authoring.serialize import serialize
from pyegeria.authoring.validate import async_validate

DRAFTS_DIR_ENV = "PYEGERIA_AUTHORING_DRAFTS_DIR"
NEEDS_USER = ("{what} acts as you: pass as_user={{'user_id': ..., 'token': <your Egeria bearer token>}}. "
              "This server never authors with its own service credentials.")
SERVICE_REFUSED = ("{user} is this server's own service account; authoring runs only as the person asking. "
                   "Pass your own credential in as_user.")


def _store() -> LocalDraftStore:
    return LocalDraftStore(os.environ.get(DRAFTS_DIR_ENV) or "~/.pyegeria/authoring-drafts")


def _service_user() -> Optional[str]:
    try:
        from pyegeria.core.config import settings
        return settings.User_Profile.user_name
    except Exception:  # noqa: BLE001
        return None


def _default_client(user_id: str, token: str) -> Any:
    from pyegeria.core.config import settings
    from pyegeria.egeria_tech_client import EgeriaTech
    return EgeriaTech(settings.Environment.egeria_view_server, settings.Environment.egeria_view_server_url,
                      user_id=user_id, token=token)


#: Builds a client from an as-user credential; tests replace it.
CLIENT_FACTORY: Callable[[str, str], Any] = _default_client


def user_client(as_user: Optional[Dict[str, Any]], what: str, *, required: bool = True) -> Any:
    """A client signed in as the caller, from their credential; None (or a refusal) without one."""
    if not as_user or not as_user.get("user_id") or not as_user.get("token"):
        if required:
            raise AuthoringRefused(NEEDS_USER.format(what=what))
        return None
    user_id = str(as_user["user_id"])
    if user_id == _service_user():
        raise AuthoringRefused(SERVICE_REFUSED.format(user=user_id))
    return CLIENT_FACTORY(user_id, str(as_user["token"]))


def _owner(user_id: Optional[str], as_user: Optional[Dict[str, Any]]) -> str:
    owner = (as_user or {}).get("user_id") or user_id
    if not owner:
        raise AuthoringRefused("Drafts are kept per user: give user_id (or as_user).")
    return str(owner)


def _draft(owner: str, kind: Optional[str], name: Optional[str], draft: Optional[Dict[str, Any]]):
    if draft is not None:
        return as_draft(draft)
    if not (kind and name):
        raise AuthoringRefused("Name a saved draft (kind and name) or pass the draft itself.")
    found = _store().load(owner, kind, name)
    if found is None:
        raise AuthoringRefused(f"You have no saved {kind} draft named {name!r}.")
    return found


def _ok(**out: Any) -> Dict[str, Any]:
    return {"ok": True, **out}


def _refusal(exc: Exception) -> Dict[str, Any]:
    return {"ok": False, "refused": str(exc)}


def _guard(fn):
    import functools
    import inspect

    if inspect.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def wrapped(*args, **kwargs):
            try:
                return await fn(*args, **kwargs)
            except (AuthoringRefused, ValueError) as exc:
                return _refusal(exc)
        return wrapped

    @functools.wraps(fn)
    def wrapped_sync(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (AuthoringRefused, ValueError) as exc:
            return _refusal(exc)
    return wrapped_sync


# ── Read-only tools ──────────────────────────────────────────────────────────

@_guard
def authoring_new_draft(kind: str, fields: Dict[str, Any], user_id: Optional[str] = None,
                        as_user: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make a draft (kind: spec, report or sheet) and keep it in your drafts. Nothing is written to Egeria."""
    owner = _owner(user_id, as_user)
    draft = new_draft(kind, **fields)
    _store().save(owner, draft)
    return _ok(draft=draft.model_dump(mode="json"), markdown=serialize(draft))


@_guard
async def authoring_new_from(new_label: str, prototype_kind: Optional[str] = None,
                             prototype_label: Optional[str] = None, template: Optional[str] = None,
                             user_id: Optional[str] = None, as_user: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Copy a prototype (a spec from pyegeria's registry, or a held Report or sheet, read as you) or a
    template into a new draft named new_label. Nothing is written to Egeria."""
    owner = _owner(user_id, as_user)
    prototype = (prototype_kind, prototype_label) if prototype_kind else None
    client = None
    if prototype and prototype_kind in ("report", "sheet"):
        client = user_client(as_user, f"Copying a held {prototype_kind}")
    draft = await async_new_from(prototype=prototype, template=template, new_label=new_label, client=client)
    _store().save(owner, draft)
    return _ok(draft=draft.model_dump(mode="json"), markdown=serialize(draft))


@_guard
async def authoring_validate(kind: Optional[str] = None, name: Optional[str] = None,
                             draft: Optional[Dict[str, Any]] = None, user_id: Optional[str] = None,
                             as_user: Optional[Dict[str, Any]] = None, dr_egeria: bool = False) -> Dict[str, Any]:
    """Validate a draft: structure, meaning (as you, if you pass as_user), and Dr.Egeria's validate (with
    dr_egeria=True and as_user). What wasn't checked is listed in not_checked."""
    owner = _owner(user_id, as_user)
    d = _draft(owner, kind, name, draft)
    client = user_client(as_user, "Validating against Egeria", required=dr_egeria)
    result = await async_validate(d, client, run=inprocess_runner(client) if (dr_egeria and client) else None)
    return _ok(validation=result.model_dump())


@_guard
async def authoring_preview(kind: Optional[str] = None, name: Optional[str] = None,
                            draft: Optional[Dict[str, Any]] = None, max_rows: int = 25,
                            user_id: Optional[str] = None, as_user: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run a draft as you and show a capped sample. Nothing is registered or cached."""
    owner = _owner(user_id, as_user)
    d = _draft(owner, kind, name, draft)
    client = user_client(as_user, "Preview")
    return _ok(preview=await async_preview(d, client=client, max_rows=max_rows))


@_guard
def authoring_diff(a: Dict[str, Any], b: Dict[str, Any], user_id: Optional[str] = None,
                   as_user: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Compare two drafts of one kind. a and b are each {"kind", "name"} (a saved draft) or a draft."""
    owner = _owner(user_id, as_user)

    def one(x):
        return _draft(owner, x.get("kind"), x.get("name"), None) if set(x) <= {"kind", "name"} else as_draft(x)
    return _ok(diff=_diff.diff(one(a), one(b)).summary())


@_guard
async def authoring_history(kind: str, label: str, as_user: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The versions Egeria holds of a published spec, Report or sheet, read as you."""
    client = user_client(as_user, "Reading history")
    return _ok(history=await async_history(kind, label, client))


@_guard
def authoring_publish_plan(kind: Optional[str] = None, name: Optional[str] = None,
                           draft: Optional[Dict[str, Any]] = None, folders: Optional[List[str]] = None,
                           visibility: str = "public", withdraw: bool = False, user_id: Optional[str] = None,
                           as_user: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The document that would publish (or, with withdraw=True, withdraw) a draft, its digest and its steps
    in words. Nothing runs: apply it with authoring_apply."""
    owner = _owner(user_id, as_user)
    if withdraw:
        return _ok(plan=withdraw_plan(kind, name, folders=folders or []))
    d = _draft(owner, kind, name, draft)
    return _ok(plan=publish_plan(d, folders=folders or [], visibility=visibility))


# ── The write tool ───────────────────────────────────────────────────────────

@_guard
def authoring_apply(step: str, confirmed: bool = False, digest: Optional[str] = None,
                    kind: Optional[str] = None, name: Optional[str] = None, draft: Optional[Dict[str, Any]] = None,
                    folders: Optional[List[str]] = None, visibility: str = "public", withdraw: bool = False,
                    user_id: Optional[str] = None, as_user: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run one step of a publish/withdraw plan as you: validate, or process. The plan is rebuilt from the
    draft now; process is refused unless confirmed=True and digest is the one you previewed."""
    if step not in ("validate", "process"):
        raise AuthoringRefused("authoring_apply runs 'validate' or 'process'; preview with authoring_publish_plan.")
    client = user_client(as_user, "Publishing")
    if step == "process" and not confirmed:
        raise AuthoringRefused("Confirm first: the document runs as you, and writes to Egeria (confirmed=True).")
    if step == "process" and not digest:
        raise AuthoringRefused("Give the digest of the plan you previewed (authoring_publish_plan).")
    owner = _owner(user_id, as_user)
    if withdraw:
        plan = withdraw_plan(kind, name, folders=folders or [])
    else:
        plan = publish_plan(_draft(owner, kind, name, draft), folders=folders or [], visibility=visibility)
    return _ok(result=apply(plan, step=step, run=inprocess_runner(client), confirmed=confirmed, digest=digest))


READ_ONLY_TOOLS = (authoring_new_draft, authoring_new_from, authoring_validate, authoring_preview, authoring_diff,
                   authoring_history, authoring_publish_plan)
WRITE_TOOLS = (authoring_apply,)


def register(srv: Any) -> None:
    """Register the authoring tools on an MCP server (`srv.tool(name=...)`)."""
    for fn in READ_ONLY_TOOLS + WRITE_TOOLS:
        srv.tool(name=fn.__name__)(fn)
