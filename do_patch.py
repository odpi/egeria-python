import sys
import re

with open("md_processing/dr_egeria.py", "r") as f:
    content = f.read()

top_level_funcs = """
def normalize_command_key(key: str) -> str:
    \"\"\"Collapse whitespace and strip for consistent command matching.\"\"\"
    import re
    return re.sub(r'\\s+', ' ', key).strip() if key else key

def register_processor(dispatcher: V2Dispatcher, base_command: str, processor_cls: Type[AsyncBaseCommandProcessor]):
    \"\"\"Register a processor for a command and its variants/aliases.\"\"\"
    from md_processing.md_processing_utils.md_processing_constants import get_command_spec, build_command_variants
    
    spec = get_command_spec(base_command)
    registered = set()
    
    names_to_register = [base_command]
    if spec:
        names_to_register.append(spec.get('display_name', ''))
        alt_names = spec.get('alternate_names', [])
        if isinstance(alt_names, str):
            alt_names = [item.strip() for item in alt_names.split(";") if item.strip()]
        names_to_register.extend(alt_names)

    for name in names_to_register:
        key = normalize_command_key(name)
        if key and key not in registered:
            dispatcher.register(key, processor_cls)
            registered.add(key)
            
    if spec:
        for variant in build_command_variants(base_command, spec):
            vkey = normalize_command_key(variant)
            if vkey and vkey not in registered:
                dispatcher.register(vkey, processor_cls)
                registered.add(vkey)
    if not spec:
        key = normalize_command_key(base_command)
        if key:
            dispatcher.register(key, processor_cls)

def setup_dispatcher(client: EgeriaTech) -> V2Dispatcher:
    \"\"\"Create and configure a V2Dispatcher with all registered processors.\"\"\"
    dispatcher = V2Dispatcher(client)
    
    def reg(base, cls):
        register_processor(dispatcher, base, cls)

    # Glossary
    reg("Create Glossary Term", TermProcessor)
    reg("Link Term-Term Relationship", TermRelationshipProcessor)
    reg("Unlink Term-Term Relationship", TermRelationshipProcessor)
    reg("Remove Term-Term Relationship", TermRelationshipProcessor)
    reg("Detach Term-Term Relationship", TermRelationshipProcessor)

    # Data Designer
    from md_processing.v2.data_designer import (
        DataValueSpecificationProcessor, DataClassProcessor, DataStructureProcessor, DataFieldProcessor, DataGrainProcessor,
        LinkDataFieldProcessor, LinkFieldToStructureProcessor, LinkDataValueDefinitionProcessor, LinkDataValueCompositionProcessor,
        LinkDataClassCompositionProcessor, LinkCertificationTypeToStructureProcessor, AttachDataDescriptionProcessor,
        AssignDataValueSpecificationProcessor, AttachDataValueSpecificationProcessor
    )

    reg("Create Data Specification", DataCollectionProcessor)
    reg("Create Data Dictionary", DataCollectionProcessor)
    reg("Create Data Structure", DataStructureProcessor)
    reg("Create Data Field", DataFieldProcessor)
    reg("Create Data Class", DataClassProcessor)
    reg("Create Data Value Specification", DataValueSpecificationProcessor)
    reg("Update Data Value Specification", DataValueSpecificationProcessor)
    reg("Create Data Grain", DataGrainProcessor)
    reg("Link Data Field", LinkDataFieldProcessor)
    reg("Link Field to Structure", LinkFieldToStructureProcessor)
    reg("Link Data Value Definition", LinkDataValueDefinitionProcessor)
    reg("Link Data Value Composition", LinkDataValueCompositionProcessor)
    reg("Link Data Class Composition", LinkDataClassCompositionProcessor)
    reg("Link Certification Type to Data Structure", LinkCertificationTypeToStructureProcessor)
    reg("Attach Data Description to Element", AttachDataDescriptionProcessor)
    reg("Assign Data Value Specification", AssignDataValueSpecificationProcessor)
    reg("Attach Data Value Specification to Element", AttachDataValueSpecificationProcessor)

    # Solution Architect (spec-driven to keep coverage aligned with compact commands)
    register_solution_architect_processors(reg)

    # Project
    reg("Create Project", ProjectProcessor)
    reg("Link Project Dependency", ProjectLinkProcessor)
    reg("Link Project Hierarchy", ProjectLinkProcessor)

    for proj_type in PROJECT_SUBTYPES:
        reg(f"Create {proj_type}", ProjectProcessor)
        reg(f"Update {proj_type}", ProjectProcessor)

    # Collection Manager
    for coll_type in COLLECTION_SUBTYPES:
        reg(f"Create {coll_type}", CollectionManagerProcessor)
        reg(f"Update {coll_type}", CollectionManagerProcessor)

    reg("Create CSV Element", CSVElementProcessor)
    reg("Add Member to Collection", CollectionLinkProcessor)
    reg("Link Agreement Item", CollectionLinkProcessor)
    reg("Link Agreement Actor", CollectionLinkProcessor)
    reg("Link Product Dependency", CollectionLinkProcessor)
    reg("Link Product-Product", CollectionLinkProcessor)
    reg("Attach Collection to Resource", CollectionLinkProcessor)
    reg("Link Digital Subscriber", CollectionLinkProcessor)

    # Governance (spec-driven to keep coverage aligned with compact commands)
    register_governance_processors(reg)
    # Reporting / View
    reg("View Report", ViewProcessor)

    # Feedback / Tags / External References
    reg("Add Comment", FeedbackProcessor)
    reg("Update Comment", FeedbackProcessor)
    reg("Create Journal Entry", FeedbackProcessor)
    reg("Create Informal Tag", TagProcessor)
    reg("Update Informal Tag", TagProcessor)
    reg("Add Informal Tag", FeedbackLinkProcessor)
    reg("Detach Informal Tag", FeedbackLinkProcessor)
    reg("Link Tag->Element", FeedbackLinkProcessor)
    reg("Link Tag", FeedbackLinkProcessor)
    reg("Detach Tag", FeedbackLinkProcessor)
    reg("Create External Reference", ExternalReferenceProcessor)
    reg("Update External Reference", ExternalReferenceProcessor)
    reg("Link External Reference", FeedbackLinkProcessor)
    reg("Detach External Reference", FeedbackLinkProcessor)
    reg("Create Related Media", ExternalReferenceProcessor)
    reg("Update Related Media", ExternalReferenceProcessor)
    reg("Link Media Reference", FeedbackLinkProcessor)
    reg("Detach Media Reference", FeedbackLinkProcessor)
    reg("Create Cited Document", ExternalReferenceProcessor)
    reg("Update Cited Document", ExternalReferenceProcessor)
    reg("Link Cited Document", FeedbackLinkProcessor)
    reg("Detach Cited Document", FeedbackLinkProcessor)
    reg("Create External Data Source", ExternalReferenceProcessor)
    reg("Update External Data Source", ExternalReferenceProcessor)
    reg("Create External Model Source", ExternalReferenceProcessor)
    reg("Update External Model Source", ExternalReferenceProcessor)
    reg("Create External Source Code", ExternalReferenceProcessor)
    reg("Update External Source Code", ExternalReferenceProcessor)
    reg("Attach Comment", FeedbackLinkProcessor)
    reg("Detach Comment", FeedbackLinkProcessor)
    reg("Attach Rating", FeedbackLinkProcessor)
    reg("Detach Rating", FeedbackLinkProcessor)
    reg("Attach Like", FeedbackLinkProcessor)
    reg("Detach Like", FeedbackLinkProcessor)
    reg("Link Accept Answer", FeedbackLinkProcessor)
    reg("Unlink Accept Answer", FeedbackLinkProcessor)
    
    return dispatcher

async def process_md_file_v2(input_file: str, output_folder: str, directive: str, client: EgeriaTech,
"""

content = content.replace("async def process_md_file_v2(input_file: str, output_folder: str, directive: str, client: EgeriaTech,", top_level_funcs)

remove_start = "    # 2. Setup v2 Dispatcher"
remove_end = "    register_processor(\"Unlink Accept Answer\", FeedbackLinkProcessor)\n"

start_idx = content.find(remove_start)
end_idx = content.find(remove_end) + len(remove_end)

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + "    # 2. Setup v2 Dispatcher\n    dispatcher = setup_dispatcher(client)\n" + content[end_idx:]

with open("md_processing/dr_egeria.py", "w") as f:
    f.write(content)

print("done script")


