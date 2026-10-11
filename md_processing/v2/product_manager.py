"""
Product Manager Processors for Dr.Egeria v2.

Handles the commands of the "Digital Products" family that wrap
`pyegeria/omvs/product_manager.py`'s subscription-type and Bitol-document calls:

- Create Subscription Type: add a one-time, periodic or ongoing-update subscription
  type to a digital product. Egeria creates the product's notification type and the
  governance action process that `Initiate Subscription` (Automation family) runs to
  provision a subscription of that type. Egeria reconciles an existing subscription
  type with the request rather than duplicating it, so the command is safe to re-run.
- Import Data Contract / Import Data Product: catalog an Open Data Contract Standard
  (ODCS) / Open Data Product Standard (ODPS) document directly as an Agreement
  classified as a DataSharingAgreement / as a DigitalProduct. Re-importing the same
  version updates the elements; a new version creates new ones. A document with no
  `id` is skipped by Egeria.
- Publish Data Contract / Publish Data Product: send such a document to an integration
  daemon, which passes it to the connectors that registered a Bitol listener.

The documents are read from a file named by the `Document File` attribute (YAML or
JSON), not written inline: YAML routinely contains `---` and `#` lines, which are
markdown horizontal rules and headings to the Dr.Egeria extractor.

Every command here is an action, not a create-or-update of a named element, so there
is no existing element to look up and no Create<->Update rewrite (same shape as the
Automation family's processors).

Problems the author can fix in the markdown (a missing file, a PERIODIC type with no
interval) raise ValueError rather than PyegeriaException: a plain-message
PyegeriaException renders with Egeria's "unable to connect to the platform / check the
URL" boilerplate, which is wrong for these. The dispatcher reports either as a failure.
"""
import os
from typing import Any, Dict, List, Optional

from loguru import logger

from md_processing.v2.processors import AsyncBaseCommandProcessor

SUBSCRIPTION_KINDS = ("ONE_TIME", "PERIODIC", "ONGOING_UPDATE")


def _v(attributes: Dict[str, Any], name: str, default=None):
    value = attributes.get(name, {}).get("value", default)
    return default if value in (None, "") else value


def _guid(attributes: Dict[str, Any], name: str) -> Optional[str]:
    guid = attributes.get(name, {}).get("guid")
    return None if not guid or str(guid).startswith("(Planned:") else guid


def _guid_list(attributes: Dict[str, Any], name: str) -> List[str]:
    guid_list = attributes.get(name, {}).get("guid_list")
    if isinstance(guid_list, list):
        return [g for g in guid_list if g and not str(g).startswith("(Planned:")]
    return []


def normalize_subscription_kind(value: Any) -> str:
    """'One-Time' / 'ongoing update' / 'PERIODIC' -> 'ONE_TIME' / 'ONGOING_UPDATE' / 'PERIODIC'."""
    kind = str(value or "ONE_TIME").strip().upper().replace("-", "_").replace(" ", "_")
    if kind not in SUBSCRIPTION_KINDS:
        raise ValueError(
            f"Subscription Kind '{value}' is not one of {', '.join(SUBSCRIPTION_KINDS)}.")
    return kind


class ProductManagerProcessor(AsyncBaseCommandProcessor):
    """Shared behaviour for the Digital Products family's action commands."""

    def supports_target_element_lookup(self) -> bool:
        # An action, not a named element: no as-is lookup, no upsert rewrite.
        return False

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    def _result(self, what: str, guid: Optional[str] = None) -> str:
        if guid:
            self.parsed_output["guid"] = guid
        logger.success(f"{self.command.verb} {self.command.object_type}: {what}" + (f" ({guid})" if guid else ""))
        return f"\n\n## {self.command.verb} {self.command.object_type}\n\n{what}" + (f": `{guid}`" if guid else "") + "\n"


class SubscriptionTypeProcessor(ProductManagerProcessor):
    """Create Subscription Type."""

    def _build(self, attributes: Dict[str, Any]) -> tuple:
        product_guid = _guid(attributes, "Digital Product")
        if not product_guid:
            raise ValueError("'Digital Product' could not be resolved to an existing digital product.")
        kind = normalize_subscription_kind(_v(attributes, "Subscription Kind"))
        interval = _v(attributes, "Subscription Notification Interval")
        monitored = _guid_list(attributes, "Monitored Resources")

        if kind == "PERIODIC" and not interval:
            raise ValueError("A PERIODIC subscription type needs a 'Subscription Notification Interval' (minutes).")
        if kind == "ONGOING_UPDATE" and not monitored:
            raise ValueError(
                "An ONGOING_UPDATE subscription type needs at least one 'Monitored Resources' element "
                "(typically the product's asset).")
        if kind == "ONE_TIME" and (interval or monitored):
            self._add_warning("A ONE_TIME subscription type ignores 'Subscription Notification Interval' and "
                              "'Monitored Resources'; Egeria will not use them.")
        if kind == "PERIODIC" and monitored:
            self._add_warning("A PERIODIC subscription type ignores 'Monitored Resources'.")

        body: Dict[str, Any] = {
            "identifier": _v(attributes, "Identifier"),
            "displayName": _v(attributes, "Display Name"),
            "description": _v(attributes, "Description"),
            "subscriptionManagerGUID": _guid(attributes, "Subscription Manager"),
            "licenseTypeGUID": _guid(attributes, "Subscription License Type"),
            "serviceLevelObjectiveGUID": _guid(attributes, "Subscription Service Level Objective"),
        }
        if kind != "ONE_TIME" and interval:
            body["notificationInterval"] = int(interval)
        if kind == "ONGOING_UPDATE":
            body["monitoredResourceGUIDs"] = monitored
        return product_guid, kind, {k: v for k, v in body.items() if v is not None}

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        product_guid, kind, body = self._build(attributes)
        client = self.client.product_manager
        create = {"ONE_TIME": client._async_create_one_time_subscription,
                  "PERIODIC": client._async_create_periodic_subscription,
                  "ONGOING_UPDATE": client._async_create_ongoing_update_subscription}[kind]
        guid = await create(product_guid, body or None)
        if not guid:
            raise ValueError(f"Egeria did not return a subscription process for the {kind} subscription type.")
        label = body.get("identifier") or body.get("displayName") or kind
        return self._result(f"Subscription type `{label}` ({kind}) added to product "
                            f"`{_v(attributes, 'Digital Product', product_guid)}`; "
                            f"governance action process", guid)


class BitolDocumentProcessor(ProductManagerProcessor):
    """Import / Publish Data Contract / Data Product -- the documents come from a file."""

    def _document_path(self, attributes: Dict[str, Any]) -> str:
        name = _v(attributes, "Document File")
        if not name:
            raise ValueError("'Document File' is required.")
        path = os.path.expanduser(str(name).strip())
        if not os.path.isabs(path):
            source = self.context.get("input_path") or self.context.get("input_file") or ""
            path = os.path.join(os.path.dirname(os.path.abspath(os.path.expanduser(source))) if source else os.getcwd(),
                                path)
        return os.path.normpath(path)

    def _read_document(self, attributes: Dict[str, Any]) -> str:
        path = self._document_path(attributes)
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            raise ValueError(f"Cannot read Document File '{path}': {e}") from e
        if not text.strip():
            raise ValueError(f"Document File '{path}' is empty.")
        return text

    async def validate_only(self) -> str:
        result = await super().validate_only()
        try:
            self._read_document(self.parsed_output.get("attributes", {}))
        except ValueError as e:
            self._add_warning(str(e))
        return result

    @property
    def _is_contract(self) -> bool:
        return self.command.object_type == "Data Contract"

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        document = self._read_document(attributes)
        client = self.client.product_manager
        kind = "data contract" if self._is_contract else "data product"
        path = self._document_path(attributes)

        if self.command.verb == "Import":
            call = client._async_import_data_contract_string if self._is_contract \
                else client._async_import_data_product_string
            guid = await call(document)
            if not guid:
                raise ValueError(
                    f"Egeria skipped the {kind} in '{path}' -- a document with no 'id' cannot be catalogued.")
            return self._result(f"Imported {kind} from `{os.path.basename(path)}` as", guid)

        # Publish
        daemon_guid = _guid(attributes, "Integration Daemon")
        if not daemon_guid:
            raise ValueError("'Integration Daemon' could not be resolved to an existing integration daemon.")
        call = client._async_publish_data_contract_string if self._is_contract \
            else client._async_publish_data_product_string
        await call(daemon_guid, document)
        return self._result(f"Published {kind} `{os.path.basename(path)}` to integration daemon "
                            f"`{_v(attributes, 'Integration Daemon', daemon_guid)}`")
