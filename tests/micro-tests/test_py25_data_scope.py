"""PY-25: Classify/Update Data Scope carry every 6.4 DataScopeProperties field (0210) and the processor sends each;
Create Data Lens carries the validity and coverage periods too."""
import json

import pytest

from md_processing.md_processing_utils.common_md_utils import set_gov_prop_body  # noqa: F401  (import check)
from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS
from md_processing.v2.curation import CLASSIFICATION_METHODS, _build_classification_properties

SPEC_DIR = "md_processing/data/compact_commands/"

# attribute (as a user types it) -> DataScopeProperties property
EXPECTED = {
    "Data Collection Start Time": "dataCollectionStartTime", "Data Collection End Time": "dataCollectionEndTime",
    "Data Validity Start Time": "dataValidityStartTime", "Data Validity End Time": "dataValidityEndTime",
    "Data Coverage Start Time": "dataCoverageStartTime", "Data Coverage End Time": "dataCoverageEndTime",
    "Min Longitude": "minLongitude", "Max Longitude": "maxLongitude", "Min Latitude": "minLatitude",
    "Max Latitude": "maxLatitude", "Min Height": "minHeight", "Max Height": "maxHeight",
    "Scope Elements": "scopeElements", "Additional Properties": "additionalProperties",
    "Effective From": "effectiveFrom", "Effective To": "effectiveTo", "Extended Properties": "extendedProperties",
}


def _family(name):
    import os
    root = os.path.join(os.path.dirname(__file__), "..", "..", SPEC_DIR)
    return json.load(open(os.path.join(root, f"{name}.json")))


def _bundle_attributes(family, bundle):
    out, b = [], family["bundles"]
    while bundle:
        out += b[bundle].get("own_attributes", [])
        bundle = b[bundle].get("inherits")
    return out


def test_every_6_4_datascope_property_is_a_property_of_the_table():
    table = set(PROPERTIES_CLASS_FIELDS["DataScopeProperties"][1])
    assert set(EXPECTED.values()) <= table
    # and the table's own set is covered: nothing in it (bar the type bookkeeping) is left without an attribute
    assert table - set(EXPECTED.values()) <= {"typeName"}, table - set(EXPECTED.values())


def test_the_data_scope_commands_carry_every_attribute():
    fam = _family("commands_curation_compact")
    attrs = set(_bundle_attributes(fam, "Data Scope Base"))
    assert set(EXPECTED) <= attrs, set(EXPECTED) - attrs
    for cmd in ("Classify Data Scope", "Update Data Scope"):
        assert fam["commands"][cmd]["bundle"] == "Data Scope Base"
        assert "generic" not in fam["commands"][cmd]["description"].lower()
    assert "Description" not in attrs  # DataScopeProperties has no description


def test_the_processor_sends_each_attribute_under_its_property_name():
    spec = CLASSIFICATION_METHODS["DataScope"]
    assert spec.fields == EXPECTED


def test_the_body_the_processor_builds_has_every_value():
    spec = CLASSIFICATION_METHODS["DataScope"]
    attributes = {
        "Data Collection Start Time": {"value": "2026-01-01T00:00:00Z"}, "Data Collection End Time": {"value": "2026-01-31T00:00:00Z"},
        "Data Validity Start Time": {"value": "2026-02-01T00:00:00Z"}, "Data Validity End Time": {"value": "2026-12-31T00:00:00Z"},
        "Data Coverage Start Time": {"value": "2025-01-01T00:00:00Z"}, "Data Coverage End Time": {"value": "2025-12-31T00:00:00Z"},
        "Min Longitude": {"value": -10.5}, "Max Longitude": {"value": 20.25}, "Min Latitude": {"value": 35.0},
        "Max Latitude": {"value": 60.0}, "Min Height": {"value": 0.0}, "Max Height": {"value": 1500.5},
        "Scope Elements": {"value": {"region": "EMEA"}}, "Additional Properties": {"value": {"owner": "ops"}},
        "Effective From": {"value": "2026-01-01T00:00:00Z"}, "Effective To": {"value": "2027-01-01T00:00:00Z"},
        "Extended Properties": {"value": {"x": "y"}},
    }
    props = _build_classification_properties(spec, attributes)
    assert props["class"] == "DataScopeProperties"
    for attr, prop in EXPECTED.items():
        assert props[prop] == attributes[attr]["value"], (attr, prop)
    assert props["minLongitude"] == -10.5 and props["maxHeight"] == 1500.5  # numbers stay numbers


def test_an_attribute_left_blank_is_not_sent():
    props = _build_classification_properties(CLASSIFICATION_METHODS["DataScope"], {"Min Latitude": {"value": 1.5}})
    assert props == {"class": "DataScopeProperties", "minLatitude": 1.5}


def test_the_old_description_mapping_is_gone():
    props = _build_classification_properties(CLASSIFICATION_METHODS["DataScope"], {"Description": {"value": "text"}})
    assert "additionalProperties" not in props


# ── Data Lens ──
def test_create_data_lens_carries_the_validity_and_coverage_periods():
    fam = _family("commands_governance_officer_compact")
    custom = set(fam["commands"]["Create Data Lens"]["custom_attributes"])
    assert {"Data Validity Start Time", "Data Validity End Time", "Data Coverage Start Time",
            "Data Coverage End Time", "Data Collection Start Time", "Data Collection End Time"} <= custom
    table = set(PROPERTIES_CLASS_FIELDS["DataLensProperties"][1])
    assert {"dataValidityStartTime", "dataValidityEndTime", "dataCoverageStartTime", "dataCoverageEndTime"} <= table


def test_the_data_lens_body_sends_them_and_the_bounds_as_numbers():
    from md_processing.md_processing_utils.common_md_utils import update_gov_body_for_type
    attrs = {
        "Data Collection Start Time": {"value": "2026-01-01T00:00:00"}, "Data Collection End Time": {"value": "2026-01-31T00:00:00"},
        "Data Validity Start Time": {"value": "2026-02-01T00:00:00"}, "Data Validity End Time": {"value": "2026-12-31T00:00:00"},
        "Data Coverage Start Time": {"value": "2025-01-01T00:00:00"}, "Data Coverage End Time": {"value": "2025-12-31T00:00:00"},
        "Min Longitude": {"value": "-10.5"}, "Max Longitude": {"value": 20.25}, "Min Latitude": {"value": "35"},
        "Max Latitude": {"value": "60"}, "Min Height": {"value": ""}, "Max Height": {"value": "1500.5"},
        "Scope Elements": {"value": {"region": "EMEA"}},
    }
    body = update_gov_body_for_type("DataLens", {}, attrs)
    for prop in ("dataCollectionStartTime", "dataCollectionEndTime", "dataValidityStartTime", "dataValidityEndTime",
                 "dataCoverageStartTime", "dataCoverageEndTime"):
        assert body[prop].startswith("20"), prop
    assert body["minLongitude"] == -10.5 and body["minLatitude"] == 35.0 and body["maxHeight"] == 1500.5
    assert body["minHeight"] is None and body["scopeElements"] == {"region": "EMEA"}
    assert all(isinstance(body[p], float) for p in ("minLongitude", "maxLongitude", "minLatitude", "maxLatitude", "maxHeight"))


def test_text_that_is_not_a_number_is_refused_not_sent():
    from pyegeria import PyegeriaException
    from md_processing.md_processing_utils.common_md_utils import update_gov_body_for_type
    with pytest.raises(PyegeriaException) as lens:
        update_gov_body_for_type("DataLens", {}, {"Min Latitude": {"value": "north"}})
    assert "Min Latitude must be a number" in str(lens.value)
    with pytest.raises(PyegeriaException) as scope:
        _build_classification_properties(CLASSIFICATION_METHODS["DataScope"], {"Max Height": {"value": "tall"}})
    assert "Max Height must be a number" in str(scope.value)


# ── through the real dispatcher and processor, with a fake client ──
from typing import Any, Dict, List  # noqa: E402

from pyegeria import NO_ELEMENTS_FOUND  # noqa: E402
from md_processing.dr_egeria import register_curation_processors  # noqa: E402
from md_processing.v2.dispatcher import V2Dispatcher  # noqa: E402
from md_processing.v2.extraction import DrECommand  # noqa: E402

_TARGET = "DataSet::Scoped Sales Feed"
_GUID = "11111111-2222-3333-4444-555555555555"


class _FakeClassificationManager:
    def __init__(self):
        self.calls: List[tuple] = []

    async def _async_add_data_scope(self, guid, body):
        self.calls.append(("add", guid, body))

    async def _async_update_data_scope(self, guid, body):
        self.calls.append(("update", guid, body))


class _FakeClient:
    def __init__(self):
        self.classification_manager = _FakeClassificationManager()

    async def __async_get_guid__(self, qualified_name=None, display_name=None, **kwargs):
        return _GUID if (qualified_name or display_name) == _TARGET else NO_ELEMENTS_FOUND


def _dispatch(verb: str, attributes: Dict[str, Any]):
    import asyncio
    client = _FakeClient()
    dispatcher = V2Dispatcher(client)
    register_curation_processors(dispatcher.register)
    raw = f"## {verb} Data Scope\n" + "".join(f"### {k}\n{v}\n" for k, v in attributes.items())
    cmd = DrECommand(verb=verb, object_type="Data Scope", attributes=attributes, raw_block=raw)
    results = asyncio.run(dispatcher.dispatch_batch([cmd], {"directive": "process"}))
    return results[0], client.classification_manager.calls


_TYPED = {
    "Target Element": _TARGET,
    "Data Collection Start Time": "2026-01-01T00:00:00", "Data Collection End Time": "2026-01-31T00:00:00",
    "Data Validity Start Time": "2026-02-01T00:00:00", "Data Validity End Time": "2026-12-31T00:00:00",
    "Data Coverage Start Time": "2025-01-01T00:00:00", "Data Coverage End Time": "2025-12-31T00:00:00",
    "Min Longitude": "-10.5", "Max Longitude": "20.25", "Min Latitude": "35", "Max Latitude": "60",
    "Min Height": "0", "Max Height": "1500.5",
}


@pytest.mark.parametrize("verb,call", [("Classify", "add"), ("Update", "update")])
def test_the_dispatched_command_sends_every_typed_attribute(verb, call):
    result, calls = _dispatch(verb, _TYPED)
    assert result["status"] == "success", result
    assert len(calls) == 1 and calls[0][0] == call and calls[0][1] == _GUID
    props = calls[0][2]["properties"]
    assert props["class"] == "DataScopeProperties"
    for attr, prop in EXPECTED.items():
        if attr in _TYPED:
            assert prop in props, (attr, prop, props)
    assert props["minLongitude"] == -10.5 and props["maxLongitude"] == 20.25
    assert props["minLatitude"] == 35.0 and props["maxHeight"] == 1500.5
    assert all(isinstance(props[p], float) for p in ("minLongitude", "maxLongitude", "minLatitude", "maxLatitude",
                                                     "minHeight", "maxHeight"))
    assert props["dataValidityEndTime"].startswith("2026-12-31")
    assert calls[0][2]["class"] == ("UpdateClassificationRequestBody" if verb == "Update"
                                    else "NewClassificationRequestBody")
