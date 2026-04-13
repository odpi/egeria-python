import json
from unittest.mock import MagicMock
from pyegeria.omvs.my_profile import MyProfile

def test_nesting():
    # Load callie.json
    with open('../sample-data/callie.json', 'r') as f:
        data = json.load(f)
    
    element = data['element']
    
    # Create MyProfile client
    client = MyProfile("view_server", "https://localhost:9443", "user_id", "password")
    
    # Define a mock columns_struct for My-User
    columns_struct = {
        "heading": "My Information",
        "formats": {
            "attributes": [
                {"name": "Full Name", "key": "full_name"},
                {"name": "Job Title", "key": "job_title"},
                {"name": "Contact Methods", "key": "contact_methods"},
                {"name": "Roles", "key": "roles"},
                {"name": "Teams", "key": "teams"},
                {"name": "Communities", "key": "communities"},
            ]
        }
    }
    
    # Run extractor
    enriched = client._extract_my_profile_properties(element, columns_struct)
    
    # Extract values for display
    attributes = enriched['formats']['attributes']
    results = {attr['name']: attr.get('value') for attr in attributes}
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    test_nesting()
