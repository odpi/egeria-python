import pytest

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
        col['value'] = element.get(key)
    return columns_struct


def test_dict_output_duplicate_display_names_are_suffixed():
    # Element has two values: one under 'guid' and one under 'GUID'
    element = {
        'elementHeader': {'guid': 'header-guid-123'},
        'properties': {},
        # Simulate additional fields exposed by extractor via keys
        'guid': 'guid-lower-value',
        'GUID': 'guid-upper-value',
    }

    # columns_struct requests two columns that intentionally share the same display name
    columns_struct = {
        'formats': {
            'attributes': [
                {'name': 'GUID', 'key': 'guid'},
                {'name': 'GUID', 'key': 'GUID'},
            ]
        }
    }

    # Run generation
    rows = generate_entity_dict(
        elements=[element],
        extract_properties_func=fake_extract,
        columns_struct=columns_struct,
        output_format='DICT',
    )

    assert isinstance(rows, list) and len(rows) == 1
    row = rows[0]

    # We expect the colliding display names to be preserved with suffixing
    # One key should be 'GUID' and the next should be 'GUID_1'
    assert 'GUID' in row
    assert any(k.startswith('GUID_') for k in row.keys() if k != 'GUID')

    # Values should match the element based on their keys
    # Order is not guaranteed; discover which is which
    vals = {k: v for k, v in row.items() if k.startswith('GUID')}
    assert 'guid-lower-value' in vals.values()
    assert 'guid-upper-value' in vals.values()