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
    # process_gov_def_context_command, 
    process_supporting_gov_def_link_detach_command,
    process_attach_subscriber_command, process_output_command,
    process_link_project_hierarchy_command,
    process_external_reference_upsert_command,
    process_link_to_external_reference_command, process_link_to_media_reference_command,
    process_link_to_cited_document_command, 
    EXT_REF_UPSERT, LINK_CITED_DOC, LINK_MEDIA, LINK_EXT_REF,
    COLLECTIONS_LIST, SIMPLE_COLLECTIONS, GOV_COM_LIST, GOV_LINK_LIST,
    LIST_COMMANDS, PROJECT_COMMANDS
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
    process_upsert_note_command, process_attach_note_log_command,
    process_upsert_informal_tag_command, process_tag_element_command
)

def setup_dispatcher() -> CommandDispatcher:
    dispatcher = CommandDispatcher()

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
    for cmd in ["Create Comment", "Update Comment"]:
        dispatcher.register(cmd, process_add_comment_command)
    
    dispatcher.register("Create Journal Entry", process_journal_entry_command)

    for cmd in ["Create Note", "Update Note"]:
        dispatcher.register(cmd, process_upsert_informal_tag_command) # Wait, check original file.
        # Original: 
        # elif potential_command in ["Create Note", "Update Note"]:
        #     result = process_upsert_note_command(client, current_block, directive)
    
    # Correcting mapping based on review
    for cmd in ["Create Note", "Update Note"]:
        dispatcher.register(cmd, process_upsert_note_command)

    for cmd in ["Link NoteLog", "Detach NoteLog"]:
        dispatcher.register(cmd, process_attach_note_log_command)

    for cmd in ["Create Informal Tag", "Update Informal Tag"]:
        dispatcher.register(cmd, process_upsert_informal_tag_command)

    for cmd in ["Link Tag", "Detach Tag", "Link Tag->Element"]:
        dispatcher.register(cmd, process_tag_element_command)

    # External References
    for cmd in EXT_REF_UPSERT:
        dispatcher.register(cmd, process_external_reference_upsert_command)
    
    for cmd in LINK_EXT_REF:
        dispatcher.register(cmd, process_link_to_external_reference_command)
        
    for cmd in LINK_MEDIA:
        dispatcher.register(cmd, process_link_to_media_reference_command)
        
    for cmd in LINK_CITED_DOC:
        dispatcher.register(cmd, process_link_to_cited_document_command)

    # Glossary
    for cmd in ["Create Glossary", "Update Glossary"]:
        dispatcher.register(cmd, process_glossary_upsert_command)

    for cmd in ["Create Term", "Update Term"]:
        dispatcher.register(cmd, process_term_upsert_command)

    for cmd in ["Create Term-Term Relationship", "Update Term-Term Relationship", 
                "Link Termss", "Detach Terms", "Link Term-Term Relationship", "Detach Term-Term Relationship"]:
        dispatcher.register(cmd, process_link_term_term_relationship_command)

    # Output / List / View
    for cmd in LIST_COMMANDS:
        dispatcher.register(cmd, process_output_command)

    # Projects
    for cmd in PROJECT_COMMANDS:
        dispatcher.register(cmd, process_project_upsert_command)

    for cmd in ["Link Parent Project", "Attach Parent Project", "Detach Parent Project"]:
        dispatcher.register(cmd, process_link_project_hierarchy_command)

    for cmd in ["Link Project Dependency", "Attach Project Dependency", "Detach Project Dependency"]:
        dispatcher.register(cmd, process_link_project_dependency_command)

    # Blueprints & Solution Components
    for cmd in ["Create Blueprint", "Update Blueprint", "Create Solution Blueprint", "Update Solution Blueprint"]:
        dispatcher.register(cmd, process_blueprint_upsert_command)

    for cmd in ["Create Solution Component", "Update Solution Component"]:
        dispatcher.register(cmd, process_solution_component_upsert_command)

    for cmd in ["Link Solution Components", "Link Solution Component Peers", "Wire Solution Components",
                "Unlink Solution Components", "Detach Solution Components", "Detach Solution Component Peers"]:
        dispatcher.register(cmd, process_component_link_unlink_command)

    # Information Supply Chain
    for cmd in ["Create Information Supply Chain", "Update Information Supply Chain"]:
        dispatcher.register(cmd, process_information_supply_chain_upsert_command)

    for cmd in ["Link Information Supply Chain Peers", "Link Information Supply Chains",
                "Link Supply Chains", "Unlink Information Supply Chain Peers",
                "Unlink Information Supply Chains", "Unlink Supply Chains"]:
        dispatcher.register(cmd, process_information_supply_chain_link_unlink_command)

    # Data Designer
    for cmd in ["Create Data Spec", "Create Data Specification", "Update Data Spec", "Update Data Specification"]:
        dispatcher.register(cmd, process_data_spec_upsert_command)

    for cmd in ["Create Data Dict", "Create Data Dictionary", "Update Data Spec", "Update Data Dictionary"]: # Note: Update Data Spec is repeated here in original
        dispatcher.register(cmd, process_data_dict_upsert_command)

    for cmd in ["Create Data Field", "Update Data Field"]:
        dispatcher.register(cmd, process_data_field_upsert_command)

    for cmd in ["Create Data Structure", "Update Data Structure"]:
        dispatcher.register(cmd, process_data_structure_upsert_command)

    for cmd in ["Create Data Class", "Update Data Class"]:
        dispatcher.register(cmd, process_data_class_upsert_command)

    for cmd in ["View Data Dictionaries", "View Data Dictionary", "View Data Specifications", "View Data Specs",
                "View Data Structures", "View Data Structure", "View Data Fields", "View Data Field",
                "View Data Classes", "View Data Class"]:
         dispatcher.register(cmd, process_output_command)

    # Collections
    for cmd in ["Create Digital Product Catalog", "Create Collection","Create Folder", "Create Root Collection",
                "Update Digital Product Catalog", "Update Collection","Update Folder", "Update Root Collection"]:
        dispatcher.register(cmd, process_collection_upsert_command)
    
    for cmd in SIMPLE_COLLECTIONS:
        dispatcher.register(cmd, process_collection_upsert_command)

    for cmd in ["Link Collection->Resource", "Detach Collection->Resource"]:
        dispatcher.register(cmd, process_attach_collection_command)

    for cmd in ["Add Member->Collection", "Detach Member->Collection", "Add Member", "Remove Member",
                "Add to Folder", "Remove from Folder"]:
        dispatcher.register(cmd, process_add_to_collection_command)


    # Digital Products & Agreements
    for cmd in ["Create Digital Product", "Create Data Product","Update Digital Product", "Update Data Product"]:
        dispatcher.register(cmd, process_digital_product_upsert_command)

    for cmd in ["Create Agreement", "Create Data Sharing Agreement", "Create Digital Subscription",
                "Create Product Subscription", "Update Agreement", "Update Data Sharing Agreement",
                "Update Digital Subscription", "Update Product Subscription"]:
        dispatcher.register(cmd, process_agreement_upsert_command)

    for cmd in ["Link Agreement->Item", "Detach Agreement->Item"]:
        dispatcher.register(cmd, process_link_agreement_item_command)
        
    for cmd in ["Link Subscriber->Subscription", "Detach Subscriber->Subscription"]:
         dispatcher.register(cmd, process_attach_subscriber_command)
         
    for cmd in ["Link Digital Products", "Detach Digital Products",
                "Link Product-Product", "Detach Product-Product"]:
        dispatcher.register(cmd, process_product_dependency_command)


    # CSV
    for cmd in ["Create CSV File"]:
        dispatcher.register(cmd, process_csv_element_upsert_command)

    # Governance
    for cmd in GOV_COM_LIST:
        dispatcher.register(cmd, process_gov_definition_upsert_command)

    for cmd in GOV_LINK_LIST:
        dispatcher.register(cmd, process_gov_def_link_detach_command)
        
    for cmd in ["Link Governance Mechanism", "Detach Governance Mechanism",
                "Link Governance Response", "Detach Governance Response"]:
        dispatcher.register(cmd, process_supporting_gov_def_link_detach_command)

    for cmd in ["Link Governed By", "Detach Governed By"]:
        dispatcher.register(cmd, process_governed_by_link_detach_command)

    return dispatcher
