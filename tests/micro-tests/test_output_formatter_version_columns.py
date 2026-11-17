"""Header version columns (createTime, updateTime, ...) reach report columns.

_extract_referenceable_properties used to return create_time and updated_by but
not update_time, so a report column keyed update_time rendered blank on every row
when it went through populate_common_columns: read as "never updated".
"""
import copy

import pytest

from pyegeria.view.output_formatter import (
    _extract_referenceable_properties,
    materialize_egeria_summary,
    populate_common_columns,
)

pytestmark = pytest.mark.unit

# The shape Egeria 6 returns: ElementVersions carries createdBy, updatedBy,
# maintainedBy, createTime, updateTime, version.
VERSIONS = {
    "createdBy": "erinoverview",
    "updatedBy": "peterprofile",
    "maintainedBy": ["erinoverview", "peterprofile"],
    "createTime": "2026-11-01T09:00:00.000+00:00",
    "updateTime": "2026-11-13T18:30:00.000+00:00",
    "version": 4,
}

ELEMENT = {
    "class": "OpenMetadataRootElement",
    "elementHeader": {
        "class": "ElementHeader",
        "headerVersion": 0,
        "status": "ACTIVE",
        "type": {"typeId": "x", "typeName": "Collection", "typeVersion": 1},
        "origin": {
            "sourceServer": "qs-metadata-store",
            "originCategory": "LOCAL_COHORT",
            "homeMetadataCollectionId": "mc-1",
            "homeMetadataCollectionName": "qs metadata store",
        },
        "versions": VERSIONS,
        "guid": "11111111-2222-3333-4444-555555555555",
    },
    "properties": {
        "class": "CollectionProperties",
        "qualifiedName": "Collection::Version Columns",
        "displayName": "Version Columns",
    },
}

# Every ElementVersions field that materialize_egeria_summary maps, and the column key.
VERSION_KEYS = {
    "version": "version",
    "created_by": "createdBy",
    "create_time": "createTime",
    "updated_by": "updatedBy",
    "update_time": "updateTime",
}


def _columns(*keys):
    return {
        "heading": "Version Columns",
        "formats": {"attributes": [{"name": k, "key": k} for k in keys]},
    }


def test_update_time_column_is_filled():
    out = populate_common_columns(copy.deepcopy(ELEMENT), _columns("display_name", "update_time"))
    cols = {c["key"]: c.get("value") for c in out["formats"]["attributes"]}
    assert cols["update_time"] == VERSIONS["updateTime"]
    assert cols["display_name"] == "Version Columns"


def test_every_version_column_is_filled():
    out = populate_common_columns(copy.deepcopy(ELEMENT), _columns(*VERSION_KEYS))
    cols = {c["key"]: c.get("value") for c in out["formats"]["attributes"]}
    for key, field in VERSION_KEYS.items():
        assert cols[key] == VERSIONS[field], key


def test_extractor_and_summary_agree_on_version_fields():
    """No version field one path materializes is missing from the other."""
    header_props = _extract_referenceable_properties(copy.deepcopy(ELEMENT))
    summary = materialize_egeria_summary(copy.deepcopy(ELEMENT))
    for key, field in VERSION_KEYS.items():
        assert summary.get(key) == VERSIONS[field], f"summary {key}"
        assert header_props.get(key) == VERSIONS[field], f"extractor {key}"
