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
    element_dictionary[key] = value

def clear_element_dictionary():
    """
    Clear the shared element dictionary.
    """
    global element_dictionary
    element_dictionary.clear()