
import json
from pathlib import Path
from pyegeria import load_app_config, EgeriaTech

load_app_config(env_file=str(Path(__file__).parent / ".env"))

user = "ivorpadlock"
password = "secret"
client = EgeriaTech(user_id=user, user_pwd=password)
token = client.create_egeria_bearer_token()

coco_user_dir = client.find_assets(search_string='cocoUserDirectory',
                                   metadata_element_type="SecretsCollection",
                                   report_spec = 'Secrets-Collection-User-Profile-Charts',
                                   output_format = 'REPORT')
# print(f"cocoUserDirectory: {json.dumps(coco_user_dir, indent=2)}")
print(coco_user_dir)
# identities = client.find_user_identities()
# print(f"identities: {json.dumps(identities, indent=2)}")

# zones = client.find_governance_definitions(search_string="*", metadata_element_type="GovernanceZone")
# print(f"zones: {json.dumps(zones, indent=2)}")

# digital_products_zone = client.find_governance_definitions(search_string="digital-products",
#                                                            metadata_element_type="GovernanceZone",
#                                                            report_spec="Governance-Zone-Overview-Charts",
#                                                            output_format="REPORT")
# # print(f"digital-products: {json.dumps(digital_products_zone, indent=2)}")
# print(digital_products_zone)