"""PY-39: the generic Markdown formatter never prints the text "None" for an unset property.

Convention (the one already used for an empty string): in FORM and MD the heading stays and the body is blank,
because a FORM is what the author fills in and an MD keeps the same shape; in REPORT and MERMAID an unset
property is left out altogether. False and 0 are values and are still printed.
"""
import copy

import pytest

from pyegeria.view.output_formatter import generate_entity_md, make_md_attribute, render_rich_value

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("output_type", ["FORM", "MD"])
def test_an_unset_attribute_keeps_its_heading_and_has_a_blank_body(output_type):
    text = make_md_attribute("Planned End Date", None, output_type)
    assert text == make_md_attribute("Planned End Date", "", output_type)
    assert text.startswith("### Planned End Date\n")
    assert "None" not in text


@pytest.mark.parametrize("output_type", ["REPORT", "MERMAID"])
def test_an_unset_attribute_is_left_out_of_a_report(output_type):
    assert make_md_attribute("Planned End Date", None, output_type) == ""


@pytest.mark.parametrize("output_type,value", [("FORM", False), ("MD", 0), ("REPORT", False), ("REPORT", 0)])
def test_false_and_zero_are_values_and_are_still_printed(output_type, value):
    assert str(value) in make_md_attribute("Flag", value, output_type)


@pytest.mark.parametrize("output_format", ["FORM", "MD", "REPORT"])
@pytest.mark.parametrize("value", [[None, "x"], {"a": None, "b": "x"}, [{"name": "n", "note": None}]])
def test_a_none_inside_a_list_or_dict_is_not_printed(output_format, value):
    assert "None" not in render_rich_value(value, output_format)


@pytest.mark.parametrize("output_format", ["FORM", "MD"])
def test_a_project_with_unset_properties_prints_no_none(output_format):
    names = ["Display Name", "Description", "Mission", "Priority", "Planned Start Date", "Planned End Date",
             "Project Phase", "Project Health", "Project Status", "Category", "Identifier", "Version Identifier"]
    columns = {"heading": "Project", "formats": {"attributes": [
        {"name": n, "key": n.lower().replace(" ", "_"), "value": None} for n in names]}}

    def extract(element, columns_struct):
        out = copy.deepcopy(columns_struct)
        out["formats"]["attributes"][0]["value"] = "My Project"
        return out

    text = generate_entity_md([{"elementHeader": {"guid": "g-1"}}], "Update Project", output_format, "Project",
                              extract, None, columns)
    assert "None" not in text
    assert "### Planned End Date" in text and "My Project" in text
