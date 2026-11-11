"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Consumer-folder trees held in Egeria: one walk, shared by report specs and dashboard sheets.

The convention (report-spec consumer folders, phases 1-2; dashboard folders, LD-1):

    <root>                                  a RootCollection, e.g. RootCollection::ReportSpecs
      <prefix><Consumer>                    one CollectionFolder per consuming tool, e.g.
        <prefix><Consumer>::<Sub> ...       ReportSpecFolder::Consumer::Portal; sub-folders allowed
          members                           what the tree publishes (ReportSpec, Dashboard, ...)

A walk goes DOWN inside one consumer folder: CollectionFolder members are followed (cycle-safe: a GUID
is read once; depth-capped), and it never goes up to a RootCollection or across into a sibling
consumer folder. "Unread is not empty": a folder whose members could not be read is named with its
reason, never treated as a folder with no members.

Parametrised by the root's qualified name, the consumer prefix, and (optionally) a member predicate
choosing which non-folder members count.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

__all__ = [
    "DEPTH_CAP",
    "Walk",
    "consumer_name",
    "find_folder",
    "is_consumer_qn",
    "is_folder",
    "is_gone_error",
    "is_top_consumer_qn",
    "read_consumer_tree",
    "walk_folder",
]

DEPTH_CAP = 5

MemberPredicate = Callable[[Dict[str, Any]], bool]
#: Given a member, its consumer's name and the notes list: the key it is indexed under, or None to
#: leave it out (append a note to say why, when the reader should know).
MemberKey = Callable[[Dict[str, Any], str, List[str]], Optional[str]]


# ── Element shapes ──

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _header(el: Dict[str, Any]) -> Dict[str, Any]:
    return el.get("elementHeader") or {}


def _guid(el: Dict[str, Any]) -> str:
    return _header(el).get("guid") or ""


def _type_names(el: Dict[str, Any]) -> List[str]:
    t = _header(el).get("type") or {}
    return [t.get("typeName") or ""] + list(t.get("superTypeNames") or [])


def _props(el: Dict[str, Any]) -> Dict[str, Any]:
    return el.get("properties") or {}


def _elements(result: Any) -> List[Dict[str, Any]]:
    if isinstance(result, dict):
        result = [result]
    if not isinstance(result, list):
        return []
    return [e for e in result if isinstance(e, dict)]


def _call(fn, *args, **kwargs):
    """Call a client method; an Egeria 'nothing found' string becomes an empty list."""
    result = fn(*args, **kwargs)
    return _elements(result)


def client_identity(client) -> str:
    return str(getattr(client, "user_id", "") or "?")


# ── Names ──

def is_consumer_qn(qn: str, prefix: str) -> bool:
    """A consumer folder or a folder inside one (its qualified name starts with `prefix`)."""
    return bool(qn) and qn.startswith(prefix) and len(qn) > len(prefix)


def is_top_consumer_qn(qn: str, prefix: str) -> bool:
    """A consumer folder itself (`<prefix><Name>`), not a sub-folder."""
    return is_consumer_qn(qn, prefix) and "::" not in qn[len(prefix):]


def consumer_name(el: Dict[str, Any], prefix: str) -> str:
    """A consumer folder's name: its displayName, else the qualified name after the prefix."""
    props = _props(el)
    qn = props.get("qualifiedName") or ""
    tail = qn[len(prefix):] if is_consumer_qn(qn, prefix) else qn
    return props.get("displayName") or tail or _guid(el)


def is_folder(el: Dict[str, Any]) -> bool:
    return "CollectionFolder" in _type_names(el)


# ── Reads ──

def find_folder(client, qn: str) -> Optional[Dict[str, Any]]:
    """The CollectionFolder whose qualified name is exactly `qn`, or None."""
    found = _call(client.get_collections_by_name, qn, metadata_element_type="CollectionFolder",
                  output_format="JSON")
    exact = [e for e in found if _props(e).get("qualifiedName") == qn]
    return exact[0] if exact else None


def is_gone_error(exc: BaseException) -> bool:
    """A read refused because the element is not visible to the caller, or not found: the folder is
    gone for this reader. Anything else (timeout, 5xx, refused connection) is a genuine error."""
    try:
        from pyegeria.view.dashboard_resolver import (
            _is_not_found_error,
            is_not_visible_error,
        )
        return bool(is_not_visible_error(exc) or _is_not_found_error(exc))
    except Exception:  # noqa: BLE001 -- if the classifiers cannot load, keep what was read (the safe side)
        return False


@dataclass
class Walk:
    """What a walk of one folder (and, when recursive, the folders inside it) found."""
    members: List[Dict[str, Any]] = field(default_factory=list)  # every non-folder member, once per GUID
    read: List[str] = field(default_factory=list)              # folders read, "Top / Sub" paths
    capped: List[str] = field(default_factory=list)            # sub-folders the depth cap stopped
    not_followed: List[Tuple[str, str]] = field(default_factory=list)
    errors: List[Tuple[str, str]] = field(default_factory=list)  # sub-folders whose members could not be read
    gone: List[Tuple[str, str]] = field(default_factory=list)    # sub-folders not visible or not found
    #: Every non-folder member's folder paths, by GUID: where in the tree each was found.
    paths: Dict[str, List[str]] = field(default_factory=dict)


def walk_folder(client, folder: Dict[str, Any], *, recursive: bool, consumer_prefix: str,
                depth_cap: int = DEPTH_CAP, stop_qns: Iterable[str] = (),
                member: Optional[MemberPredicate] = None) -> Walk:
    """Read `folder`'s members; when `recursive`, follow CollectionFolder members downwards.

    Only CollectionFolder members are followed. A GUID is read at most once (the cycle guard); a
    folder deeper than `depth_cap` below `folder` is not read and is named in `capped`. A member
    that is a RootCollection, a consumer folder (under `consumer_prefix`) other than this one, or a
    qualified name in `stop_qns` is never followed: the walk goes down inside one consumer, never up
    to the root or across into a sibling. `member`, when given, chooses which non-folder members
    count. The top folder's members are read without a guard, so an error there raises to the
    caller; an error in a sub-folder is recorded in `errors` (or `gone`, when the folder is not
    visible to the reader or no longer exists)."""
    top_qn = _props(folder).get("qualifiedName") or _guid(folder)
    stops = set(stop_qns) - {top_qn}
    w = Walk()
    seen = {_guid(folder)}
    member_guids: set = set()
    queue: List[Tuple[Dict[str, Any], int, str]] = [(folder, 0, top_qn)]
    while queue:
        current, depth, path = queue.pop(0)
        if depth == 0:
            listed = _call(client.get_collection_members, collection_guid=_guid(current), output_format="JSON")
        else:
            try:
                listed = _call(client.get_collection_members, collection_guid=_guid(current),
                               output_format="JSON")
            except Exception as exc:  # noqa: BLE001
                if is_gone_error(exc):
                    # Not visible (zoned away from the reader) or deleted: what it held is no longer
                    # published through this folder, so it is pruned, never kept as "unread".
                    w.gone.append((path, str(exc)))
                else:  # a genuine error (timeout, 5xx): an outage must not unpublish the consumer
                    w.errors.append((path, str(exc)))
                continue
        w.read.append(path)
        for m in listed:
            g = _guid(m)
            if not g:
                continue
            is_root = "RootCollection" in _type_names(m)
            if not (recursive and (is_folder(m) or is_root)):
                if member is not None and not member(m):
                    continue
                w.paths.setdefault(g, [])
                if path not in w.paths[g]:
                    w.paths[g].append(path)
                if g not in member_guids:
                    member_guids.add(g)
                    w.members.append(m)
                continue
            qn = _props(m).get("qualifiedName") or g
            sub_path = f"{path} / {qn}"
            if is_root:
                w.not_followed.append((sub_path, "a RootCollection; the walk never goes up to the root"))
            elif g in seen:
                w.not_followed.append((sub_path, "already read (a cycle, or a second path to the same folder)"))
            elif qn in stops or (is_top_consumer_qn(qn, consumer_prefix) and qn != top_qn):
                w.not_followed.append((sub_path, "another consumer folder; the walk never goes across"))
            elif depth + 1 > depth_cap:
                w.capped.append(sub_path)
            else:
                seen.add(g)
                queue.append((m, depth + 1, sub_path))
    return w


def _not_read(out: Dict[str, Any], reason: str) -> Dict[str, Any]:
    out.update(status="not read", reason=reason, consumers=[], index={})
    return out


def read_consumer_tree(client, *, root_qn: str, consumer_prefix: str, key: MemberKey, fmt: str,
                       depth_cap: int = DEPTH_CAP, member: Optional[MemberPredicate] = None,
                       count_field: str = "members") -> Dict[str, Any]:
    """Read a consumer-folder tree once and return `{key: [consumer, ...]}` with how it was read.

    The root is a RootCollection; each CollectionFolder member is one consumer, named by its
    displayName. Each consumer folder is walked recursively (cycle-safe, `depth_cap`, never into a
    sibling). `key` turns a member into the key it is indexed under (or None to leave it out).

    `status` is "read"; "partial" (some consumer folders were not fully read: `reason` and each
    consumer's own `status` say which); or "not read" (the root itself could not be read: `index`
    is empty and must never be shown as "used by none"). `consumers` lists every consumer folder,
    read or not, so a reader can claim "used by none" only against a fully read tree. Each consumer
    entry carries `count_field`: how many keys it holds."""
    identity = client_identity(client)
    out: Dict[str, Any] = {"format": fmt, "root": root_qn, "read_at": _now(), "read_as": identity,
                           "status": "read", "reason": None, "consumers": [], "index": {}, "notes": []}
    try:
        found = _call(client.get_collections_by_name, root_qn, metadata_element_type="RootCollection",
                      output_format="JSON")
    except Exception as exc:  # noqa: BLE001
        return _not_read(out, f"the root {root_qn} could not be read: {exc}")
    roots = [e for e in found if _props(e).get("qualifiedName") == root_qn]
    if not roots:
        return _not_read(out, f"the root {root_qn} was not found, or is not visible to {identity}")
    try:
        listed = _call(client.get_collection_members, collection_guid=_guid(roots[0]), output_format="JSON")
    except Exception as exc:  # noqa: BLE001
        return _not_read(out, f"the members of the root {root_qn} could not be read: {exc}")
    folders = [m for m in listed if is_folder(m)]
    out["notes"].extend(f"{_props(m).get('qualifiedName') or _guid(m)}: a member of the root that is not a "
                        f"CollectionFolder, so not a consumer" for m in listed if not is_folder(m))
    stop = [_props(f).get("qualifiedName") or "" for f in folders] + [root_qn]
    index: Dict[str, List[str]] = {}
    unread: List[str] = []
    for f in sorted(folders, key=lambda el: consumer_name(el, consumer_prefix)):
        name = consumer_name(f, consumer_prefix)
        entry = {"name": name, "qualifiedName": _props(f).get("qualifiedName"), "guid": _guid(f),
                 "status": "read", "reason": None, count_field: 0}
        out["consumers"].append(entry)
        try:
            walk = walk_folder(client, f, recursive=True, consumer_prefix=consumer_prefix, depth_cap=depth_cap,
                               stop_qns=stop, member=member)
        except Exception as exc:  # noqa: BLE001
            entry.update(status="not read", reason=str(exc))
            unread.append(name)
            continue
        problems = [f"{p}: {e}" for p, e in walk.errors]
        out["notes"].extend(f"{name}: {p} not visible or not found" for p, _e in walk.gone)
        if walk.capped:
            problems.append(f"depth cap reached ({depth_cap} levels); not read: " + ", ".join(walk.capped))
        if problems:
            entry.update(status="partial", reason="; ".join(problems))
            unread.append(name)
        keys = set()
        for m in walk.members:
            k = key(m, name, out["notes"])
            if k:
                keys.add(k)
        for k in keys:
            index.setdefault(k, []).append(name)
        entry[count_field] = len(keys)
    out["index"] = {k: sorted(v) for k, v in sorted(index.items())}
    if unread:
        out.update(status="partial", reason="not fully read: " + ", ".join(unread))
    return out
