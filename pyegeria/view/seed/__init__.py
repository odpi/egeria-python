"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

The report-spec seed: pyegeria's shipped (built-in) report specs as packaged JSON
(report-spec pipeline model §7a "Built-in migration", O-H3 "Full JSON seed"; RS-EGERIA-TIER stage 2).

- **What it holds.** Every report spec that ships with pyegeria: the built-ins (`base_report_specs`), the
  generated Dr.Egeria specs (`generated_format_sets`), the analytic demo specs (`analytic_demo_specs`) and the
  question specs (`Questions`, `Report-Types`, `Question-Specs`). Owner decision S2-2 (2026-11-09): all of them are
  the `builtin` tier, so 437 specs at 6.2.28.
- **The files.** One JSON file per family (folder), for example `Glossary Manager.json`, plus `manifest.json`
  (the seed format, the files with their counts, the label order and the census). Each file holds
  `{"format": "pyegeria-seed/1", "family": ..., "specs": [entry, ...]}`; an entry is
  `{"label", "envelope": {...}, "microflow": {microflow/1}}`. The envelope holds the fields the EGERIA tier reads
  (§8f "What is stored": heading, description, family, target_type_name, aliases, annotations) plus
  `question_spec`, so stage 3 publishes an entry as it is.
- **Loading.** `seed_report_specs()` loads the seed once per process, lazily, through
  `microflow_to_format_set`: the same converter the EGERIA tier uses. A file that fails to parse or validate is
  skipped with a warning naming the file and its first error; every other file still loads, so one bad file
  never empties the built-in tier.
- **Generating.** In stage 2 the Python constants are still the source: `python -m pyegeria.view.seed build`
  writes the seed from them and `python -m pyegeria.view.seed check` exits non-zero when the files differ (a
  micro-test runs the check). `refresh_specs` runs `build` after it regenerates the generated section. Stage 4
  reverses the direction: the constants go and the seed becomes the source.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

__all__ = [
    "SEED_FORMAT",
    "SEED_DIR",
    "MANIFEST",
    "BOOTSTRAP_CORE",
    "is_bootstrap_core",
    "seed_report_specs",
    "seed_file_of",
    "seed_skipped",
    "source_specs",
    "seed_entry",
    "build_seed_files",
    "write_seed",
    "check_seed",
    "load_seed_dir",
]

SEED_FORMAT = "pyegeria-seed/1"
SEED_DIR = Path(__file__).resolve().parent
MANIFEST = "manifest.json"

#: Labels that must always come from the seed, even when stage 3 adds copies in Egeria, so a fresh or empty
#: Egeria, or no network, still works (§7a "Built-in migration", the bootstrap core). In stage 2 this changes
#: nothing at run time; a micro-test checks that every name exists in the seed. With these, every Dr.Egeria
#: display spec is core: a label ending in one of `BOOTSTRAP_CORE_SUFFIXES` (see `is_bootstrap_core`).
BOOTSTRAP_CORE: frozenset = frozenset({
    # Dr.Egeria's display fallbacks (md_processing/v2/processors.py, feedback.py)
    "Referenceable",
    "Default",
    "Journal-Entry-DrE",
    # The question specs
    "Report-Types",
    "Questions",
    "Question-Specs",
    # The report-spec listing specs
    "Report-Specs",
    "Report-Spec-DrE-Basic",
    "Report-Spec-DrE-Advanced",
    "Report-Type-DrE-Basic",
    "Report-Type-DrE-Advanced",
})
#: Dr.Egeria renders a processed element with `<Type>-DrE[-Basic|-Advanced]` (processors.py), so every one is core.
BOOTSTRAP_CORE_SUFFIXES: Tuple[str, ...] = ("-DrE", "-DrE-Basic", "-DrE-Advanced")


def is_bootstrap_core(label: str) -> bool:
    """Whether `label` must always come from the seed (BOOTSTRAP_CORE, or a Dr.Egeria display spec)."""
    return label in BOOTSTRAP_CORE or str(label).endswith(BOOTSTRAP_CORE_SUFFIXES)


# ── Loading ──

_SEED: Optional[Any] = None              # the FormatSetDict, once loaded
_SEED_FILES: Dict[str, str] = {}         # label -> seed file name
_SEED_SKIPPED: List[Tuple[str, str]] = []  # (file, first error)


def _entry_to_format_set(entry: Dict[str, Any], column_cache: Optional[Dict[Any, Any]] = None):
    from pyegeria.view.microflow import microflow_to_format_set, parse_microflow
    if not isinstance(entry, dict) or not isinstance(entry.get("label"), str) or not entry["label"]:
        raise ValueError("an entry needs a string 'label'")
    label = entry["label"]
    env = entry.get("envelope")
    if not isinstance(env, dict):
        raise ValueError(f"'{label}': the entry needs an 'envelope' object")
    mf, stored, _notes = parse_microflow(entry.get("microflow"))
    if stored != 1:
        raise ValueError(f"'{label}': the seed holds microflow/1 only, not a format-0 list")
    try:
        return microflow_to_format_set(
            mf, label=label, heading=env.get("heading"), description=env.get("description") or "",
            target_type=env.get("target_type_name"), aliases=env.get("aliases"), family=env.get("family"),
            annotations=env.get("annotations"), question_spec=env.get("question_spec"),
            column_cache=column_cache)
    except Exception as exc:  # noqa: BLE001 -- reported with the label, as the file's first error
        raise ValueError(f"'{label}': {exc}") from exc


def _load_file(path: Path, column_cache: Optional[Dict[Any, Any]] = None) -> List[Tuple[str, Any]]:
    """The (label, FormatSet) pairs one seed file holds, in order. Raises ValueError with the first error."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"not readable JSON: {exc}") from exc
    if not isinstance(data, dict) or data.get("format") != SEED_FORMAT:
        raise ValueError(f"not a {SEED_FORMAT} file (format {data.get('format') if isinstance(data, dict) else None!r})")
    specs = data.get("specs")
    if not isinstance(specs, list):
        raise ValueError("'specs' is not a list")
    out: List[Tuple[str, Any]] = []
    seen: set = set()
    for i, entry in enumerate(specs):
        try:
            fs = _entry_to_format_set(entry, column_cache)
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"entry {i}: {exc}") from exc
        if entry["label"] in seen:
            raise ValueError(f"entry {i}: label '{entry['label']}' appears twice")
        seen.add(entry["label"])
        out.append((entry["label"], fs))
    return out


def load_seed_dir(directory: Path) -> Tuple[Any, Dict[str, str], List[Tuple[str, str]]]:
    """Load every seed file in `directory`: `(FormatSetDict in manifest order, label -> file, skipped)`.

    A file that fails to parse or validate is skipped as a whole, with a warning naming it and its first
    error; the other files still load. A label held by two files is kept from the first file (in manifest
    order) and the later file is skipped with a warning. Labels the manifest's order does not list come last."""
    from pyegeria.view._output_format_models import FormatSetDict

    directory = Path(directory)
    skipped: List[Tuple[str, str]] = []
    order: List[str] = []
    files: List[str] = []
    try:
        manifest = json.loads((directory / MANIFEST).read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or manifest.get("format") != SEED_FORMAT:
            raise ValueError(f"not a {SEED_FORMAT} manifest")
        order = [str(x) for x in manifest.get("order") or []]
        files = [str(f["file"]) for f in manifest.get("files") or [] if isinstance(f, dict) and f.get("file")]
    except Exception as exc:  # noqa: BLE001 -- without a manifest, every *.json still loads
        logger.warning(f"Report spec seed: {directory / MANIFEST} is not usable ({exc}); loading every seed file "
                       f"in name order")
        skipped.append((MANIFEST, str(exc)))
    on_disk = sorted(p.name for p in directory.glob("*.json") if p.name != MANIFEST)
    for name in files:
        if name not in on_disk:
            logger.warning(f"Report spec seed file '{name}' is listed in the manifest but missing")
            skipped.append((name, "listed in the manifest but missing"))
    to_load = [f for f in files if f in on_disk] + [f for f in on_disk if f not in files]
    loaded: Dict[str, Any] = {}
    where: Dict[str, str] = {}
    column_cache: Dict[Any, Any] = {}  # identical columns share one Column, as the constants' do
    for name in to_load:
        try:
            pairs = _load_file(directory / name, column_cache)
        except ValueError as exc:
            logger.warning(f"Report spec seed file '{name}' skipped: {exc}")
            skipped.append((name, str(exc)))
            continue
        clash = [label for label, _ in pairs if label in loaded]
        if clash:
            why = f"label(s) {clash} already loaded from {sorted({where[c] for c in clash})}"
            logger.warning(f"Report spec seed file '{name}' skipped: {why}")
            skipped.append((name, why))
            continue
        for label, fs in pairs:
            loaded[label] = fs
            where[label] = name
    result = FormatSetDict()
    for label in order:
        if label in loaded:
            result[label] = loaded.pop(label)
    for label, fs in loaded.items():
        result[label] = fs
    return result, where, skipped


def seed_report_specs():
    """The seed's report specs (the `builtin` tier), as a FormatSetDict in the registry's order. Loaded once per
    process, on first call; every later call returns the same objects."""
    global _SEED
    if _SEED is None:
        specs, where, skipped = load_seed_dir(SEED_DIR)
        _SEED_FILES.clear()
        _SEED_FILES.update(where)
        _SEED_SKIPPED[:] = skipped
        _SEED = specs
    return _SEED


def seed_file_of(label: str) -> Optional[str]:
    """The seed file a built-in label was loaded from, else None."""
    seed_report_specs()
    return _SEED_FILES.get(label)


def seed_skipped() -> List[Tuple[str, str]]:
    """The seed files skipped at load, as `(file, first error)`."""
    seed_report_specs()
    return list(_SEED_SKIPPED)


def _reset_for_tests() -> None:
    global _SEED
    _SEED = None
    _SEED_FILES.clear()
    _SEED_SKIPPED.clear()


# ── Generating (stage 2: the Python constants are the source) ──

def source_specs():
    """The shipped report specs from the Python constants, in the registry's order: built-ins, generated, the
    analytic demos, the question specs. The objects are the ones the constants hold after import (the family
    registries add aliases to them in place), so the seed carries exactly what the registry served before."""
    from pyegeria.view._output_format_models import FormatSetDict
    from pyegeria.view import base_report_formats as brf
    from pyegeria.view.analytic_demo_specs import get_analytic_demo_specs

    out = FormatSetDict()
    for source, specs in (("base_report_specs", brf.base_report_specs),
                          ("generated_format_sets", brf.generated_format_sets),
                          ("analytic_demo_specs", get_analytic_demo_specs()),
                          ("question specs", brf._QUESTION_SPEC_FORMATS)):
        for label, fs in specs.items():
            if label in out.keys():
                raise ValueError(f"report spec label '{label}' from {source} is already defined by an earlier source")
            out[label] = fs
    return out


def seed_entry(label: str, fs) -> Dict[str, Any]:
    """One seed entry: `{label, envelope, microflow}`."""
    from pyegeria.view.microflow import format_set_to_microflow
    envelope: Dict[str, Any] = {
        "heading": fs.heading,
        "description": fs.description,
        "family": fs.family,
        "target_type_name": fs.target_type,
        "aliases": list(fs.aliases or []),
    }
    if fs.annotations:
        envelope["annotations"] = {k: list(v) for k, v in fs.annotations.items()}
    if fs.question_spec is not None:
        envelope["question_spec"] = [q if isinstance(q, dict) else q.model_dump() for q in fs.question_spec]
    mf = format_set_to_microflow(fs)
    return {"label": label, "envelope": envelope,
            "microflow": mf.model_dump(mode="json", exclude_none=True)}


_UNSAFE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def family_file_name(family: Optional[str]) -> str:
    """The seed file for a family: its name with characters no file system allows replaced by '_'."""
    name = _UNSAFE.sub("_", (family or "").strip()) or "_no_family"
    return f"{name}.json"


def _depth(obj: Any) -> int:
    if isinstance(obj, dict):
        return 1 + max((_depth(v) for v in obj.values()), default=0)
    if isinstance(obj, list):
        return 1 + max((_depth(v) for v in obj), default=0)
    return 0


def _pretty(obj: Any, indent: int) -> str:
    """JSON with one line per leaf object or list (a column, a parameter, an alias list), so the files diff
    by column but stay compact."""
    one_line = json.dumps(obj, ensure_ascii=False)
    if _depth(obj) <= 1 or (isinstance(obj, dict) and "field" in obj):
        return one_line
    pad, inner = " " * indent, " " * (indent + 1)
    if isinstance(obj, dict):
        items = [f"{inner}{json.dumps(k, ensure_ascii=False)}: {_pretty(v, indent + 1)}" for k, v in obj.items()]
        return "{\n" + ",\n".join(items) + f"\n{pad}}}"
    items = [f"{inner}{_pretty(v, indent + 1)}" for v in obj]
    return "[\n" + ",\n".join(items) + f"\n{pad}]"


def _dumps(obj: Any) -> str:
    return _pretty(obj, 0) + "\n"


def _census(specs) -> Dict[str, int]:
    from pyegeria.view.spec_resolver import Unrunnable, resolve
    names = set(specs.keys())
    total = runnable = unrunnable = format_only = 0
    for label, fs in specs.items():
        total += 1
        r = resolve(fs, label, registry_names=names)
        if isinstance(r, Unrunnable):
            if r.kind == "format_only":
                format_only += 1
            else:
                unrunnable += 1
        else:
            runnable += 1
    return {"total": total, "runnable": runnable, "unrunnable": unrunnable, "format_only": format_only}


def build_seed_files(specs=None) -> Dict[str, str]:
    """The seed's files as `{file name: text}`, manifest included, built from `specs` (default: the constants)."""
    specs = source_specs() if specs is None else specs
    by_file: Dict[str, Dict[str, Any]] = {}
    lower: Dict[str, str] = {}
    for label, fs in specs.items():
        name = family_file_name(fs.family)
        other = lower.setdefault(name.lower(), name)
        if other != name:
            raise ValueError(f"families '{other}' and '{name}' would share one seed file on a case-insensitive "
                             f"file system")
        f = by_file.setdefault(name, {"format": SEED_FORMAT, "family": fs.family, "specs": []})
        f["specs"].append(seed_entry(label, fs))
    files = {name: _dumps(content) for name, content in sorted(by_file.items())}
    manifest = {
        "format": SEED_FORMAT,
        "description": ("pyegeria's shipped report specs (the builtin tier). Generated by "
                        "`python -m pyegeria.view.seed build` from the Python constants; do not edit by hand."),
        "census": _census(specs),
        "families": len(by_file),
        "files": [{"file": name, "family": by_file[name]["family"], "count": len(by_file[name]["specs"])}
                  for name in sorted(by_file)],
        "order": list(specs.keys()),
    }
    files[MANIFEST] = _dumps(manifest)
    return files


def write_seed(directory: Path = SEED_DIR, specs=None) -> Dict[str, str]:
    """Write the seed into `directory`, removing seed files no family uses any more. Returns the files written."""
    directory = Path(directory)
    files = build_seed_files(specs)
    directory.mkdir(parents=True, exist_ok=True)
    for stale in directory.glob("*.json"):
        if stale.name not in files:
            stale.unlink()
    for name, text in files.items():
        (directory / name).write_text(text, encoding="utf-8")
    return files


def check_seed(directory: Path = SEED_DIR, specs=None) -> List[str]:
    """The differences between the seed files in `directory` and what `build` would write; empty if current."""
    directory = Path(directory)
    want = build_seed_files(specs)
    have = {p.name: p.read_text(encoding="utf-8") for p in directory.glob("*.json")}
    out: List[str] = []
    for name in sorted(set(want) | set(have)):
        if name not in have:
            out.append(f"{name}: missing")
        elif name not in want:
            out.append(f"{name}: no longer generated")
        elif have[name] != want[name]:
            out.append(f"{name}: differs")
    return out
