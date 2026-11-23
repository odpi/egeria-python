"""PY-49 Q7: live 6.4 verdicts (laz, 2026-11-23) for Registered-Services and Severity-Definitions."""
from pyegeria.view.base_report_formats import base_report_specs
from pyegeria.omvs.registered_info import RegisteredInfo
from pyegeria.view.output_formatter import populate_columns_from_properties


def _keys(name):
    return [c.key for f in base_report_specs[name].formats for c in f.attributes]


def test_registered_services_drops_columns_absent_on_6_4():
    keys = _keys("Registered-Services")
    assert "service_type" not in keys and "conformance_profile" not in keys
    assert {"service_name", "service_description", "service_url_marker", "service_wiki"} <= set(keys)


def test_severity_definitions_drops_columns_absent_on_6_4():
    keys = _keys("Severity-Definitions")
    assert keys == ["name", "ordinal", "description"]


def test_url_marker_reads_the_raw_serviceURLMarker_key():
    cols = {"formats": {"attributes": [{"name": "URL Marker", "key": "service_url_marker"}]}}
    out = RegisteredInfo._extract_registered_service_properties(None, {"serviceURLMarker": "asset-owner"}, cols)
    assert out["formats"]["attributes"][0]["value"] == "asset-owner"
