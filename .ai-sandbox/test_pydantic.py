from pyegeria.models.models import SearchStringRequestBody
import json

print(f"Fields in SearchStringRequestBody: {SearchStringRequestBody.model_fields.keys()}")
for field_name, field in SearchStringRequestBody.model_fields.items():
    if field.alias:
        print(f"Field '{field_name}' has alias '{field.alias}'")
    else:
        print(f"Field '{field_name}' has no alias")

body = {
    "class": "SearchStringRequestBody",
    "searchString": "*",
    "metadataElementTypeName": "GovernancePolicy"
}

try:
    obj = SearchStringRequestBody.model_validate(body)
    print(f"Validated object: {obj}")
    print(f"metadata_element_type_name: {obj.metadata_element_type_name}")
    print(f"JSON dump: {obj.model_dump_json(exclude_none=True, by_alias=True)}")
except Exception as e:
    print(f"Validation failed: {e}")
