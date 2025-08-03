"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module defines Pydantic models for output format sets used in pyegeria.

These models provide a structured way to define and validate output formats
for different types of data, supporting composition and reuse of formats.

The module defines the following models:
- Column: Represents a column in an output format with name, key, and format attributes.
- Format: Represents a format configuration with types and columns.
- ActionParameter: Represents a parameter for an action with function, user_params, and spec_params.
- FormatSet: Represents a complete format set with heading, description, aliases, annotations, formats, and actions.
- FormatSetDict: A dictionary of format sets with methods for backward compatibility.

These models are used in the `_output_formats.py` module to replace the dictionary-based
implementation of output format sets. The models provide several advantages:
- Type validation: The models ensure that the data has the correct types and structure.
- Composition: The models support composition of formats, allowing formats to be reused and combined.
- Documentation: The models provide clear documentation of the data structure.
- IDE support: The models provide better IDE support, including autocompletion and type hints.

Example usage:
```python
from pyegeria._output_format_models import Column, Format, FormatSet

# Create columns
columns = [
    Column(name="Display Name", key="display_name"),
    Column(name="Description", key="description", format=True),
]

# Create a format
format = Format(
    types=["TABLE", "DICT"],
    columns=columns,
)

# Create a format set
format_set = FormatSet(
    heading="Example Format Set",
    description="An example format set",
    formats=[format],
)

# Convert to dictionary for backward compatibility
format_set_dict = format_set.dict()
```

The models are designed to be backward compatible with the existing dictionary-based
implementation. The `FormatSet` class has a `get` method that mimics the behavior of a
dictionary, and the `FormatSetDict` class provides dictionary-like access to the format sets.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator
from loguru import logger

def save_format_sets_to_json(format_sets: Dict[str, 'FormatSet'], file_path: str) -> None:
    """
    Save format sets to a JSON file.
    
    Args:
        format_sets: The format sets to save
        file_path: The path to save the file to
    """
    # Convert FormatSet objects to dictionaries
    serializable_dict = {key: value.dict() for key, value in format_sets.items()}
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    # Write to file
    try:
        with open(file_path, 'w') as f:
            json.dump(serializable_dict, f, indent=2)
        logger.info(f"Format sets saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving format sets to {file_path}: {e}")
        raise

def load_format_sets_from_json(file_path: str) -> Dict[str, 'FormatSet']:
    """
    Load format sets from a JSON file.
    
    Args:
        file_path: The path to load the file from
        
    Returns:
        Dict[str, FormatSet]: The loaded format sets
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Convert dictionaries to FormatSet objects
        format_sets = {}
        for key, value in data.items():
            format_sets[key] = FormatSet(**value)
        
        logger.info(f"Format sets loaded from {file_path}")
        return format_sets
    except Exception as e:
        logger.error(f"Error loading format sets from {file_path}: {e}")
        raise

class Column(BaseModel):
    """
    Represents a column in an output format.
    
    Attributes:
        name: The display name of the column
        key: The key used to access the column's value in the data
        format: Whether the column's value should be formatted
    """
    name: str
    key: str
    format: bool = False

class Format(BaseModel):
    """
    Represents a format configuration with types and columns.
    
    Attributes:
        types: The output types this format supports (e.g., "DICT", "TABLE", "ALL")
        columns: The columns to include in the output
    """
    types: List[str]
    columns: List[Union[Column, Dict[str, Any]]]
    
    @validator('columns', pre=True)
    def validate_columns(cls, v):
        """Convert dictionary columns to Column objects."""
        result = []
        for item in v:
            if isinstance(item, dict):
                result.append(Column(**item))
            else:
                result.append(item)
        return result
    
    def dict(self, *args, **kwargs):
        """Override dict method to convert Column objects back to dictionaries."""
        result = super().dict(*args, **kwargs)
        result['columns'] = [
            column if isinstance(column, dict) else column.dict()
            for column in self.columns
        ]
        return result

class ActionParameter(BaseModel):
    """
    Represents a parameter for an action.
    
    Attributes:
        function: The function to call
        user_params: Parameters that can be provided by the user
        spec_params: Parameters that are fixed for this action
    """
    function: str
    user_params: List[str] = Field(default_factory=list)
    spec_params: Dict[str, Any] = Field(default_factory=dict)

class FormatSet(BaseModel):
    """
    Represents a complete format set with heading, description, aliases, annotations, formats, and actions.
    
    Attributes:
        heading: A title for the format set
        description: A description of what the format set is for
        aliases: Alternative names that can be used to reference this format set
        annotations: Additional metadata, like wiki links
        formats: A list of format configurations
        action: Optional actions associated with the format set
    """
    heading: str
    description: str
    aliases: List[str] = Field(default_factory=list)
    annotations: Dict[str, List[str]] = Field(default_factory=dict)
    formats: List[Union[Format, Dict[str, Any]]]
    action: Optional[List[Union[ActionParameter, Dict[str, Any]]]] = None
    
    @validator('formats', pre=True)
    def validate_formats(cls, v):
        """Convert dictionary formats to Format objects."""
        result = []
        for item in v:
            if isinstance(item, dict):
                result.append(Format(**item))
            else:
                result.append(item)
        return result
    
    @validator('action', pre=True)
    def validate_action(cls, v):
        """Convert dictionary actions to ActionParameter objects."""
        if v is None:
            return None
        result = []
        for item in v:
            if isinstance(item, dict):
                result.append(ActionParameter(**item))
            else:
                result.append(item)
        return result
    
    def dict(self, *args, **kwargs):
        """Override dict method to convert nested objects back to dictionaries."""
        result = super().dict(*args, **kwargs)
        result['formats'] = [
            format if isinstance(format, dict) else format.dict()
            for format in self.formats
        ]
        if self.action:
            result['action'] = [
                action if isinstance(action, dict) else action.dict()
                for action in self.action
            ]
        return result
    
    def get(self, key, default=None):
        """
        Dictionary-like get method for backward compatibility.
        
        Args:
            key: The key to look up
            default: The default value to return if the key is not found
            
        Returns:
            The value for the key if found, otherwise the default value
        """
        if hasattr(self, key):
            return getattr(self, key)
        return default

class FormatSetDict(Dict[str, FormatSet]):
    """
    A dictionary of format sets, with methods for backward compatibility.
    
    This class allows the format sets to be accessed like a dictionary,
    while providing the validation and structure of Pydantic models.
    
    It also provides the ability to find format sets by either name or alias,
    making it easier to work with format sets without knowing their exact name.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def find_by_name_or_alias(self, key, default=None):
        """
        Find a format set by either name or alias.
        
        This method first checks if the key exists directly in the dictionary.
        If not found, it searches through all format sets to find one with a matching alias.
        
        Args:
            key: The name or alias to look up
            default: The default value to return if the key is not found
            
        Returns:
            FormatSet: The format set if found, otherwise the default value
        """
        # First try to find by name (key)
        format_set = super().get(key, None)
        
        # If not found by name, try to find by alias
        if format_set is None:
            for value in self.values():
                if key in value.aliases:
                    format_set = value
                    break
        
        # Return the format set if found, otherwise the default value
        return format_set if format_set is not None else default
    
    def get(self, key, default=None):
        """
        Get a format set by name or alias.
        
        This method first checks if the key exists directly in the dictionary.
        If not found, it searches through all format sets to find one with a matching alias.
        
        Args:
            key: The name or alias to look up
            default: The default value to return if the key is not found
            
        Returns:
            FormatSet: The format set if found, otherwise the default value
        """
        return self.find_by_name_or_alias(key, default)
    
    def values(self):
        """Get all format sets."""
        return super().values()
    
    def keys(self):
        """Get all format set names."""
        return super().keys()
    
    def items(self):
        """Get all format set items."""
        return super().items()
    
    def __getitem__(self, key):
        """
        Get a format set by name or alias.
        
        This method first checks if the key exists directly in the dictionary.
        If not found, it searches through all format sets to find one with a matching alias.
        If still not found, it raises a KeyError.
        
        Args:
            key: The name or alias to look up
            
        Returns:
            FormatSet: The format set if found
            
        Raises:
            KeyError: If the format set is not found by name or alias
        """
        format_set = self.find_by_name_or_alias(key, None)
        if format_set is None:
            raise KeyError(key)
        return format_set
    
    def __setitem__(self, key, value):
        """Set a format set by name."""
        if isinstance(value, dict):
            value = FormatSet(**value)
        super().__setitem__(key, value)
    
    def __contains__(self, key):
        """
        Check if a format set exists by name or alias.
        
        Args:
            key: The name or alias to check
            
        Returns:
            bool: True if the format set exists, False otherwise
        """
        return self.find_by_name_or_alias(key, None) is not None
    
    def to_dict(self):
        """Convert all format sets to dictionaries."""
        return {key: value.dict() for key, value in self.items()}
        
    def save_to_json(self, file_path: str) -> None:
        """
        Save format sets to a JSON file.
        
        Args:
            file_path: The path to save the file to
        """
        save_format_sets_to_json(self, file_path)
    
    @classmethod
    def load_from_json(cls, file_path: str) -> 'FormatSetDict':
        """
        Load format sets from a JSON file.
        
        Args:
            file_path: The path to load the file from
            
        Returns:
            FormatSetDict: A new FormatSetDict instance with the loaded format sets
        """
        format_sets = load_format_sets_from_json(file_path)
        return cls(format_sets)