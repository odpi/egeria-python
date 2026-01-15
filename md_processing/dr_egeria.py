"""
This is an ongoing experiment in parsing and playing with Freddie docs
"""
import os
import sys
from datetime import datetime

from loguru import logger
from pydantic import ValidationError

from rich import print
from rich.console import Console

from md_processing import (extract_command, process_provenance_command, get_current_datetime_string, command_list)

from md_processing.command_mapping import setup_dispatcher

from pyegeria import EgeriaTech, PyegeriaException, print_basic_exception, print_validation_error

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get("EGERIA_VIEW_SERVER_URL", "https://localhost:9443")
EGERIA_INTEGRATION_DAEMON = os.environ.get("EGERIA_INTEGRATION_DAEMON", "integration-daemon")
EGERIA_INTEGRATION_DAEMON_URL = os.environ.get("EGERIA_INTEGRATION_DAEMON_URL", "https://localhost:9443")
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_WIDTH = os.environ.get("EGERIA_WIDTH", 220)
EGERIA_JUPYTER = os.environ.get("EGERIA_JUPYTER", False)
EGERIA_HOME_GLOSSARY_GUID = os.environ.get("EGERIA_HOME_GLOSSARY_GUID", None)
EGERIA_GLOSSARY_PATH = os.environ.get("EGERIA_GLOSSARY_PATH", None)
EGERIA_ROOT_PATH = os.environ.get("EGERIA_ROOT_PATH", "../../")
EGERIA_INBOX_PATH = os.environ.get("EGERIA_INBOX_PATH", "md_processing/dr_egeria_inbox")
EGERIA_OUTBOX_PATH = os.environ.get("EGERIA_OUTBOX_PATH", "md_processing/dr_egeria_outbox")

log_format = "{time} | {level} | {function} | {line} | {message} | {extra}"
logger.remove()
logger.add(sys.stderr, level="ERROR", format=log_format, colorize=True)
logger.add("debug_log.log", rotation="1 day", retention="1 week", compression="zip", level="INFO", format=log_format,
           colorize=True)

@logger.catch
def process_md_file(input_file: str, output_folder:str, directive: str, server: str, url: str, userid: str,
                          user_pass: str ) -> None:
    """
    Process a markdown file by parsing and executing Dr. Egeria md_commands. Write output to a new file.
    """

    cmd_list = command_list
    console = Console(width=int(EGERIA_WIDTH))
    client = EgeriaTech(server, url, user_id=userid)
    token = client.create_egeria_bearer_token(userid, user_pass)
    
    # Initialize the dispatcher
    dispatcher = setup_dispatcher()

    updated = False
    full_file_path = os.path.join(EGERIA_ROOT_PATH, EGERIA_INBOX_PATH, input_file)
    logger.info("\n\n====================================================\n\n")
    logger.info(f"Processing Markdown File: {full_file_path}")
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
    except (Exception):
        console.print_exception(show_locals=True)
