# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Dr.Egeria commands for Egeria 6.4 Data Values (odpi/egeria#9463, model 0208): the Data Engineer family.

- Create/Update Data Value -> DataEngineer.create_data_value / update_data_value. A ``Literal Value``, ``Literal
  Value List`` or ``Literal Value Map`` makes it a LiteralDataValue (LiteralDataValueProperties, typeName
  LiteralDataValue); otherwise it is a DataValue (DataValueProperties). Updating an existing LiteralDataValue keeps
  its class. Egeria can't change an element's type, so a literal value given for an existing plain DataValue is
  refused with words.
- Link/Detach Data Value Source -> link/detach_data_value_source (DataValue -> Asset).
- Link/Detach Processing Variable -> link/detach_processing_variable (element -> DataValue, Position).
- Link/Detach Embedded Data Value -> link/detach_embedded_data_value (parent DataValue -> embedded DataValue,
  Position).

Every relationship here is uni-link: attach and detach by the two end GUIDs. Position is a whole number; 0 means
unset. Every command is gated on Egeria 6.4 (md_processing.v2.egeria_6_4).
"""
from __future__ import annotations

from typing import Any, Dict, List

from loguru import logger

from pyegeria.core import egeria_6_4_names as e64
from pyegeria.core.utils import body_slimmer
from md_processing.md_processing_utils.common_md_utils import (
    set_create_body, set_element_prop_body, set_update_body, update_element_dictionary)
from md_processing.v2.decisions import ELEMENT_ATTRIBUTE_OF
from md_processing.v2.egeria_6_4 import (
    EMPTY, Egeria64LinkProcessor, Egeria64Processor, delete_relationship_body, int_value, new_relationship_body,
    read_keys_only, value)

#: DataValue attributes and the DataValueProperties key each fills (Length and Hash are whole numbers).
DATA_VALUE_FIELDS = {
    "Data Format": "dataFormat", "Length": "length", "Data Type": "dataType", "Usage": "usage",
    "Fingerprint": "fingerprint", "Fingerprint Algorithm": "fingerprintAlgorithm", "Hash": "hash",
    "Hash Algorithm": "hashAlgorithm",
}
INT_FIELDS = ("Length", "Hash")

#: The literal attributes, each of which makes the value a LiteralDataValue.
LITERAL_FIELDS = {"Literal Value": "dataValue", "Literal Value List": "dataValueList",
                  "Literal Value Map": "dataValueMap"}


class DataValueProcessor(Egeria64Processor):
    """Create Data Value / Update Data Value (DataValue or LiteralDataValue)."""

    async def fetch_element(self, guid_: str, _max_timeout_retries: int = 2):
        element = await self.e64(self.client.data_engineer._async_get_data_value_by_guid(guid_))
        return element if isinstance(element, dict) else None

    def _type_name(self, attributes: Dict[str, Any]) -> str:
        literal_given = [n for n in LITERAL_FIELDS if value(attributes, n) not in EMPTY]
        existing = (((self.as_is_element or {}).get("elementHeader") or {}).get("type") or {}).get("typeName")
        if existing == e64.LITERAL_DATA_VALUE:
            return e64.LITERAL_DATA_VALUE
        if existing and literal_given:
            raise ValueError(f"{self.command.verb} Data Value: '{value(attributes, 'Display Name')}' is a {existing}, "
                             f"not a LiteralDataValue, and Egeria can't change an element's type, so "
                             f"{', '.join(literal_given)} can't be set on it. Create a new Data Value with the "
                             f"literal value instead. Nothing was changed.")
        return e64.LITERAL_DATA_VALUE if literal_given else e64.DATA_VALUE

    def data_value_properties(self, qualified_name: str) -> dict:
        attributes = self.parsed_output["attributes"]
        type_name = self._type_name(attributes)
        props = set_element_prop_body(type_name, qualified_name, attributes)
        fields = {key: value(attributes, name) for name, key in DATA_VALUE_FIELDS.items()}
        for name in INT_FIELDS:
            fields[DATA_VALUE_FIELDS[name]] = int_value(attributes, name)
        if type_name == e64.LITERAL_DATA_VALUE:
            fields.update({key: value(attributes, name) for name, key in LITERAL_FIELDS.items()})
        props.update({k: v for k, v in fields.items() if v not in EMPTY})
        props["class"] = f"{type_name}Properties"
        props = {k: v for k, v in body_slimmer(props).items() if v not in EMPTY}
        return read_keys_only(props, attributes, {**ELEMENT_ATTRIBUTE_OF,
                                                  **{k: n for n, k in DATA_VALUE_FIELDS.items()},
                                                  **{k: n for n, k in LITERAL_FIELDS.items()}})

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output.get("qualified_name")
        display_name = value(attributes, "Display Name")
        de = self.client.data_engineer

        if self.command.verb == "Update":
            guid_ = self.parsed_output.get("guid")
            body = set_update_body(e64.DATA_VALUE, attributes)
            body["properties"] = self.data_value_properties(qualified_name)
            body = body_slimmer(body)
            self.last_body = body
            await self.e64(de._async_update_data_value(guid_, body))
            logger.success(f"Updated Data Value '{display_name}' ({guid_})")
            update_element_dictionary(qualified_name, {"guid": guid_, "display_name": display_name})
            return await self.render_result_markdown(guid_)

        body = set_create_body(e64.DATA_VALUE, attributes)
        body["properties"] = self.data_value_properties(qualified_name)
        body.pop("initialClassifications", None)
        body = body_slimmer(body)
        self.last_body = body
        guid_ = self.extract_guid_or_raise(await self.e64(de._async_create_data_value(body)), "Create Data Value")
        self.parsed_output["guid"] = guid_
        update_element_dictionary(qualified_name, {"guid": guid_, "display_name": display_name})
        logger.success(f"Created {body['properties']['class'][:-len('Properties')]} '{display_name}' with GUID {guid_}")
        return await self.render_result_markdown(guid_)


#: OM_TYPE -> (end attributes, link method, detach method, takes Position)
DATA_VALUE_LINKS = {
    e64.DATA_VALUE_SOURCE: (("Data Value", "Asset"), "_async_link_data_value_source",
                            "_async_detach_data_value_source", False),
    e64.PROCESSING_VARIABLE: (("Element", "Data Value"), "_async_link_processing_variable",
                              "_async_detach_processing_variable", True),
    e64.EMBEDDED_DATA_VALUE: (("Parent Data Value", "Embedded Data Value"), "_async_link_embedded_data_value",
                              "_async_detach_embedded_data_value", True),
}


class DataValueLinkProcessor(Egeria64LinkProcessor):
    """Link/Detach Data Value Source, Processing Variable and Embedded Data Value (uni-link)."""

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        om_type = self.get_command_spec().get("OM_TYPE")
        (end1_name, end2_name), link, detach, positioned = DATA_VALUE_LINKS[om_type]
        end1, end2 = self.ends(attributes, end1_name, end2_name)
        de = self.client.data_engineer
        what = f"{self.command.verb} {self.command.object_type}"
        if self.command.verb in self.DETACH_VERBS:
            body = delete_relationship_body(attributes)
            self.last_body = body
            await self.e64(getattr(de, detach)(end1, end2, body))
            return f"\n\n# {what}\n\nDetached {end1_name} {end1} from {end2_name} {end2}.\n"
        # Position's spec default is 0 (unset): only a Position the document gives is sent.
        given = positioned and not (attributes.get("Position") or {}).get("is_default")
        extra = {"position": int_value(attributes, "Position")} if given else {}
        body = new_relationship_body(om_type, attributes, extra, {"position": "Position"})
        self.last_body = body
        await self.e64(getattr(de, link)(end1, end2, body))
        return f"\n\n# {what}\n\nLinked {end1_name} {end1} to {end2_name} {end2}.\n"


def register_data_value_processors(reg) -> List[str]:
    """Register the B2 commands; returns their names."""
    names = {
        "Create Data Value": DataValueProcessor, "Update Data Value": DataValueProcessor,
        "Link Data Value Source": DataValueLinkProcessor, "Detach Data Value Source": DataValueLinkProcessor,
        "Link Processing Variable": DataValueLinkProcessor, "Detach Processing Variable": DataValueLinkProcessor,
        "Link Embedded Data Value": DataValueLinkProcessor, "Detach Embedded Data Value": DataValueLinkProcessor,
    }
    for name, cls in names.items():
        reg(name, cls)
    return list(names)
