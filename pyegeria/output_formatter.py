from datetime import datetime
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from pyegeria.utils import (camel_to_title_case)
from markdown_it import MarkdownIt
from rich.console import Console
from loguru import logger
from pyegeria.config import settings

from pyegeria.mermaid_utilities import construct_mermaid_web
from pyegeria._output_formats import select_output_format_set, MD_SEPARATOR
from pyegeria.models import to_camel_case

"""
Note on select_output_format_set function:

This function and related data structures have been moved back to _output_formats.py.
Please import select_output_format_set from pyegeria._output_formats instead of from this module.
"""

Console = Console(width=settings.Environment.console_width)


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
    effective_from = element['elementHeader'].get("effectiveFrom", None)
    effective_to = element['elementHeader'].get("effectiveTo", None)

    # Get attributes from properties
    # properties = element['properties']
    # display_name = properties.get("name", "") or ""
    # if display_name == "":
    #     display_name = properties.get("displayName","")
    # description = properties.get("description", "") or ""
    # qualified_name = properties.get("qualifiedName", "") or ""
    # category = properties.get("category", "") or ""
    # version_identifier = properties.get("versionIdentifier", "") or ""
    # additional_properties = properties.get("additionalProperties", {}) or {}
    # extended_properties = properties.get("extendedProperties", {}) or {}
    #
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

        # "display_name": display_name,
        # "description": description,
        # "qualified_name": qualified_name,
        # "category": category,
        # "version_identifier": version_identifier,
        # "additional_properties": additional_properties,
        # "extended_properties": extended_properties,
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
    elif output_type in ["REPORT", "MERMAID"]:
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


def populate_columns_from_properties(element: dict, columns_struct: dict) -> dict:
    """
    Populate a columns_struct with values from the element's properties.

    The element dict is expected to have a nested 'properties' dict whose keys are in camelCase.
    The columns_struct is expected to follow the format returned by select_output_format_set, where
    columns are located at columns_struct['formats']['columns'] and each column is a dict containing
    at least a 'key' field expressed in snake_case. For each column whose snake_case key corresponds
    to a key in the element properties (after converting to camelCase), this function adds a 'value'
    entry to the column with the matching property's value.

    Args:
        element: The element containing a 'properties' dict with camelCase keys.
        columns_struct: The columns structure whose columns have snake_case 'key' fields.

    Returns:
        The updated columns_struct (the input structure is modified in place and also returned).
    """
    if not isinstance(columns_struct, dict):
        return columns_struct

    props = (element or {}).get('properties') or {}
    # If properties is not a dict, do nothing
    if not isinstance(props, dict):
        return columns_struct

    # Get the columns list if present
    formats = columns_struct.get('formats') or {}
    columns = formats.get('columns') if isinstance(formats, dict) else None
    if not isinstance(columns, list):
        return columns_struct

    for col in columns:
        try:
            key_snake = col.get('key') if isinstance(col, dict) else None
            if not key_snake:
                continue
            # Convert the snake_case key to camelCase to look up in properties
            key_camel = to_camel_case(key_snake)
            if key_camel in props:
                col['value'] = props.get(key_camel)
        except Exception as e:
            # Be resilient; log and continue
            logger.debug(f"populate_columns_from_properties: skipping column due to error: {e}")
            continue

    return columns_struct


def get_required_relationships(element: dict, columns_struct: dict) -> dict:
    """
    Populate relationship-derived column values in columns_struct based on top-level keys in the element.

    This function inspects the requested columns in columns_struct, converts each column key from
    snake_case to camelCase, and if a matching top-level key exists in the element, parses that value
    (typically lists of relationship beans) into a human-readable value (e.g., a comma-separated list
    of qualified names) and stores it under the column's 'value'. Columns not specified in the
    columns_struct are ignored. Existing non-empty 'value's are left as-is.

    Example: if a column with key 'member_of_collections' is present, this function will look for the
    top-level key 'memberOfCollections' in the element and derive a value if found.

    Args:
        element: The element dictionary containing top-level relationship lists (e.g., associatedGlossaries,
                 memberOfCollections, collectionMembers).
        columns_struct: The columns structure to augment with derived 'value's.

    Returns:
        The updated columns_struct (modified in place and returned).
    """
    if not isinstance(columns_struct, dict):
        return columns_struct

    formats = columns_struct.get('formats') or {}
    columns = formats.get('columns') if isinstance(formats, dict) else None
    if not isinstance(columns, list):
        return columns_struct

    def _extract_name_from_item(item: Any) -> Optional[str]:
        """Best-effort extraction of a display/qualified name from a relationship item."""
        try:
            if isinstance(item, dict):
                # Common pattern: item['relatedElement']['properties']['qualifiedName']
                related = item.get('relatedElement') or item.get('related_element')
                if isinstance(related, dict):
                    props = related.get('properties') or {}
                    name = (
                        props.get('qualifiedName')
                        or props.get('displayName')
                        or props.get('name')
                    )
                    if name:
                        return name
                # Sometimes the properties may be at the top level of the item
                name = (
                    item.get('qualifiedName')
                    or item.get('displayName')
                    or item.get('name')
                )
                if name:
                    return name
            elif isinstance(item, str):
                return item
        except Exception as e:
            logger.debug(f"get_required_relationships: error extracting name from item: {e}")
        return None

    for col in columns:
        try:
            if not isinstance(col, dict):
                continue
            key_snake = col.get('key')
            if not key_snake:
                continue
            # If already has a non-empty value, don't overwrite
            if col.get('value') not in (None, ""):
                continue

            # Convert the snake_case key to camelCase to look up in top-level element
            key_camel = to_camel_case(key_snake)
            if key_camel not in element:
                continue

            top_val = element.get(key_camel)
            derived_value: str = ""
            if isinstance(top_val, list):
                names: List[str] = []
                for item in top_val:
                    nm = _extract_name_from_item(item)
                    if nm:
                        names.append(nm)
                derived_value = ", ".join(names)
            elif isinstance(top_val, dict):
                nm = _extract_name_from_item(top_val)
                derived_value = nm or ""
            else:
                # Primitive or unexpected type; coerce to string if not None
                derived_value = str(top_val) if top_val is not None else ""

            col['value'] = derived_value
        except Exception as e:
            logger.debug(f"get_required_relationships: skipping column due to error: {e}")
            continue

    return columns_struct


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
    heading = columns_struct.get("heading")
    if heading == "Default Base Attributes":
        elements_md = "## Reporting on Default Base Attributes - Perhaps couldn't find a valid combination of output_format_set and output_format?\n\n"
    else:
        elements_md = ""
    base_columns = columns_struct['formats'].get('columns') if columns_struct else None

    for element in elements:
        if element is None:
                continue
        guid = element.get('elementHeader', {}).get('guid')

        # Prefer new behavior: extractor returns an updated columns_struct with values
        returned_struct = None
        if columns_struct is not None:
            try:
                returned_struct = extract_properties_func(element, columns_struct)
            except TypeError:
                # Fallback for legacy extractors without columns_struct parameter
                returned_struct = None
        
        # Legacy fallback: get props dict if no columns_struct provided/returned
        props = {}
        if returned_struct is None:
            props = extract_properties_func(element) if callable(extract_properties_func) else {}

        # Get additional properties if function is provided
        additional_props = {}
        if get_additional_props_func:
            # Use guid if available, else try to get from props
            guid_for_fmt = guid or props.get('GUID')
            additional_props = get_additional_props_func(element, guid_for_fmt, output_format)

        # Determine display name
        display_name = None
        if returned_struct is not None:
            cols = returned_struct.get('formats', {}).get('columns', [])
            # Find value from 'display_name' or 'title'
            for col in cols:
                if col.get('key') in ('display_name', 'title'):
                    display_name = col.get('value')
                    if display_name:
                        break
        else:
            display_name = props.get('display_name') or props.get('title')

        if display_name is None:
            display_name = "NO DISPLAY NAME"

        # Format header based on output format
        if output_format in ['FORM', 'MD']:
            elements_md += f"# {elements_action}\n\n"
            elements_md += f"## {entity_type} Name \n\n{display_name}\n\n"
        elif output_format == 'REPORT':
            elements_md += f'<a id="{(guid or props.get("GUID") or "No GUID" )}"></a>\n# {entity_type} Name: {display_name}\n\n'
        else:
            elements_md += f"## {entity_type} Name \n\n{display_name}\n\n"

        # Add attributes based on column spec if available, otherwise, add all (legacy)
        if returned_struct is not None:
            cols = returned_struct.get('formats', {}).get('columns', [])
            for column in cols:
                name = column.get('name')
                key = column.get('key')
                value = column.get('value')
                if value in (None, "") and key in additional_props:
                    value = additional_props[key]
                if column.get('format'):
                    value = format_for_markdown_table(value, guid)
                elements_md += make_md_attribute(name, value, output_format)
            if wk := returned_struct.get("annotations", {}).get("wikilinks", None):
                elements_md += ", ".join(wk)
        elif base_columns:
            # If we have columns but extractor didn't return struct, use legacy props lookup
            for column in base_columns:
                key = column['key']
                name = column['name']
                value = ""
                if key in props:
                    value = props[key]
                elif key in additional_props:
                    value = additional_props[key]
                if column.get('format'):
                    value = format_for_markdown_table(value, guid or props.get('GUID'))
                elements_md += make_md_attribute(name, value, output_format)
            if wk := columns_struct.get("annotations", {}).get("wikilinks", None):
                elements_md += ", ".join(wk)
        else:
            # Legacy path without columns: dump all props
            for key, value in props.items():
                if output_format in ['FORM', 'MD', 'DICT'] and key == 'mermaid':
                    continue
                if key not in ['properties', 'display_name']:
                    if key == 'mermaid' and value == '':
                        continue
                    elements_md += make_md_attribute(key.replace('_', ' '), value, output_format)
            for key, value in additional_props.items():
                elements_md += make_md_attribute(key.replace('_', ' '), value, output_format)

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
    target_type = columns_struct.get('target_type', entity_type)
    # if target_type.endswith('y'):
    #     target_type = target_type.replace('y', 'ies')
    # else:
    #     target_type = target_type.replace('s', 's')

    entity_type_plural = f"{target_type[:-1]}ies" if target_type.endswith('y') else f"{target_type}s"
    # entity_type_plural = target_type
    columns = columns_struct['formats'].get('columns', [])
    heading = columns_struct.get("heading")
    if heading == "Default Base Attributes":
        elements_md = "## Reporting on Default Base Attributes - Perhaps couldn't find a valid combination of output_format_set and output_format?\n\n"
    else:
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
        guid = element.get('elementHeader', {}).get('guid', None)

        # Extractor returns columns_struct with values when possible
        try:
            returned_struct = extract_properties_func(element, columns_struct)
        except TypeError:
            returned_struct = None

        # For help mode, bypass extraction
        if output_format == "help":
            returned_struct = {"formats": {"columns": columns}}

        # Additional props (if any)
        additional_props = {}
        if get_additional_props_func:
            additional_props = get_additional_props_func(element, guid, output_format)

        # Build row
        row = "| "
        if returned_struct is not None:
            for column in returned_struct.get('formats', {}).get('columns', []):
                key = column.get('key')
                value = column.get('value')
                if (value in (None, "")) and key in additional_props:
                    value = additional_props[key]
                if column.get('format'):
                    value = format_for_markdown_table(value, guid)
                row += f"{value} | "
        else:
            # Legacy fallback: read from props dict
            props = extract_properties_func(element)
            for column in columns:
                key = column['key']
                value = ""
                if key in props:
                    value = props[key]
                elif key in additional_props:
                    value = additional_props[key]
                if column.get('format'):
                    value = format_for_markdown_table(value, guid or props.get('GUID'))
                row += f"{value} | "

        elements_md += row + "\n"
        # if wk := columns_struct.get("annotations",{}).get("wikilinks", None):
        #     elements_md += ", ".join(wk)
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

        guid = element.get('elementHeader', {}).get('guid')

        returned_struct = None
        if columns_struct is not None:
            try:
                returned_struct = extract_properties_func(element, columns_struct)
            except TypeError as e:
                logger.info(f"Error - didn't find extractor?: {e}")
                returned_struct = None

        # Get additional properties if function is provided
        additional_props = {}
        if get_additional_props_func:
            additional_props = get_additional_props_func(element, guid, output_format)

        # Create entity dictionary
        entity_dict = {}

        columns = columns_struct['formats'].get('columns', None) if columns_struct else None
        if returned_struct is not None:
            for column in returned_struct.get('formats', {}).get('columns', []):
                key = column.get('key')
                name = column.get('name')
                value = column.get('value')
                if (value in (None, "")) and key in additional_props:
                    value = additional_props[key]
                if column.get('format'):
                    value = format_for_markdown_table(value, guid)
                entity_dict[name] = value
        elif columns:
            for column in columns:
                key = column['key']
                name = column['name']
                value = ""
                props = extract_properties_func(element)
                if key in props:
                    value = props[key]
                elif key in additional_props:
                    value = additional_props[key]
                if  column.get('format', None):
                    value = format_for_markdown_table(value, guid or props.get('GUID'))
                entity_dict[name] = value
        else:
            props = extract_properties_func(element, columns_struct)
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

def resolve_output_formats(entity_type: str,
                           output_format: str,
                           output_format_set: Optional[Union[str, dict]] = None,
                           default_label: Optional[str] = None) -> Optional[dict]:
    """
    Resolve an output format set structure given an entity type, the desired output format
    (e.g., DICT, LIST, MD, REPORT, FORM), and either a label (str) or a dict of format sets.

    Selection order:
    - If output_format_set is a str: select by label.
    - If output_format_set is a dict: use get_output_format_type_match to pick a matching format.
    - Else: try selecting by entity_type or default_label.
    - Fallback: select "Default".
    """
    from pyegeria._output_formats import select_output_format_set, get_output_format_type_match

    if isinstance(output_format_set, str):
        return select_output_format_set(output_format_set, output_format)
    if isinstance(output_format_set, dict):
        return get_output_format_type_match(output_format_set, output_format)

    label = default_label or entity_type
    fmt = select_output_format_set(label, output_format)
    if fmt is None:
        fmt = select_output_format_set("Default", output_format)
    return fmt


def overlay_additional_values(columns_struct: dict, extra: Optional[dict]) -> dict:
    """
    Overlay extra values into columns_struct only where the column's value is empty or missing.
    Returns the modified columns_struct.
    """
    if not isinstance(columns_struct, dict) or not extra:
        return columns_struct
    columns = columns_struct.get('formats', {}).get('columns')
    if not isinstance(columns, list):
        return columns_struct
    for col in columns:
        if not isinstance(col, dict):
            continue
        key = col.get('key')
        if not key:
            continue
        if col.get('value') in (None, "") and key in extra:
            col['value'] = extra[key]
    return columns_struct


def populate_common_columns(
    element: dict,
    columns_struct: dict,
    *,
    include_header: bool = True,
    include_relationships: bool = True,
    include_subject_area: bool = True,
    mermaid_source_key: str = 'mermaidGraph',
    mermaid_dest_key: str = 'mermaid'
) -> dict:
    """
    Populate the common columns in columns_struct based on a standard Egeria element shape.

    Steps:
    - Populate from element.properties (camelCase mapped from snake_case keys)
    - Optionally overlay header-derived values (GUID, type_name, times, etc.)
    - Optionally populate relationship-based columns via get_required_relationships
    - Optionally populate subject_area from element.elementHeader.subjectArea.classificationProperties.subjectAreaName
    - If a column with key == mermaid_dest_key is present, set it from mermaid_source_key
    - Do not overwrite non-empty values already set
    """
    # 1) Base properties
    col_data = populate_columns_from_properties(element, columns_struct)
    columns_list = col_data.get('formats', {}).get('columns', [])

    # 2) Header overlay
    header_props = _extract_referenceable_properties(element) if include_header else {}
    guid = header_props.get('GUID') if include_header else None
    if include_header:
        for column in columns_list:
            if not isinstance(column, dict):
                continue
            key = column.get('key')
            if not key:
                continue
            if column.get('value') not in (None, ""):
                continue
            if key in header_props:
                column['value'] = header_props.get(key)
            elif isinstance(key, str) and key.lower() == 'guid':
                column['value'] = guid

    # 3) Relationships
    if include_relationships:
        col_data = get_required_relationships(element, col_data)

    # 4) Subject area
    if include_subject_area:
        try:
            subject_area = element.get('elementHeader', {}).get('subjectArea') or ""
            subj_val = ""
            if isinstance(subject_area, dict):
                subj_val = subject_area.get('classificationProperties', {}).get('subjectAreaName', '')
            for column in columns_list:
                if column.get('key') == 'subject_area' and column.get('value') in (None, ""):
                    column['value'] = subj_val
        except Exception as e:
            logger.debug(f"populate_common_columns: subject_area handling error: {e}")

    # 5) Mermaid
    try:
        mermaid_val = element.get(mermaid_source_key, '') or ''
        for column in columns_list:
            if column.get('key') == mermaid_dest_key and column.get('value') in (None, ""):
                column['value'] = mermaid_val
                break
    except Exception as e:
        logger.debug(f"populate_common_columns: mermaid handling error: {e}")

    return col_data


def extract_mermaid_only(elements: Union[Dict, List[Dict]]) -> Union[str, List[str]]:
    """
    Extract mermaid graph data from elements.

    Args:
        elements: Dictionary or list of dictionaries containing element data

    Returns:
        String or list of strings containing mermaid graph data
    """
    if isinstance(elements, dict):
        mer = elements.get('mermaidGraph', None)
        if mer:
            return f"\n```mermaid\n{mer}\n```"
        else:
            return "---"


    result = []
    for element in elements:
        mer = element.get('mermaidGraph', "---")
        mer_out = f"\n\n```mermaid\n{mer}\n\n```" if mer else "---"
        result.append(mer_out)
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

def _extract_default_properties(self, element: dict, columns_struct: dict) -> dict:
    props = element.get('properties', {}) or {}
    normalized = {
        'properties': props,
        'elementHeader': element.get('elementHeader', {}),
    }
    # Common population pipeline
    col_data = populate_common_columns(element, columns_struct)
    columns_list = col_data.get('formats', {}).get('columns', [])

    return col_data


def _generate_default_output(self, elements: dict | list[dict], search_string: str,
                             element_type_name: str | None,
                             output_format: str = 'DICT',
                             output_format_set: dict | str = None) -> str | list[dict]:
    entity_type = 'Referenceable'
    if output_format_set:
        if isinstance(output_format_set, str):
            output_formats = select_output_format_set(output_format_set, output_format)
        elif isinstance(output_format_set, dict):
            output_formats = get_output_format_type_match(output_format_set, output_format)
        else:
            output_formats = None
    else:
        output_formats = select_output_format_set(entity_type, output_format)
    if output_formats is None:
        output_formats = select_output_format_set('Default', output_format)
    return generate_output(
        elements=elements,
        search_string=search_string,
        entity_type=entity_type,
        output_format=output_format,
        extract_properties_func=_extract_default_properties,
        get_additional_props_func=None,
        columns_struct=output_formats,
    )


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
    if not columns:
        columns_struct = select_output_format_set("Default",output_format)
        if columns_struct:
            columns = columns_struct.get('formats', {}).get('columns', None)

    target_type = columns_struct.get('target_type', entity_type) if columns_struct else entity_type
    if target_type is None:
        target_type = entity_type

    # Ensure elements is a list
    if isinstance(elements, dict):
        elements = [elements]

    # Handle empty search string
    if search_string is None or search_string == '':
        search_string = "All"

    # Set the output format to DICT to return values to table display
    if output_format == "TABLE":
        output_format = "DICT"

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
            obj_type=target_type,
            search_string=search_string,
            output_format=output_format
        )

        elements_md += generate_entity_md(
            elements=elements,
            elements_action=elements_action,
            output_format=output_format,
            entity_type=target_type,
            extract_properties_func=extract_properties_func,
            get_additional_props_func=get_additional_props_func,
            columns_struct = columns_struct
        )

        return elements_md
