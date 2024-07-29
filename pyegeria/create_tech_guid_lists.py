"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Script to create a new file to initiate tech guids.
These GUIDS should be copied into the __init__.py.

"""
import json
from rich import print, print_json
from datetime import datetime
from rich.console import Console

from pyegeria import AutomatedCuration, ServerOps

console = Console(width=200)


def build_global_guid_lists(server:str = "view-server",url: str = "https://localhost:9443",
                            user_id: str = "erinoverview", user_pwd:str = "secret") -> None:
    cur_time = datetime.now().strftime("%d-%m-%Y %H:%M")
    file_name = f"./tech_guids_{cur_time}.py"
    a_client = AutomatedCuration(server, url, user_id=user_id,
                                 user_pwd=user_pwd)
    token = a_client.create_egeria_bearer_token()
    # get all technology types

    tech_types = a_client.get_all_technology_types()
    if type(tech_types) is list:
        with open(file_name, "w") as f:
            out = f"global template_guids, integration_guids\n"
            f.write(out)
            for tech_type in tech_types:
                # get tech type details
                display_name = tech_type["name"]

                details = a_client.get_technology_type_detail(display_name)
                if type(details) is str:
                    console.print(f"{display_name} technology type has no details")
                    continue
                # get templates and update the template_guids global
                templates = details.get("catalogTemplates", "Not Found")

                if type(templates) is list:
                    for template in templates:
                        template_name = template.get("name", None).replace(' template', '')
                        template_guid = template["relatedElement"]["guid"]
                        out = f"TEMPLATE_GUIDS['{template_name}'] = '{template_guid}'\n"
                        console.print(f"Added {template_name} template with GUID {template_guid}")
                        f.write(out)
                else:
                    console.print(f"{display_name} technology type has no templates")
                # Now find the integration connector guids
                resource_list = details.get('resourceList', ' ')
                if type(resource_list) is list:
                    for resource in resource_list:
                        resource_guid = resource['relatedElement']['guid']
                        resource_type = resource['relatedElement']['type']['typeName']
                        if resource_type == "IntegrationConnector":
                            if resource['resourceUse'] == "Catalog Resource":
                                int_con = resource['relatedElement']['uniqueName']
                                int_con_name = int_con.split(':')[-1].replace('IntegrationConnector', '')

                                out = f"INTEGRATION_GUIDS['{int_con_name}'] = '{resource_guid}'\n"
                                console.print(f"Added {int_con_name} integration connector with GUID {resource_guid}")
                                f.write(out)
                else:
                    console.print(f"{display_name} technology type has no integration connectors")
            #
            #   Ok - now lets harvest integration connectors using get_integration_daemon_status from ServerOps
            #   Assume that integration daemon called integration-daemon
            #
            s_client = ServerOps('integration-daemon', url, user_id=user_id,
                                 user_pwd=user_pwd)
            integ_status = s_client.get_integration_daemon_status()

            if type(integ_status) is dict:
                connections = integ_status['integrationConnectorReports']
                for connection in connections:
                    int_con_name = connection['connectorName']
                    resource_guid = connection['connectorGUID']
                    out = f"INTEGRATION_GUIDS['{int_con_name}'] = '{resource_guid}'\n"
                    console.print(f"Added {int_con_name} integration connector with GUID {resource_guid}")
                    f.write(out)




if __name__ == "__main__":
    build_global_guid_lists()