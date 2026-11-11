"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Report specs held in Egeria, run from pyegeria: the EGERIA registry tier, its cache, the sync and
fetch-on-call (report-spec pipeline model §7a, §8f; RS-EGERIA-TIER stage 1).

**Execution never goes through Egeria on a run.** The registry's EGERIA tier is a local cache,
filled by `sync_report_specs` from configured `CollectionFolder`s (or single specs), and read
offline. Egeria is read again only when a caller asks, with `refresh_spec=True`.

Cache layout (`cache_dir()`; never under the user report specs directory)::

    ~/.pyegeria/cache/report_specs/<platform host_port>/<view server>/
        manifest.json                       written LAST; the tier loads only what it lists
        <safe-label>-<guid8>.v<N>.json      the spec: envelope + canonical microflow/1
        <same>.provenance.json              guid, qualifiedName, versions, folders, sync identity
        .sync.lock                          one writer at a time (flock, non-blocking)
        drafts/                             DRAFT/PROPOSED specs (--include-drafts); read only
                                            when PYEGERIA_REPORT_SPEC_DRAFTS=1

The spec file name carries the header version so an interrupted sync never overwrites a file the
previous manifest still names: the previous complete set stays in force until the new manifest
replaces it, and files it no longer names are deleted after that.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse

from loguru import logger

from pyegeria.view import egeria_folders as _folders
from pyegeria.view.egeria_folders import _call, _elements, _guid, _header, _props, _type_names

__all__ = [
    "CACHE_DIR_ENV",
    "FOLDERS_ENV",
    "DRAFTS_ENV",
    "SyncReport",
    "SyncAlreadyRunning",
    "SpecFetchError",
    "cache_dir",
    "configured_folders",
    "configured_root",
    "sync_report_specs",
    "refresh_consumer_index",
    "read_consumer_index",
    "build_consumer_index",
    "list_visible_restricted_specs",
    "RESTRICTED_FORMAT",
    "CONSUMER_PREFIX",
    "DEFAULT_ROOT",
    "DEPTH_CAP",
    "ROOT_ENV",
    "fetch_spec_for_call",
    "async_fetch_spec_for_call",
    "egeria_tier",
    "egeria_tier_info",
    "spec_footer",
    "fetched_spec",
    "fetched_spec_source",
    "split_tier_prefix",
    "label_from_qualified_name",
]

CACHE_DIR_ENV = "PYEGERIA_REPORT_SPEC_CACHE_DIR"
FOLDERS_ENV = "PYEGERIA_REPORT_SPEC_FOLDERS"
DRAFTS_ENV = "PYEGERIA_REPORT_SPEC_DRAFTS"
MANIFEST = "manifest.json"
LOCK = ".sync.lock"
DRAFTS_DIR = "drafts"
MANIFEST_FORMAT = "pyegeria-report-spec-cache/1"
_QN_MARKERS = ("ReportSpec::", "ReportType::")
_ACTIVE = "ACTIVE"
_DRAFT_STATUSES = ("DRAFT", "PROPOSED")
_RELOAD_INTERVAL_S = 1.0
# Consumer folders (report-spec consumer folders, phases 1-2): a RootCollection whose members are
# one CollectionFolder per consuming tool. A tool syncs its own consumer folder; sub-folders inside
# it are followed (cycle-safe, depth-capped); the root and sibling consumers are never walked into.
ROOT_ENV = "PYEGERIA_REPORT_SPEC_ROOT"
DEFAULT_ROOT = "RootCollection::ReportSpecs"
CONSUMER_PREFIX = "ReportSpecFolder::Consumer::"
DEPTH_CAP = 5
CONSUMERS = "consumers.json"
CONSUMERS_FORMAT = "pyegeria-report-spec-consumers/1"

#: Tier prefixes accepted wherever a spec name is (§7a "Resolution order"). `seed:` is stage 2's
#: name for `builtin:`; both are accepted now.
TIER_PREFIXES = {"egeria": "egeria", "builtin": "builtin", "seed": "builtin"}
_FETCHED_SUFFIX = re.compile(r"^(?P<label>.+)@v(?P<version>\d+)$")


class SyncAlreadyRunning(RuntimeError):
    """Another process holds this cache's sync lock."""


class SpecFetchError(RuntimeError):
    """A fetch-on-call could not produce a runnable spec. Never falls back to the cached copy."""


# ── Names and prefixes ──

def split_tier_prefix(name: Any) -> Tuple[Optional[str], Any]:
    """`"egeria:E-Collections"` -> `("egeria", "E-Collections")`; `"seed:X"` -> `("builtin", "X")`;
    anything else -> `(None, name)`."""
    if isinstance(name, str) and ":" in name:
        head, rest = name.split(":", 1)
        tier = TIER_PREFIXES.get(head.strip().lower())
        if tier and rest and not rest.startswith(":"):
            return tier, rest
    return None, name


def label_from_qualified_name(qn: str) -> Optional[str]:
    """The label a ReportSpec/ReportType qualified name carries: the text after the marker, after
    any local-qualifier prefix ("CocoPharma::ReportSpec::X" -> "X"). None if neither marker."""
    if not isinstance(qn, str):
        return None
    for marker in _QN_MARKERS:
        if marker in qn:
            return qn.split(marker, 1)[1] or None
    return None


def _safe(label: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", label)[:80] or "spec"


# ── Where the cache is ──

def _settings_env():
    try:
        from pyegeria.core.config import settings
        return settings.Environment
    except Exception:  # noqa: BLE001 -- settings may not load in every context
        return None


def _host_port(url: Optional[str]) -> str:
    if not url:
        return "unknown-platform"
    parsed = urlparse(url if "//" in url else f"//{url}")
    host = parsed.hostname or "unknown-host"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    return _safe(f"{host}_{port}")


def _user_specs_dir() -> Path:
    from pyegeria.view.base_report_formats import _user_report_specs_dir
    return Path(_user_report_specs_dir()).expanduser().resolve()


def cache_dir(platform_url: Optional[str] = None, view_server: Optional[str] = None,
              override: Optional[str] = None) -> Path:
    """The cache directory: `override`, else `PYEGERIA_REPORT_SPEC_CACHE_DIR`, else
    `~/.pyegeria/cache/report_specs/<platform host_port>/<view server>/`. Raises ValueError if it
    is the user report specs directory or inside it (cached specs must never be read as CONFIG)."""
    chosen = override or os.getenv(CACHE_DIR_ENV)
    if chosen:
        path = Path(chosen).expanduser()
    else:
        env = _settings_env()
        platform_url = platform_url or (getattr(env, "egeria_view_server_url", None) if env else None)
        view_server = view_server or (getattr(env, "egeria_view_server", None) if env else None)
        path = (Path("~/.pyegeria/cache/report_specs").expanduser() / _host_port(platform_url)
                / _safe(view_server or "unknown-view-server"))
    resolved = path.resolve()
    user_dir = _user_specs_dir()
    if resolved == user_dir or user_dir in resolved.parents:
        raise ValueError(f"The report spec cache directory {resolved} is inside the user report specs directory "
                         f"{user_dir}; cached specs must never be readable as user (CONFIG) specs. Set "
                         f"{CACHE_DIR_ENV} elsewhere.")
    return resolved


def configured_folders() -> List[str]:
    """The folders a plain sync takes (O-H5): `PYEGERIA_REPORT_SPEC_FOLDERS` (comma-separated
    qualified names), else config.json's "Pyegeria Report Spec Folders". Empty by default."""
    env_val = os.getenv(FOLDERS_ENV)
    if env_val is not None:
        return [p.strip() for p in env_val.split(",") if p.strip()]
    env = _settings_env()
    return list(getattr(env, "pyegeria_report_spec_folders", None) or []) if env else []


def configured_root() -> str:
    """The root of the consumer-folder tree: `PYEGERIA_REPORT_SPEC_ROOT`, else
    `RootCollection::ReportSpecs`."""
    return (os.getenv(ROOT_ENV) or "").strip() or DEFAULT_ROOT


def _is_consumer_qn(qn: str) -> bool:
    """A consumer folder or a folder inside one (its qualified name starts with the prefix)."""
    return _folders.is_consumer_qn(qn, CONSUMER_PREFIX)


def _is_top_consumer_qn(qn: str) -> bool:
    """A consumer folder itself (`ReportSpecFolder::Consumer::<Name>`), not a sub-folder."""
    return _folders.is_top_consumer_qn(qn, CONSUMER_PREFIX)


# ── Files ──

def _atomic_write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", suffix=".json", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=2, ensure_ascii=False, sort_keys=False)
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp, 0o644)  # mkstemp makes 0600; a shared cache is read by other processes
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _write_manifest(directory: Path, manifest: Dict[str, Any]) -> None:
    """Separate so a test can simulate a crash just before the manifest is written."""
    _atomic_write_json(directory / MANIFEST, manifest)


def _read_json(path: Path) -> Optional[Any]:
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _read_manifest(directory: Path) -> Dict[str, Any]:
    data = _read_json(directory / MANIFEST)
    if not isinstance(data, dict) or not isinstance(data.get("entries"), dict):
        return {"format": MANIFEST_FORMAT, "shared": False, "entries": {}, "skipped": []}
    return data


def _prune_unnamed(directory: Path, manifest: Dict[str, Any]) -> None:
    keep = {MANIFEST, CONSUMERS}
    for entry in manifest.get("entries", {}).values():
        keep.add(entry.get("file", ""))
        keep.add(entry.get("provenance", ""))
    for p in directory.iterdir():
        if p.is_file() and p.suffix == ".json" and p.name not in keep:
            try:
                p.unlink()
            except OSError as exc:
                logger.debug(f"report spec cache: could not delete {p}: {exc}")


class _SyncLock:
    """An exclusive, non-blocking lock on `<cache>/.sync.lock`. Readers never take it."""

    def __init__(self, directory: Path):
        self.path = directory / LOCK
        self.fh = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.fh = open(self.path, "a+", encoding="utf-8")
        try:
            import fcntl
            fcntl.flock(self.fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (BlockingIOError, PermissionError):
            self.fh.seek(0)
            pid = self.fh.read().strip() or "unknown"
            self.fh.close()
            self.fh = None
            raise SyncAlreadyRunning(f"a sync is already running (pid {pid}) for {self.path.parent}")
        except ImportError:  # no fcntl (Windows): best effort, no exclusion
            logger.debug("report spec cache: fcntl unavailable, sync lock is advisory only")
        self.fh.seek(0)
        self.fh.truncate()
        self.fh.write(str(os.getpid()))
        self.fh.flush()
        return self

    def __exit__(self, *exc):
        if self.fh is not None:
            try:
                self.fh.seek(0)
                self.fh.truncate()
                self.fh.flush()
            finally:
                self.fh.close()  # closing releases the flock
                self.fh = None
        return False


# ── One Egeria element -> a cache entry (or a skip reason) ──

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _version(el: Dict[str, Any]) -> int:
    v = (_header(el).get("versions") or {}).get("version")
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def _zones(el: Dict[str, Any]) -> List[str]:
    """The governance zones on an element. In Egeria 6.2 ZoneMembership is its own header key
    (`elementHeader.zoneMembership.classificationProperties.zoneMembership`), not an entry of
    `elementHeader.classifications`; both places are read, so a list-only check never reports
    "no zones" for a zoned element."""
    header = _header(el)
    found: List[str] = []
    candidates = [header.get("zoneMembership")] + [c for c in (header.get("classifications") or [])
                                                   if isinstance(c, dict)
                                                   and c.get("classificationName") == "ZoneMembership"]
    for c in candidates:
        if not isinstance(c, dict):
            continue
        z = (c.get("classificationProperties") or {}).get("zoneMembership")
        if isinstance(z, str):
            z = [z]
        found.extend(str(v) for v in (z or []) if v)
    return sorted(set(found))


ZONED_REASON = "zoned: not synced into a shared cache (until B6's public-only read)"


@dataclass
class _Built:
    label: str
    guid: str
    envelope: Dict[str, Any]
    provenance: Dict[str, Any]
    format_set: Any
    stored_format: int
    status: str
    notes: List[str] = field(default_factory=list)


class _Skip(Exception):
    def __init__(self, who: str, reason: str):
        super().__init__(reason)
        self.who = who
        self.reason = reason


def _identify(el: Dict[str, Any]) -> Tuple[str, str]:
    """(label, qualifiedName) of a ReportSpec element, or raise _Skip (not a ReportSpec, label
    mismatch)."""
    props = _props(el)
    qn = props.get("qualifiedName") or ""
    who = qn or _guid(el) or "?"
    names = _type_names(el)
    if "ReportSpec" not in names:
        raise _Skip(who, f"not a ReportSpec (it is a {names[0] or 'element of unknown type'})")
    label = label_from_qualified_name(qn)
    display = props.get("displayName")
    if label is None:
        raise _Skip(who, "label mismatch: the qualified name has neither 'ReportSpec::' nor 'ReportType::'")
    if display != label:
        raise _Skip(who, f"label mismatch: displayName {display!r} is not the qualified name's label {label!r}")
    return label, qn


def _annotations(props: Dict[str, Any], label: str, notes: List[str]) -> Dict[str, List[str]]:
    """The envelope's `annotations` (for example wikilinks). ReportSpec has no typed property for them
    yet, so stage 1 reads `additionalProperties["annotations"]`, a JSON object of string lists. A
    value that is not that is ignored, with a note."""
    raw = (props.get("additionalProperties") or {}).get("annotations")
    if raw in (None, ""):
        return {}
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
        if isinstance(data, dict) and all(isinstance(v, list) and all(isinstance(i, str) for i in v)
                                           for v in data.values()):
            return {str(k): list(v) for k, v in data.items()}
    except ValueError:
        pass
    notes.append("additionalProperties.annotations is not a JSON object of string lists; ignored")
    return {}


def _status(el: Dict[str, Any], notes: List[str]) -> str:
    status = _props(el).get("contentStatus")
    if not status:
        notes.append("the element has no contentStatus; counted as ACTIVE")
        return _ACTIVE
    return str(status).upper()


def _build(el: Dict[str, Any], *, folders: List[str], identity: str, registry_names: Optional[set] = None
           ) -> _Built:
    """Convert, check and resolve one full ReportSpec element. Raise _Skip with the reason."""
    from pyegeria.view.microflow import (AllowlistRefusal, CannotRunYet, MicroflowError, check_allowlist,
                                         microflow_to_format_set, parse_microflow)
    from pyegeria.view.spec_resolver import Unrunnable, resolve

    label, qn = _identify(el)
    props = _props(el)
    notes: List[str] = []
    status = _status(el, notes)
    try:
        mf, stored_format, parse_notes = parse_microflow(props.get("microflow"))
    except MicroflowError as exc:
        raise _Skip(label, str(exc))
    notes.extend(parse_notes)
    if stored_format == 0:
        logger.warning(f"Report spec '{label}' ({qn}) stores a format-0 micro-flow (a bare list); read as "
                       f"microflow/1. Update it with Dr.Egeria to store microflow/1.")
        notes.append("stored as format 0 (a bare list), converted to microflow/1 on read")
    try:
        check_allowlist(mf)
    except AllowlistRefusal as exc:
        raise _Skip(label, f"refused by the allowlist: {exc}")
    annotations = _annotations(props, label, notes)
    envelope = {
        "label": label,
        "heading": props.get("purpose") or label,
        "description": props.get("description") or "",
        "family": props.get("category"),
        "target_type_name": props.get("targetTypeName"),
        "aliases": list(props.get("aliases") or []),
        "output_types": list(props.get("outputTypes") or []),
        "include_preamble": props.get("includePreamble"),
        "annotations": annotations,
        "microflow": json.loads(mf.to_json()),
    }
    try:
        fs = microflow_to_format_set(mf, label=label, heading=envelope["heading"],
                                     description=envelope["description"],
                                     target_type=envelope["target_type_name"], aliases=envelope["aliases"],
                                     family=envelope["family"], annotations=annotations, notes=notes)
    except CannotRunYet as exc:
        raise _Skip(label, str(exc))
    except MicroflowError as exc:
        raise _Skip(label, str(exc))
    result = resolve(fs, label, registry_names=registry_names if registry_names is not None else _known_names())
    if isinstance(result, Unrunnable):
        raise _Skip(label, f"refused by load-time resolution: {result.unrunnable_reason}")
    versions = _header(el).get("versions") or {}
    provenance = {
        "guid": _guid(el),
        "qualified_name": qn,
        "version_identifier": props.get("versionIdentifier"),
        "header_version": _version(el),
        "update_time": versions.get("updateTime"),
        "content_status": status,
        "fetched_at": _now(),
        "folders": list(folders),
        "sync_identity": identity,
        "stored_format": stored_format,
        "notes": notes,
    }
    return _Built(label=label, guid=_guid(el), envelope=envelope, provenance=provenance, format_set=fs,
                  stored_format=stored_format, status=status, notes=notes)


def _known_names() -> set:
    """Spec names a detail_spec may name, without building the full registry (which reads this tier)."""
    from pyegeria.view import base_report_formats as brf
    names = set(brf._builtin_tier().keys())
    names |= set(brf._CONFIG_REPORT_FORMATS.keys()) | set(brf._RUNTIME_REPORT_FORMATS.keys())
    names |= set(_TIER.get("specs", {}).keys())
    return names


def _write_entry(directory: Path, built: _Built) -> Dict[str, Any]:
    base = f"{_safe(built.label)}-{built.guid[:8]}.v{built.provenance['header_version']}"
    spec_file, prov_file = f"{base}.json", f"{base}.provenance.json"
    _atomic_write_json(directory / spec_file, built.envelope)
    _atomic_write_json(directory / prov_file, built.provenance)
    return {"file": spec_file, "provenance": prov_file, "guid": built.guid,
            "qualified_name": built.provenance["qualified_name"],
            "version": built.provenance["header_version"],
            "version_identifier": built.provenance["version_identifier"],
            "folders": list(built.provenance["folders"]), "stored_format": built.stored_format,
            "fetched_at": built.provenance["fetched_at"]}


# ── The sync ──

@dataclass
class SyncReport:
    """What a sync did, shaped like `refresh_report_specs()`'s skip list: `skipped` is a list of
    `(label or qualified name, reason)` pairs."""
    cache_dir: str = ""
    folders: List[str] = field(default_factory=list)
    added: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    unchanged: List[str] = field(default_factory=list)
    pruned: List[str] = field(default_factory=list)
    skipped: List[Tuple[str, str]] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    drafts: Optional["SyncReport"] = None
    # Every folder whose members were read, sub-folders as "Top / Sub" paths (recursive sync).
    folders_read: List[str] = field(default_factory=list)
    # Sub-folders not read because the depth cap stopped the walk ("depth cap reached").
    depth_cap_reached: List[str] = field(default_factory=list)
    # The consumer index refreshed by this sync: {"status", "reason", "consumers", "labels"}, or
    # None when this sync did not refresh it (a --spec sync, or index_consumers=False).
    consumers: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        out = {k: getattr(self, k) for k in ("cache_dir", "folders", "added", "updated", "unchanged", "pruned",
                                             "notes", "folders_read", "depth_cap_reached", "consumers")}
        out["skipped"] = [list(s) for s in self.skipped]
        if self.drafts is not None:
            out["drafts"] = self.drafts.to_dict()
        return out

    def render(self) -> str:
        lines = [f"Report spec cache: {self.cache_dir}"]
        lines.append(f"Folders: {', '.join(self.folders) if self.folders else '(none)'}")
        if self.folders_read and self.folders_read != self.folders:
            lines.append(f"Folders read ({len(self.folders_read)}): {', '.join(self.folders_read)}")
        if self.depth_cap_reached:
            lines.append(f"Depth cap reached, not read: {', '.join(self.depth_cap_reached)}")
        for name in ("added", "updated", "unchanged", "pruned"):
            vals = getattr(self, name)
            lines.append(f"{name.capitalize()} ({len(vals)}): {', '.join(vals) if vals else '-'}")
        lines.append(f"Skipped ({len(self.skipped)}):" + ("" if self.skipped else " -"))
        lines.extend(f"  - {who}: {why}" for who, why in self.skipped)
        lines.extend(f"Note: {n}" for n in self.notes)
        if self.consumers is not None:
            c = self.consumers
            if c.get("status") == "not read":
                lines.append(f"Consumers: not read ({c.get('reason')})")
            else:
                extra = f"; {c.get('reason')}" if c.get("reason") else ""
                lines.append(f"Consumers: {c.get('status')} ({c.get('consumers')} consumer folders, "
                             f"{c.get('labels')} specs{extra})")
        if self.drafts is not None:
            lines.append("Drafts cache:")
            lines.extend("  " + ln for ln in self.drafts.render().splitlines())
        return "\n".join(lines)


def _find_folder(client, qn: str) -> Optional[Dict[str, Any]]:
    return _folders.find_folder(client, qn)


def _find_specs_by_label(client, label: str) -> List[Dict[str, Any]]:
    """Every ReportSpec element whose label is `label`, under either qualified-name marker."""
    seen: Dict[str, Dict[str, Any]] = {}
    for name in (label, f"ReportSpec::{label}", f"ReportType::{label}"):
        try:
            found = _call(client.get_collections_by_name, name, metadata_element_type="ReportSpec",
                          output_format="JSON")
        except Exception as exc:  # noqa: BLE001 -- one failing lookup must not hide the others
            logger.debug(f"report spec lookup by name {name!r} failed: {exc}")
            continue
        for e in found:
            if label_from_qualified_name(_props(e).get("qualifiedName") or "") == label and _guid(e):
                seen[_guid(e)] = e
    return list(seen.values())


def _get_full(client, guid: str) -> Optional[Dict[str, Any]]:
    found = _call(client.get_collection_by_guid, guid, output_format="JSON")
    return found[0] if found else None


def _client_identity(client) -> str:
    return _folders.client_identity(client)


_is_folder = _folders.is_folder
_Walk = _folders.Walk
_is_gone_error = _folders.is_gone_error


def _walk_folder(client, folder: Dict[str, Any], *, recursive: bool, depth_cap: int = DEPTH_CAP,
                 stop_qns: Iterable[str] = ()) -> _Walk:
    """The shared walk (`egeria_folders.walk_folder`) over report-spec consumer folders."""
    return _folders.walk_folder(client, folder, recursive=recursive, consumer_prefix=CONSUMER_PREFIX,
                                depth_cap=depth_cap, stop_qns=stop_qns)


def sync_report_specs(client, *, folders: Optional[Iterable[str]] = None, specs: Optional[Iterable[str]] = None,
                      include_drafts: bool = False, cache_dir: Optional[str] = None,
                      shared: Optional[bool] = None, recursive: Optional[bool] = None,
                      depth_cap: int = DEPTH_CAP, index_consumers: bool = True) -> SyncReport:
    """Sync report specs held in Egeria into the local cache (§7a "Sync").

    - `folders`: CollectionFolder qualified names. Default: `configured_folders()` (O-H5); never
      "every ReportSpec visible". Empty -> nothing is synced, and the report says so.
    - `specs`: labels to sync on their own. Only those labels change; nothing else is pruned.
    - Incremental: each folder's members are listed (guid + header version); only new specs, or
      specs with a higher header version, are fetched in full. Specs no longer a member of any
      synced folder, or gone from Egeria, are pruned and named.
    - `include_drafts`: DRAFT and PROPOSED specs go to the separate `drafts/` cache.
    - `shared`: mark the cache shared (a fetch-on-call never writes a shared cache). Default:
      keep what the manifest says (False for a new cache). A shared cache never takes a spec that
      carries a governance zone (report-spec consumer folders §9, until B6's public-only read): it
      is skipped as "zoned: not synced into a shared cache", and a cached copy is pruned.
    - `recursive`: follow CollectionFolder members of each folder (cycle-safe, at most `depth_cap`
      levels below it; never up to the root nor across into a sibling consumer folder). Default
      (None): on for consumer folders (`ReportSpecFolder::Consumer::...`), off for any other folder.
      A spec found in a sub-folder is recorded against the folder that was named. The report lists
      `folders_read`, and `depth_cap_reached` names any sub-folder the cap stopped.
    - `index_consumers`: after a folder sync, refresh the consumer index (`refresh_consumer_index`)
      in the same cache directory; `report.consumers` says whether the root was read. Its failure
      never fails the sync.
    - One bad spec never fails the sync; it is skipped with its reason. A second sync of the same
      cache while one runs raises `SyncAlreadyRunning` at once.
    """
    directory = _resolve_cache_dir(client, cache_dir)
    report = SyncReport(cache_dir=str(directory))
    spec_labels = [s for s in (specs or []) if s]
    folder_qns = list(folders) if folders is not None else ([] if spec_labels else configured_folders())
    report.folders = folder_qns
    if not folder_qns and not spec_labels:
        report.notes.append(f"no report spec folders are configured (set {FOLDERS_ENV} or config.json's "
                            f"\"Pyegeria Report Spec Folders\", or pass --folder/--spec); nothing synced")
        return report
    with _SyncLock(directory):
        identity = _client_identity(client)
        # Gather candidates: guid -> (member element, [folders])
        members: Dict[str, Tuple[Dict[str, Any], List[str]]] = {}
        unread_folders: set = set()  # read failed: keep what they held, never prune on an error
        for qn in folder_qns:
            try:
                folder = _find_folder(client, qn)
            except Exception as exc:  # noqa: BLE001
                report.skipped.append((qn, f"the folder could not be read, so its specs are kept as cached: {exc}"))
                unread_folders.add(qn)
                continue
            if folder is None:
                report.skipped.append((qn, f"folder not found, or not visible to {identity}"))
                continue
            walk_recursive = _is_consumer_qn(qn) if recursive is None else bool(recursive)
            try:
                walk = _walk_folder(client, folder, recursive=walk_recursive, depth_cap=depth_cap,
                                    stop_qns=folder_qns)
            except Exception as exc:  # noqa: BLE001
                report.skipped.append((qn, f"the folder's members could not be read, so its specs are kept as "
                                           f"cached: {exc}"))
                unread_folders.add(qn)
                continue
            report.folders_read.extend(walk.read)
            report.depth_cap_reached.extend(walk.capped)
            if walk.capped:
                # Not read is not "no longer a member": keep what the folder held, prune nothing.
                unread_folders.add(qn)
                report.notes.append(f"{qn}: depth cap reached ({depth_cap} levels below it); not read, so its "
                                    f"cached specs are kept: " + ", ".join(walk.capped))
            report.notes.extend(f"{path}: not followed, {why}" for path, why in walk.not_followed)
            report.notes.extend(f"{path}: not visible or not found, so its specs are no longer published through "
                                f"{qn}: {why}" for path, why in walk.gone)
            if walk.errors:
                unread_folders.add(qn)
                report.skipped.extend((path, f"the sub-folder's members could not be read, so {qn}'s specs are "
                                             f"kept as cached: {why}") for path, why in walk.errors)
            for m in walk.members:
                g = _guid(m)
                if g in members:
                    if qn not in members[g][1]:
                        members[g][1].append(qn)
                else:
                    members[g] = (m, [qn])
        pinned_lookups: Dict[str, List[Dict[str, Any]]] = {}
        for label in spec_labels:
            try:
                found = _find_specs_by_label(client, label)
            except Exception as exc:  # noqa: BLE001
                report.skipped.append((label, f"the spec could not be looked up: {exc}"))
                continue
            if not found:
                report.skipped.append((label, f"not found in Egeria, or not visible to {identity}"))
            pinned_lookups[label] = found

        main_dir, drafts_dir = directory, directory / DRAFTS_DIR
        main_old, drafts_old = _read_manifest(main_dir), _read_manifest(drafts_dir)
        main_new = _new_manifest(main_old, identity, shared)
        shared_cache = bool(main_new.get("shared"))  # §9: a shared cache never holds a zoned spec
        drafts_new = _new_manifest(drafts_old, identity, shared)
        drafts_report = SyncReport(cache_dir=str(drafts_dir), folders=folder_qns) if include_drafts else None

        # Identify every candidate; duplicate labels are skipped (both), with both GUIDs.
        candidates: Dict[str, List[Tuple[str, Dict[str, Any], List[str], bool]]] = {}
        visited: set = set()
        for g, (m, fl) in members.items():
            try:
                label, _qn = _identify(m)
            except _Skip as s:
                report.skipped.append((s.who, s.reason))
                continue
            candidates.setdefault(label, []).append((g, m, fl, False))
            visited.add(label)
        for label, found in pinned_lookups.items():
            for e in found:
                g = _guid(e)
                existing = [c for c in candidates.get(label, []) if c[0] == g]
                if existing:
                    continue
                try:
                    _identify(e)
                except _Skip as s:
                    report.skipped.append((s.who, s.reason))
                    continue
                candidates.setdefault(label, []).append((g, e, [], True))
                visited.add(label)
        for label, cands in list(candidates.items()):
            if len({c[0] for c in cands}) > 1:
                report.skipped.append((label, "one label held by two elements: " +
                                       ", ".join(sorted({c[0] for c in cands})) + "; neither is cached"))
                del candidates[label]

        registry_names = _known_names() | set(candidates)
        for label, [(g, m, fl, pinned)] in candidates.items():
            if shared_cache and _zones(m):
                report.skipped.append((label, f"{ZONED_REASON}; zones {', '.join(_zones(m))}"))
                continue
            status_notes: List[str] = []
            status = _status(m, status_notes)
            if status == _ACTIVE:
                target_old, target_new, target_dir, rep = main_old, main_new, main_dir, report
            elif status in _DRAFT_STATUSES and include_drafts:
                target_old, target_new, target_dir, rep = drafts_old, drafts_new, drafts_dir, drafts_report
            else:
                hint = " (pass --include-drafts)" if status in _DRAFT_STATUSES else ""
                report.skipped.append((label, f"contentStatus {status} is not synced{hint}"))
                continue
            rep.notes.extend(f"{label}: {n}" for n in status_notes)
            old = target_old["entries"].get(label)
            folders_now = sorted(set(fl) | (set(old.get("folders", [])) if (old and pinned) else set()))
            version = _version(m)
            if (old and old.get("guid") == g and int(old.get("version", -1)) >= version and version
                    and (target_dir / old.get("file", "")).is_file()):
                entry = dict(old)
                entry["folders"] = folders_now
                entry["pinned"] = bool(old.get("pinned")) or pinned
                target_new["entries"][label] = entry
                rep.unchanged.append(label)
                continue
            try:
                full = _get_full(client, g) or m
                if shared_cache and _zones(full):  # the member listing may not carry the header's zones
                    rep.skipped.append((label, f"{ZONED_REASON}; zones {', '.join(_zones(full))}"))
                    continue
                built = _build(full, folders=folders_now, identity=identity, registry_names=registry_names)
            except _Skip as s:
                rep.skipped.append((s.who, s.reason))
                continue
            except Exception as exc:  # noqa: BLE001 -- one bad spec never fails the sync
                rep.skipped.append((label, f"could not be fetched or converted: {type(exc).__name__}: {exc}"))
                continue
            entry = _write_entry(target_dir, built)
            entry["pinned"] = pinned or bool(old and old.get("pinned"))
            target_new["entries"][label] = entry
            (rep.updated if old else rep.added).append(label)
            rep.notes.extend(f"{label}: {n}" for n in built.notes)

        # Keep, re-check or prune what this sync did not visit.
        for tgt_old, tgt_new, tgt_dir, rep, in_scope in (
                (main_old, main_new, main_dir, report, True),
                (drafts_old, drafts_new, drafts_dir, drafts_report, include_drafts)):
            for label, old in tgt_old["entries"].items():
                if label in tgt_new["entries"]:
                    continue
                if not in_scope or (spec_labels and not folder_qns):
                    tgt_new["entries"][label] = old  # a --spec sync (or drafts left alone) prunes nothing else
                    continue
                if set(old.get("folders", [])) & unread_folders:
                    tgt_new["entries"][label] = old
                    continue
                if label in visited:
                    rep.pruned.append(label)  # seen but skipped this time; the skip names the reason
                    continue
                if old.get("pinned"):
                    try:
                        still = _get_full(client, old.get("guid", ""))
                    except Exception:  # noqa: BLE001
                        still = None
                    if still:
                        tgt_new["entries"][label] = old
                        continue
                    rep.pruned.append(label)
                    rep.notes.append(f"{label}: pruned, its element {old.get('guid')} no longer exists")
                    continue
                rep.pruned.append(label)
                rep.notes.append(f"{label}: pruned, no longer a member of any synced folder")

        main_new["skipped"] = [list(s) for s in report.skipped]
        if include_drafts:
            drafts_new["skipped"] = [list(s) for s in drafts_report.skipped]
            drafts_dir.mkdir(parents=True, exist_ok=True)
            _write_manifest(drafts_dir, drafts_new)
            _prune_unnamed(drafts_dir, drafts_new)
            report.drafts = drafts_report
        main_dir.mkdir(parents=True, exist_ok=True)
        _write_manifest(main_dir, main_new)
        _prune_unnamed(main_dir, main_new)
        if index_consumers and folder_qns:
            try:
                idx = refresh_consumer_index(client, cache_dir=str(main_dir), depth_cap=depth_cap)
            except Exception as exc:  # noqa: BLE001 -- the index never fails the sync
                idx = {"status": "not read", "reason": f"{type(exc).__name__}: {exc}", "consumers": [], "index": {}}
            report.consumers = {"status": idx.get("status"), "reason": idx.get("reason"),
                                "consumers": len(idx.get("consumers") or []), "labels": len(idx.get("index") or {})}
    _invalidate_tier()
    logger.info(f"Report spec sync into {directory}: {len(report.added)} added, {len(report.updated)} updated, "
                f"{len(report.unchanged)} unchanged, {len(report.pruned)} pruned, {len(report.skipped)} skipped")
    return report


def _new_manifest(old: Dict[str, Any], identity: str, shared: Optional[bool]) -> Dict[str, Any]:
    return {"format": MANIFEST_FORMAT,
            "shared": bool(old.get("shared")) if shared is None else bool(shared),
            "sync_identity": identity, "synced_at": _now(), "entries": {}, "skipped": []}


def _resolve_cache_dir(client, override: Optional[str]) -> Path:
    url = getattr(client, "platform_url", None) if client is not None else None
    server = getattr(client, "view_server", None) if client is not None else None
    return cache_dir(url, server, override)


# ── The consumer index: which tools each Egeria-held spec is published to ──

_CONSUMERS_MEMO: Dict[str, Any] = {}


def _spec_label(m: Dict[str, Any], consumer: str, notes: List[str]) -> Optional[str]:
    """A member's spec label for the consumer index; None for what the index leaves out."""
    try:
        label, _qn = _identify(m)
    except _Skip:
        return None  # not a well-formed spec: the sync reports those; the facet ignores them
    if _zones(m):
        # The index is a shared file shown to every viewer: a zoned spec's label stays out (§9).
        notes.append(f"{consumer}: {label}: {ZONED_REASON}")
        return None
    return label


def build_consumer_index(client, *, root: Optional[str] = None, depth_cap: int = DEPTH_CAP) -> Dict[str, Any]:
    """Read the consumer-folder tree once and return `{label: [consumer, ...]}` with how it was read.

    Names and labels only: no spec is fetched in full. The root (`configured_root()`) is a
    RootCollection; each CollectionFolder member is one consumer, named by its displayName. Each
    consumer folder is walked like a recursive sync (cycle-safe, `depth_cap`, never into a sibling).

    `status` is "read"; "partial" (some consumer folders were not fully read: `reason` and each
    consumer's own `status` say which); or "not read" (the root itself could not be read: `index`
    is empty and must never be shown as "used by none"). `consumers` lists every consumer folder,
    read or not, so a reader can claim "used by none" only against a fully read tree."""
    return _folders.read_consumer_tree(client, root_qn=root or configured_root(), consumer_prefix=CONSUMER_PREFIX,
                                       key=_spec_label, fmt=CONSUMERS_FORMAT, depth_cap=depth_cap,
                                       count_field="specs")


RESTRICTED_FORMAT = "pyegeria-restricted-specs/1"


def list_visible_restricted_specs(client_as_user, folders: Optional[Iterable[str]] = None, *,
                                  recursive: Optional[bool] = None, depth_cap: int = DEPTH_CAP) -> Dict[str, Any]:
    """The zone-restricted ReportSpecs one signed-in user can see in the configured folders (B6).

    A shared cache never holds a zoned spec (§9, `ZONED_REASON`), so a tool that shows restricted
    specs reads them per user with this function, **as that user's token**: Egeria enforces the
    zones, so what comes back is exactly what this user may see. Nothing is written to any cache.
    **The caller caches the result per credential identity (the token), never by bare user id**: two
    sessions of one user id can hold different zone grants, and a cache keyed on the id would show
    one session's restricted specs to the other.

    - `folders`: CollectionFolder qualified names; default `configured_folders()`. Consumer folders
      are walked recursively (as `sync_report_specs` does), any other folder reads its direct members,
      unless `recursive` says otherwise.
    - Only ACTIVE ReportSpecs that carry at least one zone are returned: public ones are the shared
      cache's business. The zones come from the full element when the member listing carries none.

    Returns `{"format", "identity", "status", "reason", "specs", "folders", "notes"}`:
    - `specs`: `[{"label", "qualified_name", "guid", "version", "zones", "folders"}]`, sorted by label.
    - `folders`: one `{"folder", "result", "detail", "count"}` per folder, `result` in
      ok | not_found | unreadable | partial. A folder that is not found, or not visible to this user,
      says so; it is never an empty list.
    - `status`: "read" (every folder read), "partial" (some read), or "not read" (none, with `reason`).
      An empty `specs` with status "read" means the folders were read and hold no restricted spec this
      user can see; `reason` then says so in words.
    """
    identity = _client_identity(client_as_user)
    folder_qns = list(folders) if folders is not None else configured_folders()
    out: Dict[str, Any] = {"format": RESTRICTED_FORMAT, "identity": identity, "status": "read", "reason": None,
                           "specs": [], "folders": [], "notes": []}
    if not folder_qns:
        out.update(status="not read", reason=f"no report spec folders are configured (set {FOLDERS_ENV} or "
                                             f"config.json's \"Pyegeria Report Spec Folders\")")
        return out
    found: Dict[str, Dict[str, Any]] = {}       # guid -> spec row
    by_label: Dict[str, set] = {}
    for qn in folder_qns:
        row = {"folder": qn, "result": "ok", "detail": None, "count": 0}
        out["folders"].append(row)
        try:
            folder = _find_folder(client_as_user, qn)
        except Exception as exc:  # noqa: BLE001 -- one folder's failure is stated, never hides the others
            row.update(result="unreadable", detail=f"the folder could not be read: {exc}")
            continue
        if folder is None:
            row.update(result="not_found", detail=f"folder not found, or not visible to {identity}")
            continue
        walk_recursive = _is_consumer_qn(qn) if recursive is None else bool(recursive)
        try:
            walk = _walk_folder(client_as_user, folder, recursive=walk_recursive, depth_cap=depth_cap,
                                stop_qns=folder_qns)
        except Exception as exc:  # noqa: BLE001
            row.update(result="unreadable", detail=f"the folder's members could not be read: {exc}")
            continue
        partial = [f"{p}: depth cap reached ({depth_cap} levels)" for p in walk.capped]
        partial += [f"{p}: could not be read: {why}" for p, why in walk.errors]
        if partial:
            row.update(result="partial", detail="; ".join(partial))
        out["notes"].extend(f"{p}: not visible to {identity}, or not found" for p, _why in walk.gone)
        for m in walk.members:
            g = _guid(m)
            try:
                label, mqn = _identify(m)
            except _Skip:
                continue  # not a ReportSpec: nothing restricted to show
            if g in found:
                if qn not in found[g]["folders"]:
                    found[g]["folders"].append(qn)
                    row["count"] += 1
                continue
            el, zones = m, _zones(m)
            if not zones:
                try:
                    el = _get_full(client_as_user, g) or m
                except Exception as exc:  # noqa: BLE001
                    out["notes"].append(f"{label}: its zones could not be read, so it is not listed: {exc}")
                    continue
                zones = _zones(el)
            if not zones:
                continue  # public: the shared cache holds it
            status = _status(el, [])
            if status != _ACTIVE:
                out["notes"].append(f"{label}: contentStatus {status}, not listed")
                continue
            found[g] = {"label": label, "qualified_name": mqn, "guid": g, "version": _version(el),
                        "zones": zones, "folders": [qn]}
            by_label.setdefault(label, set()).add(g)
            row["count"] += 1
    for label, guids in by_label.items():
        if len(guids) > 1:
            out["notes"].append(f"{label}: one label held by {len(guids)} elements ({', '.join(sorted(guids))}); "
                                f"neither is listed")
            for g in guids:
                found.pop(g, None)
    out["specs"] = sorted(found.values(), key=lambda r: r["label"])
    read = [r for r in out["folders"] if r["result"] in ("ok", "partial")]
    if not read:
        out.update(status="not read", reason="no folder could be read: " +
                   "; ".join(f"{r['folder']}: {r['detail']}" for r in out["folders"]))
    elif len(read) < len(out["folders"]) or any(r["result"] == "partial" for r in read):
        out.update(status="partial", reason="not fully read: " + "; ".join(
            f"{r['folder']}: {r['detail']}" for r in out["folders"] if r["result"] != "ok"))
    elif not out["specs"]:
        out["reason"] = (f"the folders were read as {identity} and hold no zone-restricted report spec "
                         f"visible to {identity}")
    return out


def refresh_consumer_index(client, *, cache_dir: Optional[str] = None, root: Optional[str] = None,
                           depth_cap: int = DEPTH_CAP) -> Dict[str, Any]:
    """Build the consumer index and write it to `consumers.json` in the spec cache directory.
    A "not read" result is written too, with its reason, so a reader never mistakes a failed read
    for an empty tree. Returns what was written."""
    directory = _resolve_cache_dir(client, cache_dir)
    idx = build_consumer_index(client, root=root, depth_cap=depth_cap)
    directory.mkdir(parents=True, exist_ok=True)
    _atomic_write_json(directory / CONSUMERS, idx)
    _CONSUMERS_MEMO.pop(str(directory), None)
    return idx


def read_consumer_index(*, cache_dir: Optional[str] = None, client=None) -> Dict[str, Any]:
    """The consumer index the last sync wrote (`consumers.json`), read offline and memoised on the
    file's mtime. With no index yet, or an unreadable file, the result has `status` "not read" and a
    reason: absence is never returned as an empty index."""
    try:
        directory = _resolve_cache_dir(client, cache_dir)
    except ValueError as exc:
        return {"format": CONSUMERS_FORMAT, "status": "not read", "reason": str(exc), "consumers": [], "index": {}}
    path = directory / CONSUMERS
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return {"format": CONSUMERS_FORMAT, "status": "not read", "consumers": [], "index": {},
                "reason": f"no consumer index in {directory} yet; a report-spec sync writes it"}
    memo = _CONSUMERS_MEMO.get(str(directory))
    if memo and memo[0] == mtime:
        return memo[1]
    data = _read_json(path)
    if not isinstance(data, dict) or data.get("format") != CONSUMERS_FORMAT:
        return {"format": CONSUMERS_FORMAT, "status": "not read", "consumers": [], "index": {},
                "reason": f"{path} is not a consumer index this pyegeria can read"}
    _CONSUMERS_MEMO[str(directory)] = (mtime, data)
    return data


# ── The EGERIA tier: what the registry reads ──

_TIER: Dict[str, Any] = {"key": None, "checked": 0.0, "stamp": None, "specs": {}, "meta": {}, "aliases_dropped": {}}


def _invalidate_tier() -> None:
    _TIER["checked"] = 0.0
    _TIER["stamp"] = None


def _stamp(directory: Path, with_drafts: bool) -> Tuple:
    def mt(p: Path):
        try:
            st = p.stat()
            return (st.st_mtime_ns, st.st_size)
        except OSError:
            return None
    return (mt(directory / MANIFEST), mt(directory / DRAFTS_DIR / MANIFEST) if with_drafts else None)


def _load_dir(directory: Path, tier_label: str, specs, meta: Dict[str, Any], skipped: List[Tuple[str, str]],
              shared: bool) -> None:
    from pyegeria.view.microflow import (AllowlistRefusal, CannotRunYet, MicroflowError, check_allowlist,
                                         microflow_to_format_set, parse_microflow)
    manifest = _read_manifest(directory)
    for label, entry in manifest["entries"].items():
        env = _read_json(directory / entry.get("file", ""))
        if not isinstance(env, dict) or env.get("label") != label:
            skipped.append((label, f"cache file {entry.get('file')} is missing or does not hold '{label}'"))
            continue
        try:
            mf, _fmt, _ = parse_microflow(env.get("microflow"))
            check_allowlist(mf)
            fs = microflow_to_format_set(mf, label=label, heading=env.get("heading"),
                                         description=env.get("description") or "",
                                         target_type=env.get("target_type_name"), aliases=env.get("aliases"),
                                         family=env.get("family"), annotations=env.get("annotations"))
        except (MicroflowError, AllowlistRefusal, CannotRunYet) as exc:
            skipped.append((label, f"cache file no longer loads: {exc}"))
            continue
        specs[label] = fs
        meta[label] = {"tier": "egeria", "label": label, "guid": entry.get("guid"),
                       "version": entry.get("version_identifier"), "header_version": entry.get("version"),
                       "synced_at": manifest.get("synced_at"), "fetched_at": entry.get("fetched_at"),
                       "folders": entry.get("folders", []), "cache": tier_label, "shared": shared,
                       "qualified_name": entry.get("qualified_name")}


def egeria_tier(*, force: bool = False):
    """The EGERIA tier as a FormatSetDict, loaded from the cache manifest(s). Reloaded when a
    manifest changes, checked at most once per second. Never raises: a broken cache is an empty
    tier, logged."""
    from pyegeria.view._output_format_models import FormatSetDict
    with_drafts = os.getenv(DRAFTS_ENV, "").strip().lower() in ("1", "true", "yes")
    env = _settings_env()
    raw_key = (os.getenv(CACHE_DIR_ENV), getattr(env, "egeria_view_server_url", None),
               getattr(env, "egeria_view_server", None), getattr(env, "pyegeria_user_report_specs_dir", None),
               os.getenv("PYEGERIA_USER_REPORT_SPECS_DIR"), os.getenv("PYEGERIA_USER_FORMAT_SETS_DIR"),
               with_drafts)
    now = time.monotonic()
    if not force and _TIER.get("raw_key") == raw_key and now - _TIER["checked"] < _RELOAD_INTERVAL_S:
        return _TIER["specs"]
    try:
        directory = cache_dir()
    except Exception as exc:  # noqa: BLE001
        if _TIER.get("key") != ("error", str(exc)):
            logger.warning(f"Report spec cache unavailable: {exc}")
        _TIER.update(key=("error", str(exc)), raw_key=raw_key, checked=now, specs=FormatSetDict(), meta={})
        return _TIER["specs"]
    key = (str(directory), with_drafts)
    _TIER["raw_key"] = raw_key
    stamp = _stamp(directory, with_drafts)
    _TIER["checked"] = now
    if not force and _TIER.get("key") == key and _TIER.get("stamp") == stamp:
        return _TIER["specs"]
    specs, meta, skipped = FormatSetDict(), {}, []
    if stamp[0] is not None:
        shared = bool(_read_manifest(directory).get("shared"))
        _load_dir(directory, "main", specs, meta, skipped, shared)
    if with_drafts and stamp[1] is not None:
        dspecs, dmeta = FormatSetDict(), {}
        _load_dir(directory / DRAFTS_DIR, "drafts", dspecs, dmeta, skipped, False)
        for label, fs in dspecs.items():
            if label in specs:
                logger.warning(f"Report spec '{label}': the drafts cache copy shadows the active one "
                               f"({DRAFTS_ENV}=1)")
            specs[label] = fs
            meta[label] = dict(dmeta[label], draft=True)
    for who, why in skipped:
        logger.warning(f"Report spec cache {directory}: skipping {who}: {why}")
    _TIER.update(key=key, stamp=stamp, specs=specs, meta=meta, skipped=skipped, dir=str(directory))
    return specs


def egeria_tier_info(label: str) -> Optional[Dict[str, Any]]:
    """Provenance for a label in the EGERIA tier (or a fetched `label@vN`), else None."""
    m = _FETCHED_SUFFIX.match(label or "")
    if m and (m.group("label"), int(m.group("version"))) in _FETCHED:
        return dict(_FETCHED[(m.group("label"), int(m.group("version")))][1])
    egeria_tier()
    info = _TIER.get("meta", {}).get(label)
    return dict(info) if info else None


def tier_cache_age_s(label: str) -> Optional[float]:
    info = egeria_tier_info(label)
    stamp = (info or {}).get("synced_at") or (info or {}).get("fetched_at")
    if not stamp:
        return None
    try:
        then = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return round((datetime.now(timezone.utc) - then).total_seconds(), 1)


def spec_footer(info: Optional[Dict[str, Any]]) -> Optional[str]:
    """The one-line provenance footer for REPORT/MD/HTML output of an Egeria-held spec, for example
    "E-Collections v1.0 (Egeria, synced 20:35Z)". None for local and built-in specs."""
    if not info or info.get("tier") != "egeria":
        return None
    version = f" v{info['version']}" if info.get("version") else ""
    if info.get("fetched"):
        when, verb = info.get("fetched_at"), "fetched"
    else:
        when, verb = info.get("synced_at"), "synced"
    hhmm = ""
    if when and len(when) >= 16:
        hhmm = f" {when[11:16]}Z"
    draft = ", draft" if info.get("draft") else ""
    return f"{info.get('label')}{version} (Egeria{draft}, {verb}{hhmm})"


# ── Fetch on a call (§7a "Fetch on a call") ──

#: Specs fetched with refresh_spec=True, kept for the life of the process, keyed by (label, header
#: version). Addressed internally as "egeria:<label>@v<version>".
_FETCHED: Dict[Tuple[str, int], Tuple[Any, Dict[str, Any]]] = {}


def fetched_spec(name: str):
    """The FormatSet for an internal "<label>@v<N>" name, or None."""
    m = _FETCHED_SUFFIX.match(name or "")
    if not m:
        return None
    hit = _FETCHED.get((m.group("label"), int(m.group("version"))))
    return hit[0] if hit else None


def fetched_spec_source(name: str) -> Optional[Dict[str, Any]]:
    """The provenance of a spec fetched this process ("<label>@v<N>", with or without "egeria:"), or None:
    tier, label, guid, version, header_version, fetched_at, fetched, shared, qualified_name."""
    _tier, rest = split_tier_prefix(name)
    m = _FETCHED_SUFFIX.match(rest or "") if isinstance(rest, str) else None
    if not m:
        return None
    hit = _FETCHED.get((m.group("label"), int(m.group("version"))))
    return dict(hit[1]) if hit else None


def _fetch_target(name: str) -> str:
    tier, label = split_tier_prefix(name)
    if tier == "builtin":
        raise SpecFetchError(f"refresh_spec=True fetches a spec from Egeria; '{name}' names the built-in tier")
    if not isinstance(label, str) or not label:
        raise SpecFetchError(f"refresh_spec=True needs a report spec name, not {name!r}")
    return label


def _finish_fetch(directory: Path, el: Dict[str, Any], label: str, identity: str) -> str:
    try:
        built = _build(el, folders=[], identity=identity)
    except _Skip as s:
        raise SpecFetchError(f"Report spec '{label}' was fetched from Egeria but cannot be used: {s.reason}")
    if built.label != label:
        raise SpecFetchError(f"Report spec '{label}': Egeria returned '{built.label}' instead")
    if built.status != _ACTIVE:
        raise SpecFetchError(f"Report spec '{label}' in Egeria has contentStatus {built.status}; only ACTIVE "
                             f"specs are run")
    manifest = _read_manifest(directory)
    shared = bool(manifest.get("shared"))
    version = built.provenance["header_version"]
    info = {"tier": "egeria", "label": label, "guid": built.guid,
            "version": built.provenance["version_identifier"], "header_version": version,
            "fetched_at": built.provenance["fetched_at"], "fetched": True, "shared": shared,
            "qualified_name": built.provenance["qualified_name"]}
    _FETCHED[(label, version)] = (built.format_set, info)
    if shared:
        logger.info(f"Report spec '{label}' v{version} fetched from Egeria; the cache {directory} is shared, so "
                    f"the copy is kept in this process only")
    else:
        try:
            with _SyncLock(directory):
                old = manifest["entries"].get(label) or {}
                built.provenance["folders"] = list(old.get("folders", []))
                entry = _write_entry(directory, built)
                entry["pinned"] = bool(old.get("pinned")) or not old.get("folders")
                manifest["entries"][label] = entry
                manifest.setdefault("format", MANIFEST_FORMAT)
                manifest["synced_at"] = manifest.get("synced_at") or _now()
                _write_manifest(directory, manifest)
                _prune_unnamed(directory, manifest)
            _invalidate_tier()
        except SyncAlreadyRunning as exc:
            logger.warning(f"Report spec '{label}' fetched but not written through: {exc}")
    return f"egeria:{label}@v{version}"


def _lookup_guid(directory: Path, label: str) -> Optional[str]:
    return (_read_manifest(directory)["entries"].get(label) or {}).get("guid")


def fetch_spec_for_call(client, name: str, *, cache_dir_override: Optional[str] = None) -> str:
    """Fetch `name` from Egeria for this call (sync client methods). Returns the internal name
    ("egeria:<label>@v<N>") the call should use. Writes through to a per-user cache; never to a
    shared one. Raises SpecFetchError with words; never falls back to the cached copy."""
    from pyegeria.omvs.collection_manager import CollectionManager
    label = _fetch_target(name)
    directory = _resolve_cache_dir(client, cache_dir_override)
    getter = client if hasattr(client, "get_collection_by_guid") else _collection_client(client, CollectionManager)
    try:
        guid = _lookup_guid(directory, label)
        el = _get_full(getter, guid) if guid else None
        if el is None:
            found = _find_specs_by_label(getter, label)
            if len(found) > 1:
                raise SpecFetchError(f"Report spec '{label}' is held by {len(found)} elements in Egeria: "
                                     f"{', '.join(_guid(e) for e in found)}")
            el = _get_full(getter, _guid(found[0])) if found else None
    except SpecFetchError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise SpecFetchError(f"Report spec '{label}' could not be fetched from Egeria: {exc}") from exc
    if el is None:
        raise SpecFetchError(f"Report spec '{label}' was not found in Egeria (refresh_spec=True never falls back "
                             f"to the cached copy)")
    return _finish_fetch(directory, el, label, _client_identity(client))


async def async_fetch_spec_for_call(client, name: str) -> str:
    """The async twin of `fetch_spec_for_call`, for the request helpers of an async find method."""
    from pyegeria.omvs.collection_manager import CollectionManager
    label = _fetch_target(name)
    directory = _resolve_cache_dir(client, None)
    getter = client if hasattr(client, "_async_get_collection_by_guid") else _collection_client(
        client, CollectionManager)
    try:
        guid = _lookup_guid(directory, label)
        el = None
        if guid:
            el = (_elements(await getter._async_get_collection_by_guid(guid, output_format="JSON")) or [None])[0]
        if el is None:
            seen: Dict[str, Dict[str, Any]] = {}
            for nm in (label, f"ReportSpec::{label}", f"ReportType::{label}"):
                res = _elements(await getter._async_get_collections_by_name(
                    nm, metadata_element_type="ReportSpec", output_format="JSON"))
                for e in res:
                    if label_from_qualified_name(_props(e).get("qualifiedName") or "") == label and _guid(e):
                        seen[_guid(e)] = e
            if len(seen) > 1:
                raise SpecFetchError(f"Report spec '{label}' is held by {len(seen)} elements in Egeria: "
                                     f"{', '.join(sorted(seen))}")
            if seen:
                g = next(iter(seen))
                el = (_elements(await getter._async_get_collection_by_guid(g, output_format="JSON")) or [None])[0]
    except SpecFetchError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise SpecFetchError(f"Report spec '{label}' could not be fetched from Egeria: {exc}") from exc
    if el is None:
        raise SpecFetchError(f"Report spec '{label}' was not found in Egeria (refresh_spec=True never falls back "
                             f"to the cached copy)")
    return _finish_fetch(directory, el, label, _client_identity(client))


def _collection_client(client, cls):
    """A CollectionManager on the caller's platform, as the caller (their token)."""
    cm = cls(client.view_server, client.platform_url, user_id=client.user_id, user_pwd=getattr(client, "user_pwd", None))
    token = None
    try:
        token = client.get_token()
    except Exception:  # noqa: BLE001
        token = None
    if token:
        cm.set_bearer_token(token)
    return cm
