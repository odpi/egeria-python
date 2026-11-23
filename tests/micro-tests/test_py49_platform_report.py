"""PY-49 row 9: the platform REPORT carries the servers (omagservers); the platform element does not."""
import copy

from pyegeria.omvs.runtime_manager import RuntimeManager
from pyegeria.view.base_report_formats import get_report_registry

# trimmed from the 6.4 get_platform_report response (laz, 2026-11-23); no credentials
REPORT = {
    "defaultPlatformName": "Default Platform",
    "platformURLRoot": "https://egeria:9443",
    "platformOrigin": "Egeria OMAG Server Platform (version 6.4)",
    "platformBuildProperties": {"git.build.version": "6.4"},
    "platformPublicProperties": {"hostName": "egeria"},
    "platformStartTime": "2026-11-20T10:00:00.000+00:00",
    "registeredOMAGServices": [{"serviceName": "Asset Owner"}],
    "omagservers": [
        {"class": "OMAGServerSummary", "serverName": "qs-view-server", "serverType": "View Server",
         "serverActiveStatus": "ACTIVE", "serverId": "x1"},
        {"class": "OMAGServerSummary", "serverName": "qs-metadata-store", "serverType": "Metadata Access Store",
         "serverActiveStatus": "INACTIVE", "serverId": "x2"},
    ],
}


def _columns(label):
    return [c.key for f in get_report_registry()[label].formats for c in f.attributes]


def _extract(element):
    cols = {"formats": {"attributes": [{"name": k, "key": k} for k in _columns("Platform-Report")]}}
    out = RuntimeManager._extract_platform_properties(None, copy.deepcopy(element), cols)
    return {c["key"]: c for c in out["formats"]["attributes"]}


def test_the_registry_has_a_platform_report_spec_with_the_servers_column():
    assert "omag_servers" in _columns("Platform-Report")


def test_platforms_spec_keeps_only_what_the_platform_element_can_fill():
    keys = _columns("Platforms")
    for gone in ("omag_servers", "platform_url_root", "version", "platform_origin", "platform_start_time",
                 "platform_build_properties"):
        assert gone not in keys
    assert "guid" in keys


def test_servers_show_name_and_status_and_keep_the_native_list():
    got = _extract(REPORT)["omag_servers"]
    assert got["value"] == "qs-view-server (ACTIVE), qs-metadata-store (INACTIVE)"
    assert got["native"] == [
        {"serverName": "qs-view-server", "serverType": "View Server", "serverActiveStatus": "ACTIVE"},
        {"serverName": "qs-metadata-store", "serverType": "Metadata Access Store", "serverActiveStatus": "INACTIVE"}]


def test_the_report_is_recognised_by_platformURLRoot_and_its_values_read_from_the_raw_keys():
    got = _extract(REPORT)
    assert got["platform_url_root"]["value"] == "https://egeria:9443"
    assert got["platform_origin"]["value"] == "Egeria OMAG Server Platform (version 6.4)"
    assert got["platform_start_time"]["value"] == "2026-11-20T10:00:00.000+00:00"
    assert got["platform_build_properties"]["value"] == {"git.build.version": "6.4"}
    assert got["platform_public_properties"]["value"] == {"hostName": "egeria"}


def test_the_older_spelling_is_still_recognised():
    el = {k: v for k, v in REPORT.items() if k != "platformURLRoot"} | {"platformUrlRoot": "https://old:9443"}
    assert _extract(el)["platform_url_root"]["value"] == "https://old:9443"


def test_a_report_with_no_servers_gives_blank_not_none():
    got = _extract({k: v for k, v in REPORT.items() if k != "omagservers"})["omag_servers"]
    assert got["value"] == "" and got["native"] == []


def test_guid_is_filled_from_the_platform_guid_the_caller_passed():
    import asyncio
    from unittest.mock import AsyncMock, MagicMock
    mgr = RuntimeManager.__new__(RuntimeManager)
    mgr.runtime_command_root = "http://x"
    mgr.__async_get_guid__ = AsyncMock(return_value="g-1")
    mgr._async_get_guid = mgr.__async_get_guid__
    resp = MagicMock(); resp.json.return_value = {"element": REPORT}
    mgr._async_make_request = AsyncMock(return_value=resp)
    seen = {}
    mgr._generate_platform_report_output = lambda el, *a, **k: seen.setdefault("el", el)
    asyncio.run(RuntimeManager._async_get_platform_report(mgr, platform_guid="g-1", output_format="DICT"))
    assert seen["el"]["guid"] == "g-1"
    assert "guid" not in REPORT
