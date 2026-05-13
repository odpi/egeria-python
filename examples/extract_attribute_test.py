import json
from pyegeria.omvs.governance_officer import GovernanceOfficer
from pyegeria.core.utils import discover_element_schema
from pyegeria.view.output_formatter import materialize_egeria_summary

# 1. Fetch data
client = GovernanceOfficer("qs-view-server", "https://localhost:9443", user_id="peterprofile", user_pwd="secret")
client.create_egeria_bearer_token()

# We request JSON to get the raw un-filtered object back, bypassing any report-spec filters
zones = client.find_governance_definitions(search_string="*", metadata_element_subtypes=["GovernanceZone"], output_format="JSON")

if zones and isinstance(zones, list):/
    print("Available Attributes Schema (Unfiltered):")
    
    # Materialize the raw object to flatten it and generate dynamic properties (like Vega graphs)
    materialized_zone = materialize_egeria_summary(zones[0])
    
    schema = discover_element_schema(materialized_zone)
    
    # This will print EVERY property Egeria returned, plus generated graphs!
    for path, data_type in schema.items():
        print(f" - {path}: {data_type}")
