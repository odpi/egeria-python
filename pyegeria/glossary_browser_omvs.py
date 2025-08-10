"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains an initial version of the glossary_browser omvs module. There are additional methods that will be
added in subsequent versions of the glossary_omvs module.

"""

import asyncio
from datetime import datetime

from pyegeria import NO_GLOSSARIES_FOUND, max_paging_size
from pyegeria._client import Client
from pyegeria._exceptions import InvalidParameterException, PropertyServerException, UserNotAuthorizedException
from pyegeria._globals import NO_CATEGORIES_FOUND, NO_TERMS_FOUND
from pyegeria._validators import validate_guid, validate_name, validate_search_string
from pyegeria.utils import body_slimmer
from pyegeria._output_formats import select_output_format_set, get_output_format_type_match
from pyegeria.output_formatter import (
    make_preamble, 
    make_md_attribute, 
    format_for_markdown_table,
    generate_entity_md,
    generate_entity_md_table,
    generate_entity_dict,
    generate_output,
    MD_SEPARATOR
)


class GlossaryBrowser(Client):
    """
    GlossaryBrowser is a class that extends the Client class. It provides methods to search and retrieve glossaries,
    terms, and categories.

    Attributes:

        view_server: str
            The name of the View Server to connect to.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method - this sets a default optionally used by the methods
            when the user doesn't pass the user_id on a method call.
        user_pwd: str
            The password associated with the user_id. Defaults to None

    """

    def __init__(self, view_server: str, platform_url: str, user_id: str, user_pwd: str = None, token: str = None, ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_pwd = user_pwd
        self.user_id = user_id
        self.g_browser_command_root: str

        Client.__init__(self, view_server, platform_url, user_id, user_pwd, token)


    def _extract_glossary_properties(self, element: dict, output_format: str = None) -> dict:
        """
        Extract common properties from a glossary element.

        Args:
            element (dict): The glossary element
            output_format (str, optional): The output format (FORM, REPORT, etc.)

        Returns:
            dict: Dictionary of extracted properties
        """
        guid = element['elementHeader'].get("guid", None)
        properties = element['glossaryProperties']
        display_name = properties.get("displayName", "") or ""
        description = properties.get("description", "") or ""
        language = properties.get("language", "") or ""
        usage = properties.get("usage", "") or ""
        qualified_name = properties.get("qualifiedName", "") or ""

        categories = self.get_categories_for_glossary(guid)
        cat_md_display = ''
        cat_md_qn = ''
        category_names = ''
        category_qualified_names = ''

        if type(categories) is list:
            for category in categories:
                cat_md_display += f" {category['glossaryCategoryProperties'][('displayName')]},\n"
                cat_md_qn += f" {category['glossaryCategoryProperties'][('qualifiedName')]},\n"
            category_names = cat_md_display.rstrip(',')
            category_qualified_names = cat_md_qn.rstrip(',')

        result = {
            'GUID': guid, 'properties': properties, 'display_name': display_name, 'description': description,
            'language': language, 'usage': usage, 'qualified_name': qualified_name
        }

        # Include appropriate category information based on output format
        if output_format == 'FORM':
            result['categories_qualified_names'] = category_qualified_names
        else:
            result['categories_names'] = category_names

        return result

    def _generate_entity_md(self, elements: list, elements_action: str, output_format: str, entity_type: str,
                            extract_properties_func, get_additional_props_func=None) -> str:
        """
        Generic method to generate markdown for entities (glossaries, terms, categories).

        Args:
            elements (list): List of entity elements
            elements_action (str): Action description for elements
            output_format (str): Output format
            entity_type (str): Type of entity (Glossary, Term, Category)
            extract_properties_func: Function to extract properties from an element
            get_additional_props_func: Optional function to get additional properties

        Returns:
            str: Markdown representation
        """
        return generate_entity_md(
            elements=elements,
            elements_action=elements_action,
            output_format=output_format,
            entity_type=entity_type,
            extract_properties_func=extract_properties_func,
            get_additional_props_func=get_additional_props_func
        )

    def _generate_glossary_md(self, elements: list, elements_action: str, output_format: str) -> str:
        """
        Generate markdown for glossaries.

        Args:
            elements (list): List of glossary elements
            elements_action (str): Action description for elements
            output_format (str): Output format

        Returns:
            str: Markdown representation
        """
        # Store the current output format for use by _extract_glossary_properties_with_format
        self._current_output_format = output_format

        return self._generate_entity_md(elements=elements, elements_action=elements_action, output_format=output_format,
                                        entity_type="Glossary",
                                        extract_properties_func=self._extract_glossary_properties_with_format)

    def _generate_entity_md_table(self, elements: list, search_string: str, entity_type: str, extract_properties_func,
                                  columns: list, get_additional_props_func=None, output_format: str = 'LIST') -> str:
        """
        Generic method to generate a markdown table for entities (glossaries, terms, categories).

        Args:
            elements (list): List of entity elements
            search_string (str): The search string used
            entity_type (str): Type of entity (Glossary, Term, Category)
            extract_properties_func: Function to extract properties from an element
            columns: List of column definitions, each containing 'name', 'key', and 'format' (optional)
            get_additional_props_func: Optional function to get additional properties
            output_format (str): Output format (FORM, REPORT, LIST, etc.)

        Returns:
            str: Markdown table
        """
        return generate_entity_md_table(
            elements=elements,
            search_string=search_string,
            entity_type=entity_type,
            extract_properties_func=extract_properties_func,
            columns=columns,
            get_additional_props_func=get_additional_props_func,
            output_format=output_format
        )

    def _generate_glossary_md_table(self, elements: list, search_string: str) -> str:
        """
        Generate a markdown table for glossaries.

        Args:
            elements (list): List of glossary elements
            search_string (str): The search string used

        Returns:
            str: Markdown table
        """
        # Store the current output format for use by _extract_glossary_properties_with_format
        self._current_output_format = 'LIST'  # Tables use LIST format

        columns = [{'name': 'Glossary Name', 'key': 'display_name'},
                   {'name': 'Qualified Name', 'key': 'qualified_name'},
                   {'name': 'Language', 'key': 'language', 'format': True},
                   {'name': 'Description', 'key': 'description', 'format': True},
                   {'name': 'Usage', 'key': 'usage', 'format': True},
                   {'name': 'Categories', 'key': 'categories_names', 'format': True}, ]

        return self._generate_entity_md_table(elements=elements, search_string=search_string, entity_type="Glossary",
                                              extract_properties_func=self._extract_glossary_properties_with_format,
                                              columns=columns)

    def _generate_entity_dict(self, elements: list, extract_properties_func, get_additional_props_func=None,
                              include_keys=None, exclude_keys=None, output_format: str = 'DICT') -> list:
        """
        Generic method to generate a dictionary representation of entities (glossaries, terms, categories).

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
        return generate_entity_dict(
            elements=elements,
            extract_properties_func=extract_properties_func,
            get_additional_props_func=get_additional_props_func,
            include_keys=include_keys,
            exclude_keys=exclude_keys,
            output_format=output_format
        )

    def _generate_glossary_dict(self, elements: list, output_format: str = 'DICT') -> list:
        """
        Generate a dictionary representation of glossaries.

        Args:
            elements (list): List of glossary elements
            output_format (str): Output format (FORM, REPORT, DICT, etc.)

        Returns:
            list: List of glossary dictionaries
        """
        # Store the current output format for use by _extract_glossary_properties_with_format
        self._current_output_format = output_format

        return self._generate_entity_dict(elements=elements, extract_properties_func=self._extract_glossary_properties_with_format,
                                          exclude_keys=['properties'], output_format=output_format)

    def _extract_glossary_properties_with_format(self, element: dict) -> dict:
        """
        Wrapper function for _extract_glossary_properties that passes the current output format.
        This is used internally by generate_glossaries_md.

        Args:
            element (dict): The glossary element

        Returns:
            dict: Dictionary of extracted properties
        """
        # The output_format is stored as an instance variable during generate_glossaries_md
        return self._extract_glossary_properties(element, self._current_output_format)

    def generate_glossaries_md(self, elements: list | dict, search_string: str,
                               output_format: str = 'MD', output_format_set: str | dict = None) -> str | list:
        """
        Generate markdown or dictionary representation of glossaries.

        Args:
            elements (list | dict): List or dictionary of glossary elements
            search_string (str): The search string used
            output_format (str): Output format (MD, FORM, REPORT, LIST, DICT)
            output_format_set (str | dict, optional): Output format set name or dictionary. Defaults to None.

        Returns:
            str | list: Markdown string or list of dictionaries depending on output_format
        """
        # Store the current output format for use by _extract_glossary_properties_with_format
        self._current_output_format = output_format

        # Define default columns for LIST format
        default_columns = [
            {'name': 'Glossary Name', 'key': 'display_name'},
            {'name': 'Qualified Name', 'key': 'qualified_name'},
            {'name': 'Language', 'key': 'language', 'format': True},
            {'name': 'Description', 'key': 'description', 'format': True},
            {'name': 'Usage', 'key': 'usage', 'format': True},
            {'name': 'Categories', 'key': 'categories_names', 'format': True},
        ]

        # Determine the output format set
        output_formats = None
        if output_format_set:
            if isinstance(output_format_set, str):
                output_formats = select_output_format_set(output_format_set, output_format)
            elif isinstance(output_format_set, dict):
                output_formats = get_output_format_type_match(output_format_set, output_format)
        else:
            # Use default entity type to lookup the output format
            output_formats = select_output_format_set("Glossary", output_format)
            # If no format set is found, create one with default columns
            if not output_formats and output_format == 'LIST':
                output_formats = {"formats": {"columns": default_columns}}

        return generate_output(
            elements=elements,
            search_string=search_string,
            entity_type="Glossary",
            output_format=output_format,
            extract_properties_func=self._extract_glossary_properties_with_format,
            columns_struct=output_formats
        )

    def _extract_term_properties(self, element: dict) -> dict:
        """
        Extract common properties from a term element.

        Args:
            element (dict): The term element

        Returns:
            dict: Dictionary of extracted properties
        """
        guid = element['elementHeader'].get("guid", None)
        properties = element['glossaryTermProperties']
        display_name = properties.get("displayName", "") or ""
        summary = properties.get("summary", "") or ""
        description = properties.get("description", "") or ""
        examples = properties.get("examples", "") or ""
        usage = properties.get("usage", "") or ""
        pub_version = properties.get("publishVersionIdentifier", "") or ""
        qualified_name = properties.get("qualifiedName", "") or ""
        status = element['elementHeader'].get('status', "") or ""
        aliases = ", ".join(properties.get("aliases", "")) or ""

        return {
            'GUID': guid, 'properties': properties, 'display_name': display_name, 'aliases': aliases,
            'summary': summary, 'description': description, 'examples': examples, 'usage': usage,
            'version identifier': pub_version, 'qualified_name': qualified_name, 'status': status
            }

    def _get_categories_for_term(self, term_guid: str, output_format: str = None) -> tuple[list, str]:
        """
        Get a list of categories for a given term.

        Args:
            term_guid (str): The GUID of the term
            output_format (str): Output format (FORM, REPORT, LIST, etc.)

        Returns:
            tuple: A tuple containing:
                - list: List of category names
                - str: Formatted string of category names for markdown
        """
        category_names = []
        category_list_md = "\n"

        category_list = self.get_categories_for_term(term_guid)
        if type(category_list) is str and category_list == NO_CATEGORIES_FOUND:
            category_list_md = ''
        elif isinstance(category_list, list) and len(category_list) > 0:
            first_cat = True
            for category in category_list:
                # Use qualified name for FORM output, display name for REPORT and LIST output
                if output_format in ['REPORT', 'LIST']:
                    category_name = category["glossaryCategoryProperties"].get("displayName", '---')
                else:
                    category_name = category["glossaryCategoryProperties"].get("qualifiedName", '---')

                if category_name:
                    category_names.append(category_name)
                if first_cat:
                    category_list_md += f" {category_name}\n"
                    first_cat = False
                else:
                    category_list_md += f", {category_name}\n"
        else:
            category_list_md = '---'

        return category_names, category_list_md

    def _get_term_table_properties(self, element: dict, term_guid: str, output_format: str = None) -> dict:
        """
        Get properties for a term table row.

        Args:
            element (dict): The term element
            term_guid (str): The GUID of the term
            output_format (str): Output format (FORM, REPORT, etc.)

        Returns:
            dict: Dictionary of properties for the table row
        """
        # Get glossary information
        glossary_qualified_name = self._get_glossary_name_for_element(element, output_format)

        # Get categories
        category_names, _ = self._get_categories_for_term(term_guid, output_format)
        categories_str = ", ".join(category_names) if category_names else "---"

        return {
            'glossary': glossary_qualified_name, 'categories_str': categories_str
            }

    def _generate_term_md_table(self, elements: list, search_string: str, output_format: str = 'LIST') -> str:
        """
        Generate a markdown table for terms.

        Args:
            elements (list): List of term elements
            search_string (str): The search string used
            output_format (str): Output format (FORM, REPORT, LIST, etc.)

        Returns:
            str: Markdown table
        """
        columns = [{'name': 'Term Name', 'key': 'display_name'}, {'name': 'Qualified Name', 'key': 'qualified_name'},
                   {'name': 'Aliases', 'key': 'aliases', 'format': True},
                   {'name': 'Summary', 'key': 'summary', 'format': True}, {'name': 'Glossary', 'key': 'glossary'},
                   {'name': 'Categories', 'key': 'categories_str', 'format': True}]

        # Create a wrapper function to pass output_format to _get_term_table_properties
        def get_table_props_with_format(element, term_guid, output_format_param=None):
            return self._get_term_table_properties(element, term_guid, output_format)

        return self._generate_entity_md_table(elements=elements, search_string=search_string, entity_type="Term",
                                              extract_properties_func=self._extract_term_properties, columns=columns,
                                              get_additional_props_func=get_table_props_with_format)

    def _get_term_dict_properties(self, element: dict, term_guid: str, output_format: str = None) -> dict:
        """
        Get additional properties for a term dictionary.

        Args:
            element (dict): The term element
            term_guid (str): The GUID of the term
            output_format (str): Output format (FORM, REPORT, etc.)

        Returns:
            dict: Dictionary of additional properties
        """
        # Get glossary information
        glossary_qualified_name = self._get_glossary_name_for_element(element, output_format)

        # Get categories
        category_names, _ = self._get_categories_for_term(term_guid, output_format)

        return {
            'in_glossary': glossary_qualified_name, 'categories': category_names,
            'version': element['glossaryTermProperties'].get('publishfinVersionIdentifier', '')
            }

    def _generate_term_dict(self, elements: list, output_format: str = 'DICT') -> list:
        """
        Generate a dictionary representation of terms.

        Args:
            elements (list): List of term elements
            output_format (str): Output format (FORM, REPORT, DICT, etc.)

        Returns:
            list: List of term dictionaries
        """

        # Create a wrapper function to pass output_format to _get_term_dict_properties
        def get_dict_props_with_format(element, term_guid, output_format_param=None):
            return self._get_term_dict_properties(element, term_guid, output_format)

        return self._generate_entity_dict(elements=elements, extract_properties_func=self._extract_term_properties,
                                          get_additional_props_func=get_dict_props_with_format,
                                          exclude_keys=['properties', 'pub_version']
                                          # Exclude raw properties and pub_version (renamed to version)
                                          )

    def _get_term_additional_properties(self, element: dict, term_guid: str, output_format: str = None) -> dict:
        """
        Get additional properties for a term.

        Args:
            element (dict): The term element
            term_guid (str): The GUID of the term
            output_format (str): Output format (FORM, REPORT, etc.)

        Returns:
            dict: Dictionary of additional properties
        """
        # Get glossary information
        glossary_qualified_name = self._get_glossary_name_for_element(element, output_format)

        # Get categories
        _, category_list_md = self._get_categories_for_term(term_guid, output_format)

        return {
            'in_glossary': glossary_qualified_name, 'categories': category_list_md
            }

    def _generate_term_md(self, elements: list, elements_action: str, output_format: str) -> str:
        """
        Generate markdown for terms.

        Args:
            elements (list): List of term elements
            elements_action (str): Action description for elements
            output_format (str): Output format

        Returns:
            str: Markdown representation
        """
        return self._generate_entity_md(elements=elements, elements_action=elements_action, output_format=output_format,
                                        entity_type="Term", extract_properties_func=self._extract_term_properties,
                                        get_additional_props_func=self._get_term_additional_properties)

    def generate_terms_md(self, elements: list | dict, search_string: str, output_format: str = 'MD', output_format_set: str | dict = None) -> str | list:
        """
        Generate markdown or dictionary representation of terms.

        Args:
            elements (list | dict): List or dictionary of term elements
            search_string (str): The search string used
            output_format (str): Output format (MD, MD-TABLE, DICT, FORM, REPORT)
            output_format_set (str | dict, optional): Output format set name or dictionary. Defaults to None.

        Returns:
            str | list: Markdown string or list of dictionaries depending on output_format
        """
        # Define default columns for LIST format
        default_columns = [
            {'name': 'Term Name', 'key': 'display_name'},
            {'name': 'Qualified Name', 'key': 'qualified_name'},
            {'name': 'Summary', 'key': 'summary', 'format': True},
            {'name': 'Description', 'key': 'description', 'format': True},
            {'name': 'Status', 'key': 'status'},
            {'name': 'Categories', 'key': 'categories', 'format': True},
            {'name': 'Glossary', 'key': 'glossary_name'},
        ]

        # Determine the output format set
        output_formats = None
        if output_format_set:
            if isinstance(output_format_set, str):
                output_formats = select_output_format_set(output_format_set, output_format)
            elif isinstance(output_format_set, dict):
                output_formats = get_output_format_type_match(output_format_set, output_format)
        else:
            # Use default entity type to lookup the output format
            output_formats = select_output_format_set("Term", output_format)
            # If no format set is found, create one with default columns
            if not output_formats and output_format == 'LIST':
                output_formats = {"formats": {"columns": default_columns}}

        return generate_output(
            elements=elements,
            search_string=search_string,
            entity_type="Term",
            output_format=output_format,
            extract_properties_func=self._extract_term_properties,
            get_additional_props_func=self._get_term_additional_properties,
            columns_struct=output_formats
        )

    def _get_parent_category_name(self, category_guid: str, output_format: str = None) -> str:
        """
        Get the parent category name for a given category.

        Args:
            category_guid (str): The GUID of the category
            output_format (str): Output format (FORM, REPORT, LIST, etc.)

        Returns:
            str: The parent category name or ' ' if no parent
        """
        parent_cat = self.get_category_parent(category_guid)
        if isinstance(parent_cat, str):
            return ' '

        # Return qualified name for FORM output, display name for REPORT and LIST output
        if output_format == 'FORM':
            return parent_cat['glossaryCategoryProperties']['qualifiedName']
        elif output_format in ['REPORT', 'LIST']:
            return parent_cat['glossaryCategoryProperties']['displayName']
        else:
            # Default to qualified name for backward compatibility
            return parent_cat['glossaryCategoryProperties']['qualifiedName']

    def _get_subcategories_list(self, category_guid: str, output_format: str = None) -> tuple[list, str]:
        """
        Get a list of subcategories for a given category.

        Args:
            category_guid (str): The GUID of the category
            output_format (str): Output format (FORM, REPORT, LIST, etc.)

        Returns:
            tuple: A tuple containing:
                - list: List of subcategory names
                - str: Formatted string of subcategory names for markdown
        """
        subcategories = self.get_glossary_subcategories(category_guid)
        subcategory_list = []

        if isinstance(subcategories, str) and subcategories == NO_CATEGORIES_FOUND:
            subcategory_list_md = '---'
        elif isinstance(subcategories, list) and len(subcategories) > 0:
            for subcat in subcategories:
                # Use qualified name for FORM output, display name for REPORT and LIST output
                if output_format == 'FORM':
                    subcat_name = subcat["glossaryCategoryProperties"].get("qualifiedName", '')
                elif output_format in ['REPORT', 'LIST']:
                    subcat_name = subcat["glossaryCategoryProperties"].get("displayName", '')
                else:
                    # Default to qualified name for backward compatibility
                    subcat_name = subcat["glossaryCategoryProperties"].get("qualifiedName", '')

                if subcat_name:
                    subcategory_list.append(subcat_name)
            subcategory_list_md = ", ".join(subcategory_list)
        else:
            subcategory_list_md = '---'

        return subcategory_list, subcategory_list_md

    def _get_glossary_name_for_element(self, element: dict, output_format: str = None) -> str:
        """
        Get the glossary name for a given element.

        Args:
            element (dict): The element dictionary
            output_format (str): Output format (FORM, REPORT, etc.)

        Returns:
            str: The glossary name or '---' if not found
        """
        classification_props = element["elementHeader"]['classifications'][0].get('classificationProperties', None)
        if classification_props is None:
            return '---'

        glossary_guid = classification_props.get('anchorScopeGUID', '---')
        if glossary_guid == '---':
            return '---'

        glossary = self.get_glossary_by_guid(glossary_guid)

        # Return display name for REPORT output, qualified name otherwise
        if output_format == 'REPORT':
            return glossary['glossaryProperties']['displayName']
        else:
            return glossary['glossaryProperties']['qualifiedName']

    def _extract_category_properties(self, element: dict) -> dict:
        """
        Extract common properties from a category element.

        Args:
            element (dict): The category element

        Returns:
            dict: Dictionary of extracted properties
        """
        guid = element['elementHeader'].get("guid", None)
        properties = element['glossaryCategoryProperties']
        display_name = properties.get("displayName", "") or ""
        description = properties.get("description", "") or ""
        qualified_name = properties.get("qualifiedName", "") or ""

        return {
            'GUID': guid, 'properties': properties, 'display_name': display_name, 'description': description,
            'qualified_name': qualified_name
            }

    def _get_category_table_properties(self, element: dict, category_guid: str, output_format: str = None) -> dict:
        """
        Get properties for a category table row.

        Args:
            element (dict): The category element
            category_guid (str): The GUID of the category
            output_format (str): Output format (FORM, REPORT, etc.)

        Returns:
            dict: Dictionary of properties for the table row
        """
        # Get parent category
        parent_cat_md = self._get_parent_category_name(category_guid, output_format)

        # Get subcategories
        _, subcategory_list_md = self._get_subcategories_list(category_guid, output_format)

        return {
            'parent_category': parent_cat_md, 'subcategories': subcategory_list_md
            }

    def _generate_category_md_table(self, elements: list, search_string: str, output_format: str = 'LIST') -> str:
        """
        Generate a markdown table for categories.

        Args:
            elements (list): List of category elements
            search_string (str): The search string used
            output_format (str): Output format (FORM, REPORT, etc.)

        Returns:
            str: Markdown table
        """
        columns = [{'name': 'Display Name', 'key': 'display_name'},
                   {'name': 'Description', 'key': 'description', 'format': True},
                   {'name': 'Qualified Name', 'key': 'qualified_name'},
                   {'name': 'Parent Category', 'key': 'parent_category'},
                   {'name': 'Subcategories', 'key': 'subcategories', 'format': True}]

        # Create a wrapper function to pass output_format to _get_category_table_properties
        def get_table_props_with_format(element, category_guid, output_format_param=None):
            return self._get_category_table_properties(element, category_guid, output_format)

        return self._generate_entity_md_table(elements=elements, search_string=search_string, entity_type="Category",
                                              extract_properties_func=self._extract_category_properties,
                                              columns=columns, get_additional_props_func=get_table_props_with_format)

    def _get_category_dict_properties(self, element: dict, category_guid: str, output_format: str = None) -> dict:
        """
        Get additional properties for a category dictionary.

        Args:
            element (dict): The category element
            category_guid (str): The GUID of the category
            output_format (str): Output format (FORM, REPORT, etc.)

        Returns:
            dict: Dictionary of additional properties
        """
        # Get parent category
        parent_cat_md = self._get_parent_category_name(category_guid, output_format)

        # Get subcategories
        subcategory_list, _ = self._get_subcategories_list(category_guid, output_format)

        # Get glossary information
        glossary_qualified_name = self._get_glossary_name_for_element(element, output_format)

        return {
            'parent_category': parent_cat_md, 'subcategories': subcategory_list, 'in_glossary': glossary_qualified_name
            }

    def _generate_category_dict(self, elements: list, output_format: str = 'DICT') -> list:
        """
        Generate a dictionary representation of categories.

        Args:
            elements (list): List of category elements
            output_format (str): Output format (FORM, REPORT, etc.)

        Returns:
            list: List of category dictionaries
        """

        # Create a wrapper function to pass output_format to _get_category_dict_properties
        def get_dict_props_with_format(element, category_guid, output_format_param=None):
            return self._get_category_dict_properties(element, category_guid, output_format)

        return self._generate_entity_dict(elements=elements, extract_properties_func=self._extract_category_properties,
                                          get_additional_props_func=get_dict_props_with_format,
                                          exclude_keys=['properties'],  # Exclude raw properties
                                          output_format=output_format)

    def _get_category_additional_properties(self, element: dict, category_guid: str, output_format: str = None) -> dict:
        """
        Get additional properties for a category.

        Args:
            element (dict): The category element
            category_guid (str): The GUID of the category
            output_format (str): Output format (FORM, REPORT, etc.)

        Returns:
            dict: Dictionary of additional properties
        """
        # Get parent category
        parent_cat_md = self._get_parent_category_name(category_guid, output_format)

        # Get glossary information
        glossary_qualified_name = self._get_glossary_name_for_element(element, output_format)

        # Only include subcategories if output_format is not FORM, REPORT, or MD
        if output_format not in ['FORM', 'REPORT', 'MD']:
            # Get subcategories
            _, subcategory_list_md = self._get_subcategories_list(category_guid, output_format)
            return {
                'in_glossary': glossary_qualified_name, 'parent_category': parent_cat_md,
                'subcategories': subcategory_list_md
                }
        else:
            return {
                'in_glossary': glossary_qualified_name, 'parent_category': parent_cat_md
                }

    def _generate_category_md(self, elements: list, elements_action: str, output_format: str) -> str:
        """
        Generate markdown for categories.

        Args:
            elements (list): List of category elements
            elements_action (str): Action description for elements
            output_format (str): Output format

        Returns:
            str: Markdown representation
        """

        # Create a wrapper function to pass output_format to _get_category_additional_properties
        def get_additional_props_with_format(element, category_guid, output_format_param=None):
            return self._get_category_additional_properties(element, category_guid, output_format)

        return self._generate_entity_md(elements=elements, elements_action=elements_action, output_format=output_format,
                                        entity_type="Category",
                                        extract_properties_func=self._extract_category_properties,
                                        get_additional_props_func=get_additional_props_with_format)

    def generate_categories_md(self, elements: list | dict, search_string: str,
                               output_format: str = 'MD', output_format_set: str | dict = None) -> str | list:
        """
        Generate markdown or dictionary representation of categories.

        Args:
            elements (list | dict): List or dictionary of category elements
            search_string (str): The search string used
            output_format (str): Output format (MD, LIST, DICT, FORM, REPORT)
            output_format_set (str | dict, optional): Output format set name or dictionary. Defaults to None.

        Returns:
            str | list: Markdown string or list of dictionaries depending on output_format
        """
        # Define default columns for LIST format
        default_columns = [
            {'name': 'Category Name', 'key': 'display_name'},
            {'name': 'Qualified Name', 'key': 'qualified_name'},
            {'name': 'Description', 'key': 'description', 'format': True},
            {'name': 'Parent Category', 'key': 'parent_category', 'format': True},
            {'name': 'Subcategories', 'key': 'subcategories', 'format': True},
            {'name': 'Glossary', 'key': 'glossary_name'},
        ]

        # Determine the output format set
        output_formats = None
        if output_format_set:
            if isinstance(output_format_set, str):
                output_formats = select_output_format_set(output_format_set, output_format)
            elif isinstance(output_format_set, dict):
                output_formats = get_output_format_type_match(output_format_set, output_format)
        else:
            # Use default entity type to lookup the output format
            output_formats = select_output_format_set("Category", output_format)
            # If no format set is found, create one with default columns
            if not output_formats and output_format == 'LIST':
                output_formats = {"formats": {"columns": default_columns}}

        # Create a wrapper function to pass output_format to _get_category_additional_properties
        def get_additional_props_with_format(element, category_guid, output_format_param=None):
            return self._get_category_additional_properties(element, category_guid, output_format)

        return generate_output(
            elements=elements,
            search_string=search_string,
            entity_type="Category",
            output_format=output_format,
            extract_properties_func=self._extract_category_properties,
            get_additional_props_func=get_additional_props_with_format,
            columns_struct=output_formats
        )

    #
    #       Get Valid Values for Enumerations
    #

    async def _async_get_glossary_term_statuses(self) -> [str]:
        """Return the list of glossary term status enum values. Async version.

        Parameters
        ----------


        Returns
        -------
        List[str]
            A list of glossary term statuses retrieved from the server.

        """

        url = (f"{self.platform_url}/servers/{self.view_server}"
               f"/api/open-metadata/glossary-browser/glossaries/terms/status-list")

        response = await self._async_make_request("GET", url)
        return response.json().get("statuses", [])

    def get_glossary_term_statuses(self) -> [str]:
        """Return the list of glossary term status enum values.

        Parameters
        ----------


        Returns
        -------
        list of str
            A list of glossary term statuses. Each status is represented as a string.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_glossary_term_statuses())
        return response

    async def _async_get_glossary_term_rel_statuses(self) -> [str]:
        """Return the list of glossary term relationship status enum values.  These values are stored in a
        term-to-term, or term-to-category, relationship and are used to indicate how much the relationship should be
        trusted. Async version.

        Parameters
        ----------


        Returns
        -------
        List[str]
            A list of glossary term statuses retrieved from the server.

        """

        url = (f"{self.platform_url}/servers/{self.view_server}"
               f"/api/open-metadata/glossary-browser/glossaries/terms/relationships/status-list")

        response = await self._async_make_request("GET", url)
        return response.json().get("statuses", [])

    def get_glossary_term_rel_statuses(self) -> [str]:
        """Return the list of glossary term relationship status enum values.  These values are stored in a
        term-to-term, or term-to-category, relationship and are used to indicate how much the relationship should be
        trusted.

        Parameters
        ----------


        Returns
        -------
        list of str
            A list of glossary term statuses. Each status is represented as a string.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_glossary_term_rel_statuses())
        return response

    async def _async_get_glossary_term_activity_types(self) -> [str]:
        """Return the list of glossary term activity type enum values. Async version.

        Parameters
        ----------


        Returns
        -------
        List[str]
            A list of glossary term statuses retrieved from the server.

        """

        url = (f"{self.platform_url}/servers/{self.view_server}"
               f"/api/open-metadata/glossary-browser/glossaries/terms/activity-types")

        response = await self._async_make_request("GET", url)
        return response.json().get("types", [])

    def get_glossary_term_activity_types(self) -> [str]:
        """Return the list of glossary term activity type enum values.

        Parameters
        ----------


        Returns
        -------
        list of str
            A list of glossary term statuses. Each status is represented as a string.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_glossary_term_statuses())
        return response

    async def _async_get_term_relationship_types(self) -> [str]:
        """Return the list of term relationship types enum values. Async version.

        Parameters
        ----------


        Returns
        -------
        List[str]
            A list of glossary term relationships retrieved from the server.

        """

        url = (f"{self.platform_url}/servers/{self.view_server}"
               f"/api/open-metadata/glossary-manager/glossaries/terms/relationships/type-names")

        response = await self._async_make_request("GET", url)
        return response.json().get("names", [])

    def get_term_relationship_types(self) -> [str]:
        """Return the list of term relationship type enum values.

        Parameters
        ----------


        Returns
        -------
        list of str
            A list of term relationship types. Each status is represented as a string.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_term_relationship_types())
        return response

    #
    #       Glossaries
    #

    async def _async_find_glossaries(self, search_string: str, effective_time: str = None, starts_with: bool = False,
                                     ends_with: bool = False, ignore_case: bool = False, for_lineage: bool = False,
                                     for_duplicate_processing: bool = False, type_name: str = None, start_from: int = 0,
                                     page_size: int = None, output_format: str = 'JSON', output_format_set: str | dict = None) -> list | str:
        """Retrieve the list of glossary metadata elements that contain the search string. Async version.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith, and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching glossaries. If the search string is '*' then all glossaries returned.

        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

            If not provided, the server name associated with the instance is used.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        for_lineage : bool, [default=False], optional

        for_duplicate_processing : bool, [default=False], optional
        type_name: str, [default=None], optional
            An optional parameter indicating the subtype of the glossary to filter by.
            Values include 'ControlledGlossary', 'EditingGlossary', and 'StagingGlossary'
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        output_format: str, default = 'JSON'
            Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
        output_format_set: str | dict, optional
            Output format set name or dictionary. Defaults to None.

        Returns
        -------
        List | str

        A list of glossary definitions active in the server.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        if page_size is None:
            page_size = self.page_size
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()

        validate_search_string(search_string)

        if search_string == "*":
            search_string = None

        body = {
            "class": "SearchStringRequestBody", "searchString": search_string, "effectiveTime": effective_time,
            "typeName": type_name,
            }

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
               f"by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
               f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}&forLineage={for_lineage_s}&"
               f"forDuplicateProcessing={for_duplicate_processing_s}")

        response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("elementList", NO_GLOSSARIES_FOUND)
        if element == NO_GLOSSARIES_FOUND:
            if output_format == 'JSON':
                return NO_GLOSSARIES_FOUND
            elif output_format in ['MD', 'FORM', 'REPORT', 'LIST']:
                return "\n# No glossaries found.\n"
            elif output_format == 'DICT':
                return None

        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_glossaries_md(element, search_string, output_format, output_format_set)
        return response.json().get("elementList", NO_GLOSSARIES_FOUND)

    def find_glossaries(self, search_string: str, effective_time: str = None, starts_with: bool = False,
                        ends_with: bool = False, ignore_case: bool = False, for_lineage: bool = False,
                        for_duplicate_processing: bool = False, type_name: str = None, start_from: int = 0,
                        page_size: int = None, output_format: str = "JSON", output_format_set: str | dict = None) -> list | str:
        """Retrieve the list of glossary metadata elements that contain the search string.
                The search string is located in the request body and is interpreted as a plain string.
                The request parameters, startsWith, endsWith, and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching glossaries. If the search string is '*',
            then all glossaries returned.

        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

            If not provided, the server name associated with the instance is used.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        for_lineage : bool, [default=False], optional
             Indicates the search is for lineage.
        for_duplicate_processing : bool, [default=False], optional
        type_name: str, [default=None], optional
            An optional parameter indicating the subtype of the glossary to filter by.
            Values include 'ControlledGlossary', 'EditingGlossary', and 'StagingGlossary'
         start_from : int, [default=0], optional
             When multiple pages of results are available, the page number to start from.
         page_size: int, [default=None]
             The number of items to return in a single page. If not specified, the default will be taken from
             the class instance.
         output_format: str, default = 'JSON'
            Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                LIST - output a markdown table with columns for Glossary Name, Qualified Name, Language, Description,
                Usage
                DICT - output a dictionary structure containing all attributes
         output_format_set: str | dict, optional
            Output format set name or dictionary. Defaults to None.
        Returns
        -------
        List | str

        A list of glossary definitions active in the server.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_glossaries(search_string, effective_time, starts_with, ends_with, ignore_case, for_lineage,
                                        for_duplicate_processing, type_name, start_from, page_size, output_format, output_format_set))

        return response

    async def _async_get_glossary_by_guid(self, glossary_guid: str, effective_time: str = None,
                                          output_format: str = "JSON", output_format_set: str | dict = None) -> dict | str:
        """Retrieves information about a glossary
        Parameters
        ----------
            glossary_guid : str
                Unique idetifier for the glossary
            effective_time: str, optional
                Effective time of the query. If not specified will default to any time. Time format is
                "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
            output_format: str, default = 'JSON'
            Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                LIST - output a markdown table with columns for Glossary Name, Qualified Name, Language, Description,
                Usage
                DICT - output a dictionary structure containing all attributes
            output_format_set: str | dict, optional
                Output format set name or dictionary. Defaults to None.

        Returns
        -------
        dict | str
            if output format is JSON: The glossary definition associated with the glossary_guid
            if output format is MD: A markdown string with the same information.
        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """
        output_format = output_format.upper()
        validate_guid(glossary_guid)

        body = {
            "class": "EffectiveTimeQueryRequestBody", "effectiveTime": effective_time
            }
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
               f"{glossary_guid}/retrieve")
        response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("element", NO_GLOSSARIES_FOUND)
        if element == NO_GLOSSARIES_FOUND:
            return NO_GLOSSARIES_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_glossaries_md(element, "GUID", output_format, output_format_set)
        return response.json().get("element", NO_GLOSSARIES_FOUND)

    def get_glossary_by_guid(self, glossary_guid: str, effective_time: str = None, output_format: str = "JSON", output_format_set: str | dict = None) -> dict:
        """Retrieves information about a glossary
        Parameters
        ----------
            glossary_guid : str
                Unique idetifier for the glossary
            effective_time: str, optional
                Effective time of the query. If not specified will default to any time. Time format is
                "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
            output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                LIST - output a markdown table with columns for Glossary Name, Qualified Name, Language, Description,
                Usage
                DICT - output a dictionary structure containing all attributes
            output_format_set: str | dict, optional
                Output format set name or dictionary. Defaults to None.

        Returns
        -------
        dict
            The glossary definition associated with the glossary_guid

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_glossary_by_guid(glossary_guid, effective_time, output_format, output_format_set))
        return response

    async def _async_get_glossaries_by_name(self, glossary_name: str, effective_time: str = None, start_from: int = 0,
                                            page_size: int = None, ) -> dict | str:
        """Retrieve the list of glossary metadata elements with an exactly matching qualified or display name.
            There are no wildcards supported on this request.

        Parameters
        ----------
        glossary_name: str,
            Name of the glossary to be retrieved
        effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

            If not provided, the server name associated with the instance is used.
        start_from: int, [default=0], optional
             When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.

        Returns
        -------
        None

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """

        if page_size is None:
            page_size = self.page_size
        validate_name(glossary_name)

        if effective_time is None:
            body = {"name": glossary_name}
        else:
            body = {"name": glossary_name, "effectiveTime": effective_time}

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
               f"by-name?startFrom={start_from}&pageSize={page_size}")

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elementList", "No glossaries found")

    def get_glossaries_by_name(self, glossary_name: str, effective_time: str = None, start_from: int = 0,
                               page_size: int = None, ) -> dict | str:
        """Retrieve the list of glossary metadata elements with an exactly matching qualified or display name.
            There are no wildcards supported on this request.

        Parameters
        ----------
        glossary_name: str,
            Name of the glossary to be retrieved
        effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time.

            If not provided, the server name associated with the instance is used.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_glossaries_by_name(glossary_name, effective_time, start_from, page_size))
        return response

    #
    # Glossary Categories
    #

    async def _async_get_glossary_for_category(self, glossary_category_guid: str,
                                               effective_time: str = None, ) -> dict | str:
        """Retrieve the glossary metadata element for the requested category.  The optional request body allows you to
        specify that the glossary element should only be returned if it was effective at a particular time.

        Parameters
        ----------
        glossary_category_guid: str,
            Unique identifier for the glossary category.
        effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

            If not provided, the server name associated with the instance is used.

        Returns
        -------
        A dict structure with the glossary metadata element for the requested category.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """

        body = {
            "class": "EffectiveTimeQueryRequestBody", "effectiveTime": effective_time,
            }

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
               f"for-category/{glossary_category_guid}/retrieve")

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elementList", "No categories found")

    def get_glossary_for_category(self, glossary_category_guid: str, effective_time: str = None, ) -> dict | str:
        """Retrieve the glossary metadata element for the requested category.  The optional request body allows you to
        specify that the glossary element should only be returned if it was effective at a particular time.

        Parameters
        ----------
        glossary_category_guid: str,
            Unique identifier for the glossary category.
        effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

            If not provided, the server name associated with the instance is used.

        Returns
        -------
        A dict structure with the glossary metadata element for the requested category.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_glossary_for_category(glossary_category_guid, effective_time))
        return response

    async def _async_get_glossary_subcategories(self, glossary_category_guid: str, effective_time: str = None,
                                                start_from: int = 0, page_size: int = max_paging_size,
                                                for_lineage: bool = False,
                                                for_duplicate_processing: bool = False, ) -> dict | str:
        """Glossary categories can be organized in a hierarchy. Retrieve the subcategories for the glossary category
        metadata element with the supplied unique identifier. If the requested category does not have any subcategories,
         null is returned. The optional request body contain an effective time for the query.

        Parameters
        ----------
        glossary_category_guid: str,
            Unique identifier for the glossary category.
        effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        start_from: int, [default=0], optional
            The page to start from.
        page_size: int, [default=max_paging_size], optional
            The number of results per page to return.
        for_lineage: bool, [default=False], optional
            Indicates the search is for lineage.
        for_duplicate_processing: bool, [default=False], optional
            If set to True the user will handle duplicate processing.

        Returns
        -------
        A dict list with the glossary metadata element for the requested category.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()

        body = {
            "class": "EffectiveTimeQueryRequestBody", "effectiveTime": effective_time,
            }

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
               f"categories/{glossary_category_guid}/subcategories/retrieve?startFrom={start_from}&pageSize="
               f"{page_size}&"
               f"forLineage={for_lineage_s}&forDuplicateProcessing={for_duplicate_processing_s}")
        if effective_time:
            response = await self._async_make_request("POST", url, body_slimmer(body))
        else:
            response = await self._async_make_request("POST", url)

        return response.json().get("elementList", "No categories found")

    def get_glossary_subcategories(self, glossary_category_guid: str, effective_time: str = None, start_from: int = 0,
                                   page_size: int = max_paging_size, for_lineage: bool = False,
                                   for_duplicate_processing: bool = False, ) -> dict | str:
        """Glossary categories can be organized in a hierarchy. Retrieve the subcategories for the glossary category
        metadata element with the supplied unique identifier. If the requested category does not have any subcategories,
         null is returned. The optional request body contain an effective time for the query.

        Parameters
        ----------
        glossary_category_guid: str,
            Unique identifier for the glossary category.
        effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        start_from: int, [default=0], optional
            The page to start from.
        page_size: int, [default=max_paging_size], optional
            The number of results per page to return.
        for_lineage: bool, [default=False], optional
            Indicates the search is for lineage.
        for_duplicate_processing: bool, [default=False], optional
            If set to True the user will handle duplicate processing.

        Returns
        -------
        A dict list with the glossary metadata element for the requested category.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_glossary_subcategories(glossary_category_guid, effective_time, start_from, page_size,
                                                   for_lineage, for_duplicate_processing))
        return response

    async def _async_find_glossary_categories(self, search_string: str, effective_time: str = None,
                                              starts_with: bool = False, ends_with: bool = False,
                                              ignore_case: bool = False, start_from: int = 0, page_size: int = None,
                                              output_format: str = "JSON", output_format_set: str | dict = None) -> list | str:
        """Retrieve the list of glossary category metadata elements that contain the search string.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith, and ignoreCase can be used to allow a fuzzy search.
            Async version.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching glossaries. If the search string is '*' then all glossaries returned.

        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

            If not provided, the server name associated with the instance is used.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        output_format: str, default = 'JSON'
            Type of output to produce:
            JSON - output standard json
            MD - output standard markdown with no preamble
            FORM - output markdown with a preamble for a form
            REPORT - output markdown with a preamble for a report
        output_format_set: str | dict, optional
            Output format set name or dictionary. Defaults to None.

        Returns
        -------
        List | str

        A list of glossary definitions active in the server.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        if page_size is None:
            page_size = self.page_size
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()

        validate_search_string(search_string)

        if search_string == "*":
            search_string = None

        body = {
            "class": "SearchStringRequestBody", "searchString": search_string, "effectiveTime": effective_time,
            }

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
               f"categories/by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
               f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}")
        response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("elementList", NO_CATEGORIES_FOUND)
        if element == NO_CATEGORIES_FOUND:
            if output_format == 'JSON':
                return NO_CATEGORIES_FOUND
            elif output_format in ['MD', 'FORM', 'REPORT', 'LIST']:
                return "\n# No categories found.\n"
            elif output_format == 'DICT':
                return None
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_categories_md(element, search_string, output_format, output_format_set)
        return response.json().get("elementList", NO_CATEGORIES_FOUND)

    def find_glossary_categories(self, search_string: str, effective_time: str = None, starts_with: bool = False,
                                 ends_with: bool = False, ignore_case: bool = False, start_from: int = 0,
                                 page_size: int = None, output_format: str = "JSON", output_format_set: str | dict = None) -> list | str:
        """Retrieve the list of glossary category metadata elements that contain the search string.
         The search string is located in the request body and is interpreted as a plain string.
         The request parameters, startsWith, endsWith, and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching glossaries. If the search string is '*' then all
             glossaries returned.

        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

            If not provided, the server name associated with the instance is used.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        output_format: str, default = 'JSON'
            Type of output to produce:
            JSON - output standard json
            MD - output standard markdown with no preamble
            FORM - output markdown with a preamble for a form
            REPORT - output markdown with a preamble for a report
        output_format_set: str | dict, optional
            Output format set name or dictionary. Defaults to None.

        Returns
        -------
        List | str

        A list of glossary definitions active in the server.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_glossary_categories(search_string, effective_time, starts_with, ends_with, ignore_case,
                                                 start_from, page_size, output_format, output_format_set))

        return response

    async def _async_get_categories_for_glossary(self, glossary_guid: str, start_from: int = 0,
                                                 page_size: int = None, ) -> list | str:
        """Return the list of categories associated with a glossary.
            Async version.

        Parameters
        ----------
        glossary_guid: str,
            Unique identity of the glossary

            If not provided, the server name associated with the instance is used.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of categories associated with a glossary.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        if page_size is None:
            page_size = self.page_size

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
               f"{glossary_guid}/categories/retrieve?startFrom={start_from}&pageSize={page_size}")

        response = await self._async_make_request("POST", url)
        return response.json().get("elementList", "No Categories found")

    def get_categories_for_glossary(self, glossary_guid: str, start_from: int = 0,
                                    page_size: int = None, ) -> list | str:
        """Return the list of categories associated with a glossary.

        Parameters
        ----------
        glossary_guid: str,
            Unique identity of the glossary

            If not provided, the server name associated with the instance is used.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of categories associated with a glossary.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_categories_for_glossary(glossary_guid, start_from, page_size))
        return response

    async def _async_get_categories_for_term(self, glossary_term_guid: str, start_from: int = 0,
                                             page_size: int = None, ) -> list | str:
        """Return the list of categories associated with a glossary term.
            Async version.

        Parameters
        ----------
        glossary_term_guid: str,
            Unique identity of a glossary term

        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of categories associated with a glossary term.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        if page_size is None:
            page_size = self.page_size

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/terms/"
               f"{glossary_term_guid}/categories/retrieve?startFrom={start_from}&pageSize={page_size}")

        response = await self._async_make_request("POST", url)
        return response.json().get("elementList", NO_CATEGORIES_FOUND)

    def get_categories_for_term(self, glossary_term_guid: str, start_from: int = 0,
                                page_size: int = None, ) -> list | str:
        """Return the list of categories associated with a glossary term.

        Parameters
        ----------
        glossary_term_guid: str,
            Unique identity of a glossary term

        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of categories associated with a glossary term.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_categories_for_term(glossary_term_guid, start_from, page_size))
        return response

    async def _async_get_categories_by_name(self, name: str, glossary_guid: str = None, status: [str] = ["ACTIVE"],
                                            start_from: int = 0, page_size: int = None, ) -> list | str:
        """Retrieve the list of glossary category metadata elements that either have the requested qualified name or
            display name. The name to search for is located in the request body and is interpreted as a plain string.
            The request body also supports the specification of a glossaryGUID to restrict the search to within a single
            glossary.

            Async version.

        Parameters
        ----------
        name: str,
            category name to search for.
        glossary_guid: str, optional
            The identity of the glossary to search. If not specified, all glossaries will be searched.
        start_from: int, [default=0], optional
             When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of categories with the corresponding display name or qualified name.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        if page_size is None:
            page_size = self.page_size
        validate_name(name)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/categories/"
            f"by-name?startFrom={start_from}&pageSize={page_size}")

        body = {
            "class": "GlossaryNameRequestBody", "name": name, "glossaryGUID": glossary_guid,
            "limitResultsByStatus": status,
            }

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elementList", NO_CATEGORIES_FOUND)

    def get_categories_by_name(self, name: str, glossary_guid: str = None, status: [str] = ["ACTIVE"],
                               start_from: int = 0, page_size: int = None) -> list | str:
        """Retrieve the list of glossary category metadata elements that either have the requested qualified name or
            display name. The name to search for is located in the request body and is interpreted as a plain string.
            The request body also supports the specification of a glossaryGUID to restrict the search to within a
            single glossary.

        Parameters
        ----------
        name: str,
            category name to search for.
        glossary_guid: str, optional
            The identity of the glossary to search. If not specified, all glossaries will be searched.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of categories with the corresponding display name or qualified name.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_categories_by_name(name, glossary_guid, status, start_from, page_size))
        return response

    async def _async_get_category_by_guid(self, glossary_category_guid: str, effective_time: str = None,
                                          output_format: str = 'JSON', output_format_set: str | dict = None) -> list | str:
        """Retrieve the requested glossary category metadata element.  The optional request body contain an effective
        time for the query..

        Async version.

        Parameters
        ----------
        glossary_category_guid: str
            The identity of the glossary category to search.
        effective_time: str, optional
            If specified, the category should only be returned if it was effective at the specified time.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

        output_format: str, default = 'JSON'
            Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
        output_format_set: str | dict, optional
            Output format set name or dictionary. Defaults to None.

        Returns
        -------
        List | str

        Details for the category with the glossary category GUID.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        output_format = output_format.upper()
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/categories/"
            f"{glossary_category_guid}/retrieve")

        body = {
            "class": "EffectiveTimeQueryRequestBody", "effectiveTime": effective_time,
            }

        response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("element", NO_CATEGORIES_FOUND)
        if element == NO_CATEGORIES_FOUND:
            return NO_CATEGORIES_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_categories_md(element, "GUID", output_format, output_format_set)
        return response.json().get("element", NO_CATEGORIES_FOUND)

    def get_category_by_guid(self, glossary_category_guid: str, effective_time: str = None,
                             output_format: str = 'JSON', output_format_set: str | dict = None) -> list | str:
        """Retrieve the requested glossary category metadata element.  The optional request body contain an effective
        time for the query..

        Parameters
        ----------
        glossary_category_guid: str
            The identity of the glossary category to search.
        effective_time: str, optional
            If specified, the category should only be returned if it was effective at the specified time.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

        output_format: str, default = 'JSON'
            Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
        output_format_set: str | dict, optional
            Output format set name or dictionary. Defaults to None.

        Returns
        -------
        List | str

        Details for the category with the glossary category GUID.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_category_by_guid(glossary_category_guid, effective_time, output_format))
        return response

    async def _async_get_category_parent(self, glossary_category_guid: str, effective_time: str = None, ) -> list | str:
        """Glossary categories can be organized in a hierarchy. Retrieve the parent glossary category metadata
            element for the glossary category with the supplied unique identifier.  If the requested category
            does not have a parent category, null is returned.  The optional request body contain an effective time
            for the query.

        Async version.

        Parameters
        ----------
        glossary_category_guid: str
            The identity of the glossary category to search.
        effective_time: str, optional
            If specified, the category should only be returned if it was effective at the specified time.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

            If not provided, the server name associated with the instance is used.

        Returns
        -------
        List | str

        Details for the parent category with the glossary category GUID.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/categories/"
            f"{glossary_category_guid}/parent/retrieve")

        body = {
            "class": "EffectiveTimeQueryRequestBody", "effectiveTime": effective_time,
            }

        response = await self._async_make_request("POST", url, body)
        return response.json().get("element", "No Parent Category found")

    def get_category_parent(self, glossary_category_guid: str, effective_time: str = None, ) -> list | str:
        """Glossary categories can be organized in a hierarchy. Retrieve the parent glossary category metadata
            element for the glossary category with the supplied unique identifier.  If the requested category
            does not have a parent category, null is returned.  The optional request body contain an effective time
            for the query.

        Parameters
        ----------
        glossary_category_guid: str
            The identity of the glossary category to search.
        effective_time: str, optional
            If specified, the category should only be returned if it was effective at the specified time.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).

            If not provided, the server name associated with the instance is used.

        Returns
        -------
        List | str

        Details for the parent category with the glossary category GUID.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_category_parent(glossary_category_guid, effective_time))
        return response

    def get_glossary_category_structure(self, glossary_guid: str, output_format: str = "DICT", output_format_set: str | dict = None) -> dict | str:
        """Derive the category structure of an Egeria glossary.

        This method builds a hierarchical representation of the categories in a glossary,
        showing the parent-child relationships between categories.

        Parameters
        ----------
        glossary_guid: str
            The unique identifier of the glossary.
        output_format: str, default = 'DICT'
            The format of the output:
            - DICT: Returns a Python dictionary structure
            - LIST: Returns a markdown table
            - MD: Returns a markdown outline with bullets and indentations
        output_format_set: str | dict, optional
            Output format set name or dictionary. Defaults to None.

        Returns
        -------
        dict | str
            If output_format is DICT, returns a dictionary structure representing the category hierarchy.
            If output_format is LIST, returns a markdown table representing the category hierarchy.
            If output_format is MD, returns a markdown outline with bullets and indentations.

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action
        """
        from pyegeria._validators import validate_guid

        validate_guid(glossary_guid)

        # Get all categories in the glossary
        all_categories = self.get_categories_for_glossary(glossary_guid)
        if isinstance(all_categories, str):
            return NO_CATEGORIES_FOUND

        # Create a dictionary to store categories by GUID for quick lookup
        categories_by_guid = {cat['elementHeader']['guid']: cat for cat in all_categories}

        # Identify root categories (categories with no parent)
        root_guids = []
        for cat_guid in categories_by_guid.keys():
            parent = self.get_category_parent(cat_guid)
            if isinstance(parent, str):
                root_guids.append(cat_guid)  # This category has no parent

        # Build the category tree
        category_tree = []

        def build_category_tree(category_guid):
            """Recursively build a category tree for a category."""
            if category_guid not in categories_by_guid:
                return None

            category = categories_by_guid[category_guid]
            display_name = category['glossaryCategoryProperties'].get('displayName', '---')
            qualified_name = category['glossaryCategoryProperties'].get('qualifiedName', '---')
            description = category['glossaryCategoryProperties'].get('description', '---')

            # Get subcategories
            subcategories = self.get_glossary_subcategories(category_guid)
            children = []

            if isinstance(subcategories, list):
                for subcat in subcategories:
                    subcat_guid = subcat['elementHeader']['guid']
                    child_tree = build_category_tree(subcat_guid)
                    if child_tree:
                        children.append(child_tree)

            # Get parent category information
            parent_info = None
            parent = self.get_category_parent(category_guid)
            if not isinstance(parent, str):
                parent_guid = parent['elementHeader']['guid']
                parent_name = parent['glossaryCategoryProperties'].get('displayName', '---')
                parent_info = {
                    'GUID': parent_guid, 'name': parent_name
                    }

            return {
                'GUID': category_guid, 'name': display_name, 'qualifiedName': qualified_name,
                'description': description, 'parent': parent_info, 'children': children
                }

        # Build tree for each root category
        for root_guid in root_guids:
            tree = build_category_tree(root_guid)
            if tree:
                category_tree.append(tree)

        # Format the output according to the specified output_format
        if output_format == "DICT":
            return {
                'glossary_guid': glossary_guid, 'categories': category_tree
                }
        elif output_format == "LIST":
            # Generate markdown table
            md_table = "| Category | Path | Description | Parent Category | Child Categories |\n"
            md_table += "|---------|------|-------------|----------------|------------------|\n"

            def add_categories_to_table(categories, path=""):
                nonlocal md_table
                for category in categories:
                    category_path = f"{path}/{category['name']}" if path else category['name']

                    # Get parent category name
                    parent_name = "None"
                    if category['parent']:
                        parent_name = category['parent']['name']

                    # Get child categories names
                    child_names = []
                    for child in category['children']:
                        child_names.append(child['name'])
                    child_categories = ", ".join(child_names) if child_names else "None"

                    md_table += (f"| {category['name']} | {category_path} | "
                                 f"{self._format_for_markdown_table(category['description'])} | "
                                 f"{parent_name} | {child_categories} |\n")
                    if category['children']:
                        add_categories_to_table(category['children'], category_path)

            add_categories_to_table(category_tree)
            return md_table
        elif output_format == "MD":
            # Generate markdown outline with bullets and indentations
            md_outline = f"# Category Structure for Glossary (GUID: {glossary_guid})\n\n"

            def add_categories_to_outline(categories, indent_level=0):
                nonlocal md_outline
                for category in categories:
                    # Add bullet with proper indentation
                    indent = "  " * indent_level
                    md_outline += f"{indent}- **{category['name']}**"

                    # Add description if available
                    if category['description'] and category['description'] != '---':
                        md_outline += f": {category['description']}"

                    md_outline += "\n"

                    # Process children with increased indentation
                    if category['children']:
                        add_categories_to_outline(category['children'], indent_level + 1)

            add_categories_to_outline(category_tree)
            return md_outline
        else:
            return f"Unsupported output format: {output_format}. Use 'DICT', 'LIST', or 'MD'."

    #
    #  Terms
    #

    async def _async_get_terms_for_category(self, glossary_category_guid: str, effective_time: str = None,
                                            start_from: int = 0, page_size: int = None, ) -> list | str:
        """Retrieve ALL the glossary terms in a category.
            The request body also supports the specification of an effective time for the query.

            Async Version.

        Parameters
        ----------
            glossary_category_guid : str
                Unique identifier for the glossary category to retrieve terms from.
            effective_time : str, optional
                If specified, the terms are returned if they are active at the `effective_time
                Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
            start_from: int, optional defaults to 0
                The page number to start retrieving elements from
            page_size : int, optional defaults to None
                The number of elements to retrieve
        Returns
        -------
        [dict]
            The glossary definition associated with the glossary_guid

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        """

        validate_guid(glossary_category_guid)

        if page_size is None:
            page_size = self.page_size

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/categories/"
            f"{glossary_category_guid}/terms/retrieve?startFrom={start_from}&pageSize={page_size}")

        if effective_time is not None:
            body = {"effectiveTime": effective_time}
            response = await self._async_make_request("POST", url, body)
        else:
            response = await self._async_make_request("POST", url)

        return response.json().get("elementList", "No terms found")

    def get_terms_for_category(self, glossary_category_guid: str, effective_time: str = None, start_from: int = 0,
                               page_size: int = None, ) -> list | str:
        """Retrieve ALL the glossary terms in a category.
            The request body also supports the specification of an effective time for the query.

            Async Version.

        Parameters
        ----------
            glossary_category_guid : str
                Unique identifier for the glossary category to retrieve terms from.

            effective_time : str, optional
                If specified, the terms are returned if they are active at the `effective_time.
                Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)`.
            start_from: int, optional defaults to 0
                The page number to start retrieving elements from
            page_size : int, optional defaults to None
                The number of elements to retrieve
        Returns
        -------
        dict
            The glossary definition associated with the glossary_guid

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_terms_for_category(glossary_category_guid, effective_time, start_from, page_size, ))

        return response

    async def _async_get_terms_for_glossary(self, glossary_guid: str, effective_time: str = None, start_from: int = 0,
                                            page_size: int = None, ) -> list | str:
        """Retrieve the list of glossary terms associated with a glossary.
            The request body also supports the specification of an effective time for the query.
        Parameters
        ----------
            glossary_guid : str
                Unique identifier for the glossary

            effective_time : str, optional
                If specified, terms are potentially included if they are active at the`effective_time.
                Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)`
            start_from: int, optional defaults to 0
                The page number to start retrieving elements from
            page_size : int, optional defaults to None
                The number of elements to retrieve
        Returns
        -------
        dict
            The glossary definition associated with the glossary_guid

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """

        validate_guid(glossary_guid)

        if page_size is None:
            page_size = self.page_size

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
               f"{glossary_guid}/terms/retrieve?startFrom={start_from}&pageSize={page_size}")

        if effective_time is not None:
            body = {"effectiveTime": effective_time}
            response = await self._async_make_request("POST", url, body)
        else:
            response = await self._async_make_request("POST", url)

        return response.json().get("elementList", "No terms found")

    def get_terms_for_glossary(self, glossary_guid: str, effective_time: str = None, start_from: int = 0,
                               page_size: int = None, ) -> list | str:
        """Retrieve the list of glossary terms associated with a glossary.
            The request body also supports the specification of an effective time for the query.
        Parameters
        ----------
            glossary_guid : str
                Unique identifier for the glossary

            effective_time : str, optional
                If specified, terms are potentially returned if they are active at the `effective_time`
                Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
            start_from: int, optional defaults to 0
                The page number to start retrieving elements from
            page_size : int, optional defaults to None
                The number of elements to retrieve
        Returns
        -------
        dict
            The glossary definition associated with the glossary_guid

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_terms_for_glossary(glossary_guid, effective_time, start_from, page_size))

        return response

    async def _async_get_related_terms(self, term_guid: str, effective_time: str = None, start_from: int = 0,
                                       page_size: int = None, output_format: str = "JSON") -> list | str:
        """This call retrieves details of the glossary terms linked to this glossary term.
        Notice the original org 1 glossary term is linked via the "SourcedFrom" relationship.
        Parameters
        ----------
            term_guid : str
                Unique identifier for the glossary term

            effective_time : str, optional
                If specified, term relationships are included if they are active at the `effective_time`.
                Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
            start_from: int, optional defaults to 0
                The page number to start retrieving elements from
            page_size : int, optional defaults to None
                The number of elements to retrieve
        Returns
        -------
        dict
            The glossary definition associated with the glossary_guid

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """

        validate_guid(term_guid)

        if page_size is None:
            page_size = self.page_size

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/terms/"
               f"{term_guid}/related-terms?startFrom={start_from}&pageSize={page_size}")

        if effective_time is not None:
            body = {"effectiveTime": effective_time}
            response = await self._async_make_request("POST", url, body)
        else:
            response = await self._async_make_request("POST", url)

        term_elements = response.json().get("elementList", NO_TERMS_FOUND)
        if term_elements == NO_TERMS_FOUND:
            if output_format == 'JSON':
                return NO_TERMS_FOUND
            elif output_format in ['MD', 'FORM', 'REPORT', 'LIST']:
                return "\n# No Terms found.\n"
            elif output_format == 'DICT':
                return None
        if output_format != "JSON":  # return a simplified markdown representation
            return self.generate_related_terms_md(term_elements, term_guid, output_format)
        return response.json().get("elementList", NO_TERMS_FOUND)

    def get_related_terms(self, term_guid: str, effective_time: str = None, start_from: int = 0, page_size: int = None,
                          output_format="JSON") -> list | str:
        """This call retrieves details of the glossary terms linked to this glossary term.
        Notice the original org 1 glossary term is linked via the "SourcedFrom" relationship..
        Parameters
        ----------
            term_guid : str
                Unique identifier for the glossary term

            effective_time : str, optional
                If specified, term relationships are included if they are active at the `effective_time`.
                Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
            start_from: int, optional defaults to 0
                The page number to start retrieving elements from
            page_size : int, optional defaults to None
                The number of elements to retrieve
        Returns
        -------
        dict
            The glossary definition associated with the glossary_guid

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_related_terms(term_guid, effective_time, start_from, page_size, output_format))

        return response

    def generate_related_terms_md(self, term_elements: list, term_guid: str, output_format: str = 'MD', output_format_set: str | dict = None) -> str | list:
        """
        Generate a simplified representation of related terms.

        Args:
            term_elements (list): List of term elements with relationship information
            term_guid (str): GUID of the term for which to generate related terms
            output_format (str): Output format (MD, LIST, DICT, etc.)
            output_format_set (str | dict, optional): Output format set name or dictionary. Defaults to None.

        Returns:
            str | list: Markdown string or list of dictionaries depending on output_format
        """
        # Get the first term's display name and qualified name
        term_name = "Term"
        try:
            term_info = self.get_term_by_guid(term_guid, output_format="DICT")
            # Handle case where term_info is a list of dictionaries
            if isinstance(term_info, list) and len(term_info) > 0:
                term_info = term_info[0]  # Get the first term
            if isinstance(term_info, dict) and 'display_name' in term_info:
                term_name = term_info['display_name']
        except:
            # If we can't get the term info, just use the default name
            pass

        # Create a list to store the simplified related terms
        related_terms = []

        # Process each term element
        for element in term_elements:
            # Extract relationship type from the relationship header
            relationship_type = element['relatedBy']['relationshipHeader']['type']['typeName']

            # Extract related term information
            related_term = {
                'first_term_display_name': term_name, 'first_term_qualified_name': term_info.get('qualified_name', ''),
                'related_term_display_name': element['glossaryTermProperties'].get('displayName', ''),
                'related_term_qualified_name': element['glossaryTermProperties'].get('qualifiedName', ''),
                'relationship_type': relationship_type
                }

            related_terms.append(related_term)

        # Define default columns for LIST format
        default_columns = [
            {'name': 'First Term', 'key': 'first_term_display_name'},
            {'name': 'First Term Qualified Name', 'key': 'first_term_qualified_name'},
            {'name': 'Related Term', 'key': 'related_term_display_name'},
            {'name': 'Related Term Qualified Name', 'key': 'related_term_qualified_name'},
            {'name': 'Relationship Type', 'key': 'relationship_type'},
        ]

        # Determine the output format set
        output_formats = None
        if output_format_set:
            if isinstance(output_format_set, str):
                output_formats = select_output_format_set(output_format_set, output_format)
            elif isinstance(output_format_set, dict):
                output_formats = get_output_format_type_match(output_format_set, output_format)
        else:
            # Use default entity type to lookup the output format
            output_formats = select_output_format_set("RelatedTerms", output_format)

        # Return based on output format
        if output_format == 'DICT':
            return related_terms

        # For MD, LIST, FORM, REPORT formats, create a markdown representation
        md_output = f"# Related Terms for {term_name}\n\n"

        if output_format == 'LIST':
            # If we have an output format set with columns, use those
            columns = default_columns
            if output_formats and 'formats' in output_formats and 'columns' in output_formats['formats']:
                columns = output_formats['formats']['columns']
            
            # Create a table header
            header_row = "| "
            separator_row = "|"
            for column in columns:
                header_row += f"{column['name']} | "
                separator_row += "------------|"
            
            md_output += header_row + "\n"
            md_output += separator_row + "\n"

            # Add data rows
            for term in related_terms:
                row = "| "
                for column in columns:
                    key = column['key']
                    value = term.get(key, '')
                    row += f"{value} | "
                md_output += row + "\n"
        else:
            # For other formats, create a more detailed representation
            for term in related_terms:
                md_output += f"## {term['relationship_type']} Relationship\n\n"
                md_output += (f"**First Term:** {term['first_term_display_name']} ("
                              f"{term['first_term_qualified_name']})\n\n")
                md_output += f"**Related Term:** {term['related_term_display_name']} ({term['related_term_qualified_name']})\n\n"
                md_output += "---\n\n"

        return md_output

    def get_term_details(self, term_name: str, effective_time: str = None, output_format: str = 'DICT', output_format_set: str | dict = None) -> dict | str:
        """Retrieve detailed information about a term, combining basic term details and related terms.

        This method combines the term details retrieved from get_term_by_guid and the related terms
        information from generate_related_terms_md.

        Parameters
        ----------
        term_name : str
            Either the display name or the qualified name of the term to retrieve.
        effective_time : str, optional
            Time at which the term is active. If not specified, the current time is used.
        output_format : str, default = 'DICT'
            Type of output to produce:
                DICT - output a dictionary with combined term details and related terms
                REPORT - output a markdown report with combined term details and related terms
        output_format_set : str | dict, optional
            Output format set name or dictionary. Defaults to None.

        Returns
        -------
        dict | str
            A dictionary or markdown string containing the combined term details and related terms.

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.
        """
        # Check if the output format is supported
        if output_format not in ["DICT", "REPORT"]:
            return f"Unsupported output format: {output_format}. Supported formats are DICT and REPORT."

        # Search for the term using the qualified name
        terms = self.get_terms_by_name(term_name, effective_time=effective_time, output_format="DICT")

        # Check if we found any terms
        if not terms or (isinstance(terms, str) and terms == NO_TERMS_FOUND):
            return f"No term found with name: {term_name}"

        # Make sure we only have one term
        if isinstance(terms, list) and len(terms) > 1:
            return f"Multiple terms found with name: {term_name} - please specify the qualified name."

        term_details = terms[0]

        # Get related terms
        try:
            related_terms_response = self.get_related_terms(term_details.get('guid', ''), output_format="DICT")
        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException):
            # If we can't get related terms, set to empty list
            related_terms_response = []

        # If no related terms were found, set to empty list
        if isinstance(related_terms_response, str) and related_terms_response == NO_TERMS_FOUND:
            related_terms = []
        elif related_terms_response is None:
            related_terms = []
        else:
            related_terms = related_terms_response

        # Combine the data
        if output_format == "DICT":
            # Create a combined dictionary
            combined_data = {
                "term_details": term_details, "related_terms": related_terms
                }
            return combined_data
        elif output_format == "REPORT":
            # Create a markdown report
            md_output = f"# Term Details Report for `{term_name}` \n\n"

            # Add term details
            md_output += "## Basic Term Information\n\n"
            md_output += f"**Display Name:** {term_details.get('display_name', '')}\n\n"
            md_output += f"**Qualified Name:** {term_details.get('qualified_name', '')}\n\n"
            md_output += f"**GUID:** {term_details.get('guid', '')}\n\n"

            if 'summary' in term_details and term_details['summary']:
                md_output += f"**Summary:** {term_details.get('summary', '')}\n\n"

            if 'description' in term_details and term_details['description']:
                md_output += f"**Description:** {term_details.get('description', '')}\n\n"

            if 'examples' in term_details and term_details['examples']:
                md_output += f"**Examples:** {term_details.get('examples', '')}\n\n"

            if 'usage' in term_details and term_details['usage']:
                md_output += f"**Usage:** {term_details.get('usage', '')}\n\n"

            if 'aliases' in term_details and term_details['aliases']:
                md_output += f"**Aliases:** {term_details.get('aliases', '')}\n\n"

            if 'status' in term_details and term_details['status']:
                md_output += f"**Status:** {term_details.get('status', '')}\n\n"

            if 'in_glossary' in term_details and term_details['in_glossary']:
                md_output += f"**Glossary:** {term_details.get('in_glossary', '')}\n\n"

            if 'categories' in term_details and term_details['categories']:
                md_output += f"**Categories:** {', '.join(term_details.get('categories', []))}\n\n"

            # Add related terms
            md_output += "## Related Terms\n\n"

            if not related_terms:
                md_output += "No related terms found.\n\n"
            else:
                # Create a table for related terms
                md_output += "| Related Term | Qualified Name | Relationship Type |\n"
                md_output += "|--------------|---------------|-------------------|\n"

                for term in related_terms:
                    md_output += f"| {term.get('related_term_display_name', '')} | "
                    md_output += f"{term.get('related_term_qualified_name', '')} | "
                    md_output += f"{term.get('relationship_type', '')} |\n"

            return md_output
        else:
            return f"Unsupported output format: {output_format}. Supported formats are DICT and REPORT."

    async def _async_get_glossary_for_term(self, term_guid: str, effective_time: str = None) -> dict | str:
        """Retrieve the glossary metadata element for the requested term.  The optional request body allows you to
            specify that the glossary element should only be returned if it was effective at a particular time.

            Async Version.

        Parameters
        ----------
        term_guid : str
            The unique identifier for the term.

        effective_time : datetime, optional
            If specified, the term information will be retrieved if it is active at the `effective_time`.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

        Returns
        -------
        dict
            The glossary information retrieved for the specified term.
        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """

        validate_guid(term_guid)

        body = {
            "class": "EffectiveTimeQueryRequestBody", "effectiveTime": effective_time,
            }
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
               f"for-term/{term_guid}/retrieve")

        response = await self._async_make_request("POST", url, body_slimmer(body))
        return response.json().get("element", NO_GLOSSARIES_FOUND)

    def get_glossary_for_term(self, term_guid: str, effective_time: str = None) -> dict | str:
        """Retrieve the glossary metadata element for the requested term.  The optional request body allows you to
            specify that the glossary element should only be returned if it was effective at a particular time.

            Async Version.

        Parameters
        ----------
        term_guid : str
            The unique identifier for the term.

        effective_time : datetime, optional
            TIf specified, the term information will be retrieved if it is active at the `effective_time`.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).

        Returns
        -------
        dict
            The glossary information retrieved for the specified term.
        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_glossary_for_term(term_guid, effective_time))
        return response

    async def _async_get_terms_by_name(self, term: str, glossary_guid: str = None, status_filter: list = [],
                                       effective_time: str = None, for_lineage: bool = False,
                                       for_duplicate_processing: bool = False, start_from: int = 0,
                                       page_size: int = None, output_format="JSON", output_format_set: str | dict = None) -> list:
        """Retrieve glossary terms by display name or qualified name. Async Version.

        Parameters
        ----------
        term : str
            The term to search for in the glossaries.
        glossary_guid : str, optional
            The GUID of the glossary to search in. If not provided, the search will be performed in all glossaries.
        status_filter : list, optional
            A list of status values to filter the search results. Default is an empty list, which means no filtering.

        effective_time : datetime, optional
            If specified, the term information will be retrieved if it is active at the `effective_time`.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage : bool, optional
            Flag to indicate whether the search should include lineage information. Default is False.
        for_duplicate_processing : bool, optional
            Flag to indicate whether the search should include duplicate processing information. Default is False.
        start_from : int, optional
            The index of the first term to retrieve. Default is 0.
        page_size : int, optional
            The number of terms to retrieve per page. If not provided, it will use the default page size.
        output_format: str, default = 'JSON'
            Type of output to produce:
            JSON - output standard json
            MD - output standard markdown with no preamble
            FORM - output markdown with a preamble for a form
            REPORT - output markdown with a preamble for a report
            DICT - output a simplified DICT structure
        output_format_set: str | dict, optional
            Output format set name or dictionary. Defaults to None.

        Returns
        -------
        list
            A list of terms matching the search criteria. If no terms are found, it returns the string "No terms found".

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        """

        if page_size is None:
            page_size = self.page_size

        validate_name(term)

        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()

        body = {
            "class": "GlossaryNameRequestBody", "glossaryGUID": glossary_guid, "name": term,
            "effectiveTime": effective_time, "limitResultsByStatus": status_filter,
            }
        # body = body_slimmer(body)

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
               f"terms/by-name?startFrom={start_from}&pageSize={page_size}&"
               f"&forLineage={for_lineage_s}&forDuplicateProcessing={for_duplicate_processing_s}")

        # print(f"\n\nURL is: \n {url}\n\nBody is: \n{body}")
        response = await self._async_make_request("POST", url, body_slimmer(body))
        term_elements = response.json().get("elementList", NO_TERMS_FOUND)
        if term_elements == NO_TERMS_FOUND:
            if output_format == 'JSON':
                return NO_TERMS_FOUND
            elif output_format in ['MD', 'FORM', 'REPORT', 'LIST']:
                return "\n# No Terms found.\n"
            elif output_format == 'DICT':
                return None
        if output_format != "JSON":  # return a simplified markdown representation
            return self.generate_terms_md(term_elements, term, output_format, output_format_set)
        return response.json().get("elementList", NO_TERMS_FOUND)

    def get_terms_by_name(self, term: str, glossary_guid: str = None, status_filter: list = [],
                          effective_time: str = None, for_lineage: bool = False, for_duplicate_processing: bool = False,
                          start_from: int = 0, page_size: int = None, output_format="JSON", output_format_set: str | dict = None) -> list:
        """Retrieve glossary terms by display name or qualified name.

        Parameters
        ----------
        term : str
            The term to search for in the glossaries.
        glossary_guid : str, optional
            The GUID of the glossary to search in. If not provided, the search will be performed in all glossaries.
        status_filter : list, optional
            A list of status values to filter the search results. Default is an empty list, which means no filtering.

        effective_time : datetime, optional
            If specified, the term information will be retrieved if it is active at the `effective_time`.
             Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage : bool, optional
            Flag to indicate whether the search should include lineage information. Default is False.
        for_duplicate_processing : bool, optional
            Flag to indicate whether the search should include duplicate processing information. Default is False.
        start_from : int, optional
            The index of the first term to retrieve. Default is 0.
        page_size : int, optional
            The number of terms to retrieve per page. If not provided, it will use the default page size.
         output_format: str, default = 'JSON'
            Type of output to produce:
            JSON - output standard json
            MD - output standard markdown with no preamble
            FORM - output markdown with a preamble for a form
            REPORT - output markdown with a preamble for a report
            DICT - output a simplified DICT structure
         output_format_set: str | dict, optional
            Output format set name or dictionary. Defaults to None.

        Returns
        -------
        list
            A list of terms matching the search criteria. If no terms are found,
            it returns the string "No terms found".

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_terms_by_name(term, glossary_guid, status_filter, effective_time, for_lineage,
                                          for_duplicate_processing, start_from, page_size, output_format, output_format_set))
        return response

    async def _async_get_term_by_guid(self, term_guid: str, output_format: str = 'JSON', output_format_set: str | dict = None) -> dict | str:
        """Retrieve a term using its unique id. Async version.
        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve.
        output_format: str, default = 'JSON'
            Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
        output_format_set: str | dict, optional
            Output format set name or dictionary. Defaults to None.

        Returns
        -------
        dict | str
            A dict detailing the glossary term represented by the GUID. If no term is found, the string
            "No term found" will be returned.

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.
        """
        output_format = output_format.upper()
        validate_guid(term_guid)

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/terms/"
               f"{term_guid}/retrieve")
        response = await self._async_make_request("POST", url)
        term_element = response.json().get("element", NO_TERMS_FOUND)
        if term_element == NO_TERMS_FOUND:
            return NO_TERMS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_terms_md(term_element, "GUID", output_format, output_format_set)
        return response.json().get("element", NO_TERMS_FOUND)

    def get_term_by_guid(self, term_guid: str, output_format: str = 'JSON', output_format_set: str | dict = None) -> dict | str:
        """Retrieve a term using its unique id. Async version.
        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve.
        output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
        output_format_set: str | dict, optional
            Output format set name or dictionary. Defaults to None.
        Returns
        -------
        dict | str
            A dict detailing the glossary term represented by the GUID. If no term is found, the string
            "No term found" will be returned.
        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_term_by_guid(term_guid, output_format, output_format_set))

        return response

    async def _async_get_term_versions(self, term_guid: str, effective_time: str = None, from_time: str = None,
                                       to_time: str = None, oldest_first: bool = False, for_lineage: bool = False,
                                       for_duplicate_processing: bool = False, start_from: int = 0,
                                       page_size=max_paging_size,

                                       ) -> list | str:
        """Retrieve the versions of a glossary term. Async version.
        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve.

        start_from : int, optional
            The index of the first term to retrieve. Default is 0.
        page_size : int, optional
            The number of terms to retrieve per page. If not provided, it will use the default page size.
        Returns
        -------
        list | str
            A [dict] detailing the glossary term represented by the GUID. If no term is found, the string
            "No term found" will be returned.

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.

        Args:
            term_guid:
            effective_time:
            from_time:
            to_time:
            oldest_first:
            for_lineage:
            for_duplicate_processing:
            start_from:
            page_size:
        """

        body = {
            "effective_time": effective_time, "fromTime": from_time, "toTime": to_time, "forLineage": for_lineage,
            "forDuplicateProcessing": for_duplicate_processing
            }

        oldest_first_s = str(oldest_first).lower()
        validate_guid(term_guid)

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/terms/"
               f"{term_guid}/history?startFrom={start_from}&pageSize={page_size}&oldestFirst={oldest_first_s}&"
               f"forDuplicateProcessing={for_duplicate_processing}&forLineage={for_lineage}")

        response = await self._async_make_request("POST", url, body_slimmer(body))
        return response.json().get("elementList", "No term found")

    def get_term_versions(self, term_guid: str, effective_time: str = None, from_time: str = None, to_time: str = None,
                          oldest_first: bool = False, for_lineage: bool = False, for_duplicate_processing: bool = False,
                          start_from: int = 0, page_size=max_paging_size, ) -> dict | str:
        """Retrieve the versions of a glossary term.
        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve.

        start_from : int, optional
            The index of the first term to retrieve. Default is 0.
        page_size : int, optional
            The number of terms to retrieve per page. If not provided, it will use the default page size.
        Returns
        -------
        [dict] | str
            A [dict] detailing the glossary term represented by the GUID. If no term is found, the string
            "No term found" will be returned.

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_term_versions(term_guid, effective_time, from_time, to_time, oldest_first, for_lineage,
                                          for_duplicate_processing, start_from, page_size))

        return response

    async def _async_get_term_revision_logs(self, term_guid: str, start_from: int = 0, page_size=None, ) -> dict | str:
        """Retrieve the revision log history for a term. Async version.
        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve.

        start_from : int, optional
            The index of the first term to retrieve. Default is 0.
        page_size : int, optional
            The number of terms to retrieve per page. If not provided, it will use the default page size.
        Returns
        -------
        dict | str
            A dict detailing the glossary term revision log history. If no term is found, the string
            "No log found" will be returned.

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.
        """

        if page_size is None:
            page_size = self.page_size

        validate_guid(term_guid)

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/elements/"
               f"{term_guid}/note-logs/retrieve?startFrom={start_from}&pageSize={page_size}")

        response = await self._async_make_request("POST", url)
        return response.json().get("elementList", "No log found")

    def get_term_revision_logs(self, term_guid: str, start_from: int = 0, page_size=None, ) -> dict | str:
        """Retrieve the revision log history for a term.
        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve.

        start_from : int, optional
            The index of the first term to retrieve. Default is 0.
        page_size : int, optional
            The number of terms to retrieve per page. If not provided, it will use the default page size.
        Returns
        -------
        dict | str
            A dict detailing the glossary term revision log history. If no term is found, the string
            "No log found" will be returned.

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_term_revision_logs(term_guid, start_from, page_size))

        return response

    async def _async_get_term_revision_history(self, term_revision_log_guid: str, start_from: int = 0,
                                               page_size=None, ) -> dict | str:
        """Retrieve the revision history for a glossary term. Async version.

        Parameters
        ----------
        term_revision_log_guid : str
            The GUID of the glossary term revision log to retrieve.

        start_from : int, optional
            The index of the first term to retrieve. Default is 0.
        page_size : int, optional
            The number of terms to retrieve per page. If not provided, it will use the default page size.
        Returns
        -------
        dict | str
            A dict detailing the glossary term revision history.

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.


        Notes
        -----
        This revision history is created automatically.  The text is supplied on the update request.
        If no text is supplied, the value "None" is show.
        """

        if page_size is None:
            page_size = self.page_size

        validate_guid(term_revision_log_guid)

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/note-logs/"
               f"{term_revision_log_guid}/notes/retrieve?startFrom={start_from}&pageSize={page_size}")

        response = await self._async_make_request("POST", url)
        return response.json().get("elementList", "No logs found")

    def get_term_revision_history(self, term_revision_log_guid: str, start_from: int = 0,
                                  page_size=None, ) -> dict | str:
        """Retrieve the revision history for a glossary term.

        Parameters
        ----------
        term_revision_log_guid : str
            The GUID of the glossary term revision log to retrieve.

        start_from : int, optional
            The index of the first term to retrieve. Default is 0.
        page_size : int, optional
            The number of terms to retrieve per page. If not provided, it will use the default page size.
        Returns
        -------
        dict | str
            A dict detailing the glossary term revision history.

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.


        Notes
        -----
        This revision history is created automatically.  The text is supplied on the update request.
        If no text is supplied, the value "None" is show.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_term_revision_history(term_revision_log_guid, start_from, page_size))

        return response

    def list_term_revision_history(self, term_guid: str, output_format: str = "DICT", output_format_set: str | dict = None) -> list | str:
        """
        Retrieve the revision history for a term.

        This method retrieves the revision logs associated with a term, and for each revision log,
        retrieves the revision history. The results are formatted according to the specified output format.

        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve the revision history for.
        output_format : str, optional
            The format in which to return the results. Can be "DICT", "MD", or "LIST".
            Defaults to "DICT".
        output_format_set : str | dict, optional
            Output format set name or dictionary. Defaults to None.

        Returns
        -------
        list | str
            If output_format is "DICT", returns a list of dictionaries containing the revision history.
            If output_format is "MD", returns a markdown representation of the revision history.
            If output_format is "LIST", returns a markdown table of the revision history.
            If no revision logs are found, returns a string message "No revision logs found".
        """
        validate_guid(term_guid)

        # Get revision logs for the term
        revision_logs = self.get_term_revision_logs(term_guid)
        if isinstance(revision_logs, str):
            return "No revision logs found"

        # Process each revision log
        all_entries = []
        for log in revision_logs:
            log_guid = log['elementHeader']['guid']
            qualified_name = log.get('properties', {}).get('qualifiedName', '---')

            # Get revision history for this log
            history = self.get_term_revision_history(log_guid)
            if isinstance(history, str):
                continue

            # Process each entry in the history
            for entry in history:
                # Extract update time from the title
                title = entry.get('properties', {}).get('title', '---')

                keyword_index = title.index('on')
                update_time = title[keyword_index + 2:].strip()

                entry_data = {
                    'qualifiedName': qualified_name, 'title': title,
                    'text': entry.get('properties', {}).get('text', '---'), 'updateTime': update_time
                    # Use extracted date/time or fall back to title
                    }
                all_entries.append(entry_data)

        # Sort entries by update time
        sorted_entries = sorted(all_entries, key=lambda x: x['updateTime'] if x['updateTime'] != '---' else '',
                                reverse=True)

        # Return in the specified format
        if output_format == "DICT":
            return sorted_entries
        elif output_format == "LIST":
            # Create markdown table
            if not sorted_entries:
                return "No revision entries found"

            # Get headers
            headers = sorted_entries[0].keys()

            # Create header row
            header_row = " | ".join(headers)
            separator_row = " | ".join(["---"] * len(headers))

            # Create rows
            rows = []
            for entry in sorted_entries:
                row = " | ".join(str(entry.get(header, "---")) for header in headers)
                rows.append(row)

            # Combine into table
            markdown_table = f"{header_row}\n{separator_row}\n" + "\n".join(rows)
            return markdown_table
        elif output_format == "MD":
            # Create markdown representation
            if not sorted_entries:
                return "No revision entries found"

            md_output = "\n"

            for entry in sorted_entries:
                md_output += f"* Note Log Name: \n{entry['qualifiedName']}\n\n"
                md_output += f"* Note Log Entry Title: \n{entry['title']}\n\n"
                md_output += f"* Note Log Entry: \n\t{entry['text']}\n\n"
                md_output += "---\n\n"

            return md_output
        else:
            # Default to DICT format
            return sorted_entries

    def list_full_term_history(self, term_guid: str, output_format: str = "DICT", output_format_set: str | dict = None) -> list | str:
        """
        Retrieves and formats the entire version history of a specific term in the repository.
        The version history is either returned as a list of dictionaries or in a Markdown table
        format.

        The returned history includes details about the creation and update timestamps, user
        information, and additional glossary term properties such as `displayName`,
        `qualifiedName`, `description`, and others.

        Parameter
        ---------
        term_guid: The unique identifier of the glossary term for which the version
            history needs to be retrieved.
        output_format: The format in which the history should be returned. It can be
            either "DICT" (a list of dictionaries) or "LIST" (a Markdown table).
            Defaults to "DICT".
        output_format_set: str | dict, optional
            Output format set name or dictionary. Defaults to None.

        Returns
        -------
        list | str: A list of dictionaries representing the version history
            (if output_format is "DICT"), or a Markdown table of the version details
            (if output_format is "LIST"). If no history is found, returns a string
            message "No History Found".
        """
        history = self.get_term_versions(term_guid)
        if type(history) is str:
            return "No History Found"
        version_history = []
        for ver in history:
            create_time = ver["elementHeader"]["versions"].get("createTime", " ")
            update_time = ver["elementHeader"]["versions"].get("createTime", " ")
            created_by = ver["elementHeader"]["versions"].get("createdBy", " ")
            updated_by = ver["elementHeader"]["versions"].get("updatedBy", "---")
            version = ver["elementHeader"]["versions"].get("version")

            qualified_name = ver["glossaryTermProperties"].get("qualifiedName", ' ')
            display_name = ver["glossaryTermProperties"].get("displayName", ' ')
            summary = ver["glossaryTermProperties"].get("summary", ' ')
            description = ver["glossaryTermProperties"].get("description", ' ')
            examples = ver["glossaryTermProperties"].get("examples", ' ')
            usage = ver["glossaryTermProperties"].get("usage", ' ')
            version_identifier = ver["glossaryTermProperties"].get("versionIdentifier", ' ')

            version_history.append({
                "version": version, "displayName": display_name, "summary": summary, "created": create_time,
                "updated": update_time, "createdBy": created_by, "updatedBy": updated_by,
                "qualifiedName": qualified_name, "description": description, "examples": examples, "usage": usage,
                "versionIdentifier": version_identifier,
                })
        sorted_history = sorted(version_history, key=lambda i: i['version'], reverse=True)
        if output_format == "DICT":
            return sorted_history
        elif output_format == "LIST":
            # Get the headers from the keys of the first dictionary
            headers = sorted_history[0].keys()

            # Create the header row
            header_row = " | ".join(headers)
            separator_row = " | ".join(["---"] * len(headers))  # Markdown separator row

            # Create the rows for the table
            rows = []
            for entry in sorted_history:
                row = " | ".join(str(entry.get(header, "---")) for header in headers)
                rows.append(row)

            # Combine everything into a Markdown table string
            markdown_table = f"{header_row}\n{separator_row}\n" + "\n".join(rows)
            return markdown_table
        else:
            return None

    async def _async_find_glossary_terms(self, search_string: str, glossary_guid: str = None, status_filter: list = [],
                                         effective_time: str = None, starts_with: bool = False, ends_with: bool = False,
                                         ignore_case: bool = False, for_lineage: bool = False,
                                         for_duplicate_processing: bool = False, start_from: int = 0,
                                         page_size: int = None, output_format: str = "JSON", output_format_set: str | dict = None) -> list | str:
        """Retrieve the list of glossary term metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to use to find matching glossaries. If the search string is '*' then all glossaries returned.
        glossary_guid str
            Identifier of the glossary to search within. If None, then all glossaries are searched.
        status_filter: list, default = [], optional
            Filters the results by the included Term statuses (such as 'ACTIVE', 'DRAFT'). If not specified,
            the results will not be filtered.
        effective_time: str, [default=None], optional
            If specified, the term information will be retrieved if it is active at the `effective_time`.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

            If not provided, the server name associated with the instance is used.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        for_lineage : bool, [default=False], optional

        for_duplicate_processing : bool, [default=False], optional

        start_from: str, [default=0], optional
            Page of results to start from
        page_size : int, optional
            Number of elements to return per page - if None, then default for class will be used.
        output_format: str, default = 'JSON'
          Type of output to produce:
            JSON - output standard json
            MD - output standard markdown with no preamble
            FORM - output markdown with a preamble for a form
            REPORT - output markdown with a preamble for a report

        Returns
        -------
        List | str

        A list of term definitions

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        The search string is located in the request body and is interpreted as a plain string.
        The request parameters, startsWith, endsWith, and ignoreCase can be used to allow a fuzzy search.
        The request body also supports the specification of a glossaryGUID to restrict the search to within a single
        glossary.
        """

        if page_size is None:
            page_size = self.page_size
        if effective_time is None:
            effective_time = datetime.now().isoformat()
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()
        if search_string == "*":
            search_string = None

        # validate_search_string(search_string)

        body = {
            "class": "GlossarySearchStringRequestBody", "glossaryGUID": glossary_guid, "searchString": search_string,
            "effectiveTime": effective_time, "limitResultsByStatus": status_filter,
            }

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
               f"terms/by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
               f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}&forLineage={for_lineage_s}&"
               f"forDuplicateProcessing={for_duplicate_processing_s}")

        response = await self._async_make_request("POST", url, body_slimmer(body))
        term_elements = response.json().get("elementList", NO_TERMS_FOUND)
        if term_elements == NO_TERMS_FOUND:
            if output_format == 'JSON':
                return NO_TERMS_FOUND
            elif output_format in ['MD', 'FORM', 'REPORT', 'LIST']:
                return "\n# No Terms found.\n"
            elif output_format == 'DICT':
                return None
        if output_format != "JSON":  # return a simplified markdown representation
            return self.generate_terms_md(term_elements, search_string, output_format, output_format_set)
        return response.json().get("elementList", NO_TERMS_FOUND)

    def find_glossary_terms(self, search_string: str, glossary_guid: str = None, status_filter: list = [],
                            effective_time: str = None, starts_with: bool = False, ends_with: bool = False,
                            ignore_case: bool = False, for_lineage: bool = False,
                            for_duplicate_processing: bool = False, start_from: int = 0, page_size: int = None,
                            output_format: str = "JSON", output_format_set: str | dict = None) -> list | str:
        """Retrieve the list of glossary term metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to use to find matching glossaries. If the search string is '*' then all glossaries
            returned.
        glossary_guid str
            Identifier of the glossary to search within. If None, then all glossaries are searched.
        status_filter: list, default = [], optional
            Filters the results by the included Term statuses (such as 'ACTIVE', 'DRAFT'). If not specified,
            the results will not be filtered.
        effective_time: str, [default=None], optional
            If specified, the term information will be retrieved if it is active at the `effective_time`.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

            If not provided, the server name associated with the instance is used.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        for_lineage : bool, [default=False], optional

        for_duplicate_processing : bool, [default=False], optional

        start_from: str, [default=0], optional
            Page of results to start from
        page_size : int, optional
            Number of elements to return per page - if None, then default for class will be used.
        output_format: str, default = 'JSON'
            Type of output to produce:
            JSON - output standard json
            MD - output standard markdown with no preamble
            FORM - output markdown with a preamble for a form
            REPORT - output markdown with a preamble for a report
        output_format_set: str | dict, optional
            Output format set name or dictionary. Defaults to None.

        Returns
        -------
        List | str

        A list of term definitions

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        The search string is located in the request body and is interpreted as a plain string.
        The request parameters, startsWith, endsWith, and ignoreCase can be used to allow a fuzzy search.
        The request body also supports the specification of a glossaryGUID to restrict the search to within a
        single glossary.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_glossary_terms(search_string, glossary_guid, status_filter, effective_time, starts_with,
                                            ends_with, ignore_case, for_lineage, for_duplicate_processing, start_from,
                                            page_size, output_format, output_format_set))

        return response

    #
    #   Feedback
    #
    async def _async_get_comment(self, commemt_guid: str, effective_time: str, for_lineage: bool = False,
                                 for_duplicate_processing: bool = False, ) -> dict | list:
        """Retrieve the comment specified by the comment GUID"""

        validate_guid(commemt_guid)

        if effective_time is None:
            effective_time = datetime.now().isoformat()

        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()

        body = {"effective_time": effective_time}

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/comments/"
               f"{commemt_guid}?forLineage={for_lineage_s}&"
               f"forDuplicateProcessing={for_duplicate_processing_s}")

        # print(f"\n\nURL is: \n {url}\n\nBody is: \n{body}")

        response = await self._async_make_request("POST", url, body)
        return response.json()

    async def _async_add_comment_reply(self, comment_guid: str, is_public: bool, comment_type: str, comment_text: str,
                                       for_lineage: bool = False, for_duplicate_processing: bool = False, ) -> str:
        """Reply to a comment"""

        validate_guid(comment_guid)
        validate_name(comment_type)

        is_public_s = str(is_public).lower()
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()

        body = {
            "class": "CommentRequestBody", "commentType": comment_type, "commentText": comment_text,
            "isPublic": is_public,
            }

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/comments/"
               f"{comment_guid}/replies?isPublic={is_public_s}&forLineage={for_lineage_s}&"
               f"forDuplicateProcessing={for_duplicate_processing_s}")

        # print(f"\n\nURL is: \n {url}\n\nBody is: \n{body}")

        response = await self._async_make_request("POST", url, body)
        return response

    async def _async_update_comment(self, comment_guid: str, is_public: bool, comment_type: str, comment_text: str,
                                    is_merge_update: bool = False, for_lineage: bool = False,
                                    for_duplicate_processing: bool = False, ) -> str:
        """Update the specified comment"""

        validate_guid(comment_guid)
        validate_name(comment_type)

        is_public_s = str(is_public).lower()
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()

        body = {
            "class": "CommentRequestBody", "commentType": comment_type, "commentText": comment_text,
            "isPublic": is_public,
            }

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/comments/"
               f"{comment_guid}/replies?isPublic={is_public_s}&forLineage={for_lineage_s}&"
               f"forDuplicateProcessing={for_duplicate_processing_s}")

        # print(f"\n\nURL is: \n {url}\n\nBody is: \n{body}")

        response = await self._async_make_request("POST", url, body)
        return response

    async def _async_find_comment(self, search_string: str, glossary_guid: str = None, status_filter: list = [],
                                  effective_time: str = None, starts_with: bool = False, ends_with: bool = False,
                                  ignore_case: bool = False, for_lineage: bool = False,
                                  for_duplicate_processing: bool = False, start_from: int = 0, page_size: int = None, ):
        """Find comments by search string"""

        if page_size is None:
            page_size = self.page_size
        if effective_time is None:
            effective_time = datetime.now().isoformat()
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()
        if search_string == "*":
            search_string = None

        # validate_search_string(search_string)

        body = {
            "class": "GlossarySearchStringRequestBody", "glossaryGUID": glossary_guid, "searchString": search_string,
            "effectiveTime": effective_time, "limitResultsByStatus": status_filter,
            }
        # body = body_slimmer(body)

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
               f"terms/by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
               f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}&forLineage={for_lineage_s}&"
               f"forDuplicateProcessing={for_duplicate_processing_s}")

        # print(f"\n\nURL is: \n {url}\n\nBody is: \n{body}")

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elementList", "No terms found")


if __name__ == "__main__":
    print("Main-Glossary Browser")
