from md_processing.md_processing_utils.md_processing_constants import load_commands

# Ensure compact command specs are loaded before any v2 processing
load_commands()
"""
This is an ongoing experiment in parsing and playing with Freddie docs
"""
import os
import sys
import uuid
from typing import Type, Callable
import re

from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.box import Box
from rich.markdown import Markdown

import asyncio
from md_processing import (process_provenance_command, get_current_datetime_string)
from md_processing.md_processing_utils.common_md_proc_utils import set_parse_summary_mode, set_usage_level
from md_processing.md_processing_utils.common_md_utils import set_attribute_log_level
from md_processing.md_processing_utils.md_processing_constants import PROJECT_SUBTYPES, COLLECTION_SUBTYPES
from md_processing.v2 import (
    UniversalExtractor, V2Dispatcher, AsyncBaseCommandProcessor,
    TermProcessor, TermRelationshipProcessor,
    DataCollectionProcessor, DataStructureProcessor, DataFieldProcessor, DataClassProcessor,
    BlueprintProcessor, ComponentProcessor, SupplyChainProcessor, SolutionLinkProcessor,
    SolutionArchitectProcessor,
    ProjectProcessor, ProjectLinkProcessor,
    CollectionManagerProcessor, CSVElementProcessor, CollectionLinkProcessor,
    GovernanceProcessor, GovernanceLinkProcessor, GovernanceContextProcessor,
    FeedbackProcessor, TagProcessor, ExternalReferenceProcessor, FeedbackLinkProcessor,
    ViewProcessor
)

from pyegeria import EgeriaTech, PyegeriaException, print_basic_exception, print_validation_error
from pyegeria.core.config import settings

# Configure logging - module level default
log_format = "{time} | {level} | {function} | {line} | {message} | {extra}"

# Only configure logging if we are running as main
if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stderr, level="WARNING", format=log_format, colorize=True)
    logger.add("debug_log.log", rotation="1 day", retention="1 week", compression="zip", level="WARNING", format=log_format,
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


def register_solution_architect_processors(register_processor: Callable[[str, Type[AsyncBaseCommandProcessor]], None]) -> None:
    """Register solution architect processors from compact command specs."""
    from md_processing.md_processing_utils.md_processing_constants import (
        COMMAND_DEFINITIONS,
        build_command_variants,
        load_commands,
    )

    load_commands()
    specs = COMMAND_DEFINITIONS.get("Command Specifications", {})
    link_verbs = {"Link", "Attach", "Add", "Detach", "Unlink", "Remove"}

    for base_name, spec in specs.items():
        if not isinstance(spec, dict):
            continue
        if spec.get("family") != "Solution Architect":
            continue
        
        variants = build_command_variants(base_name, spec)
        
        # Determine processor class
        if base_name.split(" ", 1)[0] in link_verbs:
            processor_cls = SolutionLinkProcessor
        elif "Blueprint" in base_name:
            processor_cls = BlueprintProcessor
        elif "Component" in base_name and "Link" not in base_name:
            processor_cls = ComponentProcessor
        elif "Information Supply Chain" in base_name and "Link" not in base_name:
            processor_cls = SupplyChainProcessor
        else:
            processor_cls = SolutionArchitectProcessor
            
        register_processor(base_name, processor_cls)

def register_governance_processors(register_processor: Callable[[str, Type[AsyncBaseCommandProcessor]], None]) -> None:
    """Register governance processors from compact command specs to avoid hard-coded drift."""
    from md_processing.md_processing_utils.md_processing_constants import (
        COMMAND_DEFINITIONS,
        build_command_variants,
        load_commands,
    )

    load_commands()
    specs = COMMAND_DEFINITIONS.get("Command Specifications", {})
    link_verbs = {"Link", "Attach", "Add", "Detach", "Unlink", "Remove"}

    for base_name, spec in specs.items():
        if not isinstance(spec, dict):
            continue
        if spec.get("family") != "Governance Officer":
            continue

        variants = build_command_variants(base_name, spec)
        processor_cls = GovernanceLinkProcessor if base_name.split(" ", 1)[0] in link_verbs else GovernanceProcessor
        for variant in variants:
            register_processor(variant, processor_cls)

    # Context retrieval is not in compact command specs; keep explicit registration.
    register_processor("View Governance Definition Context", GovernanceContextProcessor)


def normalize_command_key(key: str) -> str:
    """Collapse whitespace and strip for consistent command matching."""
    import re
    return re.sub(r'\s+', ' ', key).strip() if key else key

def register_processor(dispatcher: V2Dispatcher, base_command: str, processor_cls: Type[AsyncBaseCommandProcessor]):
    """Register a processor for a command and its variants/aliases."""
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
    """Create and configure a V2Dispatcher with all registered processors."""
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

                            parse_summary: str = "none", attribute_logs: str = "info",
                            usage_level: str = None, summary_only: bool = False,
                            debug: bool = False) -> None:
    """
    Async processing path for Dr.Egeria v2.
    """
    if usage_level:
        set_usage_level(usage_level)
    set_parse_summary_mode(parse_summary)
    set_attribute_log_level(attribute_logs)

    # Debug mode: intercept all HTTP requests to log URL and body to the console
    _orig_make_request = None
    if debug:
        import json as _json_debug
        from pyegeria.core._base_server_client import BaseServerClient
        _orig_make_request = BaseServerClient._async_make_request

        async def _debug_make_request(self_inner, request_type, endpoint,
                                      payload=None, time_out=30, is_json=True, params=None):
            import inspect as _inspect

            _url_str = endpoint
            if params:
                _url_str += f"  (params: {params})"

            # Walk up the call stack and collect up to 3 relevant frames,
            # skipping asyncio/stdlib internals and this closure itself.
            _skip_path_parts = {'asyncio', 'concurrent', 'importlib', 'contextlib'}
            _skip_file_prefixes = ('<frozen', '<string', '<stdin')
            _frames = []
            for _fi in _inspect.stack()[1:15]:
                _fname = _fi.filename
                if any(_fname.startswith(p) for p in _skip_file_prefixes):
                    continue
                _norm = _fname.replace('\\', '/')
                if any(part in _norm for part in _skip_path_parts):
                    continue
                # Show last 3 path components for readability
                _short = '/'.join(_norm.split('/')[-3:])
                _frames.append(f"{_short}:{_fi.lineno} in {_fi.function}()")
                if len(_frames) >= 3:
                    break
            _caller_str = "\n             ← ".join(_frames) if _frames else "unknown"

            console.print(f"\n[bold dark_orange][DEBUG] {request_type} → {_url_str}[/bold dark_orange]")
            console.print(f"[dark_orange][DEBUG] Called from: {_caller_str}[/dark_orange]")
            if payload is not None:
                if isinstance(payload, dict):
                    console.print(
                        f"[dark_orange][DEBUG] Body:\n{_json_debug.dumps(payload, indent=2)}[/dark_orange]"
                    )
                elif isinstance(payload, str):
                    try:
                        _parsed = _json_debug.loads(payload)
                        console.print(
                            f"[dark_orange][DEBUG] Body:\n{_json_debug.dumps(_parsed, indent=2)}[/dark_orange]"
                        )
                    except Exception:
                        console.print(f"[dark_orange][DEBUG] Body: {payload}[/dark_orange]")
            return await _orig_make_request(self_inner, request_type, endpoint,
                                            payload, time_out, is_json, params)

        BaseServerClient._async_make_request = _debug_make_request
        console.print(
            "[bold yellow][DEBUG] Request debug mode ENABLED — all Egeria API requests will be logged.[/bold yellow]\n"
        )

    expanded_input = os.path.abspath(os.path.expanduser(input_file))
    if os.path.exists(expanded_input):
        full_file_path = expanded_input
    elif EGERIA_INBOX_PATH in input_file:
        full_file_path = os.path.abspath(os.path.expanduser(os.path.join(EGERIA_ROOT_PATH, input_file)))
    else:
        full_file_path = os.path.abspath(os.path.expanduser(os.path.join(EGERIA_ROOT_PATH, EGERIA_INBOX_PATH, input_file)))

    logger.info(f"v2: Processing Markdown File: {full_file_path}")
    console.print(f"[cyan]v2: Processing Markdown File: {full_file_path}[/cyan]")

    if directive == "process":
        console.print("\n[bold cyan]*** INFO: PROCESS MODE ***[/bold cyan]")
        console.print("[cyan]Dr. Egeria will EXECUTE these commands and make PERMANENT CHANGES to Egeria.[/cyan]\n")
    
    try:
        with open(full_file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        console.print(f"[red]Error: File not found at path: {full_file_path}[/red]")
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
    dispatcher = setup_dispatcher(client)

    context = {
        "directive": directive,
        "input_file": input_file,
        "request_id": str(uuid.uuid4()),
        "debug": debug,
    }
    
    # 3. Execution (Parallel)
    # We dispatch all commands in the document concurrently.
    # Note: Complex documents with inter-command dependencies may require a more 
    # sophisticated strategy in the future.
    try:
        results = await dispatcher.dispatch_batch(commands, context)
    except Exception as e:
        from pyegeria.core._exceptions import print_basic_exception, print_validation_error
        import traceback
        from pydantic import ValidationError
        console.print("[bold red]Exception occurred during batch processing:[/bold red]")
        traceback.print_exc()
        if hasattr(e, 'response'):
            console.print(f"[red]Response: {getattr(e, 'response', None)}[/red]")
        if hasattr(e, 'status_code'):
            console.print(f"[red]Status code: {getattr(e, 'status_code', None)}[/red]")
        if hasattr(e, 'request'):
            console.print(f"[red]Request: {getattr(e, 'request', None)}[/red]")
        if isinstance(e, ValidationError):
            print_validation_error(e)
        elif 'Pyegeria' in type(e).__name__:
            print_basic_exception(e)
        else:
            console.print(f"[red]{repr(e)}[/red]")
        return

    # 4. Handle results
    final_output = []

    # 4a. Print analysis to console (for both validate and process) if not summary_only
    # (Removed redundant loop, consolidation in progress)
    
    # Custom box style for dotted line row separators
    DOTTED = Box(
        "┏━┳┓\n"
        "┃ ┃┃\n"
        "┡━╇┩\n"
        "│ ││\n"
        "├·┼┤\n"
        "├─┼┤\n"
        "│ ││\n"
        "└─┴┘\n"
    )

    summary_table = Table(title="Dr. Egeria v2 Processing Summary", show_header=True, header_style="bold magenta", 
                          show_lines=True, box=DOTTED)
    summary_table.add_column("Markdown Command", style="cyan", overflow="fold")
    summary_table.add_column("Canonical Command", style="bright_cyan", overflow="fold")
    summary_table.add_column("Status", style="bold", overflow="fold")
    summary_table.add_column("Found", style="green", overflow="fold")
    summary_table.add_column("Display Name", style="blue", overflow="fold")
    summary_table.add_column("Qualified Name", style="magenta", overflow="fold")
    summary_table.add_column("Message", min_width=36, overflow="fold")

    updated = False
    prov_found = False
    
    # Process results for summary, file assembly, and display
    for res in results:
        # 4a. Display command analysis or block content (if not summary_only)
        if not summary_only:
            is_cmd = res.get("is_command", True)
            if is_cmd:
                if res.get("analysis"):
                    console.print(f"\n[bold blue]=== Command Analysis: {res.get('verb')} {res.get('object_type')} ===[/bold blue]")
                    console.print(Markdown(res["analysis"]))
                    console.print("\n")
                elif directive in ("validate", "display") and res.get("output"):
                    from md_processing.md_processing_utils.common_md_utils import render_markdown
                    render_markdown(res["output"])
            else:
                if directive in ("validate", "display") and res.get("output"):
                    from md_processing.md_processing_utils.common_md_utils import render_markdown
                    render_markdown(res["output"])

        # 4b. Handle provenance section if encountered
        if res.get("verb") == "Provenance":
            prov_found = True
            final_output.append(process_provenance_command(input_file, ""))
        else:
            final_output.append(res["output"])

        # 4c. Only add actual commands to the summary table
        if not res.get("is_command", True):
            continue

        # Skip Provenance from summary table as it's a meta-command
        if res.get("verb") == "Provenance":
            continue

        status_color = "green" if res["status"] == "success" else "red" if res["status"] == "failure" else "yellow"
        found_str = "Yes" if res.get("found") else "No"
        summary_table.add_row(
            f"{res.get('verb', '')} {res.get('markdown_object_type', res.get('object_type', ''))}".strip(),
            f"{res.get('verb', '')} {res.get('object_type', '')}".strip(),
            f"[{status_color}]{res['status'].upper()}[/{status_color}]",
            found_str,
            res.get("display_name", ""),
            res.get("qualified_name", ""),
            res["message"]
        )
        if res["status"] == "success" and directive == "process":
            updated = True

    # Add Provenance if not already present
    if not prov_found:
        final_output.append(process_provenance_command(input_file, ""))

    # (Consolidated loops, no separate output print here)

    # Display warnings and errors (always, even in summary_only)
    has_warnings = any(res.get("warnings") for res in results)
    has_errors = any(res.get("errors") for res in results if res.get("is_command", True))

    if has_errors:
        console.print("[bold red]Processing Errors:[/bold red]\n")
        for res in results:
            errors = res.get("errors", [])
            if errors:
                console.print(f"[red]-- {res['verb']} {res['object_type']} ({res.get('qualified_name', 'Unknown')}) --[/red]")
                for e in errors:
                    console.print(f"   [red]* {e}[/red]")
        console.print("\n")

    if has_warnings:
        console.print("[bold yellow]Processing Warnings:[/bold yellow]\n")
        for res in results:
            warnings = res.get("warnings", [])
            if warnings:
                console.print(f"[yellow]-- {res['verb']} {res['object_type']} ({res.get('qualified_name', 'Unknown')}) --[/yellow]")
                for w in warnings:
                    console.print(f"   [yellow]* {w}[/yellow]")
        console.print("\n")

    # Finally, print the summary table last
    console.print("\n")
    console.print(summary_table)
    console.print("\n")
    if directive == "process" and updated:
        # Re-assemble the file (using joined outputs)
        content_to_write = "\n".join(final_output)
        
        path, filename = os.path.split(input_file)
        new_filename = f"processed-{get_current_datetime_string()}-{filename}"
        
        if output_folder:
            new_file_path = os.path.abspath(os.path.expanduser(os.path.join(EGERIA_ROOT_PATH, EGERIA_OUTBOX_PATH, output_folder, new_filename)))
        else:
            new_file_path = os.path.abspath(os.path.expanduser(os.path.join(EGERIA_ROOT_PATH, EGERIA_OUTBOX_PATH, new_filename)))
            
        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)

        with open(new_file_path, 'w') as f2:
            f2.write(content_to_write)
            
        has_failures = any(res.get("status") == "failure" for res in results if res.get("is_command", True) and res.get("verb") != "Provenance")
        if has_failures:
            console.print(f"==> [bold yellow]COMPLETED WITH ERRORS[/bold yellow]: Output written to [blue]{new_file_path}[/blue]")
        else:
            console.print(f"==> [bold green]SUCCESS[/bold green]: Output written to [blue]{new_file_path}[/blue]")
    elif directive == "process":
        console.print("[yellow]No updates detected. New File not created.[/yellow]")

    # Restore the original _async_make_request if we monkey-patched it
    if _orig_make_request is not None:
        from pyegeria.core._base_server_client import BaseServerClient
        BaseServerClient._async_make_request = _orig_make_request
        console.print(
            "\n[bold yellow][DEBUG] Request debug mode DISABLED — Egeria API request logging stopped.[/bold yellow]"
        )

    console.print(f"\n[bold green]v2: Processing complete for '{input_file}'[/bold green]")
    logger.info("v2: Processing complete")


@logger.catch
def process_md_file(input_file: str, output_folder: str, directive: str, server: str, url: str, userid: str,
                          user_pass: str, parse_summary: str = "none",
                          attribute_logs: str = "debug", usage_level: str = None,
                          summary_only: bool = False, debug: bool = False) -> None:
    """
    Process a markdown file by parsing and executing Dr. Egeria md_commands. Write output to a new file.

    This always uses the v2 async engine. The legacy v1 engine has been removed.
    """
    if usage_level:
        set_usage_level(usage_level)
    client = EgeriaTech(server, url, user_id=userid)
    client.create_egeria_bearer_token(userid, user_pass)
    asyncio.run(process_md_file_v2(input_file, output_folder, directive, client, parse_summary, attribute_logs,
                                   usage_level, summary_only, debug=debug))

if __name__ == "__main__":
    import argparse
    import asyncio
    parser = argparse.ArgumentParser(description="Process Dr. Egeria Markdown files using v2.")
    parser.add_argument("--input-file", required=True, help="Input markdown file name (in Inbox)")
    parser.add_argument("--output-folder", default="", help="Optional output subfolder (in Outbox)")
    parser.add_argument("--directive", default="validate",
                        choices=["display", "validate", "process"],
                        help="Action to perform (default: validate). Overridden by --validate or --process.")
    parser.add_argument("--validate", dest="do_validate", action="store_true",
                        help="Shortcut: validate without making changes (overrides --directive)")
    parser.add_argument("--process", dest="do_process", action="store_true",
                        help="Shortcut: execute all commands and write to Egeria (overrides --directive)")
    parser.add_argument("--advanced", action="store_true", help="Use Advanced usage level (default: Basic)")
    parser.add_argument("--summary-only", action="store_true", help="Only display the summary table and errors/warnings")
    parser.add_argument("--debug", action="store_true", help="Print each Egeria API request URL and body to the console")

    args = parser.parse_args()

    # Resolve directive: explicit shortcut flags take priority
    directive = args.directive
    if args.do_process:
        directive = "process"
    elif args.do_validate:
        directive = "validate"

    # Run the async v2 processor
    user = os.environ.get("EGERIA_USER", "erinoverview")
    password = os.environ.get("EGERIA_USER_PASSWORD", "secret")
    client = EgeriaTech(settings.Environment.egeria_view_server, settings.Environment.egeria_view_server_url, user_id=user)
    client.create_egeria_bearer_token(user, password)

    asyncio.run(
        process_md_file_v2(
            args.input_file,
            args.output_folder,
            directive,
            client,
            usage_level="Advanced" if args.advanced else "Basic",
            summary_only=args.summary_only,
            debug=args.debug,
        )
    )
