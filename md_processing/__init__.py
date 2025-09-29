"""
This package contains functions to parse and process Egeria Markdown (Freddie)
"""
from md_processing.md_commands.governance_officer_commands import (process_gov_definition_upsert_command,
                                                                   process_gov_def_link_detach_command,
                                                                   process_supporting_gov_def_link_detach_command,
                                                                   process_gov_def_context_command, process_governed_by_link_detach_command
                                                                   )


from md_processing.md_commands.product_manager_commands import (process_digital_product_upsert_command,
                                                                process_agreement_upsert_command,
                                                                process_collection_upsert_command,
                                                                process_link_agreement_item_command,
                                                                process_add_to_collection_command,
                                                                process_product_dependency_command,
                                                                process_attach_collection_command,
                                                                process_attach_subscriber_command,
                                                                process_csv_element_upsert_command,
                                                               )

from md_processing.md_commands.solution_architect_commands import (process_blueprint_upsert_command,
                                                                   process_solution_component_upsert_command,
                                                                   process_component_link_unlink_command,
                                                                   process_information_supply_chain_upsert_command,
                                                                   process_information_supply_chain_link_unlink_command,
                                                                   process_sol_arch_list_command)

from md_processing.md_commands.data_designer_commands import (process_data_field_upsert_command,
                                                              process_data_spec_upsert_command,
                                                              process_data_dict_upsert_command,
                                                              process_data_structure_upsert_command)

from md_processing.md_commands.glossary_commands import (process_glossary_upsert_command,
                                                         process_term_upsert_command,
                                                         process_link_term_term_relationship_command,
                                                         )
from md_processing.md_commands.project_commands import (process_project_upsert_command, process_link_project_dependency_command,
                                                        process_link_project_hierarchy_command)

from md_processing.md_commands.ext_ref_commands import (process_external_reference_upsert_command,
                                                        process_link_to_media_reference_command,
                                                        process_link_to_external_reference_command,
                                                        process_link_to_cited_document_command,

                                                        )

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
# Import message constants

from md_processing.md_processing_utils.common_md_proc_utils import process_output_command
from md_processing.md_commands.view_commands import process_format_set_action, process_output_command