"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario tests for MetadataExpert OMVS.
"""
import time
from datetime import datetime
from rich.console import Console
from pyegeria.omvs.metadata_expert import MetadataExpert
from pyegeria.core._exceptions import PyegeriaException

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"

console = Console()

def run_scenario():
    console.print("[bold cyan]Starting Metadata Expert Scenario Test[/bold cyan]")
    client = MetadataExpert(VIEW_SERVER, PLATFORM_URL, USER_ID)
    
    try:
        client.create_egeria_bearer_token(USER_ID, "secret")
    except Exception as e:
        console.print(f"[yellow]Warning: Could not create bearer token (server might be down): {e}[/yellow]")

    try:
        # 1. Create Element
        console.print("1. Creating metadata element...")
        qname = f"ScenarioElement-{datetime.now().timestamp()}"
        create_body = {
            "class": "NewOpenMetadataElementRequestBody",
            "typeName": "Referenceable",
            "properties": {
                "class": "ElementProperties",
                "propertyValueMap": {
                    "qualifiedName": {
                        "class": "PrimitiveTypePropertyValue",
                        "typeName": "string",
                        "primitiveValue": qname
                    }
                }
            }
        }
        guid = client.create_metadata_element(create_body)
        console.print(f"   Created element with GUID: [green]{guid}[/green]")
        
        # 2. Update Element
        console.print("2. Updating element properties...")
        update_body = {
            "class": "UpdatePropertiesRequestBody",
            "properties": {
                "class": "ElementProperties",
                "propertyValueMap": {
                    "description": {
                        "class": "PrimitiveTypePropertyValue",
                        "typeName": "string",
                        "primitiveValue": "Scenario description"
                    }
                }
            }
        }
        client.update_metadata_element_properties(guid, update_body)
        console.print("   Updated properties successfully.")
        
        # 3. Classify Element
        console.print("3. Classifying element...")
        classify_body = {
            "class": "NewClassificationRequestBody"
        }
        client.classify_metadata_element(guid, "Confidentiality", classify_body)
        console.print("   Classified element as Confidentiality.")
        
        # 4. Delete Element
        console.print("4. Deleting element...")
        delete_body = {
            "class": "OpenMetadataDeleteRequestBody"
        }
        client.delete_metadata_element(guid, delete_body)
        console.print("   Deleted element successfully.")
        
        console.print("[bold green]Scenario completed successfully![/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]Scenario failed: {e}[/bold red]")

if __name__ == "__main__":
    run_scenario()
