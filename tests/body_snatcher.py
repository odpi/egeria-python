from pyegeria import EgeriaTech
from rich import print_json, print

import json

try:
    m_client = EgeriaTech(
        "qs-view-server",
        "https://localhost:9443",
        user_id="erinoverview",
        )
    token = m_client.create_egeria_bearer_token("erinoverview", "secret")


    response = m_client.get_all_entity_defs()
    for entity in response:
        if isinstance(response, (list, dict)):
            print_json("\n\n" + json.dumps(response, indent=4))
        elif type(response) is tuple:
            print(f"Type is {type(response)}")
            print_json("\n\n" + json.dumps(response, indent=4))
        elif type(response) is str:
            print("\n\nGUID is: " + response)
    assert True

except Exception as e:
    print(e)


finally:
    m_client.close_session()