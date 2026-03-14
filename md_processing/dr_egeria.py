"""
This is an ongoing experiment in parsing and playing with Freddie docs
"""
import os
import sys
import uuid
from typing import Type
from datetime import datetime

from loguru import logger
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

import asyncio
from md_processing import (extract_command, process_provenance_command, get_current_datetime_string, command_list)
from md_processing.md_processing_utils.common_md_proc_utils import set_parse_summary_mode
from md_processing.md_processing_utils.common_md_utils import set_attribute_log_level, ALL_GOVERNANCE_DEFINITIONS
from md_processing.md_processing_utils.md_processing_constants import PROJECT_COMMANDS
from md_processing.v1_legacy.command_mapping import setup_dispatcher
from md_processing.v2 import (
    UniversalExtractor, v2Dispatcher, AsyncBaseCommandProcessor,
    GlossaryProcessor, TermProcessor, TermRelationshipProcessor,
    DataCollectionProcessor, DataStructureProcessor, DataFieldProcessor, DataClassProcessor,
    BlueprintProcessor, ComponentProcessor, SupplyChainProcessor, SolutionLinkProcessor,
    ProjectProcessor, ProjectLinkProcessor,
    CollectionProcessor, ProductProcessor, AgreementProcessor, CSVElementProcessor, ProductLinkProcessor,
    GovernanceProcessor, GovernanceLinkProcessor, GovernanceContextProcessor,
    FeedbackProcessor, TagProcessor, ExternalReferenceProcessor, FeedbackLinkProcessor
)

from pyegeria import EgeriaTech, PyegeriaException, print_basic_exception, print_validation_error
from pyegeria.core.config import settings

# Configure logging - module level default
log_format = "{time} | {level} | {function} | {line} | {message} | {extra}"

# Only configure logging if we are running as main
if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stderr, level="INFO", format=log_format, colorize=True)
    logger.add("debug_log.log", rotation="1 day", retention="1 week", compression="zip", level="INFO", format=log_format,
               colorize=True)

# Load configuration from config/config.json with environment variable overrides
app_config = settings.Environment

# Get configuration values with environment variable fallbacks
EGERIA_METADATA_STORE = app_config.egeria_metadata_store
EGERIA_KAFKA_ENDPOINT = app_config.egeria_kafka_endpoint
EGERIA_PLATFORM_URL = app_config.egeria_platform_url
EGERIA_VIEW_SERVER = app_config.egeria_view_server
EGERIA_VIEW_SERVER_URL = app_config.egeria_view_server_url
EGERIA_INTEGRATION_DAEMON = app_config.egeria_integration_daemon
EGERIA_INTEGRATION_DAEMON_URL = app_config.egeria_integration_daemon_url
EGERIA_WIDTH = int(app_config.console_width or 220)
console = Console(width=EGERIA_WIDTH)
EGERIA_JUPYTER = bool(app_config.egeria_jupyter)
EGERIA_GLOSSARY_PATH = app_config.egeria_glossary_path
EGERIA_ROOT_PATH = app_config.pyegeria_root
EGERIA_INBOX_PATH = app_config.dr_egeria_inbox
EGERIA_OUTBOX_PATH = app_config.dr_egeria_outbox

# User credentials and admin credentials are only from environment variables (not stored in config for security)
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")

# Legacy environment variables (deprecated, kept for backward compatibility)
EGERIA_HOME_GLOSSARY_GUID = os.environ.get("EGERIA_HOME_GLOSSARY_GUID", None)

async def process_md_file_v2(input_file: str, output_folder: str, directive: str, client: EgeriaTech, 
                            parse_summary: str = "none", attribute_logs: str = "debug") -> None:
    """
    Async processing path for Dr.Egeria v2.
    """
    set_parse_summary_mode(parse_summary)
    set_attribute_log_level(attribute_logs)
    
    if os.path.exists(input_file):
        full_file_path = input_file
    elif EGERIA_INBOX_PATH in input_file:
        full_file_path = os.path.join(EGERIA_ROOT_PATH, input_file)
    else:
        full_file_path = os.path.join(EGERIA_ROOT_PATH, EGERIA_INBOX_PATH, input_file)
        
    logger.info(f"v2: Processing Markdown File: {full_file_path}")
    console.print(f"v2: Processing Markdown File: {full_file_path}")

    if directive == "process":
        print("\n[bold red]*** WARNING: PROCESS MODE ***[/bold red]")
        print("[red]Dr. Egeria will EXECUTE these commands and make PERMANENT CHANGES to Egeria.[/red]\n")
    
    try:
        with open(full_file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at path: {full_file_path}")
        return

    # 1. Extract commands using UniversalExtractor
    extractor = UniversalExtractor(content)
    commands = extractor.extract_commands()
    
    if not commands:
        logger.warning(f"No valid Egeria Markdown commands found in {full_file_path}")
        console.print(f"[bold yellow]Warning:[/bold yellow] No valid Egeria commands could be parsed from [cyan]'{input_file}'[/cyan].")
        console.print("Ensure your markdown file uses correctly formatted headers (e.g. `## Create Glossary`) that match known commands.")
        return
        
    # 2. Setup v2 Dispatcher
    dispatcher = v2Dispatcher(client)
    from md_processing.md_processing_utils.md_processing_constants import get_command_spec, build_command_variants

    def register_processor(base_command: str, processor_cls: Type[AsyncBaseCommandProcessor]):
        """Register a processor for a base command and all its variants/alternates."""
        spec = get_command_spec(base_command)
        if spec:
            variants = build_command_variants(base_command, spec)
            for variant in variants:
                dispatcher.register(variant, processor_cls)
        else:
            dispatcher.register(base_command, processor_cls)

    # Glossary
    register_processor("Create Glossary", GlossaryProcessor)
    register_processor("Create Glossary Term", TermProcessor)
    register_processor("Link Term-Term Relationship", TermRelationshipProcessor)

    # Data Designer
    register_processor("Create Data Specification", DataCollectionProcessor)
    register_processor("Create Data Dictionary", DataCollectionProcessor)
    register_processor("Create Data Structure", DataStructureProcessor)
    register_processor("Create Data Field", DataFieldProcessor)
    register_processor("Create Data Class", DataClassProcessor)
    register_processor("Link Data Field", DataFieldProcessor) # Uses same processor as fields usually? Or generic link?

    # Solution Architect
    register_processor("Create Solution Blueprint", BlueprintProcessor)
    register_processor("Create Solution Component", ComponentProcessor)
    register_processor("Create Information Supply Chain", SupplyChainProcessor)
    register_processor("Link Solution Component Peers", SolutionLinkProcessor)
    register_processor("Link Information Supply Chain Peers", SolutionLinkProcessor)
    register_processor("Link Information Supply Chain Segment", SolutionLinkProcessor)

    # Project
    register_processor("Create Project", ProjectProcessor)
    register_processor("Link Project Dependency", ProjectLinkProcessor)
    register_processor("Link Project Hierarchy", ProjectLinkProcessor)

    # Alternate Project Commands (Campaign, Task, etc.)
    for proj_cmd in PROJECT_COMMANDS:
        dispatcher.register(proj_cmd, ProjectProcessor)

    # Product Manager
    register_processor("Create Collection", CollectionProcessor)
    register_processor("Update Collection", CollectionProcessor)
    register_processor("Create Root Collection", CollectionProcessor)
    register_processor("Update Root Collection", CollectionProcessor)
    register_processor("Create Folder", CollectionProcessor)
    register_processor("Update Folder", CollectionProcessor)
    register_processor("Create Digital Product", ProductProcessor)
    register_processor("Update Digital Product", ProductProcessor)
    register_processor("Create Data Sharing Agreement", AgreementProcessor)
    register_processor("Update Data Sharing Agreement", AgreementProcessor)
    register_processor("Create CSV Element", CSVElementProcessor)
    register_processor("Add Member to Collection", ProductLinkProcessor)
    register_processor("Link Agreement Item", ProductLinkProcessor)
    register_processor("Link Product Dependency", ProductLinkProcessor)
    register_processor("Link Product-Product", ProductLinkProcessor)
    register_processor("Attach Collection to Resource", ProductLinkProcessor)
    register_processor("Link Digital Subscriber", ProductLinkProcessor)

    # Governance
    from md_processing.md_processing_utils.md_processing_constants import GOV_COM_LIST
    for gov_cmd in GOV_COM_LIST:
        register_processor(gov_cmd, GovernanceProcessor)
    
    # Fallback to catch any from the list that might be missing from GOV_COM_LIST or use a different verb
    for gov_type in ALL_GOVERNANCE_DEFINITIONS + ["Data Lens"]:
        register_processor(f"Create {gov_type}", GovernanceProcessor)
        register_processor(f"Update {gov_type}", GovernanceProcessor)
    
    # Generic registration for gov links
    register_processor("Link Governance Peer", GovernanceLinkProcessor)
    register_processor("Detach Governance Peer", GovernanceLinkProcessor)
    register_processor("Link Governance Supporting", GovernanceLinkProcessor)
    register_processor("Detach Governance Supporting", GovernanceLinkProcessor)
    register_processor("Link Governed By", GovernanceLinkProcessor)
    register_processor("Detach Governed By", GovernanceLinkProcessor)
    register_processor("View Governance Definition Context", GovernanceContextProcessor)

    # Feedback / Tags / External References
    register_processor("Add Comment", FeedbackProcessor)
    register_processor("Update Comment", FeedbackProcessor)
    register_processor("Create Journal Entry", FeedbackProcessor)
    register_processor("Create Informal Tag", TagProcessor)
    register_processor("Update Informal Tag", TagProcessor)
    register_processor("Add Informal Tag", FeedbackLinkProcessor)
    register_processor("Detach Informal Tag", FeedbackLinkProcessor)
    register_processor("Link Tag->Element", FeedbackLinkProcessor)
    register_processor("Link Tag", FeedbackLinkProcessor)
    register_processor("Detach Tag", FeedbackLinkProcessor)
    register_processor("Create External Reference", ExternalReferenceProcessor)
    register_processor("Update External Reference", ExternalReferenceProcessor)
    register_processor("Link External Reference", FeedbackLinkProcessor)
    register_processor("Detach External Reference", FeedbackLinkProcessor)
    register_processor("Create Related Media", ExternalReferenceProcessor)
    register_processor("Update Related Media", ExternalReferenceProcessor)
    register_processor("Link Related Media", FeedbackLinkProcessor)
    register_processor("Detach Related Media", FeedbackLinkProcessor)
    register_processor("Create Cited Document", ExternalReferenceProcessor)
    register_processor("Update Cited Document", ExternalReferenceProcessor)
    register_processor("Link Cited Document", FeedbackLinkProcessor)
    register_processor("Detach Cited Document", FeedbackLinkProcessor)
    
    context = {
        "directive": directive,
        "input_file": input_file,
        "request_id": str(uuid.uuid4())
    }
    
    # 3. Execution (Parallel)
    # We dispatch all commands in the document concurrently.
    # Note: Complex documents with inter-command dependencies may require a more 
    # sophisticated strategy in the future.
    results = await dispatcher.dispatch_batch(commands, context)
    
    # 4. Handle results and display summary
    final_output = []
    summary_table = Table(title="Dr. Egeria v2 Processing Summary", show_header=True, header_style="bold magenta")
    summary_table.add_column("Command", style="cyan")
    summary_table.add_column("Status", style="bold")
    summary_table.add_column("Qualified Name", style="magenta")
    summary_table.add_column("GUID", style="yellow")
    summary_table.add_column("Message")

    updated = False
    for res in results:
        final_output.append(res["output"])
        status_color = "green" if res["status"] == "success" else "red" if res["status"] == "failure" else "yellow"
        summary_table.add_row(
            f"{res['verb']} {res['object_type']}",
            f"[{status_color}]{res['status'].upper()}[/{status_color}]",
            res.get("qualified_name", ""),
            res.get("guid", ""),
            res["message"]
        )
        if res["status"] == "success" and directive == "process":
            updated = True

    console.print("\n")
    console.print(summary_table)
    console.print("\n")

    has_warnings = any(res.get("warnings") for res in results)

    # Display warnings for both validate and process
    if has_warnings:
        console.print("[bold yellow]Processing Warnings:[/bold yellow]\n")
        for res in results:
            warnings = res.get("warnings", [])
            if warnings:
                console.print(f"[yellow]-- {res['verb']} {res['object_type']} ({res.get('qualified_name', 'Unknown')}) --[/yellow]")
                for w in warnings:
                    console.print(f"   [yellow]* {w}[/yellow]")
        console.print("\n")

    if directive == "validate":
        from md_processing.md_processing_utils.common_md_utils import render_markdown
        console.print("[bold cyan]Validation Diagnosis Summary:[/bold cyan]\n")
        for res in results:
            if res.get("output"):
                render_markdown(res["output"])
        console.print("\n")

    if directive == "process" and updated:
        # Re-assemble the file (simplified for now, using the joined outputs)
        content_to_write = "\n---\n".join(final_output)
        
        path, filename = os.path.split(input_file)
        new_filename = f"processed-{get_current_datetime_string()}-{filename}"
        
        if output_folder:
            new_file_path = os.path.join(EGERIA_ROOT_PATH, EGERIA_OUTBOX_PATH, output_folder, new_filename)
        else:
            new_file_path = os.path.join(EGERIA_ROOT_PATH, EGERIA_OUTBOX_PATH, new_filename)
            
        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)

        with open(new_file_path, 'w') as f2:
            f2.write(content_to_write)
            
        console.print(f"==> [bold green]SUCCESS[/bold green]: Output written to [blue]{new_file_path}[/blue]")
    elif directive == "process":
        console.print("[yellow]No updates detected. New File not created.[/yellow]")

    console.print(f"\n[bold green]v2: Processing complete for '{input_file}'[/bold green]")
    logger.info("v2: Processing complete")


@logger.catch
def process_md_file(input_file: str, output_folder: str, directive: str, server: str, url: str, userid: str,
                          user_pass: str, parse_summary: str = "none",
                          attribute_logs: str = "debug") -> None:
    """
    Process a markdown file by parsing and executing Dr. Egeria md_commands. Write output to a new file.
    """
    use_v2 = os.environ.get("DR_EGERIA_V2", "true").lower() in ("true", "1", "yes")

    if use_v2:
        client = EgeriaTech(server, url, user_id=userid)
        client.create_egeria_bearer_token(userid, user_pass)
        asyncio.run(process_md_file_v2(input_file, output_folder, directive, client, parse_summary, attribute_logs))
        return

    set_parse_summary_mode(parse_summary)
    set_attribute_log_level(attribute_logs)

    cmd_list = command_list
    # console = Console(width=int(EGERIA_WIDTH))
    client = EgeriaTech(server, url, user_id=userid)
    token = client.create_egeria_bearer_token(userid, user_pass)
    
    # Initialize the dispatcher
    dispatcher = setup_dispatcher()

    updated = False
    full_file_path = os.path.join(EGERIA_ROOT_PATH, EGERIA_INBOX_PATH, input_file)
    logger.info("\n\n====================================================\n\n")
    logger.info(f"Processing Markdown File: {full_file_path}")
    print(f"Processing Markdown File: {full_file_path}")

    if directive != "validate":
        console.print("\n[bold red]*** WARNING: PROCESS MODE ***[/bold red]")
        console.print("[red]Dr. Egeria will EXECUTE these commands and make PERMANENT CHANGES to Egeria.[/red]\n")
    try:
        with open(full_file_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found at path: {full_file_path}")
        return {}  # Return empty dict if file not found

    final_output = []
    prov_found = False
    prov_output = (f"\n# Provenance\n\n* Results from processing file {input_file} on "
                   f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    h1_blocks = []
    current_block = ""
    in_h1_block = False

    # Helper function to process the current block
    def process_current_block(current_block):
        nonlocal updated, final_output, prov_found, prov_output, h1_blocks, in_h1_block

        if not current_block:
            return  # No block to process

        potential_command = extract_command(current_block)  # Extract object_action
        if potential_command in cmd_list:
            # Process the block based on the object_action
            if potential_command == "Provenance":
                result = process_provenance_command(input_file, current_block)
                prov_found = True
            else:
                # Use the dispatcher for all other commands
                result = dispatcher.dispatch(potential_command, client, current_block, directive)

            # Error handling logic
            if result is None and potential_command != "Provenance":
                handler = dispatcher.get_handler(potential_command)
                if not handler:
                     print(f"\n===> Unknown command: {potential_command}")
                
            if result:
                if directive == "process":
                    updated = True
                    final_output.append(result)
                elif directive == "validate":
                    pass 
            elif directive == "process":
                # Only warn if it looked like a valid command but failed (or was unknown)
                print(f"\n==>\tErrors found while processing command: \'{potential_command}\'\n"
                      f"\tPlease correct and try again. \n")
                final_output.append(current_block)
                final_output.append('\n____\n')
        else:
            # If there is no object_action, append the block as-is
            final_output.append(current_block)

    # Main parsing loop
    for line in lines:
        line = line.strip()  # Remove leading/trailing whitespace

        # Handle a new H1 block (starting with `# `)
        if line.startswith("# "):
            if in_h1_block:
                # Process the current block before starting a new one
                process_current_block(current_block)

            # Start a new H1 block
            current_block = line
            in_h1_block = True

        # Handle the end of a block (line starts with `---`)
        elif line.startswith("___") or line.startswith("---"):
            if in_h1_block:
                # Process the current block when it ends with `---`
                current_block += f"\n{line}"
                process_current_block(current_block)
                current_block = ""  # Clear the block
                in_h1_block = False

        # Add lines to the current H1 block
        elif in_h1_block:
            current_block += f"\n{line}"

        # Append non-H1 content directly to the output
        else:
            final_output.append(line)

    # Ensure the final H1 block is processed if the file doesn't end with `---`
    if in_h1_block:
        process_current_block(current_block)

    # Join the final output list into a single string
    final_output = "\n".join(final_output) if isinstance(final_output, list) else final_output

    try:
        if updated:
            path, filename = os.path.split(input_file)  # Get both parts
            new_filename = f"processed-{get_current_datetime_string()}-{filename}"  # Create the new filename
            
            if output_folder:
                new_file_path = os.path.join(EGERIA_ROOT_PATH, EGERIA_OUTBOX_PATH, output_folder, new_filename)
            else:
                new_file_path = os.path.join(EGERIA_ROOT_PATH, EGERIA_OUTBOX_PATH, new_filename)
            os.makedirs(os.path.dirname(new_file_path), exist_ok=True)

            with open(new_file_path, 'w') as f2:
                f2.write(final_output)
                if not prov_found:
                    f2.write(prov_output)
            print(f"\n==> Output written to {new_file_path}")
        else:
            if directive != 'display':
                print("\nNo updates detected. New File not created.")
                # logger.error(f"===> Unknown Command?  <===") 

    except PyegeriaException as e:
        print_basic_exception(e)
    except ValidationError as e:
        print_validation_error(e)

if __name__ == "__main__":
    import argparse
    import asyncio
    parser = argparse.ArgumentParser(description="Process Dr. Egeria Markdown files using v2.")
    parser.add_argument("--input-file", required=True, help="Input markdown file name (in Inbox)")
    parser.add_argument("--output-folder", default="", help="Optional output subfolder (in Outbox)")
    parser.add_argument("--directive", default="process", choices=["display", "validate", "process"], help="Action to perform")
    
    args = parser.parse_args()
    
    # Run the async v2 processor
    asyncio.run(
        process_md_file_v2(
            args.input_file, 
            args.directive, 
            args.output_folder
        )
    )
