# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
The shared _async_get_name_request helper takes the name to match as
``filter_string``. Callers that passed it as ``name=`` put it in **kwargs
instead, so the request went out with a null filter and Egeria rejected it
(OPEN-METADATA-400-004 ... getSchemaTypesByName ... is null). Confirmed live
for SchemaMaker.get_schema_types_by_name.
"""
from typing import Any, cast

import pytest

from pyegeria.omvs.schema_maker import SchemaMaker


@pytest.mark.asyncio
@pytest.mark.parametrize("cls, method", [
    (SchemaMaker, "_async_get_schema_types_by_name"),
    (SchemaMaker, "_async_get_schema_attributes_by_name"),
    # DataDiscovery.get_analysis_reports_by_name now delegates (deprecated) to
    # AssetMaker.get_assets_by_name, which is listed; see test_issue165_replacements.py.
])
async def test_name_is_sent_as_filter_string(cls, method):
    captured = {}

    async def fake_get_name_request(url, **kwargs):
        captured.update(kwargs)
        return []

    client = cls.__new__(cls)
    client.platform_url = "https://localhost:9443"
    client.view_server = "qs-view-server"
    client._async_get_name_request = fake_get_name_request

    await getattr(cls, method)(cast(Any, client), "QN::Example")

    assert captured["filter_string"] == "QN::Example"
    assert "name" not in captured
