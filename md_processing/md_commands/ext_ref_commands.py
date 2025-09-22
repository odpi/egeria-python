"""
This file contains Dr. Egeria commands for working with External References.
"""

import json
from typing import Optional

from loguru import logger
from pydantic import ValidationError
from rich import print
from rich.markdown import Markdown

from md_processing.md_processing_utils.common_md_proc_utils import (parse_upsert_command, parse_view_command,
                                                                    )
from md_processing.md_processing_utils.common_md_utils import (set_update_body, set_element_prop_body,
                                                               set_delete_request_body, set_create_body,
                                                               set_rel_request_body_for_type,
                                                               set_rel_prop_body, )
from md_processing.md_processing_utils.common_md_utils import (update_element_dictionary,
                                                               )
from md_processing.md_processing_utils.extraction_utils import (extract_command_plus, update_a_command)

from pyegeria import PyegeriaException, print_basic_exception, print_validation_error
from pyegeria import body_slimmer
from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.utils import make_format_set_name_from_type


# EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "170"))
# console = Console(width=EGERIA_WIDTH)



def process_external_reference_upsert_command(egeria_client: EgeriaTech, txt: str,
                                              directive: str = "display") -> Optional[str]:
    """
    Processes a project create or update object_action by extracting key attributes such as
    glossary name, language, description, and usage from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """

    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)
    if not parsed_output:
        logger.error(f"No output for `{object_action}`")
        return None

    valid = parsed_output['valid']
    exists = parsed_output['exists']

    qualified_name = parsed_output.get('qualified_name', None)
    guid = parsed_output.get('guid', None)

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']

    display_name = attributes['Display Name'].get('value', None)
    status = attributes.get('Status', {}).get('value', None)
    output_set = make_format_set_name_from_type(object_type)
    #

    if directive == "display":
        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
        return valid

    elif directive == "process":
        try:
            obj = "External Reference"
            EXTERNAL_REFERENCE_PROPS = ["ExternalReferenceProperties", "ExternalDataSourceProperties",
                                        "ExternalModelSourceProperties",
                                        "RelatedMediaProperties", "CitedDocumentProperties"]

            EXTERNAL_REFERENCE_TYPES = ["ExternalReference", "ExternalDataSource", "ExternalModelSource",
                                        "RelatedMedia", "CitedDocument"]


            #   Set the property body for a glossary collection
            #
            prop_body = set_element_prop_body(obj, qualified_name, attributes)
            prop_body["referenceTitle"] = attributes.get('Reference Title', {}).get('value', None)
            prop_body["referenceAbstract"] = attributes.get('Reference Abstract', {}).get('value', None)
            prop_body["authors"] = attributes.get('Authors', {}).get('value', None)
            prop_body["organization"] = attributes.get('Organization', {}).get('value', None)
            prop_body["url"] = attributes.get('URL', {}).get('value', None)
            prop_body["sources"] = attributes.get('Sources', {}).get('value', None)
            prop_body["license"] = attributes.get('License', {}).get('value', None)
            prop_body["copyright"] = attributes.get('Copyright', {}).get('value', None)
            prop_body["attribution"] = attributes.get('Attribution', {}).get('value', None)

            if object_type == "RelatedMedia":
                prop_body["class"]  = "RelatedProperties"
                prop_body["mediaType"]  = attributes.get('Media Type', {}).get('value', None)
                prop_body["mediaTypeOtherId"] = attributes.get('Media Type Other ID', {}).get('value', None)
                prop_body["defaultMediaUsage"]= attributes.get('Default Media Usage', {}).get('value', None)
                prop_body["defaultMediaUsageOtherId"] = attributes.get('Default Media Usage Other ID', {}).get('value', None)
            elif object_type == "CitedDocument":
                prop_body["class"]  = "CitedDocumentProperties"
                prop_body["numberOfPages"]  = attributes.get('Number of Pages', {}).get('value', None)
                prop_body["pageRange"] = attributes.get('Page Range', {}).get('value', None)
                prop_body["publicationSeries"] = attributes.get('Publication Series', {}).get('value', None)
                prop_body["publicationSeriesVolume"] = attributes.get('Publication Series Volume', {}).get('value', None)
                prop_body["publisher"] = attributes.get('Publisher', {}).get('value', None)
                prop_body["edition"] = attributes.get('Edition', {}).get('value', None)
                prop_body["firstPublicationDate"] = attributes.get('First Publication Date', {}).get('value', None)
                prop_body["publicationDate"] = attributes.get('Publication Date', {}).get('value', None)
                prop_body["publicationCity"] = attributes.get('Publication City', {}).get('value', None)
                prop_body["publicationYear"] = attributes.get('Publication Year', {}).get('value', None)
                prop_body["publicationNumbers"]= attributes.get('Publication Numbers', {}).get('value', None)



            if object_action == "Update":
                if not exists:
                    msg = (f" Element `{display_name}` does not exist! Updating result document with Create "
                           f"{object_action}\n")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif not valid:
                    msg = ("  The input data is invalid and cannot be processed. \nPlease review")
                    logger.error(msg)
                    print(Markdown(f"==> Validation of {command} failed!!\n"))
                    print(Markdown(msg))
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))


                body = set_update_body(obj, attributes)
                body['properties'] = prop_body

                egeria_client.update_external_reference(guid, body)
                # if status:
                #     egeria_client.update_external_reference_status(guid, status)

                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                return egeria_client.get_external_reference_by_guid(guid, element_type= object_type,
                                                            output_format='MD', output_format_set = output_set)


            elif object_action == "Create":
                if valid is False and exists:
                    msg = (f"Project `{display_name}` already exists and result document updated changing "
                           f"`Create` to `Update` in processed output\n\n___")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif not valid:
                    msg = ("The input data is invalid and cannot be processed. \nPlease review")
                    logger.error(msg)
                    print(Markdown(f"==> Validation of {command} failed!!\n"))
                    print(Markdown(msg))
                    return None

                else:
                    body = set_create_body(object_type,attributes)

                    # if this is a root or folder (maybe more in the future), then make sure that the classification is set.
                    # body["initialClassifications"] = set_object_classifications(object_type, attributes, None)

                    body["properties"] = prop_body
                    slim_body = body_slimmer(body)
                    guid = egeria_client.create_external_reference(body = slim_body)
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        msg = f"Created Element `{display_name}` with GUID {guid}\n\n___"
                        logger.success(msg)
                        return egeria_client.get_external_reference_by_guid(guid, element_type=object_type,
                                                                            output_format='MD',
                                                                            output_format_set=output_set)
                    else:
                        msg = f"Failed to create element `{display_name}` with GUID {guid}\n\n___"
                        logger.error(msg)
                        return None

        except PyegeriaException as e:
            logger.error(f"Pyegeria error performing {command}: {e}")
            print_basic_exception(e)
            return None
        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
    else:
        return None



def process_link_to_external_reference_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """ Link a referenceable to an external reference."""

    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_view_command(egeria_client, object_type, object_action,
                                       txt, directive)

    if not parsed_output:
        logger.error(f"No output for `{object_action}`")
        print(Markdown("## Parsing failed"))
        return None

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']

    element_guid = attributes.get('Element Name', {}).get('guid', None)
    external_reference_guid = attributes.get('External Reference', {}).get('guid', None)

    valid = parsed_output['valid']
    exists = element_guid is not None and external_reference_guid is not None
    prop_body = set_rel_prop_body("ExternalReferenceLink", attributes)

    if directive == "display":

        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
            logger.error(msg)
            print(Markdown(f"==> Validation of {command} failed!!\n"))
        return valid

    elif directive == "process":

        try:
            if object_action == "Detach":
                if not exists:
                    msg = " Link  does not exist! Updating result document with Link object_action\n"
                    logger.error(msg)
                    out = parsed_output['display'].replace('Link', 'Detach', 1)
                    return out
                elif not valid:
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))
                    body = set_delete_request_body(object_type, attributes)

                    egeria_client.detach_external_reference(element_guid, external_reference_guid, body)

                    logger.success(f"===> Detached segment  from `{element_guid}`to {external_reference_guid}\n")
                    out = parsed_output['display'].replace('Unlink', 'Link', 1)

                    return (out)


            elif object_action == "Link":
                if valid is False and exists:
                    msg = "-->  Link already exists and result document updated changing `Link` to `Detach` in processed output\n"
                    logger.error(msg)

                elif valid is False:
                    msg = f"==>{object_type} Link is not valid and can't be created"
                    logger.error(msg)
                    return

                else:
                    body = set_rel_request_body_for_type("ExternalReferencesLink", attributes)
                    body['properties'] = prop_body

                    egeria_client.link_external_reference(element_guid,
                                                      external_reference_guid,
                                                      body=body_slimmer(body))
                    msg = f"==>Created {object_type} link \n"
                    logger.success(msg)
                    out = parsed_output['display'].replace('Link', 'Detach', 1)
                    return out

        except ValidationError as e:
            print_validation_error(e)
            logger.error(f"Validation Error performing {command}: {e}")
            return None
        except PyegeriaException as e:
            print_basic_exception(e)
            logger.error(f"PyegeriaException occurred: {e}")
            return None

        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None



def process_link_to_media_reference_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") \
        -> Optional[str]:
    #     """ Link a referenceable to a related media reference."""
    #
    #

    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_view_command(egeria_client, object_type, object_action,
                                       txt, directive)

    if not parsed_output:
        logger.error(f"No output for `{object_action}`")
        print(Markdown("## Parsing failed"))
        return None

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']

    element_guid = attributes.get('Element Name', {}).get('guid', None)
    media_reference_guid = attributes.get('Media Reference', {}).get('guid', None)
    media_id = attributes.get('Media Id', {}).get('value', None)
    media_usage = attributes.get('Media Usage', {}).get('value', None)
    media_usage_other_id = attributes.get('Media Usage Other Id', {}).get('value', None)

    valid = parsed_output['valid']
    exists = element_guid is not None and media_reference_guid is not None
    prop_body = set_rel_prop_body("MediaReference", attributes)
    prop_body["mediaId"] = media_id
    prop_body["mediaUsageId"] = media_usage
    prop_body["mediaUsageOtherId"] = media_usage_other_id


    if directive == "display":

        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
            logger.error(msg)
            print(Markdown(f"==> Validation of {command} failed!!\n"))
        return valid

    elif directive == "process":

        try:
            if object_action == "Detach":
                if not exists:
                    msg = " Link  does not exist! Updating result document with Link object_action\n"
                    logger.error(msg)
                    out = parsed_output['display'].replace('Link', 'Detach', 1)
                    return out
                elif not valid:
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))
                    body = set_delete_request_body(object_type, attributes)

                    egeria_client.detach_cited_document(element_guid, media_reference_guid, body)

                    logger.success(f"===> Detached segment  from `{element_guid}`to {media_reference_guid}\n")
                    out = parsed_output['display'].replace('Unlink', 'Link', 1)

                    return (out)


            elif object_action == "Link":
                if valid is False and exists:
                    msg = "-->  Link already exists and result document updated changing `Link` to `Detach` in processed output\n"
                    logger.error(msg)

                elif valid is False:
                    msg = f"==>{object_type} Link is not valid and can't be created"
                    logger.error(msg)
                    return

                else:
                    body = set_rel_request_body_for_type("CitedDocumentLink", attributes)
                    body['properties'] = prop_body

                    egeria_client.link_cited_document(element_guid,
                                                      media_reference_guid,
                                                      body=body_slimmer(body))
                    msg = f"==>Created {object_type} link \n"
                    logger.success(msg)
                    out = parsed_output['display'].replace('Link', 'Detach', 1)
                    return out

        except ValidationError as e:
            print_validation_error(e)
            logger.error(f"Validation Error performing {command}: {e}")
            return None
        except PyegeriaException as e:
            print_basic_exception(e)
            logger.error(f"PyegeriaException occurred: {e}")
            return None

        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None

def process_link_to_cited_document_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") \
        -> Optional[str]:

#     """ Link a referenceable to a cited document."""
#

    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_view_command(egeria_client, object_type, object_action,
                                       txt, directive)

    if not parsed_output:
        logger.error(f"No output for `{object_action}`")
        print(Markdown("## Parsing failed"))
        return None

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']

    element_guid = attributes.get('Element Name', {}).get('guid', None)
    cited_document_guid = attributes.get('Cited Document', {}).get('guid', None)
    reference_id = attributes.get('Reference Id', {}).get('value', None)
    pages = attributes.get('Pages', {}).get('value', None)

    valid = parsed_output['valid']
    exists = element_guid is not None and cited_document_guid  is not None
    prop_body = set_rel_prop_body("CitedDocumentLink", attributes)
    prop_body["referenceId"] = reference_id
    prop_body["pages"] = pages



    if directive == "display":

        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
            logger.error(msg)
            print(Markdown(f"==> Validation of {command} failed!!\n"))
        return valid

    elif directive == "process":


        try:
            if object_action == "Detach":
                if not exists:
                    msg = f" Link  does not exist! Updating result document with Link object_action\n"
                    logger.error(msg)
                    out = parsed_output['display'].replace('Link', 'Detach', 1)
                    return out
                elif not valid:
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))
                    body = set_delete_request_body(object_type, attributes)

                    egeria_client.detach_cited_document(element_guid, cited_document_guid,body)

                    logger.success(f"===> Detached segment  from `{element_guid}`to {cited_document_guid}\n")
                    out = parsed_output['display'].replace('Unlink', 'Link', 1)

                    return (out)


            elif object_action == "Link":
                if valid is False and exists:
                    msg = "-->  Link already exists and result document updated changing `Link` to `Detach` in processed output\n"
                    logger.error(msg)

                elif valid is False:
                    msg = f"==>{object_type} Link is not valid and can't be created"
                    logger.error(msg)
                    return

                else:
                    body = set_rel_request_body_for_type("CitedDocumentLink", attributes)
                    body['properties'] = prop_body

                    egeria_client.link_cited_document(element_guid,
                                                       cited_document_guid,
                                                        body=body_slimmer(body))
                    msg = f"==>Created {object_type} link \n"
                    logger.success(msg)
                    out = parsed_output['display'].replace('Link', 'Detach', 1)
                    return out

        except ValidationError as e:
            print_validation_error(e)
            logger.error(f"Validation Error performing {command}: {e}")
            return None
        except PyegeriaException as e:
            print_basic_exception(e)
            logger.error(f"PyegeriaException occurred: {e}")
            return None

        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None