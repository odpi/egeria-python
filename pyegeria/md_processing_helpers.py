#
# from typing import List, Optional
#
# import os
# import re
#
# from rich import box, print
# from rich.console import Console
# from rich.markdown import Markdown
#
# from pyegeria import body_slimmer
# from pyegeria._globals import NO_TERMS_FOUND, NO_GLOSSARIES_FOUND, NO_TERMS_FOUND, NO_ELEMENTS_FOUND, NO_PROJECTS_FOUND, NO_CATEGORIES_FOUND
# from pyegeria.egeria_tech_client import EgeriaTech
# from pyegeria.md_processing_utils import extract_attribute, get_element_by_name, process_element_identifiers
# from pyegeria.project_manager_omvs import ProjectManager
# from pyegeria.glossary_manager_omvs import GlossaryManager
# ERROR = "ERROR-> "
# INFO = "INFO- "
# WARNING = "WARNING-> "
# pre_command = "\n---\n==> Processing object_action:"
#
#
#
# def process_q_name_list(egeria_client: EgeriaTech, element_type:str, txt:str )-> tuple[str | None,list | None,str | None,bool,bool]:
#     msg = ""
#     known_guid = None
#     valid = True
#     exists = False
#     elements = ""
#     new_element_list = []
#
#     elements_txt = extract_attribute(txt, [element_type])
#
#     if elements_txt is None:
#         msg += f"* {INFO}No {element_type}s found\n"
#
#     else:
#         element_list = re.split(r'[,\n]+', elements_txt)
#
#         for element in element_list:
#             element_el = element.strip()
#
#                 # Get the element using the generalized function
#             known_q_name, known_guid, status_msg, el_valid, el_exists = get_element_by_name(
#                 egeria_client, element_type,txt)
#             msg += status_msg
#             if exists and valid:
#                 elements = f"{element_el}, {elements}" # list of the input names
#                 new_element_list.append(known_q_name) # list of qualified names
#             valid = valid and el_valid
#             exists = exists and el_exists
#
#         if elements:
#             elements += "\n"
#             msg += f"* {INFO}Found {element_type}s: {elements}"
#         else:
#             msg += f"* {INFO}List contains one or more invalid elements.\n"
#         return elements,new_element_list, msg, valid, exists