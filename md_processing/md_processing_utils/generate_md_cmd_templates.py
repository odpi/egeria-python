"""
This file contains general utility functions for processing Egeria Markdown
"""
import os
import sys
import io
import copy
import argparse
from collections import defaultdict
from loguru import logger
from rich import print
from rich.console import Console

from md_processing.md_processing_utils.md_processing_constants import (load_commands,
                                                                       COMMAND_DEFINITIONS, add_default_link_attributes,
                                                                       add_default_upsert_attributes)

from pyegeria.core._globals import DEBUG_LEVEL


# Constants
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))
EGERIA_ROOT_PATH = os.environ.get("EGERIA_ROOT_PATH", ".")
EGERIA_INBOX_PATH = os.environ.get("EGERIA_INBOX_PATH", ".")

console = Console(width=EGERIA_WIDTH)

debug_level = DEBUG_LEVEL
global COMMAND_DEFINITIONS

# ---------------------------------------------------------------------------
# Level ordering and visibility
# ---------------------------------------------------------------------------

LEVEL_ORDER = ["Common", "Domain", "Basic", "Advanced", "Expert", "Invisible"]


def _level_visible(attr_level: str, usage_level: str = "Advanced") -> bool:
    """Return True if attr_level should be rendered at the given usage_level ceiling.

    'Invisible' and 'Expert' are never rendered in templates.
    Unknown level values default to visible so nothing is accidentally hidden.
    """
    attr_level = (attr_level or "Basic").strip()
    if attr_level in ("Invisible", "Expert"):
        return False
    try:
        return LEVEL_ORDER.index(attr_level) <= LEVEL_ORDER.index(usage_level)
    except ValueError:
        return True  # unknown value — show rather than hide


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

def _write_attr_block(out: io.StringIO, key: str, value: dict) -> None:
    """Write a single ## attribute block into the StringIO buffer."""
    out.write(f"\n## {key}\n")
    out.write(f">\t**Input Required**: {value.get('input_required', 'false')}\n\n")
    out.write(f">\t**Description**: {value.get('description', '')}\n\n")

    labels = value.get("attr_labels") or ""
    if labels.strip():
        out.write(f">\t**Alternative Labels**: {labels}\n\n")

    valid_values = value.get("valid_values") or ""
    if isinstance(valid_values, str):
        vv = valid_values.strip()
    elif isinstance(valid_values, list):
        vv = ",".join(valid_values)
    else:
        vv = valid_values

    if vv:
        out.write(f">\t**Valid Values**: {vv}\n\n")

    default_value = value.get("default_value") or ""
    if default_value.strip():
        out.write(f">\t**Default Value**: {default_value}\n\n")


def _print_attr(key: str, value: dict) -> None:
    """Mirror of _write_attr_block for console output."""
    print(f"\n### {key}")
    print(f">\tInput Required: {value.get('input_required', 'false')}")
    print(f">\tDescription: {value.get('description', '')}")
    labels = value.get("attr_labels") or ""
    if labels.strip():
        print(f">\tAlternative Labels: {labels}")
    valid_values = value.get("valid_values") or ""
    if isinstance(valid_values, str):
        vv = valid_values.strip()
    elif isinstance(valid_values, list):
        vv = ",".join(valid_values)
    else:
        vv = valid_values

    if vv:
        print(f">\tValid Values: {vv}")

    default_value = value.get("default_value") or ""
    if default_value.strip():
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
    parser.add_argument("--advanced", action="store_true", default=False, help="Enable advanced level attributes")
    parser.add_argument("--family", type=str, default=None, help="Generate for a specific family")
    args = parser.parse_args()

    commands = COMMAND_DEFINITIONS["Command Specifications"]

    # Create base output directory if it doesn't exist
    base_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "family_docs")
    os.makedirs(base_output_dir, exist_ok=True)

    # -----------------------------------------------------------------------
    # Group commands by family — include any command with a visible level
    # -----------------------------------------------------------------------
    families: dict[str, list[str]] = {}
    usage_level = "Advanced" if args.advanced else "Basic"
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

            # Build full attribute list (command-specific + injected defaults)
            distinguished_attributes = values['Attributes']
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
                for key, value in attribute.items():
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
            command_output.write(f"# {command}\n>\t{command_description}\n")
            print(f"\n# {command}\n>\t{command_description}")

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

                for key, value in attr_list:
                    _write_attr_block(command_output, key, value)
                    _print_attr(key, value)

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