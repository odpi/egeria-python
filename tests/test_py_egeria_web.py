#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sys

def call_dr_egeria_process(file_name, base_url="http://localhost:8085"):
    """
    Make a REST call to the Dr. Egeria process API endpoint.
    
    Args:
        file_name (str): The name of the file to process
        base_url (str): The base URL of the Apache web server
        
    Returns:
        dict: The JSON response from the API
    """
    # Construct the full URL with the query parameter
    url = f"{base_url}/api/dr.egeria/process"
    params = {"file-name": file_name}
    
    try:
        # Make the GET request
        response = requests.get(url, params=params)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the JSON response
        result = response.json()
        
        print(f"API call successful: {result}")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return {"status": "error", "message": str(e)}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return {"status": "error", "message": f"Invalid JSON response: {e}"}

if __name__ == "__main__":
    # Get the file name from command line arguments or use a default
    file_name = sys.argv[1] if len(sys.argv) > 1 else "example.md"
    
    # Call the API
    result = call_dr_egeria_process(file_name)
    
    # Print the result in a formatted way
    print("\nResult:")
    print(f"Status: {result.get('status')}")
    print(f"Message: {result.get('message')}")