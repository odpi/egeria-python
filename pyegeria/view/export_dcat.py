# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""export_dcat: a DCAT-AP 3 catalog of Egeria Assets (SD-2), as JSON-LD or Turtle.

Registered as the analytic function ``export_dcat`` and run by the built-in DOCUMENT spec
"DCAT Catalog" (SD-1's document output type). The mapping is the design's §7 table
(DESIGN-REPORT-SPECS-STANDARD-DOCUMENTS-DCAT-BITOL-2026-11-11, owner decision D2):

=========================  ====================================================================
DCAT                       Egeria
=========================  ====================================================================
dcat:Catalog               the scope collection (title, description, publisher from Ownership),
                           or a search over the asset domain
dcat:Dataset               each Asset in scope. DigitalProducts and Agreements (Bitol's) and any
                           other non-Asset member are named in notes, never exported
dcat:Distribution          the Asset's Connection -> Endpoint (accessURL) and, for a DataFile,
                           its pathName (downloadURL); mediaType / format from the file type
dcat:DataService           a DeployedAPI Asset's endpoint (endpointURL, servesDataset)
dct:publisher              the Ownership classification's owner
dct:license                the License relationship (LicenseType)
dct:accessRights           ZoneMembership: none -> PUBLIC, zoned -> NON_PUBLIC
dcat:keyword               SearchKeywords
dcat:theme                 glossary terms by SemanticAssignment (meanings)
dct:issued / dct:modified  element header createTime / updateTime
dct:identifier             qualifiedName; the GUID is adms:identifier
dcat:landingPage           the Asset's url, else an ExternalReference's url
=========================  ====================================================================

**Absence-as-answer.** Every property left out for some dataset is named in ``notes``, with the
datasets and the reason. A member Egeria refuses with a 403 (zone security, ISSUE-182) is noted as
"not visible to <viewer>"; it is never reported as absent from the collection. Egeria also leaves
out of a member listing what the viewer cannot see, which the notes always say.

**The viewer.** Everything is read with the client the routine is given (the caller's own,
``egeria_client:EgeriaTech``): no service account, no shared cache.

**Paging.** Members (and search results) are read page by page, startFrom advancing by the page
size, until a page comes back empty; a short page is not the last page (Egeria's paging contract).
A page that repeats what was already read ends the reading with a note.

**Determinism.** Node IRIs are built from GUIDs (``urn:egeria:guid:<guid>``), never blank nodes,
and the output is sorted by node and property, so the same metadata gives the same bytes.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import quote

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCAT, DCTERMS, FOAF, RDF, SKOS, XSD

ADMS = Namespace("http://www.w3.org/ns/adms#")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
ACCESS_RIGHT = Namespace("http://publications.europa.eu/resource/authority/access-right/")
FILE_TYPE = Namespace("http://publications.europa.eu/resource/authority/file-type/")
IANA = "http://www.iana.org/assignments/media-types/"

PREFIXES = {"dcat": DCAT, "dct": DCTERMS, "adms": ADMS, "foaf": FOAF, "vcard": VCARD, "skos": SKOS,
            "xsd": XSD, "rdf": RDF}

#: The JSON-LD @context: inline (a validator never fetches one), prefixes only.
JSONLD_CONTEXT = {p: str(ns) for p, ns in sorted(PREFIXES.items())}

#: Types that are Bitol's, not DCAT's (owner decision D2). Matched on the type or a supertype.
BITOL_TYPES = ("DigitalProduct", "Agreement")

#: File extension -> (IANA media type, EU file-type code).
_FILE_TYPES = {
    "csv": ("text/csv", "CSV"), "json": ("application/json", "JSON"), "parquet": ("application/vnd.apache.parquet", "PARQUET"),
    "xml": ("application/xml", "XML"), "txt": ("text/plain", "TXT"), "xlsx": (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "XLSX"),
    "avro": ("application/avro", "AVRO"), "pdf": ("application/pdf", "PDF"), "html": ("text/html", "HTML"),
    "yaml": ("application/yaml", "YAML"), "yml": ("application/yaml", "YAML"),
}

_GUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
_MAX_PAGES = 1000  # a bound, never a silent truncation: reaching it is noted

#: The relationships one Asset read asks Egeria for: only what the mapping uses, so a heavily
#: surveyed Asset is not read with all its annotations and lineage.
ASSET_RELATIONSHIPS = ["ResourceConnection", "ConnectToEndpoint", "License", "SearchKeywordLink",
                       "SemanticAssignment", "ExternalReferenceLink", "APIEndpoint", "ServerEndpoint"]


def _iri(guid: str, *suffix: str) -> URIRef:
    return URIRef("urn:egeria:guid:" + guid + "".join(f":{s}" for s in suffix))


def _is_list(result: Any) -> bool:
    return isinstance(result, list)


def _type_names(element: Dict[str, Any]) -> Tuple[str, List[str]]:
    t = (element.get("elementHeader") or {}).get("type") or {}
    return t.get("typeName") or "", list(t.get("superTypeNames") or [])


def _qn(element: Dict[str, Any]) -> str:
    props = element.get("properties") or {}
    return props.get("qualifiedName") or (element.get("elementHeader") or {}).get("guid") or "?"


def _guid(element: Dict[str, Any]) -> str:
    return (element.get("elementHeader") or {}).get("guid") or ""


def _related(element: Dict[str, Any], key: str) -> List[Dict[str, Any]]:
    """The related elements under one of an element's relationship lists (Egeria 6 shape:
    a list of {relationshipHeader, relatedElement, ...})."""
    value = element.get(key)
    items = value if isinstance(value, list) else [value] if isinstance(value, dict) else []
    return [i.get("relatedElement") for i in items if isinstance(i, dict) and isinstance(i.get("relatedElement"), dict)]


def _date(value: Optional[str]) -> Optional[Literal]:
    if not value:
        return None
    return Literal(value.replace("+00:00", "Z"), datatype=XSD.dateTime)


def _as_iri(address: str) -> Optional[URIRef]:
    """An endpoint address or path as an IRI: a URL as it is, an absolute path as file://."""
    if not address:
        return None
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", address):
        return URIRef(quote(address, safe=":/?#[]@!$&'()*+,;=%~"))
    if address.startswith("/"):
        return URIRef("file://" + quote(address, safe="/:~"))
    return None


class _Notes:
    """Notes grouped by what was left out, so the same gap across many datasets is one sentence."""

    def __init__(self) -> None:
        self.general: List[str] = []
        self.by_reason: Dict[str, List[str]] = {}

    def add(self, sentence: str) -> None:
        if sentence not in self.general:
            self.general.append(sentence)

    def omitted(self, reason: str, qn: str) -> None:
        self.by_reason.setdefault(reason, []).append(qn)

    def render(self) -> List[str]:
        out = list(self.general)
        for reason in sorted(self.by_reason):
            names = sorted(set(self.by_reason[reason]))
            out.append(f"{reason} for {len(names)} dataset{'s' if len(names) != 1 else ''}: {'; '.join(names)}")
        return out


# ── Reads (as the client's user) ──

def _paged(read, page_size: int, notes: _Notes, what: str) -> List[Dict[str, Any]]:
    """Read pages until one comes back empty, advancing startFrom by the full page size each time
    (Egeria's paging contract: a short page is not the last page, and only an empty one is). Egeria
    answers "no elements" with a string, which counts as an empty page. A page that brings no
    element not already read (a server that ignores startFrom) ends the reading, with a note; it is
    never counted twice (ISSUE-185)."""
    items: List[Dict[str, Any]] = []
    seen: set = set()
    start = 0
    for _ in range(_MAX_PAGES):
        page = read(start, page_size)
        if not _is_list(page) or not page:
            return items
        new = [e for e in page if _guid(e) not in seen]
        if not new:
            notes.add(f"Stopped reading {what} at startFrom {start}: Egeria answered with elements already read "
                      f"(it repeated a page), so later pages, if any, were not read.")
            return items
        seen.update(_guid(e) for e in new)
        items.extend(new)
        start += page_size
    notes.add(f"Stopped reading {what} after {_MAX_PAGES} pages of {page_size}: the catalog may be incomplete.")
    return items


def _not_visible(exc: BaseException) -> bool:
    from pyegeria.view.dashboard_resolver import is_not_visible_error
    return is_not_visible_error(exc)


def _not_found(exc: BaseException) -> bool:
    from pyegeria.core._exceptions import PyegeriaNotFoundException
    return isinstance(exc, PyegeriaNotFoundException) or "-404-" in str(exc)


def _read_scope(client: Any, scope: str) -> Dict[str, Any]:
    """The scope collection, by GUID or qualifiedName (exact match)."""
    if _GUID.match(scope):
        found = client.get_collection_by_guid(scope, output_format="JSON", graph_query_depth=0)
        if isinstance(found, dict):
            return found
        raise ValueError(f"export_dcat: no collection with GUID {scope} is visible to {client.user_id}")
    found = client.get_collections_by_name(scope, output_format="JSON", graph_query_depth=0)
    exact = [c for c in found if _qn(c) == scope] if _is_list(found) else []
    if not exact:
        raise ValueError(f"export_dcat: no collection with qualifiedName '{scope}' is visible to {client.user_id}")
    return exact[0]


# ── The mapping ──

class _Builder:
    def __init__(self, viewer: str) -> None:
        self.g = Graph()
        for prefix, ns in PREFIXES.items():
            self.g.bind(prefix, ns)
        self.viewer = viewer
        self.notes = _Notes()

    def _agent(self, owner: str, owner_type: str = "") -> URIRef:
        node = URIRef("urn:egeria:owner:" + quote(owner, safe=""))
        self.g.add((node, RDF.type, FOAF.Agent))
        self.g.add((node, FOAF.name, Literal(owner)))
        return node

    @staticmethod
    def _owner(element: Dict[str, Any]) -> Tuple[str, str]:
        ownership = (element.get("elementHeader") or {}).get("ownership") or {}
        props = ownership.get("classificationProperties") or {}
        return str(props.get("owner") or ""), str(props.get("ownerTypeName") or "")

    def _identity(self, node: URIRef, element: Dict[str, Any]) -> None:
        guid = _guid(element)
        self.g.add((node, DCTERMS.identifier, Literal(_qn(element))))
        ident = _iri(guid, "identifier")
        self.g.add((node, ADMS.identifier, ident))
        self.g.add((ident, RDF.type, ADMS.Identifier))
        self.g.add((ident, SKOS.notation, Literal(guid)))
        versions = (element.get("elementHeader") or {}).get("versions") or {}
        for prop, key in ((DCTERMS.issued, "createTime"), (DCTERMS.modified, "updateTime")):
            value = _date(versions.get(key))
            if value is not None:
                self.g.add((node, prop, value))

    def catalog(self, element: Optional[Dict[str, Any]], *, search_string: Optional[str] = None) -> URIRef:
        if element is not None:
            node = _iri(_guid(element))
            props = element.get("properties") or {}
            self.g.add((node, RDF.type, DCAT.Catalog))
            self.g.add((node, DCTERMS.title, Literal(props.get("displayName") or _qn(element))))
            if not props.get("displayName"):
                self.notes.add(f"Catalog title is the collection's qualifiedName: it has no displayName.")
            if props.get("description"):
                self.g.add((node, DCTERMS.description, Literal(props["description"])))
            else:
                self.notes.add("Catalog dct:description omitted: the collection has no description.")
            owner, owner_type = self._owner(element)
            if owner:
                self.g.add((node, DCTERMS.publisher, self._agent(owner, owner_type)))
            else:
                self.notes.add("Catalog dct:publisher omitted: the collection has no Ownership classification "
                               "(DCAT-AP requires a publisher for a Catalog).")
            self._identity(node, element)
            return node
        node = URIRef("urn:egeria:search:" + quote(search_string or "", safe=""))
        self.g.add((node, RDF.type, DCAT.Catalog))
        self.g.add((node, DCTERMS.title, Literal(f"Egeria assets matching '{search_string}'")))
        self.g.add((node, DCTERMS.description, Literal(
            f"Assets in Egeria's asset domain whose properties match the search string '{search_string}', "
            f"as visible to {self.viewer}.")))
        self.g.add((node, DCTERMS.identifier, Literal(f"search:{search_string}")))
        self.notes.add("Catalog dct:publisher omitted: a search has no owner (DCAT-AP requires a publisher "
                       "for a Catalog).")
        return node

    def dataset(self, catalog: URIRef, element: Dict[str, Any]) -> None:
        guid, qn = _guid(element), _qn(element)
        props = element.get("properties") or {}
        header = element.get("elementHeader") or {}
        type_name, supers = _type_names(element)
        node = _iri(guid)
        self.g.add((catalog, DCAT.dataset, node))
        self.g.add((node, RDF.type, DCAT.Dataset))
        self.g.add((node, DCTERMS.title, Literal(props.get("displayName") or qn)))
        if not props.get("displayName"):
            self.notes.omitted("dct:title is the qualifiedName (no displayName)", qn)
        if props.get("description"):
            self.g.add((node, DCTERMS.description, Literal(props["description"])))
        else:
            self.notes.omitted("dct:description omitted: the Asset has no description", qn)
        self._identity(node, element)

        # Access rights: the viewer rule. A zoned Asset is only here because the viewer can read it.
        zones = ((header.get("zoneMembership") or {}).get("classificationProperties") or {}).get("zoneMembership")
        rights = ACCESS_RIGHT.NON_PUBLIC if zones else ACCESS_RIGHT.PUBLIC
        self.g.add((node, DCTERMS.accessRights, rights))
        self.g.add((rights, RDF.type, DCTERMS.RightsStatement))

        owner, owner_type = self._owner(element)
        if owner:
            self.g.add((node, DCTERMS.publisher, self._agent(owner, owner_type)))
        else:
            self.notes.omitted("dct:publisher omitted: no Ownership classification", qn)

        licences = _related(element, "licenses")
        for lic in licences:
            lp = lic.get("properties") or {}
            lnode = URIRef(lp["url"]) if lp.get("url") and _as_iri(lp["url"]) else _iri(_guid(lic))
            self.g.add((node, DCTERMS.license, lnode))
            self.g.add((lnode, RDF.type, DCTERMS.LicenseDocument))
            self.g.add((lnode, DCTERMS.title, Literal(lp.get("displayName") or _qn(lic))))
            self.g.add((lnode, DCTERMS.identifier, Literal(_qn(lic))))
        if not licences:
            self.notes.omitted("dct:license omitted: no License relationship", qn)

        keywords = [k.get("properties", {}).get("keyword") or k.get("properties", {}).get("displayName")
                    for k in _related(element, "searchKeywords")]
        for kw in sorted(k for k in keywords if k):
            self.g.add((node, DCAT.keyword, Literal(kw)))
        if not any(keywords):
            self.notes.omitted("dcat:keyword omitted: no SearchKeywords", qn)

        terms = _related(element, "meanings")
        for term in terms:
            tp = term.get("properties") or {}
            tnode = _iri(_guid(term))
            self.g.add((node, DCAT.theme, tnode))
            self.g.add((tnode, RDF.type, SKOS.Concept))
            self.g.add((tnode, SKOS.prefLabel, Literal(tp.get("displayName") or _qn(term))))
        if not terms:
            self.notes.omitted("dcat:theme omitted: no glossary term by SemanticAssignment", qn)

        landing = props.get("url") or next((r.get("properties", {}).get("url") for r in _related(element, "externalReferences")
                                           if (r.get("properties") or {}).get("url")), None)
        if landing and _as_iri(landing):
            self.g.add((node, DCAT.landingPage, _as_iri(landing)))
        else:
            self.notes.omitted("dcat:landingPage omitted: no url and no ExternalReference with a url", qn)

        self._distributions(node, element, type_name, supers)

    def _endpoints(self, element: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Endpoints reachable from the Asset: Connection -> (side link) Endpoint, or a direct endpoint."""
        found: List[Dict[str, Any]] = []
        for item in element.get("connections") or []:
            if not isinstance(item, dict):
                continue
            for side in item.get("sideLinks") or []:
                rel = (side or {}).get("relatedElement") or {}
                if _type_names(rel)[0] == "Endpoint" or "Endpoint" in _type_names(rel)[1]:
                    found.append(rel)
        for key in ("endpoint", "apiEndpoints", "serverEndpoints"):
            found.extend(r for r in _related(element, key))
        unique = {(_guid(e)): e for e in found if _guid(e)}
        return [unique[k] for k in sorted(unique)]

    def _distributions(self, node: URIRef, element: Dict[str, Any], type_name: str, supers: List[str]) -> None:
        qn, guid = _qn(element), _guid(element)
        props = element.get("properties") or {}
        is_file = "DataFile" in supers or type_name == "DataFile"
        is_api = "DeployedAPI" in supers or type_name == "DeployedAPI"
        path = props.get("pathName") if is_file else None
        endpoints = self._endpoints(element)
        addresses = sorted({(e.get("properties") or {}).get("networkAddress") for e in endpoints} - {None, ""})
        usable = [a for a in addresses if _as_iri(a) is not None]
        if not usable and not (path and _as_iri(path) is not None):
            if addresses:
                self.notes.omitted("dcat:distribution omitted: the endpoint address is not a URL or an absolute "
                                   "path, and DCAT-AP requires a distribution's accessURL", qn)
            else:
                self.notes.omitted("dcat:distribution omitted: no access path (no Connection with an Endpoint"
                                   + (", no pathName" if is_file else "") + ")", qn)
            return
        addresses = usable
        ext = (props.get("fileExtension") or (path.rsplit(".", 1)[-1] if path and "." in path else "")).lower()
        media = _FILE_TYPES.get(ext)
        for i, address in enumerate(addresses or [path]):
            dist = _iri(guid, "distribution", str(i))
            self.g.add((node, DCAT.distribution, dist))
            self.g.add((dist, RDF.type, DCAT.Distribution))
            access = _as_iri(address)
            self.g.add((dist, DCAT.accessURL, access))
            if path and _as_iri(path) is not None:
                self.g.add((dist, DCAT.downloadURL, _as_iri(path)))
            if media:
                media_node, format_node = URIRef(IANA + media[0]), FILE_TYPE[media[1]]
                self.g.add((dist, DCAT.mediaType, media_node))
                self.g.add((media_node, RDF.type, DCTERMS.MediaType))
                self.g.add((dist, DCTERMS["format"], format_node))
                self.g.add((format_node, RDF.type, DCTERMS.MediaTypeOrExtent))
            elif props.get("deployedImplementationType") or props.get("fileType"):
                self.notes.omitted("dcat:mediaType omitted: the file type is not one this exporter maps", qn)
            if is_api:
                svc = _iri(guid, "service")
                self.g.add((svc, RDF.type, DCAT.DataService))
                self.g.add((svc, DCTERMS.title, Literal(props.get("displayName") or qn)))
                self.g.add((svc, DCAT.endpointURL, access))
                self.g.add((svc, DCAT.servesDataset, node))
                self.g.add((dist, DCAT.accessService, svc))


# ── Serialisation ──

def _sort_jsonld(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _sort_jsonld(value[k]) for k in sorted(value)}
    if isinstance(value, list):
        items = [_sort_jsonld(v) for v in value]
        return sorted(items, key=lambda v: json.dumps(v, sort_keys=True))
    return value


def serialise(graph: Graph, fmt: str) -> str:
    """The graph as Turtle or JSON-LD (compacted with the inline prefix @context), sorted so the
    same graph always gives the same text."""
    if fmt == "turtle":
        return graph.serialize(format="turtle")
    raw = json.loads(graph.serialize(format="json-ld", context=JSONLD_CONTEXT, auto_compact=True))
    nodes = raw.get("@graph", [raw] if "@id" in raw else [])
    nodes = [{k: v for k, v in n.items() if k != "@context"} for n in nodes]
    doc = {"@context": JSONLD_CONTEXT,
           "@graph": sorted((_sort_jsonld(n) for n in nodes), key=lambda n: n.get("@id", ""))}
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


# ── The routine ──

def export_dcat(client: Any, scope: Optional[str] = None, search_string: Optional[str] = None,
                format: str = "jsonld", page_size: int = 50, **_ignored: Any) -> Dict[str, Any]:
    """Export the Assets in ``scope`` (a collection qualifiedName or GUID) or matching
    ``search_string`` as a DCAT-AP 3 catalog. Returns ``{"text", "notes"}`` (SD-1's exporter shape).

    ``format`` is ``jsonld`` (default) or ``turtle``. Read as the client's user."""
    fmt = (format or "jsonld").lower().replace("-", "")
    if fmt in ("ttl",):
        fmt = "turtle"
    if fmt not in ("jsonld", "turtle"):
        raise ValueError(f"export_dcat: format '{format}' is not jsonld or turtle")
    if not scope and not search_string:
        raise ValueError("export_dcat needs a scope (a collection qualifiedName or GUID) or a search_string")
    page_size = int(page_size or 50)
    viewer = getattr(client, "user_id", None) or "the caller"
    b = _Builder(viewer)

    if scope:
        collection = _read_scope(client, scope)
        catalog = b.catalog(collection)
        guid = _guid(collection)
        members = _paged(lambda s, n: client.get_collection_members(
            collection_guid=guid, start_from=s, page_size=n, output_format="JSON", graph_query_depth=0), page_size, b.notes,
            f"the members of {_qn(collection)}")
        b.notes.add(f"Read as {viewer}: Egeria leaves members in zones {viewer} cannot see out of the member "
                    f"listing, so this catalog lists only what {viewer} can see.")
    else:
        catalog = b.catalog(None, search_string=search_string)
        members = _paged(lambda s, n: client.find_in_asset_domain(
            search_string=search_string, start_from=s, page_size=n, output_format="JSON", graph_query_depth=0), page_size, b.notes,
            f"the assets matching '{search_string}'")
        b.notes.add(f"Read as {viewer}: Egeria leaves assets in zones {viewer} cannot see out of a search, so this "
                    f"catalog lists only what {viewer} can see.")

    seen = set()
    exported = 0
    for member in sorted(members, key=_guid):
        guid = _guid(member)
        if not guid or guid in seen:
            continue
        seen.add(guid)
        type_name, supers = _type_names(member)
        kinds = [t for t in BITOL_TYPES if t == type_name or t in supers]
        if kinds:
            b.notes.add(f"{_qn(member)}: a {kinds[0]}, not a DCAT dataset (Bitol)")
            continue
        if not (type_name == "Asset" or "Asset" in supers):
            b.notes.add(f"{_qn(member)}: a {type_name or 'element of unknown type'}, not an Asset, so not a DCAT dataset")
            continue
        try:
            element = client.get_element_by_guid(guid, output_format="JSON",
                                                 include_only_relationships=ASSET_RELATIONSHIPS)
        except Exception as exc:  # noqa: BLE001 -- classified below, never silently dropped
            if _not_visible(exc):
                b.notes.add(f"{_qn(member)}: not visible to {viewer} (Egeria refused the read: zone security); "
                            f"it is in scope but not exported")
            elif _not_found(exc):
                b.notes.add(f"{_qn(member)}: listed in scope but no longer found when read; not exported")
            else:
                b.notes.add(f"{_qn(member)}: could not be read ({type(exc).__name__}); not exported")
            continue
        if not isinstance(element, dict):
            b.notes.add(f"{_qn(member)}: listed in scope but no longer found when read; not exported")
            continue
        b.dataset(catalog, element)
        exported += 1

    if exported == 0:
        b.notes.add(f"No dataset exported: no Asset in scope is visible to {viewer}.")
    if not any(True for _ in b.g.subjects(RDF.type, DCAT.DataService)):
        b.notes.add("dcat:DataService omitted: no DeployedAPI with an endpoint in scope.")
    b.notes.add("dcat:contactPoint omitted: this exporter does not read owners' contact details.")
    return {"text": serialise(b.g, fmt), "notes": b.notes.render()}
