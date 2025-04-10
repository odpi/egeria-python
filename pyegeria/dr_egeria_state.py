"""
This module provides shared state for the pyegeria package.
It contains variables that need to be accessed and modified by multiple modules.
"""

# Dictionary to store element information to avoid redundant API calls
element_dictionary = {}

def get_element_dictionary():
    """
    Get the shared element dictionary.
    
    Returns:
        dict: The shared element dictionary
    """
    global element_dictionary
    return element_dictionary

def update_element_dictionary(key, value):
    """
    Update the shared element dictionary with a new key-value pair.
    
    Args:
        key (str): The key to update
        value (dict): The value to associate with the key
    """
    global element_dictionary
    if (key is None or value is None):
        print(f"===>ERROR Key is {key} and value is {value}")
        return
    element_dictionary[key] = value

def clear_element_dictionary():
    """
    Clear the shared element dictionary.
    """
    global element_dictionary
    element_dictionary.clear()

def is_present(value: str) -> bool:
    global element_dictionary
    present = value in element_dictionary.keys() or any(value in inner_dict.values() for inner_dict in element_dictionary.values())
    return present

def find_key_with_value( value: str) -> str | None:
    """
    Finds the top-level key whose nested dictionary contains the given value.

    Args:
        data (dict): A dictionary where keys map to nested dictionaries.
        value (str): The value to search for.

    Returns:
        str | None: The top-level key that contains the value, or None if not found.
    """
    global element_dictionary
    # Check if the value matches a top-level key
    if value in element_dictionary.keys():
        return value

    # Check if the value exists in any of the nested dictionaries
    for key, inner_dict in element_dictionary.items():
        if value in inner_dict.values():
            return key

    return None  # If value not found

