"""
Processor for glossary entities.
"""

from typing import Dict, Optional, Tuple

from rich import print
from rich.markdown import Markdown

from pyegeria._globals import NO_GLOSSARIES_FOUND
from pyegeria.glossary_manager_omvs import GlossaryManager

from .base_processor import EntityProcessor
from .constants import ERROR, INFO, WARNING, pre_command


class GlossaryProcessor(EntityProcessor):
    """Processor for glossary entities."""
    
    def __init__(self, client: GlossaryManager, element_dictionary: Dict[str, Dict[str, str]]):
        """
        Initialize the glossary processor.
        
        Args:
            client: The GlossaryManager client
            element_dictionary: Dictionary to store entity information
        """
        super().__init__(client, element_dictionary)
    
    def validate(self, obj_action: str, glossary_name: str, language: str, 
                description: str, usage: str, q_name: str = None) -> Tuple[bool, bool, Optional[str], Optional[str]]:
        """
        Validate a glossary command.
        
        Args:
            obj_action: The action (Create or Update)
            glossary_name: The glossary name
            language: The language
            description: The description
            usage: The usage
            q_name: The qualified name (for Update)
            
        Returns:
            Tuple of (is_valid, exists, known_guid, known_q_name)
        """
        valid = True
        msg = ""
        known_glossary_guid = None
        known_q_name = None

        glossary_details = self.client.get_glossaries_by_name(glossary_name)
        if glossary_details == NO_GLOSSARIES_FOUND:
            glossary_exists = False
        else:
            glossary_exists = True

        if glossary_name is None:
            msg = f"* {ERROR}Glossary name is missing\n"
            valid = False
        if language is None:
            msg += f"* {ERROR}Language is missing\n"
            valid = False
        if description is None:
            msg += f"* {INFO}Description is missing\n"

        if len(glossary_details) > 1 and glossary_exists:
            msg += f"* {ERROR}More than one glossary with name {glossary_name} found\n"
            valid = False
        if len(glossary_details) == 1:
            known_glossary_guid = glossary_details[0]['elementHeader'].get('guid', None)
            known_q_name = glossary_details[0]['glossaryProperties'].get('qualifiedName', None).strip()

        if obj_action == "Update":
            if not glossary_exists:
                msg += f"* {ERROR}Glossary {glossary_name} does not exist\n"
                valid = False

            if q_name is None:
                msg += f"* {INFO}Qualified Name is missing => can use known qualified name of {known_q_name}\n"
                valid = True
            elif q_name != known_q_name:
                msg += (
                    f"* {ERROR}Glossary `{glossary_name}` qualifiedName mismatch between {q_name} and {known_q_name}\n")
                valid = False
            if valid:
                msg += f"* -->Glossary `{glossary_name}` exists and can be updated\n"
                self.element_dictionary[known_q_name] = {'display_name': glossary_name, 'guid': known_glossary_guid}
            else:
                msg += f"* --> validation failed\n"

            print(Markdown(msg))
            return valid, glossary_exists, known_glossary_guid, known_q_name

        elif obj_action == "Create":
            if glossary_exists:
                msg += f"{ERROR}Glossary {glossary_name} already exists\n"

            elif valid:
                msg += f"-->It is valid to create Glossary \'{glossary_name}\'\n"
                expected_q_name = self.client.__create_qualified_name__('Glossary', glossary_name)
                self.element_dictionary[expected_q_name] = {'display_name': glossary_name}

            print(Markdown(msg))
            return valid, glossary_exists, known_glossary_guid, known_q_name
    
    def process(self, txt: str, directive: str = "display") -> Optional[str]:
        """
        Process a glossary command.
        
        Args:
            txt: The markdown text containing the command
            directive: The processing directive (display, validate, or process)
            
        Returns:
            Updated markdown text or None
        """
        command = self.extract_command(txt)
        object_type = command.split(' ')[1].strip()
        object_action = command.split(' ')[0].strip()

        glossary_name = self.extract_attribute(txt, ['Glossary Name'])
        print(Markdown(f"{pre_command} `{command}` for glossary: `\'{glossary_name}\'` with directive: `{directive}` "))
        language = self.extract_attribute(txt, ['Language'])
        description = self.extract_attribute(txt, ['Description'])
        usage = self.extract_attribute(txt, ['Usage'])

        glossary_display = (f"\n* Command: {command}\n\t* Glossary Name: {glossary_name}\n\t"
                        f"* Language: {language}\n\t* Description:\n{description}\n"
                        f"* Usage: {usage}\n")

        if object_action == 'Update':
            q_name = self.extract_attribute(txt, ['Qualified Name'])
            guid = self.extract_attribute(txt, ['GUID', 'guid', 'Guid'])
            glossary_display += f"* Qualified Name: {q_name}\n\t* GUID: {guid}\n\n"
        else:
            q_name = None
            guid = None

        if directive == "display":
            print(Markdown(glossary_display))
            return None

        elif directive == "validate":
            is_valid, exists, known_guid, known_q_name = self.validate(
                object_action, glossary_name, language, description, usage, q_name)
            valid = is_valid if is_valid else None
            return valid

        elif directive == "process":
            is_valid, exists, known_guid, known_q_name = self.validate(
                object_action, glossary_name, language, description, usage, q_name)
            if not is_valid:
                return None
                
            if object_action == "Update":
                if not exists:
                    print(
                        f"\n{ERROR}Glossary {glossary_name} does not exist! Updating result document with Create command\n")
                    return self.update_a_command(txt, command, object_type, known_q_name, known_guid)

                body = {
                    "class": "ReferenceableRequestBody", "elementProperties": {
                        "class": "GlossaryProperties", "qualifiedName": known_q_name, "description": description,
                        "language": language, "usage": usage
                        }
                    }
                self.client.update_glossary(known_guid, body)
                print(f"\n-->Updated Glossary {glossary_name} with GUID {known_guid}")
                self.element_dictionary[known_q_name] = {
                    'guid': known_guid, 'display_name': glossary_name
                    }
                return self.client.get_glossary_by_guid(known_guid, output_format='MD')
                
            elif object_action == "Create":
                glossary_guid = None

                if exists:
                    print(f"\nGlossary {glossary_name} already exists and result document updated\n")
                    return self.update_a_command(txt, command, object_type, known_q_name, known_guid)
                else:
                    glossary_guid = self.client.create_glossary(glossary_name, description, language, usage)
                    glossary = self.client.get_glossary_by_guid(glossary_guid)
                    if glossary == NO_GLOSSARIES_FOUND:
                        print(f"{ERROR}Just created with GUID {glossary_guid} but Glossary not found\n")
                        return None
                    qualified_name = glossary['glossaryProperties']["qualifiedName"]
                    self.element_dictionary[qualified_name] = {
                        'guid': glossary_guid, 'display_name': glossary_name
                        }
                    return self.client.get_glossary_by_guid(glossary_guid, output_format = 'MD')