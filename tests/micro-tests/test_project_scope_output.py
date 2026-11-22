# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""PY-5 / EG-14: Project ``properties.scope`` (odpi/egeria #9448) must appear in the formatted output.

The server round-trips scope; the default "Projects" report spec (PROJECT_COLUMNS) had no Scope column, so
DICT/MD/REPORT output silently dropped it.
"""
from unittest.mock import patch

from pyegeria.omvs.project_manager import ProjectManager


def _client() -> ProjectManager:
    with patch("pyegeria.core._base_server_client.BaseServerClient.check_connection", return_value=""):
        return ProjectManager(view_server="fake-view", platform_url="https://fake:9443",
                              user_id="fake-user", user_pwd="fake-pwd")


def _element(scope=None):
    props = {"class": "ProjectProperties", "qualifiedName": "Project::scope-test", "displayName": "Scope Test",
             "description": "d", "projectStatus": "ACTIVE", "priority": 1}
    if scope is not None:
        props["scope"] = scope
    return {"class": "OpenMetadataRootElement",
            "elementHeader": {"guid": "3bd40b37-3d70-4caa-9733-91548ba0eee1",
                              "type": {"typeName": "Project"}, "origin": {}, "versions": {}},
            "properties": props}


def _out(fmt, scope):
    return _client()._generate_project_output([_element(scope)], "scope", "Project", fmt, "Projects")


def test_dict_has_scope():
    rows = _out("DICT", "In: portal. Out: billing.")
    assert rows[0]["Scope"] == "In: portal. Out: billing."


def test_md_and_report_have_scope_column_and_value():
    for fmt in ("MD", "REPORT"):
        text = _out(fmt, "In: portal. Out: billing.")
        assert "Scope" in text and "In: portal. Out: billing." in text, fmt


def test_unset_scope_is_empty_in_dict():
    # DICT rows are keyed by column name; an unset value is None like every other unset column.
    # (MD/REPORT render every unset column as the text "None" -- generic formatter behaviour, not Scope-specific.)
    assert _out("DICT", None)[0]["Scope"] in (None, "")
    assert _out("DICT", "")[0]["Scope"] in (None, "")


def test_my_user_projects_detail_has_scope():
    from pyegeria.view.base_report_formats import get_report_registry
    fs = get_report_registry()["My-User-Projects-Detail"]
    assert "Scope" in [c.name for f in fs.formats for c in f.attributes]
