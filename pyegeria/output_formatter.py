from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from rich.console import Console

console = Console(width= 250)
# Constants
MD_SEPARATOR = "\n---\n\n"

def make_preamble(obj_type: str, search_string: str, output_format: str = 'MD') -> Tuple[str, Optional[str]]:
    """
    Creates a preamble string and an elements action based on the given object type, search string,
    and output format.

    Args:
        obj_type: The type of object being updated or reported on (e.g., "Product", "Category").
        search_string: The search string used to filter objects. Defaults to "All Elements" if None.
        output_format: A format identifier determining the output structure.
            JSON - output standard json
            MD - output standard markdown with no preamble
            FORM - output markdown with a preamble for a form
            REPORT - output markdown with a preamble for a report

    Returns:
        tuple: A tuple containing:
            - A string representing the formatted update or report preamble.
            - A string or None indicating the action description for the elements,
              depending on the output format.
    """
    search_string = search_string if search_string else "All Elements"
    elements_action = "Update " + obj_type
    if output_format == "FORM":
        preamble = (f"\n# Update {obj_type} Form - created at {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                    f"\t {obj_type} found from the search string:  `{search_string}`\n\n")
        return preamble, elements_action
    elif output_format == "REPORT":
        elements_md = (f"# {obj_type} Report - created at {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                       f"\t{obj_type}  found from the search string:  `{search_string}`\n\n")
        elements_action = None
        return elements_md, elements_action
    else:
        return "\n", elements_action

def make_md_attribute(attribute_name: str, attribute_value: str, output_type: str) -> Optional[str]:
    """
    Create a markdown attribute line for a given attribute name and value.

    Args:
        attribute_name: The name of the attribute
        attribute_value: The value of the attribute
        output_type: The output format (FORM, MD, REPORT)

    Returns:
        str: Formatted markdown for the attribute
    """
    output = ""
    attribute_value = attribute_value.strip() if attribute_value else ""
    attribute_title = attribute_name.title() if attribute_name else ""
    if output_type in ["FORM", "MD"]:
        output = f"## {attribute_title}\n{attribute_value}\n\n"
    elif output_type == "REPORT":
        if attribute_value:
            output = f"## {attribute_title}\n{attribute_value}\n\n"
    return output

def format_for_markdown_table(text: str) -> str:
    """
    Format text for markdown tables by replacing newlines with spaces and escaping pipe characters.
    No truncation is applied to allow full-length text display regardless of console width.

    Args:
        text (str): The text to format

    Returns:
        str: Formatted text safe for markdown tables
    """
    if not text:
        return ""
    # Replace newlines with spaces and escape pipe characters
    return text.replace("\n", " ").replace("|", "\\|")

def generate_entity_md(elements: List[Dict], 
                      elements_action: str, 
                      output_format: str, 
                      entity_type: str,
                      extract_properties_func: Callable, 
                      get_additional_props_func: Optional[Callable] = None) -> str:
    """
    Generic method to generate markdown for entities.

    Args:
        elements (list): List of entity elements
        elements_action (str): Action description for elements
        output_format (str): Output format
        entity_type (str): Type of entity (Glossary, Term, Category, etc.)
        extract_properties_func: Function to extract properties from an element
        get_additional_props_func: Optional function to get additional properties

    Returns:
        str: Markdown representation
    """
    elements_md = ""

    for element in elements:
        props = extract_properties_func(element)

        # Get additional properties if function is provided
        additional_props = {}
        if get_additional_props_func:
            additional_props = get_additional_props_func(element, props['guid'], output_format)

        # Format header based on output format
        if output_format in ['FORM', 'MD']:
            elements_md += f"# {elements_action}\n\n"
            elements_md += f"## {entity_type} Name \n\n{props['display_name']}\n\n"
        elif output_format == 'REPORT':
            elements_md += f"# {entity_type} Name: {props['display_name']}\n\n"
        else:
            elements_md += f"## {entity_type} Name \n\n{props['display_name']}\n\n"

        # Add common attributes
        for key, value in props.items():
            if key not in ['guid', 'properties', 'display_name']:
                elements_md += make_md_attribute(key.replace('_', ' '), value, output_format)

        # Add additional properties
        for key, value in additional_props.items():
            elements_md += make_md_attribute(key.replace('_', ' '), value, output_format)

        # Add GUID
        elements_md += make_md_attribute("GUID", props['guid'], output_format)

        # Add separator if not the last element
        if element != elements[-1]:
            elements_md += MD_SEPARATOR

    return elements_md

def generate_entity_md_table(elements: List[Dict], 
                            search_string: str, 
                            entity_type: str, 
                            extract_properties_func: Callable,
                            columns: List[Dict], 
                            get_additional_props_func: Optional[Callable] = None, 
                            output_format: str = 'LIST') -> str:
    """
    Generic method to generate a markdown table for entities.

    Args:
        elements (list): List of entity elements
        search_string (str): The search string used
        entity_type (str): Type of entity (Glossary, Term, Category, etc.)
        extract_properties_func: Function to extract properties from an element
        columns: List of column definitions, each containing 'name', 'key', and 'format' (optional)
        get_additional_props_func: Optional function to get additional properties
        output_format (str): Output format (FORM, REPORT, LIST, etc.)

    Returns:
        str: Markdown table
    """
    # Handle pluralization - if entity_type ends with 'y', use 'ies' instead of 's'
    entity_type_plural = f"{entity_type[:-1]}ies" if entity_type.endswith('y') else f"{entity_type}s"

    elements_md = f"# {entity_type_plural} Table\n\n"
    elements_md += f"{entity_type_plural} found from the search string: `{search_string}`\n\n"

    # Add column headers
    header_row = "| "
    separator_row = "|"
    for column in columns:
        header_row += f"{column['name']} | "
        separator_row += "-------------|"

    elements_md += header_row + "\n"
    elements_md += separator_row + "\n"

    # Add rows
    for element in elements:
        props = extract_properties_func(element)

        # Get additional properties if function is provided
        additional_props = {}
        if get_additional_props_func:
            additional_props = get_additional_props_func(element, props['guid'], output_format)

        # Build row
        row = "| "
        for column in columns:
            key = column['key']
            value = ""

            # Check if the key is in props or additional_props
            if key in props:
                value = props[key]
            elif key in additional_props:
                value = additional_props[key]

            # Format the value if needed
            if 'format' in column and column['format']:
                value = format_for_markdown_table(value)

            row += f"{value} | "

        elements_md += row + "\n"

    return elements_md

def generate_entity_dict(elements: List[Dict], 
                        extract_properties_func: Callable, 
                        get_additional_props_func: Optional[Callable] = None,
                        include_keys: Optional[List[str]] = None, 
                        exclude_keys: Optional[List[str]] = None, 
                        output_format: str = 'DICT') -> List[Dict]:
    """
    Generic method to generate a dictionary representation of entities.

    Args:
        elements (list): List of entity elements
        extract_properties_func: Function to extract properties from an element
        get_additional_props_func: Optional function to get additional properties
        include_keys: Optional list of keys to include in the result (if None, include all)
        exclude_keys: Optional list of keys to exclude from the result (if None, exclude none)
        output_format (str): Output format (FORM, REPORT, DICT, etc.)

    Returns:
        list: List of entity dictionaries
    """
    result = []

    for element in elements:
        props = extract_properties_func(element)

        # Get additional properties if function is provided
        additional_props = {}
        if get_additional_props_func:
            additional_props = get_additional_props_func(element, props['guid'], output_format)

        # Create entity dictionary
        entity_dict = {}

        # Add properties based on include/exclude lists
        for key, value in props.items():
            if key != 'properties':  # Skip the raw properties object
                if (include_keys is None or key in include_keys) and (
                        exclude_keys is None or key not in exclude_keys):
                    entity_dict[key] = value

        # Add additional properties
        for key, value in additional_props.items():
            if (include_keys is None or key in include_keys) and (exclude_keys is None or key not in exclude_keys):
                entity_dict[key] = value

        result.append(entity_dict)

    return result

def extract_mermaid_only(elements: Union[Dict, List[Dict]]) -> Union[str, List[str]]:
    """
    Extract mermaid graph data from elements.

    Args:
        elements: Dictionary or list of dictionaries containing element data

    Returns:
        String or list of strings containing mermaid graph data
    """
    if isinstance(elements, dict):
        return elements.get('mermaidGraph', '___')

    result = []
    for element in elements:
        result.append(element.get('mermaidGraph', '___'))
    return result

def extract_basic_dict(elements: Union[Dict, List[Dict]]) -> Union[Dict, List[Dict]]:
    """
    Extract basic dictionary data from elements.

    Args:
        elements: Dictionary or list of dictionaries containing element data

    Returns:
        Dictionary or list of dictionaries with extracted data
    """
    if isinstance(elements, dict):
        body = {'guid': elements['elementHeader']['guid']}
        for key in elements['properties']:
            body[key] = elements['properties'][key]

        # Add classifications if present
        classifications = elements['elementHeader'].get('classifications', [])
        if classifications:
            classification_names = ""
            for classification in classifications:
                classification_names += f"* {classification['classificationName']}\n"
            body['classification_names'] = classification_names

        return body

    result = []
    for element in elements:
        body = {'guid': element['elementHeader']['guid']}
        for key in element['properties']:
            body[key] = element['properties'][key]

        # Add classifications if present
        classifications = element['elementHeader'].get('classifications', [])
        if classifications:
            classification_names = ""
            for classification in classifications:
                classification_names += f"* {classification['classificationName']}\n"
            body['classifications'] = classification_names

        result.append(body)
    return result

def generate_output(elements: Union[Dict, List[Dict]], 
                   search_string: str,
                   entity_type: str,
                   output_format: str,
                   extract_properties_func: Callable,
                   get_additional_props_func: Optional[Callable] = None,
                   columns: Optional[List[Dict]] = None) -> Union[str, List[Dict]]:
    """
    Generate output in the specified format for the given elements.

    Args:
        elements: Dictionary or list of dictionaries containing element data
        search_string: The search string used to find the elements
        entity_type: The type of entity (e.g., "Glossary", "Term", "Category")
        output_format: The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID)
        extract_properties_func: Function to extract properties from an element
        get_additional_props_func: Optional function to get additional properties
        columns: Optional list of column definitions for table output

    Returns:
        Formatted output as string or list of dictionaries
    """
    # Ensure elements is a list
    if isinstance(elements, dict):
        elements = [elements]

    # Handle empty search string
    if search_string is None or search_string == '':
        search_string = "All"

    # Generate output based on format
    if output_format == 'MERMAID':
        return extract_mermaid_only(elements)

    elif output_format == 'DICT':
        return generate_entity_dict(
            elements=elements,
            extract_properties_func=extract_properties_func,
            get_additional_props_func=get_additional_props_func,
            exclude_keys=['properties'],
            output_format=output_format
        )

    elif output_format == 'LIST':
        if columns is None:
            raise ValueError("Columns must be provided for LIST output format")

        return generate_entity_md_table(
            elements=elements,
            search_string=search_string,
            entity_type=entity_type,
            extract_properties_func=extract_properties_func,
            columns=columns,
            get_additional_props_func=get_additional_props_func,
            output_format=output_format
        )

    else:  # MD, FORM, REPORT
        elements_md, elements_action = make_preamble(
            obj_type=entity_type,
            search_string=search_string,
            output_format=output_format
        )

        elements_md += generate_entity_md(
            elements=elements,
            elements_action=elements_action,
            output_format=output_format,
            entity_type=entity_type,
            extract_properties_func=extract_properties_func,
            get_additional_props_func=get_additional_props_func
        )

        return elements_md
