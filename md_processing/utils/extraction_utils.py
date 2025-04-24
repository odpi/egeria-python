"""
This file contains functions for extracting data from text for Egeria Markdown processing
"""
import re

from md_processing.utils.common_utils import INFO

def extract_command_plus(block: str) -> tuple[str, str, str] | None:
    """
    Extracts a multi-word object and its associated action from the given block of text.

    This function searches for a pattern in the format of `#...##` or `#...\n`
    inside the provided string `block`. The matched pattern is split into
    two parts: the action and the object type. The action is expected to
    be the first part, while the rest is treated as the object type. If
    no match is found, the function returns None.

    Lines beginning with '>' are ignored.

    Args:
        block: A string containing the block of text to search for the
            command and action.

    Returns:
        A tuple containing the command, the object type and the object action if a
        match is found. Otherwise, returns None.
    """
    # Filter out lines beginning with '>'
    filtered_lines = [line for line in block.split('\n') if not line.strip().startswith('>')]
    filtered_block = '\n'.join(filtered_lines)

    match = re.search(r"#(.*?)(?:##|\n|$)", filtered_block)  # Using a non capturing group
    if match:
        clean_match = match.group(1).strip()
        if ' ' in clean_match:
            parts = clean_match.split(' ')
            object_action = parts[0].strip()
            # Join the rest of the parts to allow object_type to be one or two words
            object_type = ' '.join(parts[1:]).strip()
        else:
            object_type = clean_match.split(' ')[1].strip()
            object_action = clean_match.split(' ')[0].strip()

        return clean_match, object_type, object_action
    return None


def extract_command(block: str) -> str | None:
    """
    Extracts a command from a block of text that is contained between a single hash ('#') and
    either a double hash ('##'), a newline character, or the end of the string.

    The function searches for a specific pattern within the block of text and extracts the
    content that appears immediately after a single hash ('#'). Ensures that the extracted
    content is appropriately trimmed of leading or trailing whitespace, if present.

    Args:
        block: A string representing the block of text to process. Contains the content
            in which the command and delimiters are expected to be present.

    Returns:
        The extracted command as a string if a match is found, otherwise None.
    """
    match = re.search(r"#(.*?)(?:##|\n|$)", block)  # Using a non capturing group
    if match:
        return match.group(1).strip()
    return None


def extract_attribute(text: str, labels: list[str]) -> str | None:
    """
        Extracts the attribute value from a string.

        Args:
            text: The input string.
            labels: List of equivalent labels to search for

        Returns:
            The value of the attribute, or None if not found.

        Note:
            Lines beginning with '>' are ignored.
        """
    # Iterate over the list of labels
    for label in labels:
        # Construct pattern for the current label
        pattern = rf"## {re.escape(label)}\n(.*?)(?:#|___|>|$)"  # modified from --- to enable embedded tables
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # Extract matched text
            matched_text = match.group(1).strip()

            # Filter out lines beginning with '>'
            filtered_lines = [line for line in matched_text.split('\n') if not line.strip().startswith('>')]
            filtered_text = '\n'.join(filtered_lines)

            # Replace consecutive \n with a single \n
            extracted_text = re.sub(r'\n+', '\n', filtered_text)
            if not extracted_text.isspace() and extracted_text:
                return extracted_text  # Return the cleaned text - I removed the title casing

    return None


def process_simple_attribute(txt: str, labels: list[str], if_missing: str = INFO) -> str | None:
    """
    Processes a simple attribute from a string.

    Args:
        txt: The input string.
        labels: List of equivalent labels to search for
        if_missing: The message level to use if the attribute is missing.

    Returns:
        The value of the attribute, or None if not found.
    """
    from md_processing.utils.common_utils import debug_level, print_msg

    attribute = extract_attribute(txt, labels)
    if attribute is None and if_missing:
        msg = f"No {labels[0]} found"
        print_msg(if_missing, msg, debug_level)
    return attribute


def process_name_list(egeria_client, element_type: str, txt: str, element_labels: list[str]) -> tuple[list, list, bool, bool]:
    """
    Processes a list of names from a string.

    Args:
        egeria_client: The Egeria client to use for validation.
        element_type: The type of element to process.
        txt: The input string.
        element_labels: List of equivalent labels to search for

    Returns:
        A tuple containing:
        - A list of element names
        - A list of element qualified names
        - A boolean indicating if all elements are valid
        - A boolean indicating if any elements exist
    """
    from md_processing.utils.common_utils import debug_level, print_msg
    from md_processing.utils.validation_utils import get_element_by_name

    element_names = []
    element_q_names = []
    all_valid = True
    any_exist = False

    # Get the list of element names
    element_list = process_simple_attribute(txt, element_labels)
    if element_list:
        # Split the list by commas or newlines
        element_names = list(filter(None, re.split(r'[,\n]+', element_list.strip())))
        
        # Validate each element
        for element_name in element_names:
            element_name = element_name.strip()
            if element_name:
                element = get_element_by_name(egeria_client, element_type, element_name)
                if element:
                    any_exist = True
                    element_q_name = element.get('qualifiedName', None)
                    if element_q_name:
                        element_q_names.append(element_q_name)
                    else:
                        all_valid = False
                        msg = f"Element {element_name} has no qualified name"
                        print_msg("ERROR", msg, debug_level)
                else:
                    all_valid = False
                    msg = f"Element {element_name} not found"
                    print_msg("ERROR", msg, debug_level)

    return element_names, element_q_names, all_valid, any_exist