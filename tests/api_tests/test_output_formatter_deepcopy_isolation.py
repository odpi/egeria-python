from pyegeria.output_formatter import generate_entity_dict


def fake_extract(element: dict, columns_struct: dict | None = None):
    """Populate provided columns_struct values from element by key.
    This mimics the extract_properties_func contract used by generate_entity_dict
    when a columns_struct is provided.
    """
    if columns_struct is None:
        return element
    fmt = columns_struct.get('formats', {})
    cols = fmt.get('attributes', [])
    for col in cols:
        key = col.get('key')
        if key is None:
            continue
        # simulate populate_common_columns header overlay behavior
        # prefer explicit element key (already set on element), fallback to properties
        col['value'] = element.get(key)
    return columns_struct


def test_generate_entity_dict_uses_per_element_copy_to_avoid_leakage():
    # Two elements with distinct guids and qualified names
    e1 = {
        'elementHeader': {'guid': 'guid-1'},
        'properties': {'qualifiedName': 'Q1', 'displayName': 'D1'},
        'guid': 'guid-1',
        'qualified_name': 'Q1',
        'type_name': 'TypeA',
    }
    e2 = {
        'elementHeader': {'guid': 'guid-2'},
        'properties': {'qualifiedName': 'Q2', 'displayName': 'D2'},
        'guid': 'guid-2',
        'qualified_name': 'Q2',
        'type_name': 'TypeB',
    }

    columns_struct = {
        'formats': {
            'attributes': [
                {'name': 'Qualified Name', 'key': 'qualified_name'},
                {'name': 'GUID', 'key': 'guid'},
                {'name': 'Type Name', 'key': 'type_name'},
            ]
        }
    }

    rows = generate_entity_dict(
        elements=[e1, e2],
        extract_properties_func=fake_extract,
        columns_struct=columns_struct,
        output_format='DICT',
    )

    assert isinstance(rows, list) and len(rows) == 2

    r1, r2 = rows
    # Ensure no value leakage: each row's GUID and Qualified Name correspond to its own element
    assert r1['GUID'] == 'guid-1'
    assert r1['Qualified Name'] == 'Q1'
    assert r1['Type Name'] == 'TypeA'

    assert r2['GUID'] == 'guid-2'
    assert r2['Qualified Name'] == 'Q2'
    assert r2['Type Name'] == 'TypeB'
