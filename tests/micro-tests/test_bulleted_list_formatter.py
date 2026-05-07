import pytest
from pyegeria.view.output_formatter import generate_entity_md_table
from pyegeria.view._output_format_models import Column
from typing import List, Dict

def test_generate_entity_md_table_with_column_objects():
    # Construct columns as Column objects
    columns = [
        Column(name="Members", key="members", format="bulleted-list"),
    ]
    columns_struct = {
        "target_type": "Collection",
        "formats": {
            "attributes": columns
        }
    }
    
    # Mock extractor function that returns a Column object in the struct
    def extract_props(element, struct):
        # Return a struct where 'attributes' is a list of Column objects
        # We need to set the value for the 'members' key
        col = Column(name="Members", key="members", format="bulleted-list", value=['a', 'b', 'c'])
        return {
            'formats': {
                'attributes': [col]
            }
        }
    
    elements = [{"elementHeader": {"guid": "123"}}]
    
    # This should not raise AttributeError
    try:
        out = generate_entity_md_table(
            elements=elements,
            search_string="*",
            entity_type="Collection",
            extract_properties_func=extract_props,
            columns_struct=columns_struct,
            output_format="LIST"
        )
        assert "a" in out
        assert "b" in out
        assert "c" in out
        assert "<ul>" in out or "<li>" in out or "<br>" in out # Check for bulleted formatting
    except AttributeError as e:
        pytest.fail(f"generate_entity_md_table raised AttributeError: {e}")
