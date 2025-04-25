"""
This package contains functions to parse and process Egeria Markdown (Freddie)
"""

# Re-export all functions from the original md_processing_utils.py to maintain backward compatibility
from md_processing.md_processing_utils.common_utils import (
    render_markdown, is_valid_iso_date, set_debug_level, get_current_datetime_string, print_msg,
    EGERIA_WIDTH, console, message_types, debug_level,
    get_element_dictionary, update_element_dictionary, clear_element_dictionary, is_present, find_key_with_value
)

from md_processing.md_processing_utils.md_processing_constants import ALWAYS, ERROR, INFO, WARNING, pre_command, command_seperator, EXISTS_REQUIRED

from md_processing.md_processing_utils.extraction_utils import (
    extract_command_plus, extract_command, extract_attribute, process_simple_attribute, process_name_list,
    process_element_identifiers, get_element_by_name, update_a_command
)


from md_processing.md_processing_utils.md_processing_constants import (
    GLOSSARY_NAME_LABELS, CATEGORY_NAME_LABELS, PARENT_CATEGORY_LABELS, CHILD_CATEGORY_LABELS,
    TERM_NAME_LABELS, PROJECT_NAME_LABELS, BLUEPRINT_NAME_LABELS, COMPONENT_NAME_LABELS,
    SOLUTION_ROLE_LABELS, SOLUTION_ACTOR_ROLE_LABELS, SOLUTION_LINKING_ROLE_LABELS,
    OUTPUT_LABELS, SEARCH_LABELS, GUID_LABELS, ELEMENT_OUTPUT_FORMATS, TERM_RELATIONSHPS,
    command_list
)

from md_processing.md_commands.glossary_commands import (
    process_glossary_upsert_command, process_glossary_list_command, process_glossary_structure_command,
    process_category_upsert_command, update_category_parent, process_category_list_command,
    update_term_categories, process_term_upsert_command, process_create_term_term_relationship_command,
    process_term_list_command, process_term_details_command, process_term_history_command,
    process_term_revision_history_command
)

# from md_processing.md_commands.category_commands import (
#     process_category_upsert_command, update_category_parent, process_category_list_command
# )
#
# from md_processing.md_commands.term_commands import (
#     update_term_categories, process_term_upsert_command, process_create_term_term_relationship_command,
#     process_term_list_command, process_term_details_command, process_term_history_command,
#     process_term_revision_history_command
# )

from md_processing.md_commands.project_commands import (
    process_per_proj_upsert_command
)

from md_processing.md_commands.blueprint_commands import (
    process_blueprint_upsert_command, process_solution_component_upsert_command
)

# Also include process_provenance_command which doesn't fit neatly into any category
from md_processing.md_processing_utils.common_utils import process_provenance_command