# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Validators for DOCUMENT report-spec outputs (SD-1).

A document validator is a callable ``(text, media_type, **options) -> (valid, findings)``:

- ``valid`` is a bool;
- ``findings`` is a list of sentences, one per problem (empty when there is none).

Validators are registered by name, mirroring ``register_analytic_functions``: a name that is
already registered raises ``DocumentValidatorCollision``. A DOCUMENT format names its validator
in ``document.validator`` and passes any options in ``document.validator_options``.

Two built-ins ship with pyegeria:

- ``json-schema``: option ``schema``, a JSON Schema (path, ``file://`` URL or ``package:``
  resource) to check JSON or YAML text against;
- ``shacl``: option ``shapes``, a SHACL shapes graph (same kinds of reference) to check RDF
  text against with pySHACL.

**A validator never fetches over the network.** A schema or shapes reference is package data
(``package:<dotted.package>/<resource path>``); programmatic callers may also give a local path or a
``file://`` URL, but a report spec may not (``spec_option_refusal``), since specs can be held in
Egeria and written by any user. A failed validator's ``reason`` never quotes parser text. An ``http(s)``
reference raises ``DocumentValidatorRefused``, and so does RDF text whose JSON-LD ``@context``
names a remote document (rdflib would fetch it). The executor reports a raised validator as
``not_validated`` with the error, never as a finding.
"""
from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple
from urllib.parse import unquote, urlparse

DocumentValidator = Callable[..., Tuple[bool, List[str]]]


class DocumentValidatorCollision(ValueError):
    """A document validator name is already registered."""


class DocumentValidatorRefused(ValueError):
    """A validator was asked to do something it never does (such as fetch over the network)."""


# ── Reading local references only ──

def read_local_reference(ref: str, *, what: str) -> str:
    """Read the text a schema/shapes reference names: a filesystem path, a ``file://`` URL or a
    ``package:<dotted.package>/<resource path>`` resource. Anything that would need the network
    is refused with a sentence."""
    if not isinstance(ref, str) or not ref.strip():
        raise DocumentValidatorRefused(f"no {what} was given to the validator")
    ref = ref.strip()
    scheme = urlparse(ref).scheme.lower()
    if scheme in {"http", "https", "ftp"}:
        raise DocumentValidatorRefused(
            f"the {what} '{ref}' is a network address; a validator never fetches over the network. "
            f"Give a local path, a file:// URL or a package: resource")
    if ref.startswith("package:"):
        package, _, resource = ref[len("package:"):].partition("/")
        if not package or not resource:
            raise DocumentValidatorRefused(
                f"the {what} '{ref}' is not of the form package:<dotted.package>/<resource path>")
        target = resources.files(package)
        for part in resource.split("/"):
            target = target / part
        return target.read_text(encoding="utf-8")
    if scheme == "file":
        return Path(unquote(urlparse(ref).path)).read_text(encoding="utf-8")
    return Path(ref).expanduser().read_text(encoding="utf-8")


# ── The json-schema built-in ──

def _parse_structured_text(text: str, media_type: str) -> Any:
    mt = (media_type or "").lower()
    if "yaml" in mt:
        import yaml
        return yaml.safe_load(text)
    return json.loads(text)


def json_schema_validator(text: str, media_type: str, *, schema: str) -> Tuple[bool, List[str]]:
    """Check JSON (or YAML, by media type) ``text`` against the JSON Schema ``schema`` names.

    A ``$ref`` the schema cannot resolve locally is an error, not a fetch: the validator is given
    an empty ``referencing.Registry`` with no ``retrieve``, so an unknown (remote) ``$ref`` raises
    ``Unresolvable`` instead of going to the network."""
    import jsonschema

    schema_doc = json.loads(read_local_reference(schema, what="JSON Schema"))
    instance = _parse_structured_text(text, media_type)
    from referencing import Registry

    validator_cls = jsonschema.validators.validator_for(schema_doc)
    validator_cls.check_schema(schema_doc)
    # An empty registry with no `retrieve`: a $ref the schema cannot resolve locally raises
    # Unresolvable. Without `registry=`, jsonschema falls back to a registry that urlopens remote
    # $refs (SD-1 read-back C1).
    validator = validator_cls(schema_doc, registry=Registry())
    errors = sorted(validator.iter_errors(instance),
                    key=lambda e: (list(map(str, e.absolute_path)), e.message))
    findings = [f"{'/' + '/'.join(map(str, e.absolute_path)) if e.absolute_path else '(document)'}: {e.message}"
                for e in errors]
    return (not findings, findings)


# ── The shacl built-in ──

_RDF_FORMATS = {
    "application/ld+json": "json-ld",
    "application/json": "json-ld",
    "text/turtle": "turtle",
    "application/x-turtle": "turtle",
    "application/rdf+xml": "xml",
    "application/n-triples": "nt",
    "application/n-quads": "nquads",
    "application/trig": "trig",
    "text/n3": "n3",
}


def rdf_format_for(media_type: str) -> str:
    """The rdflib parser name for an RDF media type; refuses one it does not know."""
    fmt = _RDF_FORMATS.get((media_type or "").split(";")[0].strip().lower())
    if fmt is None:
        raise DocumentValidatorRefused(f"the media type '{media_type}' is not an RDF serialisation the "
                                       f"shacl validator reads ({', '.join(sorted(_RDF_FORMATS))})")
    return fmt


def _remote_contexts(node: Any) -> List[str]:
    """Every ``@context``/``@import`` value in a JSON-LD document that names another document."""
    found: List[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key in ("@context", "@import"):
                for item in value if isinstance(value, list) else [value]:
                    if isinstance(item, str):
                        found.append(item)
                    else:
                        found.extend(_remote_contexts(item))
            else:
                found.extend(_remote_contexts(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(_remote_contexts(item))
    return found


def parse_rdf_offline(text: str, media_type: str, *, what: str = "document"):
    """Parse RDF text into an rdflib Graph without any network access. A JSON-LD document whose
    ``@context`` names another document is refused (rdflib would fetch it)."""
    from rdflib import Graph

    fmt = rdf_format_for(media_type)
    if fmt == "json-ld":
        remote = _remote_contexts(json.loads(text))
        if remote:
            raise DocumentValidatorRefused(
                f"the {what}'s JSON-LD @context names another document ({len(set(remote))} reference(s)); "
                f"reading it would fetch over the network, which a validator never does. Inline the context")
    graph = Graph()
    graph.parse(data=text, format=fmt)
    return graph


def _short(graph, node) -> str:
    if node is None:
        return "(no path)"
    try:
        return graph.namespace_manager.normalizeUri(node)
    except Exception:  # noqa: BLE001 -- a blank node or an odd IRI: show it as is
        return str(node)


def shacl_findings(data_graph, shapes_graph) -> Tuple[bool, List[str]]:
    """Run pySHACL and return ``(conforms, findings)``; one finding per validation result, as
    "<severity> <focus node> <path>: <message>", sorted so the list is stable. Warnings and
    infos are listed but do not make the document invalid."""
    import pyshacl
    from rdflib import Namespace
    from rdflib.namespace import RDF

    SH = Namespace("http://www.w3.org/ns/shacl#")
    conforms, results_graph, _ = pyshacl.validate(
        data_graph, shacl_graph=shapes_graph, inference="none", allow_warnings=True,
        do_owl_imports=False, advanced=True)
    for prefix, ns in list(data_graph.namespace_manager.namespaces()):
        results_graph.namespace_manager.bind(prefix, ns, override=False)
    findings: List[str] = []
    for result in results_graph.subjects(RDF.type, SH.ValidationResult):
        severity = results_graph.value(result, SH.resultSeverity)
        focus = results_graph.value(result, SH.focusNode)
        path = results_graph.value(result, SH.resultPath)
        message = results_graph.value(result, SH.resultMessage)
        sev = _short(results_graph, severity).split(":")[-1].split("#")[-1] if severity is not None else "Violation"
        findings.append(f"{sev} {_short(results_graph, focus)} {_short(results_graph, path)}: "
                        f"{message if message is not None else 'does not conform'}")
    return bool(conforms), sorted(findings)


def shacl_validator(text: str, media_type: str, *, shapes: str,
                    shapes_media_type: str = "text/turtle") -> Tuple[bool, List[str]]:
    """Check RDF ``text`` (JSON-LD, Turtle, … by media type) against the SHACL ``shapes`` graph."""
    shapes_graph = parse_rdf_offline(read_local_reference(shapes, what="SHACL shapes"),
                                     shapes_media_type, what="shapes graph")
    data_graph = parse_rdf_offline(text, media_type)
    return shacl_findings(data_graph, shapes_graph)


def make_shacl_validator(shapes: str, shapes_media_type: str = "text/turtle") -> DocumentValidator:
    """A ``(text, media_type)`` validator bound to one shapes graph, parsed once on first use.
    Used to register a named validator for one standard (e.g. ``dcat-ap-3-shacl``)."""
    cache: Dict[str, Any] = {}

    def _validate(text: str, media_type: str, **_ignored: Any) -> Tuple[bool, List[str]]:
        if "shapes" not in cache:
            cache["shapes"] = parse_rdf_offline(read_local_reference(shapes, what="SHACL shapes"),
                                                shapes_media_type, what="shapes graph")
        return shacl_findings(parse_rdf_offline(text, media_type), cache["shapes"])

    return _validate


# ── The registry ──

_BUILTIN_VALIDATORS: Dict[str, DocumentValidator] = {
    "json-schema": json_schema_validator,
    "shacl": shacl_validator,
}
_RUNTIME_VALIDATORS: Dict[str, DocumentValidator] = {}


def get_document_validators() -> Dict[str, DocumentValidator]:
    """Every registered document validator, built-ins first."""
    return {**_BUILTIN_VALIDATORS, **_RUNTIME_VALIDATORS}


def get_document_validator(name: str):
    """The validator registered under ``name``, or None."""
    return get_document_validators().get(name)


def register_document_validators(new_validators: Dict[str, DocumentValidator], *,
                                 source: str = "runtime") -> None:
    """Add document validators by name. A name already registered raises
    ``DocumentValidatorCollision`` and nothing from this call is added."""
    existing = get_document_validators()
    for name, fn in new_validators.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"a document validator needs a non-empty name (from {source})")
        if not callable(fn):
            raise ValueError(f"document validator '{name}' from {source} is not callable")
        if name in existing:
            raise DocumentValidatorCollision(
                f"Document validator '{name}' already exists; cannot register from {source}")
    _RUNTIME_VALIDATORS.update(new_validators)


def unregister_document_validator(name: str) -> bool:
    """Remove a runtime-registered validator; built-ins cannot be removed."""
    return _RUNTIME_VALIDATORS.pop(name, None) is not None


def clear_runtime_document_validators() -> None:
    _RUNTIME_VALIDATORS.clear()


# ── Running a document's validator (the executor's half of the contract) ──

#: Validator options that name a file to read. From a spec definition (which may be held in Egeria
#: and written by any user) each must be a ``package:`` reference: pyegeria's own package data or an
#: installed exporter package's. Local paths and file:// URLs stay available to programmatic
#: callers only (``make_shacl_validator(path)``, ``json_schema_validator(..., schema=path)``).
REFERENCE_OPTIONS = ("schema", "shapes")


def spec_option_refusal(options: Dict[str, Any] | None) -> str | None:
    """Why a spec's validator_options are refused, or None. Only ``package:`` references may name a
    file from a spec definition (SD-1 read-back C2)."""
    for key in REFERENCE_OPTIONS:
        value = (options or {}).get(key)
        if value is None:
            continue
        if not isinstance(value, str) or not value.strip().startswith("package:"):
            return (f"validator option '{key}' must be a package: reference (package:<dotted.package>/<path>) "
                    f"when it comes from a report spec; a spec may not name a local file or URL")
    return None


def _error_words(exc: BaseException) -> str:
    """What a failed validator says in ``reason``: never the parser's text, which can quote the input
    (the document, or a schema/shapes file). The error type, plus line and column when known, and our
    own refusal sentences, which carry no file content."""
    if isinstance(exc, DocumentValidatorRefused):
        return f"{type(exc).__name__}: {exc}"
    try:  # jsonschema wraps referencing's errors; name the real one
        exc = object.__getattribute__(exc, "_wrapped")
    except AttributeError:
        pass
    ref = getattr(exc, "ref", None)
    if isinstance(ref, str):  # a $ref the schema could not resolve: name it (it is the schema's, not input)
        return f"{type(exc).__name__}: the $ref {ref} is not resolvable without a network fetch"
    line = getattr(exc, "lineno", None) or getattr(exc, "lines", None)
    col = getattr(exc, "colno", None)
    mark = getattr(exc, "problem_mark", None)
    if mark is not None:
        line, col = getattr(mark, "line", -1) + 1, getattr(mark, "column", -1) + 1
    where = ""
    if isinstance(line, int):
        where = f" at line {line}" + (f", column {col}" if isinstance(col, int) else "")
    return f"{type(exc).__name__}{where}"

def run_document_validator(text: str, media_type: str, validator: str | None,
                           options: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """The ``validation`` block of a DOCUMENT result. Always returned, never omitted:

    - ``state``: ``valid`` | ``invalid`` | ``not_validated``;
    - ``validator``: the declared name, or None;
    - ``findings``: the validator's sentences (empty when it found nothing or did not run);
    - ``reason``: why the document was not validated, or None when it was.

    A validator that raises is ``not_validated`` with its error type (and line/column) as the
    reason, never the parser's text: a crash says nothing about the document, so it is never
    reported as a finding or as ``invalid``. ``options`` come from a spec definition, so a
    ``schema``/``shapes`` option that is not a ``package:`` reference is refused (not run)."""
    if not validator:
        return {"state": "not_validated", "validator": None, "findings": [],
                "reason": "no validator is declared for this standard"}
    fn = get_document_validator(validator)
    if fn is None:
        return {"state": "not_validated", "validator": validator, "findings": [],
                "reason": f"the validator {validator} is not registered"}
    refusal = spec_option_refusal(options)
    if refusal:
        return {"state": "not_validated", "validator": validator, "findings": [],
                "reason": f"the validator {validator} was not run: {refusal}"}
    try:
        valid, findings = fn(text, media_type, **(options or {}))
    except Exception as exc:  # noqa: BLE001 -- any crash is reported, never raised or counted as a finding
        return {"state": "not_validated", "validator": validator, "findings": [],
                "reason": f"the validator {validator} failed: {_error_words(exc)}"}
    findings = [str(f) for f in (findings or [])]
    return {"state": "valid" if valid else "invalid", "validator": validator, "findings": findings,
            "reason": None}
