from pyegeria.view.output_formatter import generate_output, populate_columns_from_properties


def test_generate_output_list_handles_none_target_type_in_columns_struct():
    columns_struct = {
        "target_type": None,
        "heading": "Default Base Attributes",
        "formats": {
            "attributes": [
                {"name": "Display Name", "key": "display_name"},
                {"name": "Qualified Name", "key": "qualified_name"},
            ]
        },
    }

    elements = [
        {
            "elementHeader": {"guid": "123"},
            "properties": {
                "displayName": "Sample",
                "qualifiedName": "Sample::1",
            },
        }
    ]

    out = generate_output(
        elements=elements,
        search_string="*",
        entity_type=None,
        output_format="LIST",
        extract_properties_func=populate_columns_from_properties,
        columns_struct=columns_struct,
    )

    assert isinstance(out, str)
    assert "Referenceables Table" in out
    assert "Sample" in out

