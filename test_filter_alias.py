#!/usr/bin/env python3
"""Test that FilterRequestBody model works correctly with alias"""

import sys
sys.path.insert(0, '.')

from pydantic import Field, ValidationError
from typing import Annotated, Literal

# Simplified version of the model to test
class TestFilterRequestBody:
    """Test the filter alias"""
    pass

# Direct test
from pydantic import BaseModel

class FilterRequestBody(BaseModel):
    class Config:
        populate_by_name = True  # Allow both alias and field name
    
    class_: Annotated[Literal["FilterRequestBody"], Field(alias="class")]
    filter_string: Annotated[str, Field(alias="filter")]

# Test 1: Create with 'filter' key (what we pass in dict)
try:
    body_dict = {
        'class': 'FilterRequestBody',
        'filter': 'test_value',
    }
    model = FilterRequestBody.model_validate(body_dict)
    print('✓ Test 1 PASSED: Model accepts "filter" key in dict')
    
    # Test 2: Check JSON output has 'filter' not 'filter_string'
    json_output = model.model_dump_json(by_alias=True, exclude_none=True)
    print(f'✓ Test 2: JSON output = {json_output}')
    
    if '"filter"' in json_output and '"filter_string"' not in json_output:
        print('✓ Test 3 PASSED: JSON uses "filter" key (correct for Egeria)')
    else:
        print('✗ Test 3 FAILED: JSON has wrong key')
        
except ValidationError as e:
    print(f'✗ FAILED: {e}')