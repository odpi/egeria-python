"""
This package contains functions to parse and process Egeria Markdown (Freddie)
"""
from md_processing.md_commands.governance_officer_commands import (process_gov_definition_upsert_command,
                                                                   process_gov_def_link_detach_command,
                                                                   process_gov_definition_list_command,
                                                                   process_gov_def_context_command)


from md_processing.md_commands.product_manager_commands import (process_digital_product_upsert_command,
                                                                process_agreement_upsert_command,
                                                                process_collection_list_command,
                                                                process_collection_upsert_command,
                                                                process_link_agreement_item_command)

from md_processing.md_commands.solution_architect_commands import (process_blueprint_upsert_command,
                                                                   process_solution_component_upsert_command,
                                                                   process_component_link_unlink_command,
                                                                   process_information_supply_chain_upsert_command,
                                                                   process_information_supply_chain_link_unlink_command,
                                                                   process_sol_arch_list_command)

from md_processing.md_commands.data_designer_commands import (process_data_field_upsert_command,
                                                              process_data_spec_upsert_command,
                                                              process_data_dict_upsert_command,
                                                              process_data_collection_list_command,
                                                              process_data_structure_list_command,
                                                              process_data_field_list_command,
                                                              process_data_class_list_command,
                                                              process_data_structure_upsert_command)

from md_processing.md_commands.glossary_commands import (process_glossary_upsert_command, process_glossary_list_command,
                                                         process_glossary_structure_command,
                                                         process_category_upsert_command, update_category_parent,
                                                         process_category_list_command, update_term_categories,
                                                         process_term_upsert_command,
                                                         process_create_term_term_relationship_command,
                                                         process_term_list_command, process_term_details_command,
                                                         process_term_history_command,
                                                         process_term_revision_history_command)
from md_processing.md_commands.project_commands import (process_per_proj_upsert_command)
# Re-export all functions from the original md_processing_utils.py to maintain backward compatibility
from md_processing.md_processing_utils.common_md_utils import (render_markdown, is_valid_iso_date, set_debug_level,
                                                               get_current_datetime_string, print_msg, EGERIA_WIDTH,
                                                               console, debug_level, get_element_dictionary,
                                                               update_element_dictionary, clear_element_dictionary,
                                                               is_present, find_key_with_value,
                                                               process_provenance_command, set_metadata_source_request_body,
                                                               set_rel_request_body, set_filter_request_body,
                                                               set_update_body, set_peer_gov_def_request_body,
                                                                set_gov_prop_body, set_prop_body, set_create_body,

                                                               )
from md_processing.md_processing_utils.extraction_utils import (extract_command_plus, extract_command,
                                                                extract_attribute, process_simple_attribute,
                                                                process_name_list, process_element_identifiers,
                                                                get_element_by_name, update_a_command)
from md_processing.md_processing_utils.md_processing_constants import (ALWAYS, ERROR, INFO, WARNING, pre_command,
                                                                       command_seperator, EXISTS_REQUIRED,
                                                                       GLOSSARY_NAME_LABELS, CATEGORY_NAME_LABELS,
                                                                       PARENT_CATEGORY_LABELS, CHILD_CATEGORY_LABELS,
                                                                       TERM_NAME_LABELS, PROJECT_NAME_LABELS,
                                                                       BLUEPRINT_NAME_LABELS, COMPONENT_NAME_LABELS,
                                                                       SOLUTION_ROLE_LABELS, SOLUTION_ACTOR_ROLE_LABELS,
                                                                       SOLUTION_LINKING_ROLE_LABELS, OUTPUT_LABELS,
                                                                       SEARCH_LABELS, GUID_LABELS,
                                                                       ELEMENT_OUTPUT_FORMATS, TERM_RELATIONSHPS,
                                                                       command_list, COMMAND_DEFINITIONS, GOV_COM_LIST,
                                                                       GOV_LINK_LIST, COLLECTIONS_LIST, SIMPLE_COLLECTIONS,)
# Import functions from md_processing_constants
from md_processing.md_processing_utils.md_processing_constants import (load_commands, get_command_spec, get_attribute,
                                                                       get_attribute_labels, get_alternate_names)
# Import message constants
from md_processing.md_processing_utils.message_constants import (message_types, ALWAYS, ERROR, INFO, WARNING)

