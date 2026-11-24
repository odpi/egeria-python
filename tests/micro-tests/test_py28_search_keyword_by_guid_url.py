"""PY-28: get-search-keyword-by-guid POSTs .../classification-explorer/search-keywords/{guid}/retrieve
(ClassificationExplorerResource: @PostMapping("/search-keywords/{searchKeywordGUID}/retrieve")); the bare
.../search-keywords/{guid} answered 404."""
import asyncio
from unittest.mock import AsyncMock

from pyegeria.core._server_client import ServerClient

GUID = "6b0b3c8e-1c36-4f0e-8a4e-111111111111"


class _Stub(ServerClient):
    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return "http://x/api/open-metadata/"


def test_the_url_ends_with_retrieve():
    obj = _Stub.__new__(_Stub)
    obj._async_get_guid_request = AsyncMock(return_value={"element": {}})
    asyncio.run(ServerClient._async_get_search_keyword_by_guid(obj, GUID))
    url = obj._async_get_guid_request.call_args.args[0]
    assert url == f"http://x/api/open-metadata/classification-explorer/search-keywords/{GUID}/retrieve", url


def test_the_other_search_keyword_urls_are_unchanged():
    import inspect
    src = inspect.getsource(ServerClient)
    for tail in ("search-keywords/{keyword_guid}/update", "search-keywords/{keyword_guid}/remove",
                 "search-keywords/by-keyword", "search-keywords/by-search-string"):
        assert tail in src, tail
