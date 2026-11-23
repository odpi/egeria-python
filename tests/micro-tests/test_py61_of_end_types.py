"""PY-61: an `of:<end>.<attribute>` source is checked against the entity type at that relationship end (and its
supertypes), both from the 6.4 typedefs, not against the union of every entity type."""
import importlib.util
import pathlib

import pytest

from pyegeria.view import column_source as cs
from pyegeria.view.column_source import check_source, check_source_with_warnings

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _gen():
    spec = importlib.util.spec_from_file_location("gen_pcf61", ROOT / "scripts/gen_properties_class_fields.py")
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    return gen


def test_a_right_end_attribute_passes():
    assert check_source("of:serverEndpoints.networkAddress") == []          # an Endpoint has a network address
    assert check_source("of:serverForEndpoint.deployedImplementationType") == []   # the server end is ITInfrastructure


def test_a_supertype_attribute_passes():
    assert check_source("of:serverEndpoints.qualifiedName") == []           # Referenceable, an Endpoint supertype
    assert check_source("of:serverEndpoints.displayName") == []


def test_a_wrong_end_attribute_is_refused_naming_relationship_end_type_and_attribute():
    errors = check_source("of:serverEndpoints.deployedImplementationType")
    assert len(errors) == 1
    words = errors[0]
    assert "ServerEndpoint" in words and "serverEndpoints" in words and "Endpoint" in words
    assert "deployedImplementationType" in words
    assert check_source("of:serverForEndpoint.networkAddress") != []        # the other end has no network address


def test_an_attribute_no_type_has_is_still_refused():
    assert check_source("of:serverEndpoints.nonsenseAttribute") != []


def test_an_unknown_end_type_falls_back_to_the_union_and_says_so(monkeypatch):
    table = {k: v for k, v in cs._end_entity_types().items() if k != "serverEndpoints"}
    monkeypatch.setattr(cs, "_end_entity_types", lambda: table)
    errors, warnings = check_source_with_warnings("of:serverEndpoints.deployedImplementationType")
    assert errors == []                                                      # accepted by the union check ...
    assert warnings and "serverEndpoints" in warnings[0] and "union" in warnings[0]   # ... never silently
    errors, warnings = check_source_with_warnings("of:serverEndpoints.nonsenseAttribute")
    assert errors and warnings                                               # a typo is still refused


def test_a_known_end_gives_no_warning():
    assert check_source_with_warnings("of:serverEndpoints.networkAddress") == ([], [])


def test_the_validator_reports_the_warning_and_the_error():
    import asyncio
    from pyegeria.authoring import SpecDraft, validate
    from pyegeria.view._output_format_models import FormatSet
    fs = FormatSet(target_type="SoftwareServer", heading="t", description="d", family="x", formats=[
        {"types": ["TABLE"], "attributes": [{"name": "Bad", "key": "bad", "source": "of:serverEndpoints.deployedImplementationType"}]}])
    result = validate(SpecDraft(label="T-Test", format_set=fs))
    assert any("deployedImplementationType" in e and "serverEndpoints" in e for e in result.errors)


def test_the_generator_reads_end_types_and_entity_supertypes_from_the_typedefs():
    gen = _gen()
    names = gen.type_name_constants({"x/OpenMetadataType.java": """
        ENDPOINT("11111111-1111-1111-1111-111111111111", "Endpoint", X),
        IT_INFRASTRUCTURE("22222222-2222-2222-2222-222222222222", "ITInfrastructure", X),
        REFERENCEABLE("33333333-3333-3333-3333-333333333333", "Referenceable", X),
        OPEN_METADATA_ROOT("44444444-4444-4444-4444-444444444444", "OpenMetadataRoot", X),
    """})
    archive = '''
        EntityDef a = archiveHelper.getDefaultEntityDef(OpenMetadataType.OPEN_METADATA_ROOT,
                                                        null);
        EntityDef b = archiveHelper.getDefaultEntityDef(OpenMetadataType.REFERENCEABLE,
                                                        this.archiveBuilder.getEntityDef(OpenMetadataType.OPEN_METADATA_ROOT.typeName));
        EntityDef c = archiveHelper.getDefaultEntityDef(OpenMetadataType.ENDPOINT,
                                                        this.archiveBuilder.getEntityDef(OpenMetadataType.REFERENCEABLE.typeName));
        final String end1AttributeName = "serverForEndpoint";
        relationshipEndDef = archiveHelper.getRelationshipEndDef(this.archiveBuilder.getEntityDef(OpenMetadataType.IT_INFRASTRUCTURE.typeName),
                                                                 end1AttributeName,
                                                                 d, null, ANY);
        final String end2AttributeName = "serverEndpoints";
        relationshipEndDef = archiveHelper.getRelationshipEndDef(this.archiveBuilder.getEntityDef(OpenMetadataType.ENDPOINT.typeName),
                                                                 end2AttributeName,
                                                                 d, null, ANY);
    '''
    archives = {"x/OpenMetadataTypesArchive1_2.java": archive}
    assert gen.supertype_chains(gen.entity_typedef_supers(archives, names)) == {
        "Referenceable": ("OpenMetadataRoot",), "Endpoint": ("Referenceable", "OpenMetadataRoot")}
    assert gen.relationship_end_types(archives, names) == {
        "serverForEndpoint": ("ITInfrastructure",), "serverEndpoints": ("Endpoint",)}


def test_the_tables_cover_the_relationship_lists():
    from md_processing.md_processing_utils.properties_class_fields import END_ENTITY_TYPES, ENTITY_SUPERTYPES
    from pyegeria.view.egeria_relationship_fields import RELATIONSHIP_FIELDS
    assert END_ENTITY_TYPES["serverEndpoints"] == ("Endpoint",)
    assert ENTITY_SUPERTYPES["Endpoint"][0] == "Referenceable"
    covered = [k for k in RELATIONSHIP_FIELDS if k in END_ENTITY_TYPES]
    assert len(covered) > len(RELATIONSHIP_FIELDS) * 0.8, (len(covered), len(RELATIONSHIP_FIELDS))


def test_the_constant_parser_takes_any_guid_shape_egeria_wrote():
    """F4: 11 constants have a GUID that is upper/mixed case or 35/37 characters long, so a strict 36-char
    lowercase pattern dropped them (Port, PortAlias, IncidentReport, CloudProvider ...)."""
    gen = _gen()
    got = gen.type_name_constants({"x/OpenMetadataType.java": """
    PORT("e3d9FD9F-d5eD-2aed-CC98-0bc21aB6f71C",
         "Port",
         OpenMetadataWikiPages.MODEL_0217_PORTS),
    INCIDENT_REPORT("072f252b-dea7-4b88-bb2e-8f741c9ca7f6e",
                    "IncidentReport", X),
    CLOUD_PROVIDER_CLASSIFICATION("a2bfdd08-d0a8-49db-bc97-7f240628104",
                                  "CloudProvider", X),
    PLAIN("11111111-1111-1111-1111-111111111111", "Plain", X),
"""})
    assert got == {"PORT": "Port", "INCIDENT_REPORT": "IncidentReport", "CLOUD_PROVIDER_CLASSIFICATION": "CloudProvider",
                   "PLAIN": "Plain"}


def test_the_four_ends_the_parser_used_to_miss_now_have_types():
    from md_processing.md_processing_utils.properties_class_fields import END_ENTITY_TYPES, ENTITY_SUPERTYPES
    for end in ("incidentReports", "ports", "portDelegatingFrom", "portDelegatingTo"):
        assert END_ENTITY_TYPES.get(end), end
    for entity in ("IncidentReport", "Port", "PortAlias", "PortImplementation", "RecentAccess",
                   "ResourceMeasureAnnotation"):
        assert entity in ENTITY_SUPERTYPES, entity


def test_the_parser_finds_every_enum_entry_in_the_6_4_source():
    import os
    import re
    src, ref = os.environ.get("EGERIA_6_4_SRC"), os.environ.get("EGERIA_6_4_REF", "90232870b2")
    if not src:
        pytest.skip("set EGERIA_6_4_SRC to a checkout of odpi/egeria at the table's sha")
    gen = _gen()
    sources = {p: t for p, t in gen.read_sources(src, ref).items() if p.endswith("/OpenMetadataType.java")}
    assert sources
    text = next(iter(sources.values()))
    # every enum entry starts a line as NAME("<guid>", with the type name on that or a following line
    entries = re.findall(r"^\s{4}([A-Z][A-Z0-9_]*)\(\s*\"[^\"]+\"\s*,\s*\"[^\"]+\"", text, re.M)
    assert len(entries) > 600
    assert set(gen.type_name_constants(sources)) == set(entries)
