"""
This package contains functions to parse and process Egeria Markdown (Freddie)
"""
# Re-export all functions from the original md_processing_utils.py to maintain backward compatibility
from md_processing.md_processing_utils.common_md_utils import (render_markdown, is_valid_iso_date, set_debug_level,
                                                               get_current_datetime_string, print_msg, EGERIA_WIDTH,
                                                               debug_level, get_element_dictionary,
                                                               update_element_dictionary, clear_element_dictionary,
                                                               is_present, find_key_with_value,
                                                               process_provenance_command, set_delete_request_body,
                                                               set_rel_request_body, set_filter_request_body,
                                                               set_update_body, set_peer_gov_def_request_body, set_rel_prop_body,
                                                               set_gov_prop_body, set_element_prop_body, set_create_body,
                                                               GOVERNANCE_POLICIES, GOVERNANCE_CONTROLS, GOVERNANCE_DRIVERS
                                                               )
from md_processing.md_processing_utils.extraction_utils import (extract_command_plus, extract_command,
                                                                extract_attribute, process_simple_attribute,
                                                                process_name_list, process_element_identifiers,
                                                                get_element_by_name, update_a_command)
from md_processing.md_processing_utils.md_processing_constants import ( pre_command,
                                                                       command_seperator, EXISTS_REQUIRED,
                                                                       GLOSSARY_NAME_LABELS,
                                                                       TERM_NAME_LABELS, PROJECT_NAME_LABELS,
                                                                       BLUEPRINT_NAME_LABELS, COMPONENT_NAME_LABELS,
                                                                       SOLUTION_ROLE_LABELS, SOLUTION_ACTOR_ROLE_LABELS,
                                                                       SOLUTION_LINKING_ROLE_LABELS, OUTPUT_LABELS,
                                                                       SEARCH_LABELS, GUID_LABELS,
                                                                       ELEMENT_OUTPUT_FORMATS, TERM_RELATIONSHPS,
                                                                       command_list, COMMAND_DEFINITIONS, GOV_COM_LIST,
                                                                       GOV_LINK_LIST, COLLECTIONS_LIST, SIMPLE_COLLECTIONS,
                                                                       LIST_COMMANDS, PROJECT_COMMANDS, EXT_REF_UPSERT,
                                                                       LINK_EXT_REF, LINK_MEDIA, LINK_CITED_DOC)
# Import functions from md_processing_constants
from md_processing.md_processing_utils.md_processing_constants import (load_commands, get_command_spec, get_attribute,
                                                                       get_attribute_labels, get_alternate_names)

from md_processing.md_processing_utils.common_md_proc_utils import process_output_command
