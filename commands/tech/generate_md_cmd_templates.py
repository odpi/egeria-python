"""
This file contains general utility functions for processing Egeria Markdown
"""
import os
import sys
import io
import copy
import argparse
from typing import Optional, List
from collections import defaultdict
from loguru import logger
from rich import print
from rich.console import Console

from md_processing.md_processing_utils.md_processing_constants import (load_commands,
                                                                       COMMAND_DEFINITIONS, add_default_link_attributes,
                                                                       add_default_upsert_attributes)

from pyegeria import ServerClient, EgeriaTech
from pyegeria.core.config import get_app_config


# Load application configuration
config = get_app_config()
env = config.Environment
user_profile = config.User_Profile

EGERIA_WIDTH = env.console_width
EGERIA_ROOT_PATH = env.pyegeria_root
EGERIA_INBOX_PATH = env.egeria_inbox

console = Console(width=EGERIA_WIDTH)

debug_level = config.Debug.debug_mode
global COMMAND_DEFINITIONS

# ---------------------------------------------------------------------------
# Level ordering and visibility
# ---------------------------------------------------------------------------

LEVEL_ORDER = ["Common", "Domain", "Basic", "Advanced", "Expert", "Invisible"]


def _level_visible(attr_level: str, usage_level: str = "Advanced") -> bool:
    """Return True if attr_level should be rendered at the given usage_level ceiling.

    'Invisible' is never rendered in templates.
    'Expert' and 'Advanced' are only rendered when usage_level is 'Advanced'.
    """
    attr_level = (attr_level or "Basic").strip()
    if attr_level == "Invisible":
        return False

    # User's definition:
    # Basic usage: Common, Domain, Basic
    # Advanced usage: Common, Domain, Basic, Advanced, Expert
    if usage_level == "Basic":
        return attr_level in ("Common", "Domain", "Basic")

    # Advanced usage level (or any other) defaults to everything except Invisible
    return True


load_commands('commands.json')

log_format = "D {time} | {level} | {function} | {line} | {message} | {extra}"
logger.remove()
logger.add(sys.stderr, level="INFO", format=log_format, colorize=True)
full_file_path = os.path.join(EGERIA_ROOT_PATH, EGERIA_INBOX_PATH, "data_designer_debug.log")
# logger.add(full_file_path, rotation="1 day", retention="1 week", compression="zip", level="TRACE", format=log_format,
#            colorize=True)
logger.add("debug_log", rotation="1 day", retention="1 week", compression="zip", level="TRACE", format=log_format,
           colorize=True)


# ---------------------------------------------------------------------------
# Attribute block writer (shared by file output and console output)
# ---------------------------------------------------------------------------

def _write_attr_block(out: io.StringIO, key: str, value: dict, client: Optional[ServerClient] = None) -> None:
    """Write a single ## attribute block into the StringIO buffer."""
    out.write(f"\n## {key}\n")
    out.write(f">\t**Input Required**: {value.get('input_required', 'false')}\n\n")
    
    attr_type = value.get("data_type") or value.get("style") or ""
    if attr_type:
        out.write(f">\t**Attribute Type**: {attr_type}\n\n")
        
    out.write(f">\t**Description**: {value.get('description', '')}\n\n")

    labels = value.get("attr_labels") or ""
    if labels.strip():
        out.write(f">\t**Alternative Labels**: {labels}\n\n")

    valid_values = value.get("valid_values") or ""
    prop_name = value.get("property_name")
    
    dynamic_default = None
    if prop_name and client:
        try:
            valid_elements = client.get_valid_metadata_values(prop_name)
            if valid_elements:
                if not valid_values:
                    valid_values = "; ".join([el.get("preferredValue") for el in valid_elements if el.get("preferredValue")])
                
                # Look for dynamic default
                for el in valid_elements:
                    if el.get("additionalProperties", {}).get("isDefaultValue") == "true":
                        dynamic_default = el.get("preferredValue")
                        break
        except Exception:
            pass

    if isinstance(valid_values, str):
        vv = valid_values.strip()
    elif isinstance(valid_values, list):
        vv = ",".join(valid_values)
    else:
        vv = valid_values

    if vv:
        out.write(f">\t**Valid Values**: {vv}\n\n")

    default_value = value.get("default_value") or dynamic_default or ""
    if str(default_value).strip():
        out.write(f">\t**Default Value**: {default_value}\n\n")


def _print_attr(key: str, value: dict, client: Optional[ServerClient] = None) -> None:
    """Mirror of _write_attr_block for console output."""
    print(f"\n## {key}")
    print(f">\tInput Required: {value.get('input_required', 'false')}")
    
    attr_type = value.get("data_type") or value.get("style") or ""
    if attr_type:
        print(f">\tAttribute Type: {attr_type}")
        
    print(f">\tDescription: {value.get('description', '')}")
    labels = value.get("attr_labels") or ""
    if labels.strip():
        print(f">\tAlternative Labels: {labels}")
        
    valid_values = value.get("valid_values") or ""
    prop_name = value.get("property_name")
    
    dynamic_default = None
    if prop_name and client:
        try:
            valid_elements = client.get_valid_metadata_values(prop_name)
            if valid_elements:
                if not valid_values:
                    valid_values = "; ".join([el.get("preferredValue") for el in valid_elements if el.get("preferredValue")])
                
                # Look for dynamic default
                for el in valid_elements:
                    if el.get("additionalProperties", {}).get("isDefaultValue") == "true":
                        dynamic_default = el.get("preferredValue")
                        break
        except Exception:
            pass

    if isinstance(valid_values, str):
        vv = valid_values.strip()
    elif isinstance(valid_values, list):
        vv = ",".join(valid_values)
    else:
        vv = valid_values

    if vv:
        print(f">\tValid Values: {vv}")

    default_value = value.get("default_value") or dynamic_default or ""
    if str(default_value).strip():
        print(f">\tDefault Value: {default_value}")


@logger.catch
def main():
    """Generate markdown command templates organised by family.

    Each command file is structured as:

        # <Command Name>
        > <description>

        # Required
        ## <attr>  ...   (input_required=true, any visible level)

        # Common Properties
        ## <attr>  ...   (level=Common, optional)

        # <DisplayName> Properties
        ## <attr>  ...   (level=Domain, optional; heading uses command display_name)

        # Additional Properties
        ## <attr>  ...   (level=Basic, optional)

        # Advanced Properties
        ## <attr>  ...   (level=Advanced, optional)

    Sections with no attributes are omitted entirely.
    Link commands only ever produce Required and Advanced sections from defaults;
    their Domain section is populated once Tinderbox re-exports level=Domain on
    command-specific attributes.
    """
    parser = argparse.ArgumentParser(description="Generate markdown command templates organised by family.")
    parser.add_argument("--usage-level", dest="usage_level", choices=["Basic", "Advanced"], default=None,
                        help="Egeria usage level (Basic or Advanced)")
    parser.add_argument("--advanced", action="store_true", default=False, help="Enable advanced level attributes (deprecated: use --usage-level)")
    parser.add_argument("--family", type=str, default=None, help="Generate for a specific family")
    parser.add_argument("--server", default=env.egeria_view_server, help="Egeria view server name")
    parser.add_argument("--url", default=env.egeria_view_server_url, help="Egeria platform URL")
    parser.add_argument("--userid", default=user_profile.user_name, help="Egeria user ID")
    parser.add_argument("--pass", dest="user_pass", default=user_profile.user_pwd, help="Egeria user password")
    args = parser.parse_args()

    client = None
    if args.url:
        try:
            client = ServerClient(args.server, args.url, user_id=args.userid)
            client.create_egeria_bearer_token(args.userid, args.user_pass)
            logger.info(f"Connected to Egeria at {args.url} for dynamic valid values")
        except Exception as e:
            logger.warning(f"Could not connect to Egeria: {e}. Falling back to static values.")

    commands = COMMAND_DEFINITIONS["Command Specifications"]

    # Determine usage level
    usage_level = args.usage_level
    if not usage_level:
        usage_level = "Advanced" if args.advanced else (os.environ.get("EGERIA_USAGE_LEVEL") or user_profile.egeria_usage_level or "Advanced")
    
    # Create base output directory if it doesn't exist
    usage_folder = usage_level.lower()
    base_output_dir = os.path.join(EGERIA_ROOT_PATH, "templates", usage_folder)
    os.makedirs(base_output_dir, exist_ok=True)

    # -----------------------------------------------------------------------
    # Group commands by family — include any command with a visible level
    # -----------------------------------------------------------------------
    families: dict[str, list[str]] = {}
    for command, values in commands.items():
        if command == "exported":
            continue
        cmd_level = values.get("level", "")
        if not _level_visible(cmd_level, usage_level=usage_level):
            continue
        family = values.get("family", "Other")

        if args.family and family != args.family:
            continue

        families.setdefault(family, []).append(command)

    # -----------------------------------------------------------------------
    # Process each family
    # -----------------------------------------------------------------------
    for family, command_list in sorted(families.items()):

        family_dir = os.path.join(base_output_dir, family)
        os.makedirs(family_dir, exist_ok=True)
        print(f"\n# Family: {family}\n")

        for command in sorted(command_list):
            values = commands[command]
            command_description = values.get("description", "")
            command_verb        = values.get("verb", "")
            # display_name drives the Domain section heading, e.g. "Data Field Properties"
            display_name        = values.get("display_name") or command
            alternate_names_raw = values.get("alternate_names")
            if isinstance(alternate_names_raw, list):
                alternate_names = ", ".join(alternate_names_raw)
            else:
                alternate_names = alternate_names_raw or ""

            # Build full attribute list (command-specific + injected defaults)
            distinguished_attributes = values['Attributes']
            alternate_names = values.get("alternate_names") or ""

            if command_verb == "Link":
                attributes = add_default_link_attributes(copy.deepcopy(distinguished_attributes))
            else:
                # Create, Update, and anything else uses upsert defaults
                attributes = add_default_upsert_attributes(copy.deepcopy(distinguished_attributes))

            # -----------------------------------------------------------
            # Bucket attributes into sections.
            # Required attrs (input_required=True) are pulled out first
            # regardless of their level, then optional attrs are grouped
            # by level.  Within each bucket, order follows the attribute
            # list so Tinderbox export ordering is preserved.
            #
            # required_keys prevents an attr appearing in both Required
            # and a level section when input_required=True and the attr
            # also has a Common/Domain level set.
            # -----------------------------------------------------------
            required_attrs: list[tuple[str, dict]] = []
            sectioned_attrs: dict[str, list[tuple[str, dict]]] = defaultdict(list)
            required_keys: set[str] = set()

            for attribute in attributes:
                if "name" in attribute:
                    key = attribute["name"]
                    value = attribute
                else:
                    # Fallback for old single-key dict structure
                    if not attribute:
                        continue
                    key, value = list(attribute.items())[0]

                attr_level = (value.get("level") or "Basic").strip()

                if not _level_visible(attr_level, usage_level=usage_level):
                    continue

                if value.get("input_required", False) is True:
                    if key not in required_keys:
                        required_attrs.append((key, value))
                        required_keys.add(key)
                else:
                    sectioned_attrs[attr_level].append((key, value))

            # -----------------------------------------------------------
            # Build the output buffer
            # -----------------------------------------------------------
            command_output = io.StringIO()
            command_output.write(f"# {command}\n")
            if command_description:
                command_output.write(f"> {command_description}\n")
            if alternate_names:
                command_output.write(f">\n>\t**Alternative Names**: {alternate_names}\n")

            print(f"\n# {command}")
            if command_description:
                print(f"> {command_description}")
            if alternate_names:
                print(f">\n>\t**Alternative Names**: {alternate_names}")

            # Section order and labels.
            # The Domain section heading is personalised with display_name.
            section_plan = [
                ("_required_", "Required",                   required_attrs),
                ("Domain",     f"{display_name} Properties", sectioned_attrs.get("Domain",   [])),
                ("Common",     "Common Properties",          sectioned_attrs.get("Common",   [])),
                ("Basic",      "Additional Properties",      sectioned_attrs.get("Basic",    [])),
                ("Advanced",   "Advanced Properties",        sectioned_attrs.get("Advanced", [])),
            ]

            for _level_key, section_title, attr_list in section_plan:
                if not attr_list:
                    continue   # omit empty sections entirely

                # command_output.write(f"\n# {section_title}\n")
                # print(f"\n# {section_title}")

                for key, value in attr_list:
                    _write_attr_block(command_output, key, value, client=client)
                    _print_attr(key, value, client=client)

            # -----------------------------------------------------------
            # Save to file
            # -----------------------------------------------------------
            command_filename = command.replace(" ", "_").replace(":", "").replace("/", "_")
            command_file_path = os.path.join(family_dir, f"{command_filename}.md")

            with open(command_file_path, 'w') as f:
                f.write(command_output.getvalue())

            logger.info(f"Saved command documentation to {command_file_path}")
            print("\n___\n")


#

if __name__ == "__main__":
    main()