"""PY-62: a generated spec always shows what names an element (display_name, qualified_name, guid) when its target has them."""
from commands.tech.gen_report_specs import _lead_with_universal_columns
from pyegeria.view._output_format_models import Column
from pyegeria.view.base_report_formats import get_report_registry

GAINED = ["Secrets-Store-Element-DrE-Advanced", "Secrets-Store-Element-DrE-Basic",
          "UC-Catalog-Element-DrE-Advanced", "UC-Catalog-Element-DrE-Basic", "ToDo-DrE-Advanced", "Note-DrE-Basic"]


def _all_keys(label):
    return {c.key for f in get_report_registry()[label].formats for c in f.attributes}


def test_the_rule_prepends_only_the_missing_columns_in_order():
    cols = [Column(name="Description", key="description"), Column(name="GUID", key="guid")]
    out = _lead_with_universal_columns(cols, {"display_name", "qualified_name", "description"})
    assert [c.key for c in out] == ["display_name", "qualified_name", "description", "guid"]


def test_the_rule_gives_guid_but_not_absent_attributes():
    out = _lead_with_universal_columns([Column(name="D", key="description")], {"description"})
    assert [c.key for c in out] == ["guid", "description"]


def test_an_unknown_target_type_gets_nothing():
    cols = [Column(name="D", key="description")]
    assert _lead_with_universal_columns(cols, None) == cols


def test_the_specs_that_showed_no_name_or_guid_now_do():
    for label in GAINED:
        assert {"display_name", "qualified_name", "guid"} <= _all_keys(label), label


def test_the_new_columns_lead_the_list_format():
    fs = get_report_registry()["Secrets-Store-Element-DrE-Advanced"]
    list_format = next(f for f in fs.formats if "LIST" in f.types)
    assert [c.key for c in list_format.attributes][:3] == ["display_name", "qualified_name", "guid"]


def test_every_generated_spec_with_an_entity_target_has_a_guid():
    # OpenMetadataTypeDef (Enum Def, Type Def) is a type definition, not an element: it has no catalog entry
    # (target_attrs is None), so the rule leaves it alone
    missing = [l for l, fs in get_report_registry().items() if "-DrE-" in l and fs.target_type != "OpenMetadataTypeDef"
               and not any(c.key == "guid" for f in fs.formats for c in f.attributes)]
    assert missing == []
