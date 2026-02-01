from md_processing.command_dispatcher import CommandDispatcher

# Import all command handlers
from md_processing.md_commands.project_commands import process_link_project_dependency_command
from md_processing.md_commands.product_manager_commands import process_csv_element_upsert_command
from md_processing import (
    process_glossary_upsert_command, process_term_upsert_command,
    process_provenance_command,
    process_project_upsert_command, process_blueprint_upsert_command,
    process_solution_component_upsert_command, process_component_link_unlink_command,
    process_link_term_term_relationship_command,
    process_information_supply_chain_upsert_command,
    process_information_supply_chain_link_unlink_command,
    process_digital_product_upsert_command, process_agreement_upsert_command,
    process_collection_upsert_command, process_link_agreement_item_command,
    process_gov_definition_upsert_command,
    process_governed_by_link_detach_command,
    process_gov_def_link_detach_command, process_product_dependency_command,
    process_add_to_collection_command, process_attach_collection_command,
    process_supporting_gov_def_link_detach_command,
    process_attach_subscriber_command, process_output_command,
    process_link_project_hierarchy_command,
    process_external_reference_upsert_command,
    process_link_to_external_reference_command, process_link_to_media_reference_command,
    process_link_to_cited_document_command,
)
from md_processing.md_processing_utils.md_processing_constants import (
    load_commands, COMMAND_DEFINITIONS, get_command_variants_for_specs
)

from md_processing.md_commands.data_designer_commands import (
    process_data_spec_upsert_command,
    process_data_dict_upsert_command,
    process_data_field_upsert_command,
    process_data_structure_upsert_command,
    process_data_class_upsert_command
)

from md_processing.md_commands.feedback_commands import (
    process_add_comment_command, process_journal_entry_command,
    process_upsert_informal_tag_command, process_tag_element_command
)


def _command_specs() -> dict:
    specs = COMMAND_DEFINITIONS.get("Command Specifications", {})
    return {name: spec for name, spec in specs.items() if isinstance(spec, dict)}


def _names_for_family(specs: dict, family: str) -> set[str]:
    return {name for name, spec in specs.items() if spec.get("family") == family}


def _spec_names(specs: dict, *names: str) -> set[str]:
    return {name for name in names if name in specs}


def _register_spec_commands(dispatcher: CommandDispatcher, spec_names: set[str], handler) -> None:
    for cmd in get_command_variants_for_specs(set(spec_names)):
        dispatcher.register(cmd, handler)

def setup_dispatcher() -> CommandDispatcher:
    load_commands("commands.json")
    dispatcher = CommandDispatcher()
    specs = _command_specs()

    # Provenance
    dispatcher.register("Provenance", lambda client, block, directive: process_provenance_command(client.input_file if hasattr(client, 'input_file') else "unknown", block)) 
    # Note: process_provenance_command in dr_egeria takes (input_file, current_block). 
    # But dispatch calls with (client, current_block, directive). 
    # We might need to adjust the signature or use a wrapper.
    # Actually, in dr_egeria.py: result = process_provenance_command(input_file, current_block)
    # The dispatcher will likely be called as dispatch(command, client, block, directive)
    # Use a lambda to adapt if necessary, or better yet, standardized handler signatures.
    # For now, let's keep the mapping logic close to the original.

    # Feedback Commands
    feedback_specs = _names_for_family(specs, "Feedback Manager")
    _register_spec_commands(dispatcher, _spec_names(specs, "Create Comment"), process_add_comment_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Create Journal Entry"), process_journal_entry_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Create Informal Tag"), process_upsert_informal_tag_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Link Tag->Element"), process_tag_element_command)

    # External References
    ext_ref_specs = _names_for_family(specs, "External Reference")
    ext_ref_upsert = {name for name in ext_ref_specs if name.startswith("Create ")}
    _register_spec_commands(dispatcher, ext_ref_upsert, process_external_reference_upsert_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Link External Reference Link"),
                            process_link_to_external_reference_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Link Media Reference Link"),
                            process_link_to_media_reference_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Link Cited Document Link"),
                            process_link_to_cited_document_command)

    # Glossary
    _register_spec_commands(dispatcher, _spec_names(specs, "Create Glossary"), process_glossary_upsert_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Create Glossary Term"), process_term_upsert_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Link Term-Term Relationship"),
                            process_link_term_term_relationship_command)

    # Output / List / View
    _register_spec_commands(dispatcher, _names_for_family(specs, "General"), process_output_command)

    # Projects
    project_specs = _names_for_family(specs, "Project")
    project_upsert = {name for name in project_specs if name.startswith("Create ")}
    _register_spec_commands(dispatcher, project_upsert, process_project_upsert_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Link Project Dependency"),
                            process_link_project_dependency_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Link Project Hierarchy"),
                            process_link_project_hierarchy_command)

    # Blueprints & Solution Components
    _register_spec_commands(dispatcher, _spec_names(specs, "Create Solution Blueprint"),
                            process_blueprint_upsert_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Create Solution Component", "Create Solution Role"),
                            process_solution_component_upsert_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Link Solution Component Peers"),
                            process_component_link_unlink_command)

    # Information Supply Chain
    _register_spec_commands(dispatcher, _spec_names(specs, "Create Information Supply Chain"),
                            process_information_supply_chain_upsert_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Link Information Supply Chain Peers"),
                            process_information_supply_chain_link_unlink_command)

    # Data Designer
    _register_spec_commands(dispatcher, _spec_names(specs, "Create Data Specification"),
                            process_data_spec_upsert_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Create Data Dictionary"),
                            process_data_dict_upsert_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Create Data Field"),
                            process_data_field_upsert_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Create Data Structure"),
                            process_data_structure_upsert_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Create Data Class"),
                            process_data_class_upsert_command)

    # Digital Products & Agreements
    dpm_specs = _names_for_family(specs, "Digital Product Manager")
    _register_spec_commands(dispatcher, _spec_names(specs, "Create Collection", "Create Digital Product Catalog"),
                            process_collection_upsert_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Create Digital Product"),
                            process_digital_product_upsert_command)
    _register_spec_commands(dispatcher,
                            _spec_names(specs, "Create Agreement", "Create Data Sharing Agreement",
                                        "Create Digital Subscription"),
                            process_agreement_upsert_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Create CSV File"),
                            process_csv_element_upsert_command)
    _register_spec_commands(dispatcher,
                            _spec_names(specs, "Link Agreement->Item", "Link Agreement->T&C", "Link Contracts"),
                            process_link_agreement_item_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Link Subscriber->Subscription"),
                            process_attach_subscriber_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Link Collection->Resource"),
                            process_attach_collection_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Add Member->Collection"),
                            process_add_to_collection_command)
    _register_spec_commands(dispatcher, _spec_names(specs, "Link Product-Product"),
                            process_product_dependency_command)

    # Governance
    gov_specs = _names_for_family(specs, "Governance Officer")
    gov_create = {name for name in gov_specs if name.startswith("Create ")}
    _register_spec_commands(dispatcher, gov_create, process_gov_definition_upsert_command)

    gov_link = {name for name in gov_specs if name.startswith("Link ")}
    supporting = _spec_names(specs, "Link Governance Mechanism", "Link Governance Response")
    governed_by = _spec_names(specs, "Link Governed By")
    _register_spec_commands(dispatcher, gov_link - supporting - governed_by, process_gov_def_link_detach_command)
    _register_spec_commands(dispatcher, supporting, process_supporting_gov_def_link_detach_command)
    _register_spec_commands(dispatcher, governed_by, process_governed_by_link_detach_command)

    return dispatcher
