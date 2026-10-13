# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
ISSUE-111: with body=None, _async_new_relationship_request builds
{"properties": {"class": prop[0]}}. Eleven ConnectionMaker/DataDiscovery link
methods passed the relationship type name (or a near-miss) as prop[0], so the
default body named a properties class Egeria does not have and the link was
refused. Each must name the class the Egeria REST service checks for with
`instanceof` (ConnectionMakerRESTServices / DataDiscoveryRESTServices).
"""
import json

import pytest

from pyegeria.omvs.connection_maker import ConnectionMaker
from pyegeria.omvs.data_discovery import DataDiscovery


class _Response:
    def json(self):
        return {"class": "GUIDResponse", "guid": "rel-guid"}


def _client(cls, sent: list, monkeypatch):
    monkeypatch.setattr(cls, "check_connection", lambda self: "test")
    client = cls("view-server", "https://localhost:1", "user", "pwd")

    async def fake_make_request(method, url, body=None, *args, **kwargs):
        sent.append(json.loads(body) if isinstance(body, str) else body)
        return _Response()

    client._async_make_request = fake_make_request
    return client


CASES = [
    (ConnectionMaker, "_async_link_connection_connector_type", "ConnectionConnectorTypeProperties"),
    (ConnectionMaker, "_async_link_connection_endpoint", "ConnectToEndpointProperties"),
    (ConnectionMaker, "_async_link_embedded_connection", "EmbeddedConnectionProperties"),
    (ConnectionMaker, "_async_link_asset_to_connection", "ResourceConnectionProperties"),
    (ConnectionMaker, "_async_link_resource_to_connection", "ResourceConnectionProperties"),
    (ConnectionMaker, "_async_link_endpoint_to_it_asset", "ServerEndpointProperties"),
    (DataDiscovery, "_async_attach_annotation_to_report", "ReportedAnnotationProperties"),
    (DataDiscovery, "_async_link_annotation_to_described_element", "AssociatedAnnotationProperties"),
    (DataDiscovery, "_async_link_annotation_to_its_predecessor", "AnnotationExtensionProperties"),
    (DataDiscovery, "_async_link_resource_profile_data", "ResourceProfileDataProperties"),
    (DataDiscovery, "_async_link_annotation_match", "AnnotationMatchProperties"),
    (DataDiscovery, "_async_link_request_for_action_target", "RequestForActionTargetProperties"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("cls, method, expected", CASES, ids=[c[1] for c in CASES])
async def test_default_body_names_real_properties_class(cls, method, expected, monkeypatch):
    sent: list = []
    client = _client(cls, sent, monkeypatch)

    await getattr(client, method)("guid-1", "guid-2", None)

    assert sent[0]["class"] == "NewRelationshipRequestBody"
    assert sent[0]["properties"]["class"] == expected
