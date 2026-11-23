"""PY-27: the content-status filter defaults to none, so Egeria returns ANY status (a null filter means any; an
element created without a status stores null). An explicit list is still sent unchanged."""
import asyncio
import inspect
import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from pyegeria.omvs.asset_maker import AssetMaker
from pyegeria.omvs.classification_explorer import ClassificationExplorer

ASYNC = [(AssetMaker, "_async_find_data_assets"), (AssetMaker, "_async_get_data_assets_by_category"),
         (ClassificationExplorer, "_async_find_authored_elements"),
         (ClassificationExplorer, "_async_find_authored_elements_by_category")]
SYNC = [(AssetMaker, "find_data_assets"), (AssetMaker, "get_data_assets_by_category"),
        (ClassificationExplorer, "find_authored_elements"), (ClassificationExplorer, "find_authored_elements_by_category")]


def _lenient(self, name):
    if name.startswith("__"):
        raise AttributeError(name)
    return "http://x"


def _stub(cls):
    cls = type(cls.__name__, (cls,), {"__getattr__": _lenient})
    obj = cls.__new__(cls)
    resp = MagicMock()
    resp.json.return_value = {"elements": []}
    obj._async_make_request = AsyncMock(return_value=resp)
    obj._async_refresh_report_spec = AsyncMock(return_value=None)
    return obj


def _body(cls, name, **kwargs):
    obj = _stub(cls)
    try:
        asyncio.run(getattr(obj, name)("x", **kwargs))
    except Exception:
        pass  # after the request was built; the body is what is under test
    assert obj._async_make_request.called, name
    call = obj._async_make_request.call_args
    return json.loads(call.args[2] if len(call.args) > 2 else call.kwargs["payload"])


@pytest.mark.parametrize("cls,name", ASYNC, ids=[n for _, n in ASYNC])
def test_the_default_body_has_no_content_status_filter(cls, name):
    body = _body(cls, name)
    assert "contentStatusList" not in body and "contentStatus" not in body, body


@pytest.mark.parametrize("cls,name", ASYNC, ids=[n for _, n in ASYNC])
def test_an_explicit_active_list_is_still_sent(cls, name):
    assert _body(cls, name, content_status_list=["ACTIVE"])["contentStatusList"] == ["ACTIVE"]


@pytest.mark.parametrize("cls,name", ASYNC, ids=[n for _, n in ASYNC])
def test_an_explicit_list_is_sent_unchanged(cls, name):
    assert _body(cls, name, content_status_list=["DRAFT", "ACTIVE"])["contentStatusList"] == ["DRAFT", "ACTIVE"]


@pytest.mark.parametrize("cls,name", ASYNC + SYNC, ids=[n for _, n in ASYNC + SYNC])
def test_the_signature_defaults_to_none_and_the_docs_say_any(cls, name):
    param = inspect.signature(getattr(cls, name)).parameters["content_status_list"]
    assert param.default is None
    doc = inspect.getdoc(getattr(cls, name)) or ""
    assert "any content status" in doc.lower() and 'default = ["ACTIVE"]' not in doc
