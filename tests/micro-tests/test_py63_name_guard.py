"""PY-63: no by-name or by-type helper ever sends a null, missing or "*" filter (Egeria refuses it with HTTP 400)."""
import asyncio
import importlib
import inspect
import json
import pkgutil
from unittest.mock import AsyncMock, MagicMock

import pytest

import pyegeria.omvs as omvs_pkg
from pyegeria import PyegeriaInvalidParameterException
from pyegeria.core._server_client import ServerClient
from pyegeria.omvs.runtime_manager import RuntimeManager

# helpers whose key is in the URL path, not the filter (name_required=False)
PATH_KEYED = {"_async_get_catalog_targets", "_async_get_tech_types_for_open_metadata_type",
              "_async_get_endpoints_for_asset"}
# not by-name style: get_name_request is used for their lookups but the first parameter is not a name/type filter
NOT_BY_NAME = PATH_KEYED


def _name_helpers():
    """(class, helper name) for every `_async_get_*` method whose source calls `_async_get_name_request`."""
    found = []
    for mod in pkgutil.iter_modules(omvs_pkg.__path__):
        module = importlib.import_module(f"pyegeria.omvs.{mod.name}")
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ != module.__name__:
                continue
            for name, fn in cls.__dict__.items():
                if name.startswith("_async_get_") and inspect.iscoroutinefunction(inspect.unwrap(fn)):
                    try:
                        src = inspect.getsource(inspect.unwrap(fn))
                    except (OSError, TypeError):
                        continue
                    if "self._async_get_name_request(" in src:
                        found.append((cls, name))
    # the core ServerClient ones are inherited by every OMVS class: test them once
    for name in ("_async_get_note_logs_by_name", "_async_get_tags_by_name", "_async_get_search_keyword_by_keyword"):
        found.append((ServerClient, name))
    return sorted(set(found), key=lambda t: (t[0].__name__, t[1]))


HELPERS = _name_helpers()


def _lenient(self, name):
    """A stub client: any URL root or setting the helper reads and the test did not set is a placeholder."""
    if name.startswith("__"):
        raise AttributeError(name)
    return "http://x"


def _stubbed(cls):
    cls = type(cls.__name__, (cls,), {"__getattr__": _lenient})
    obj = cls.__new__(cls)
    resp = MagicMock()
    resp.json.return_value = {"elements": []}
    obj._async_make_request = AsyncMock(return_value=resp)
    obj._async_refresh_report_spec = AsyncMock(return_value=None)
    return obj


def _call(obj, name, key):
    fn = getattr(obj, name)
    sig = inspect.signature(fn)
    params = [p for p in sig.parameters.values() if p.name != "self"]
    kwargs = {}
    for p in params:
        if p.name in ("filter_string", "name", "filter") or p.name == params[0].name:
            kwargs[p.name] = key
            break
    return asyncio.run(fn(**kwargs))


def test_the_reflection_found_the_helpers():
    assert len(HELPERS) > 55, len(HELPERS)


@pytest.mark.parametrize("cls,name", [h for h in HELPERS if h[1] not in NOT_BY_NAME],
                         ids=[f"{c.__name__}.{n[7:]}" for c, n in HELPERS if n not in NOT_BY_NAME])
@pytest.mark.parametrize("key", [None, "", "*"])
def test_no_helper_sends_a_null_missing_or_star_filter(cls, name, key):
    obj = _stubbed(cls)
    # helpers with their own default (platforms, by_type) first apply it; none may reach Egeria without a name
    try:
        _call(obj, name, key)
    except PyegeriaInvalidParameterException:
        # refused before sending: by the helper's own check or by PY-63's guard
        obj._async_make_request.assert_not_called()
        return
    except Exception:
        # an unrelated stub problem after the request was built still must not have sent a null filter
        pass
    for call in obj._async_make_request.call_args_list:
        body = json.loads(call.args[2]) if len(call.args) > 2 and isinstance(call.args[2], str) else {}
        assert body.get("filter") not in (None, "", "*") or "filter" not in body and False, (name, body)


def test_the_refusal_names_the_helper_the_key_and_the_find():
    obj = _stubbed(ServerClient)
    with pytest.raises(PyegeriaInvalidParameterException) as info:
        asyncio.run(obj._async_get_tags_by_name("*"))
    text = str(info.value)
    assert "get_tags_by_name needs a name" in text and "find_tags" in text and "list all" in text


def test_a_non_name_key_says_which_key_it_needs():
    from pyegeria.omvs.connection_maker import ConnectionMaker
    obj = _stubbed(ConnectionMaker)
    with pytest.raises(PyegeriaInvalidParameterException) as info:
        asyncio.run(obj._async_get_endpoints_by_network_address(None))
    assert "needs a network address" in str(info.value)


@pytest.mark.parametrize("module,cls,helper,real", [
    ("pyegeria.core._server_client", ServerClient, "_async_get_tags_by_name", "tag1"),
    ("pyegeria.omvs.actor_manager", "ActorManager", "_async_get_skills_by_name", "Python"),
    ("pyegeria.omvs.glossary_manager", "GlossaryManager", "_async_get_terms_by_name", "Term A"),
    ("pyegeria.omvs.asset_maker", "AssetMaker", "_async_get_assets_by_name", "My Asset"),
    ("pyegeria.omvs.project_manager", "ProjectManager", "_async_get_projects_by_name", "Proj"),
    ("pyegeria.omvs.runtime_manager", "RuntimeManager", "_async_get_servers_by_name", "qs-view-server"),
])
def test_a_real_name_is_still_sent(module, cls, helper, real):
    klass = cls if not isinstance(cls, str) else getattr(importlib.import_module(module), cls)
    obj = _stubbed(klass)
    try:
        _call(obj, helper, real)
    except PyegeriaInvalidParameterException:
        raise
    except Exception:
        pass
    assert obj._async_make_request.called
    body = json.loads(obj._async_make_request.call_args.args[2])
    assert body["filter"] == real


def test_the_path_keyed_helpers_still_send_without_a_filter():
    from pyegeria.omvs.automated_curation import AutomatedCuration
    obj = _stubbed(AutomatedCuration)
    obj.ref_curation_command_base = "http://x"
    try:
        asyncio.run(obj._async_get_catalog_targets("6b0b3c8e-1c36-4f0e-8a4e-111111111111"))
    except Exception:
        pass
    assert obj._async_make_request.called


# ── platforms keeps the PY-58 routing, and always sends a type ──
def test_platforms_star_calls_by_type_which_sends_the_default_type_never_null():
    obj = _stubbed(RuntimeManager)
    obj.default_platform_name = "Default Local OMAG Server Platform"
    obj.runtime_command_root = "http://x/runtime-manager"
    try:
        asyncio.run(RuntimeManager._async_get_platforms_by_name(obj, "*"))
    except Exception:
        pass
    assert obj._async_make_request.called
    sent = json.loads(obj._async_make_request.call_args.args[2])
    assert sent["filter"] == "OMAG Server Platform"
    assert obj._async_make_request.call_args.args[1].endswith("platforms/by-deployed-implementation-type")


def test_platforms_default_comes_before_the_guard():
    obj = _stubbed(RuntimeManager)
    obj.default_platform_name = "Default Local OMAG Server Platform"
    obj.runtime_command_root = "http://x/runtime-manager"
    try:
        asyncio.run(RuntimeManager._async_get_platforms_by_name(obj, None))
    except Exception:
        pass
    sent = json.loads(obj._async_make_request.call_args.args[2])
    assert sent["filter"] == "Default Local OMAG Server Platform"  # None took the default, then passed the guard


def test_the_platforms_docstring_says_all_platforms_of_the_default_type():
    assert "OF THE DEFAULT TYPE" in RuntimeManager._async_get_platforms_by_name.__doc__ or \
        "OF THE DEFAULT TYPE" in inspect.unwrap(RuntimeManager._async_get_platforms_by_name).__doc__
