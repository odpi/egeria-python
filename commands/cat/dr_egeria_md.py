"""
This is an ongoing experiment in parsing and playing with Freddie docs
"""
import os
import sys
from datetime import datetime

from loguru import logger

log_format = "{time} | {level} | {function} | {line} | {message} | {extra}"
logger.remove()
logger.add(sys.stderr, level="INFO", format=log_format, colorize=True)
logger.add("debug_log.log", rotation="1 day", retention="1 week", compression="zip", level="TRACE", format=log_format,
           colorize=True)
import click
from rich import print
from rich.console import Console
from md_processing.md_processing_utils.common_md_utils import setup_log

from md_processing import (extract_command, process_glossary_upsert_command, process_term_upsert_command,
                           process_category_upsert_command, process_provenance_command, get_current_datetime_string,
                           process_per_proj_upsert_command, command_list, process_blueprint_upsert_command,
                           process_solution_component_upsert_command, process_component_link_unlink_command,
                           process_term_list_command,
                           process_category_list_command, process_glossary_list_command, process_term_history_command,
                           process_glossary_structure_command, process_term_revision_history_command,
                           process_create_term_term_relationship_command, process_term_details_command,
                           process_information_supply_chain_upsert_command,
                           process_information_supply_chain_link_unlink_command, process_sol_arch_list_command,
                           process_digital_product_upsert_command, process_agreement_upsert_command,
                           process_collection_list_command, process_collection_upsert_command, process_link_agreement_item_command,
                           process_gov_definition_upsert_command, GOV_COM_LIST, GOV_LINK_LIST,
                           process_gov_def_link_detach_command, process_gov_definition_list_command,
                           process_gov_def_context_command, COLLECTIONS_LIST, SIMPLE_COLLECTIONS)
from md_processing.md_commands.data_designer_commands import (process_data_spec_upsert_command,
                                                              process_data_dict_upsert_command,
                                                              process_data_collection_list_command,
                                                              process_data_structure_list_command,
                                                              process_data_field_list_command,
                                                              process_data_class_list_command,
                                                              process_data_field_upsert_command,
                                                              process_data_structure_upsert_command,
                                                              process_data_class_upsert_command)
from pyegeria import EgeriaTech

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

setup_log()
@click.command("process_markdown_file", help="Process a markdown file and return the output as a string.")
@click.option("--input-file", help="Markdown file to process.", default="dr_egeria_intro_part1.md", required=True,
              prompt=False)
@click.option("--output-folder", help="Output folder.", default="", required=False)
@click.option("--directive", default="process", help="How to process the file",
              type=click.Choice(["display", "validate", "process"], case_sensitive=False), prompt=False, )
@click.option("--server", default=EGERIA_VIEW_SERVER, help="Egeria view server to use.")
@click.option("--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to")
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--user_pass", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@logger.catch
def process_markdown_file(input_file: str, output_folder:str, directive: str, server: str, url: str, userid: str,
                          user_pass: str, ) -> None:
    """
    Process a markdown file by parsing and executing Dr. Egeria md_commands. Write output to a new file.
    """

    cmd_list = command_list
    console = Console(width=int(EGERIA_WIDTH))
    client = EgeriaTech(server, url, user_id=userid)
    token = client.create_egeria_bearer_token(userid, user_pass)

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
                   f"{datetime.now().strftime("%Y-%m-%d %H:%M")}\n")
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

            elif potential_command in ["Create Glossary", "Update Glossary"]:
                result = process_glossary_upsert_command(client, current_block, directive)
            elif potential_command in ["Create Category", "Update Category"]:
                result = process_category_upsert_command(client, current_block, directive)
            elif potential_command in ["Create Term", "Update Term"]:
                result = process_term_upsert_command(client, current_block, directive)
            elif potential_command in ["Create Term-Term Relationship", "Update Term-Term Relationship"]:
                result = process_create_term_term_relationship_command(client, current_block, directive)
            elif potential_command in ["List Term History", "Term History"]:
                result = process_term_history_command(client, current_block, directive)
            elif potential_command in ["List Term Details"]:
                result = process_term_details_command(client, current_block, directive)
            elif potential_command in ["List Term Update History", "List Term Revision History"]:
                result = process_term_revision_history_command(client, current_block, directive)
            elif potential_command in ["List Terms", "List Glossary Terms"]:
                result = process_term_list_command(client, current_block, directive)
            elif potential_command in ["List Categories", "List Glossary Categories"]:
                result = process_category_list_command(client, current_block, directive)
            elif potential_command in ["List Glossary Structure"]:
                result = process_glossary_structure_command(client, current_block, directive)
            elif potential_command in ["List Glossaries"]:
                result = process_glossary_list_command(client, current_block, directive)
            elif potential_command in ["Create Personal Project", "Update Personal Project"]:
                result = process_per_proj_upsert_command(client, current_block, directive)
            elif potential_command in ["Create Blueprint", "Update Blueprint", "Create Solution Blueprint",
                                       "Update Solution Blueprint"]:
                result = process_blueprint_upsert_command(client, current_block, directive)
            elif potential_command in ["View Solution Blueprints", "View Blueprint", "View Solution Blueprint"]:
                result = process_sol_arch_list_command(client, current_block, "Solution Blueprints", directive)
            elif potential_command in ["View Solution Component", "View Solution Components"]:
                result = process_sol_arch_list_command(client, current_block, "Solution Components", directive)
            elif potential_command in ["View Solution Roles", "View Solution Role"]:
                result = process_sol_arch_list_command(client, current_block, "Solution Roles", directive)
            elif potential_command in ["View Information Supply Chain", "View Information Supply Chains"]:
                result = process_sol_arch_list_command(client, current_block, "Information Supply Chains", directive)
            elif potential_command in ["Create Solution Component", "Update Solution Component"]:
                result = process_solution_component_upsert_command(client, current_block, directive)
            elif potential_command in ["Link Solution Components", "Link Solution Component Peers", "Wire Solution Components",
                                       "Unlink Solution Components", "Detach Solution Components", "Detach Solution Component Peers"]:
                result = process_component_link_unlink_command(client, current_block, directive)
            elif potential_command in ["Create Information Supply Chain", "Update Information Supply Chain"]:
                result = process_information_supply_chain_upsert_command(client, current_block, directive)

            elif potential_command in ["Link Information Supply Chain Peers", "Link Information Supply Chains",
                                       "Link Supply Chains", "Unlink Information Supply Chain Peers",
                                       "Unlink Information Supply Chains", "Unlink Supply Chains"]:
                result = process_information_supply_chain_link_unlink_command(client, current_block, directive)

            elif potential_command in ["Create Data Spec", "Create Data Specification", "Update Data Spec",
                                       "Update Data Specification"]:
                result = process_data_spec_upsert_command(client, current_block, directive)
            elif potential_command in ["Create Data Dict", "Create Data Dictionary", "Update Data Spec",
                                       "Update Data Dictionary"]:
                result = process_data_dict_upsert_command(client, current_block, directive)
            elif potential_command in ["Create Data Field", "Update Data Field"]:
                result = process_data_field_upsert_command(client, current_block, directive)
            elif potential_command in ["Create Data Structure", "Update Data Structure"]:
                result = process_data_structure_upsert_command(client, current_block, directive)
            elif potential_command in ["Create Data Class", "Update Data Class"]:
                result = process_data_class_upsert_command(client, current_block, directive)
            elif potential_command in ["View Data Dictionaries", "View Data Dictionary", "View Data Specifications",
                                       "View Data Specs"]:
                result = process_data_collection_list_command(client, current_block, directive)
            elif potential_command in ["View Data Structures", "View Data Structure"]:
                result = process_data_structure_list_command(client, current_block, directive)
            elif potential_command in ["View Data Fields", "View Data Field"]:
                result = process_data_field_list_command(client, current_block, directive)
            elif potential_command in ["View Data Classes", "View Data Class"]:
                result = process_data_class_list_command(client, current_block, directive)
            elif potential_command in ["Create Digital Product", "Create Data Product","Update Digital Product", "Update Data Product"]:
                result = process_digital_product_upsert_command(client, current_block, directive)
            elif potential_command in ["Create Agreement", "Create Data Sharing Agreement", "Update Agreement", "Update Data Sharing Agreement"]:
                result = process_agreement_upsert_command(client, current_block, directive)
            elif potential_command in SIMPLE_COLLECTIONS:
                result = process_collection_upsert_command(client, current_block, directive)
            elif potential_command in GOV_COM_LIST:
                result = process_gov_definition_upsert_command(client, current_block, directive)
            elif potential_command in ['View Governance Definitions', 'List Governance Definitions',
                                       'View Gov Definitions', 'List Gov Definitions']:
                result = process_gov_definition_list_command(client, current_block, directive)
            elif potential_command in COLLECTIONS_LIST:
                result = process_collection_list_command(client, current_block, directive)



            else:
                # If object_action is not recognized, keep the block as-is
                result = None
                print(f"\n===> Unknown command: {potential_command}")
            # print(json.dumps(dr_egeria_state.get_element_dictionary(), indent=4))
            if result:
                if directive == "process":
                    updated = True
                    final_output.append(result)  # print(json.dumps(dr_egeria_state.get_element_dictionary(), indent=4))
                elif directive == "validate":
                    pass  # print(json.dumps(dr_egeria_state.get_element_dictionary(), indent=4))
            elif directive == "process":
                # Handle errors (skip this block but notify the user)
                print(f"\n==>\tErrors found while processing command: \'{potential_command}\'\n"
                      f"\tPlease correct and try again. \n")
                final_output.append(current_block)
                final_output.append('\n___\n')
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
        elif line.startswith("___"):
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
    final_output = "\n".join(final_output)

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
            click.echo(f"\n==> Output written to {new_file_path}")
        else:
            if directive != 'display':
                click.echo("\nNo updates detected. New File not created.")
                logger.error("===> Unknown Command? <===")

    except (Exception):
        console.print_exception(show_locals=True)


# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--server", help="Name of the server to display status for")
#     parser.add_argument("--url", help="URL Platform to connect to")
#     parser.add_argument("--userid", help="User Id")
#     parser.add_argument("--password", help="User Password")
#     parser.add_argument("--time_out", help="Time Out")
#
#     args = parser.parse_args()
#
#     server = args.server if args.server is not None else EGERIA_VIEW_SERVER
#     url = args.url if args.url is not None else EGERIA_PLATFORM_URL
#     userid = args.userid if args.userid is not None else EGERIA_USER
#     user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
#     time_out = args.time_out if args.time_out is not None else 60
#     try:
#         input_file = Prompt.ask("Markdown File name to process:", default="")
#         directive = Prompt.ask("Processing Directive:", choices=[ "display", "validate", "process"],
#         default="validate")
#
#         process_markdown_file(input_file, directive, server, url, userid, user_pass)
#     except KeyboardInterrupt:
#         pass
#
#
# if __name__ == "__main__":
#     main()

if __name__ == "__main__":
    process_markdown_file()