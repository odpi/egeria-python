from datetime import datetime
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from pyegeria.utils import (camel_to_title_case)
from markdown_it import MarkdownIt
from rich.console import Console
from loguru import logger

from pyegeria.mermaid_utilities import construct_mermaid_web
from pyegeria._output_formats import select_output_format_set, MD_SEPARATOR

"""
Note on select_output_format_set function:

This function and related data structures have been moved back to _output_formats.py.
Please import select_output_format_set from pyegeria._output_formats instead of from this module.
"""

console = Console(width= 250)


def _extract_referenceable_properties(element: dict[str, Any]) -> dict[str, Any]:
    # Get general header attributes
    guid = element['elementHeader'].get("guid", None)
    metadata_collection_id = element['elementHeader']['origin'].get("homeMetadataCollectionId", None)
    metadata_collection_name = element['elementHeader']['origin'].get("homeMetadataCollectionName", None)
    origin_category = element['elementHeader'].get("origin_category", None)
    created_by = element['elementHeader']["versions"].get("createdBy", None)
    create_time = element['elementHeader']["versions"].get("createTime", None)
    updated_by = element['elementHeader']["versions"].get("updatedBy", None)
    version = element['elementHeader']["versions"].get("version", None)
    type_name = element['elementHeader']["type"].get("typeName", None)
    classifications = element['elementHeader'].get("classifications", [])

    # Get attributes from properties
    properties = element['properties']
    display_name = properties.get("name", "") or ""
    if display_name == "":
        display_name = properties.get("displayName","")
    description = properties.get("description", "") or ""
    qualified_name = properties.get("qualifiedName", "") or ""
    category = properties.get("category", "") or ""
    version_identifier = properties.get("versionIdentifier", "") or ""
    additional_properties = properties.get("additionalProperties", {}) or {}
    extended_properties = properties.get("extendedProperties", {}) or {}
    effective_from = element['elementHeader'].get("effectiveFrom", None)
    effective_to = element['elementHeader'].get("effectiveTo", None)

    return {
        "GUID": guid,
        "metadata_collection_id": metadata_collection_id,
        "metadata_collection_name": metadata_collection_name,
        "origin_category": origin_category,
        "created_by": created_by,
        "create_time": create_time,
        "updated_by": updated_by,
        "version": version,
        "type_name": type_name,
        "classifications": classifications,

        "display_name": display_name,
        "description": description,
        "qualified_name": qualified_name,
        "category": category,
        "version_identifier": version_identifier,
        "additional_properties": additional_properties,
        "extended_properties": extended_properties,
        "effective_from": effective_from,
        "effective_to": effective_to,
        }






def markdown_to_html(markdown_text: str) -> str:
    """
    Convert markdown text to HTML, with special handling for mermaid code blocks.

    Args:
        markdown_text: The markdown text to convert

    Returns:
        HTML string
    """
    # Initialize markdown-it
    md = MarkdownIt()

    # Find all mermaid code blocks
    mermaid_blocks = re.findall(r'```mermaid\n(.*?)\n```', markdown_text, re.DOTALL)

    # Replace each mermaid block with a placeholder
    placeholders = []
    for i, block in enumerate(mermaid_blocks):
        placeholder = f"MERMAID_PLACEHOLDER_{i}"
        markdown_text = markdown_text.replace(f"```mermaid\n{block}\n```", placeholder)
        placeholders.append((placeholder, block))

    # Convert markdown to HTML
    html_text = md.render(markdown_text)

    # Replace placeholders with rendered mermaid HTML
    for placeholder, mermaid_block in placeholders:
        mermaid_html = construct_mermaid_web(mermaid_block)
        html_text = html_text.replace(placeholder, mermaid_html)

    # Add basic HTML structure
    html_text = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Egeria Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #3498db; }}
            pre {{ background-color: #f8f8f8; padding: 10px; border-radius: 5px; overflow-x: auto; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        {html_text}
    </body>
    </html>
    """

    return html_text

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
    # search_string = search_string if search_string else "All Elements"
    elements_md = ""
    elements_action = "Update " + obj_type
    if output_format == "FORM":
        preamble = f"\n# Update {obj_type} Form - created at {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        if search_string:
            preamble +=  f"\t {obj_type} found from the search string:  `{search_string}`\n\n"
        return preamble, elements_action
    elif output_format == "REPORT":
        elements_md += (f"# {obj_type} Report - created at {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
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
    if isinstance(attribute_value,str):
        attribute_value = attribute_value.strip() if attribute_value else ""
    elif isinstance(attribute_value,list) and len(attribute_value) > 0:
        attribute_value = ",\n".join(attribute_value)
    if attribute_name:
        if attribute_name.upper() == "GUID":
            attribute_title = attribute_name.upper()
        else:
            # attribute_title = attribute_name.title()
            attribute_title = camel_to_title_case(attribute_name)
    else:
        attribute_title = ""

    if output_type in ["FORM", "MD"]:
        if attribute_name.lower() in [ "mermaid", "links", "implemented by", "sub_components"]:
            return '\n'

        output = f"## {attribute_title}\n{attribute_value}\n\n"
    elif output_type == "REPORT":
        if attribute_title in ['Mermaid Graph', 'Mermaid']:
            output = f"## Mermaid Graph\n\n```mermaid\n{attribute_value}\n```\n"
        elif attribute_value:
            output = f"## {attribute_title}\n{attribute_value}\n\n"
    return output

def format_for_markdown_table(text: str, guid: str = None) -> str:
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
    if isinstance(text, list):
        text = "\n".join(text)
    t = text.replace("\n", " ").replace("|", "\\|")
    if '::' in t and guid:
        t = f" [{t}](#{guid}) "
    return t


def generate_entity_md(elements: List[Dict],
                      elements_action: str, 
                      output_format: str, 
                      entity_type: str,
                      extract_properties_func: Callable, 
                      get_additional_props_func: Optional[Callable] = None,
                       columns_struct: [dict] = None) -> str:
    """
    Generic method to generate markdown for entities.

    Args:
        elements (list): List of entity elements
        elements_action (str): Action description for elements
        output_format (str): Output format
        entity_type (str): Type of entity (Glossary, Term, Category, etc.)
        extract_properties_func: Function to extract properties from an element
        get_additional_props_func: Optional function to get additional properties
        columns (list): List of column name structures

    Returns:
        str: Markdown representation
    """
    elements_md = ""
    columns = columns_struct['formats'].get('columns') if columns_struct else None

    for element in elements:
        if element is None:
            continue
        props = extract_properties_func(element)

        # Get additional properties if function is provided
        additional_props = {}
        if get_additional_props_func:
            additional_props = get_additional_props_func(element,props['GUID'], output_format)

        display_name = props.get('display_name', None)
        if display_name is None:
            display_name = props.get('title', None)
            if display_name is None:
                display_name = "NO DISPLAY NAME"

        # Format header based on output format
        if output_format in ['FORM', 'MD']:
            elements_md += f"# {elements_action}\n\n"
            elements_md += f"## {entity_type} Name \n\n{display_name}\n\n"
        elif output_format == 'REPORT':
            elements_md += f'<a id="{props.get("GUID","No GUID")}"></a>\n# {entity_type} Name: {display_name}\n\n'
        else:
            elements_md += f"## {entity_type} Name \n\n{display_name}\n\n"

       # Add attributes based on column spec if available, otherwise, add all
        if columns:
            for column in columns:
                key = column['key']
                name = column['name']
                value = ""

                # Check if the key is in props or additional_props
                if key in props:
                    value = props[key]
                elif key in additional_props:
                    value = additional_props[key]
                # Format the value if needed
                if 'format' in column and column['format']:
                    value = format_for_markdown_table(value, props['GUID'])
                # elements_md += make_md_attribute(key.replace('_', ' '), value, output_format)
                elements_md += make_md_attribute(name, value, output_format)

        else:
            for key, value in props.items():
                if output_format in ['FORM', 'MD', 'DICT'] and key == 'mermaid':
                    continue
                if key not in [ 'properties', 'display_name']:
                    if key == "mermaid" and value == '':
                        continue
                    elements_md += make_md_attribute(key.replace('_', ' '), value, output_format)
            # Add additional properties
            for key, value in additional_props.items():
                elements_md += make_md_attribute(key.replace('_', ' '), value, output_format)

        # # Add GUID
        # elements_md += make_md_attribute("GUID",props['GUID'], output_format)

        if wk := columns_struct.get("annotations", {}).get("wikilinks", None):
            elements_md += ", ".join(wk)
        # Add separator if not the last element
        if element != elements[-1]:
            elements_md += MD_SEPARATOR

    return elements_md

def generate_entity_md_table(elements: List[Dict], 
                            search_string: str, 
                            entity_type: str, 
                            extract_properties_func: Callable,
                            columns_struct: dict,
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
    columns = columns_struct['formats'].get('columns', [])

    elements_md = ""
    if output_format == "LIST":
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
        if output_format == "help":
            props = element
        else:
            props = extract_properties_func(element)

        # Get additional properties if function is provided
        additional_props = {}
        if get_additional_props_func:
            additional_props = get_additional_props_func(element,props['GUID'], output_format)

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
                value = format_for_markdown_table(value, props['GUID'])

            row += f"{value} | "

        elements_md += row + "\n"
        if wk := columns_struct.get("annotations",{}).get("wikilinks", None):
            elements_md += ", ".join(wk)
    return elements_md

def generate_entity_dict(elements: List[Dict], 
                        extract_properties_func: Callable, 
                        get_additional_props_func: Optional[Callable] = None,
                        include_keys: Optional[List[str]] = None, 
                        exclude_keys: Optional[List[str]] = None,
                        columns_struct: dict = None,
                        output_format: str = 'DICT') -> List[Dict]:
    """
    Generic method to generate a dictionary representation of entities.

    Args:
        elements (list): List of entity elements
        extract_properties_func: Function to extract properties from an element
        get_additional_props_func: Optional function to get additional properties
        include_keys: Optional list of keys to include in the result (if None, include all)
        exclude_keys: Optional list of keys to exclude from the result (if None, exclude none)
        columns_struct: Optional dict of columns to include (if None, include all)
        output_format (str): Output format (FORM, REPORT, DICT, etc.)

    Returns:
        list: List of entity dictionaries
    """
    result = []

#####
    # Add attributes based on column spec if available, otherwise, add all
    for element in elements:
        if element is None:
            continue
        props = extract_properties_func(element)
        # Get additional properties if function is provided
        additional_props = {}
        if get_additional_props_func:
            additional_props = get_additional_props_func(element,props['GUID'], output_format)

        # Create entity dictionary
        entity_dict = {}

        columns = columns_struct['formats'].get('columns', None) if columns_struct else None
        if columns:
            for column in columns:
                key = column['key']
                name = column['name']
                value = ""

                # Check if the key is in props or additional_props
                if key in props:
                    value = props[key]
                elif key in additional_props:
                    value = additional_props[key]
                # Format the value if needed
                if  column.get('format', None):
                    value = format_for_markdown_table(value, props['GUID'])
                entity_dict[name] = value

        else:
            # Add properties based on include/exclude lists
            for key, value in props.items():
                if key not in ['properties', 'mermaid']:  # Skip the raw properties object
                    if (include_keys is None or key in include_keys) and (
                            exclude_keys is None or key not in exclude_keys):
                        entity_dict[key] = value

            # Add additional properties
            for key, value in additional_props.items():
                if (include_keys is None or key in include_keys) and (exclude_keys is None or key not in exclude_keys):
                    entity_dict[key] = value

        result.append(entity_dict)
    #####
    # for element in elements:
    #     if element is None:
    #         continue
    #     props = extract_properties_func(element)
    #
    #     # Get additional properties if function is provided
    #     additional_props = {}
    #     if get_additional_props_func:
    #         additional_props = get_additional_props_func(element,props['GUID'], output_format)
    #
    #     # Create entity dictionary
    #     entity_dict = {}
    #
    #     # Add properties based on include/exclude lists
    #     for key, value in props.items():
    #         if key not in [ 'properties', 'mermaid']:  # Skip the raw properties object
    #             if (include_keys is None or key in include_keys) and (
    #                     exclude_keys is None or key not in exclude_keys):
    #                 entity_dict[key] = value
    #
    #     # Add additional properties
    #     for key, value in additional_props.items():
    #         if (include_keys is None or key in include_keys) and (exclude_keys is None or key not in exclude_keys):
    #             entity_dict[key] = value
    #
    #     result.append(entity_dict)

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
            classification_names = "["
            for classification in classifications:
                if len(classification_names) > 1:
                    classification_names += ", "
                classification_names += f"{classification['classificationName']}"
            body['classification_names'] = classification_names + ']'

        return body

    result = []
    for element in elements:
        if element is None:
            continue
        body = {'guid': element['elementHeader']['guid']}
        for key in element['properties']:
            body[key] = element['properties'][key]

        # Add classifications if present
        classifications = element['elementHeader'].get('classifications', [])
        if classifications:
            classification_names = "["
            for classification in classifications:
                if len(classification_names) > 1:
                    classification_names += ", "
                classification_names += f"{classification['classificationName']}"
            body['classifications'] = classification_names + ']'

        result.append(body)
    return result

def generate_output(elements: Union[Dict, List[Dict]], 
                   search_string: str,
                   entity_type: str,
                   output_format: str,
                   extract_properties_func: Callable,
                   get_additional_props_func: Optional[Callable] = None,
                   columns_struct: dict = None) -> Union[str, list[dict]]:
    """
    Generate output in the specified format for the given elements.

    Args:
        elements: Dictionary or list of dictionaries containing element data
        search_string: The search string used to find the elements
        entity_type: The type of entity (e.g., "Glossary", "Term", "Category")
        output_format: The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID, HTML)
        extract_properties_func: Function to extract properties from an element
        get_additional_props_func: Optional function to get additional properties
        columns: Optional list of column definitions for table output

    Returns:
        Formatted output as string or list of dictionaries
    """
    columns = columns_struct['formats'].get('columns',None) if columns_struct else None
    # Ensure elements is a list
    if isinstance(elements, dict):
        elements = [elements]

    # Handle empty search string
    if search_string is None or search_string == '':
        search_string = "All"

    # Generate output based on format
    if output_format == 'MERMAID':
        return extract_mermaid_only(elements)

    elif output_format == 'HTML':
        # First generate the REPORT format output
        report_output = generate_output(
            elements=elements,
            search_string=search_string,
            entity_type=entity_type,
            output_format="REPORT",
            extract_properties_func=extract_properties_func,
            get_additional_props_func=get_additional_props_func,
            columns_struct=columns_struct
        )

        # Convert the markdown to HTML
        return markdown_to_html(report_output)

    elif output_format == 'DICT':
        return generate_entity_dict(
            elements=elements,
            extract_properties_func=extract_properties_func,
            get_additional_props_func=get_additional_props_func,
            exclude_keys=['properties'],
            columns_struct=columns_struct,
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
            columns_struct=columns_struct,
            get_additional_props_func=get_additional_props_func,
            output_format=output_format
        )

    else:  #  MD, FORM, REPORT
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
            get_additional_props_func=get_additional_props_func,
            columns_struct = columns_struct
        )

        return elements_md
