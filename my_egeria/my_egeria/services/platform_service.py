# Python
"""
Shim module to support tests that monkeypatch:
    services.egeria_connection.PlatformServices

The tests only need this symbol to exist so monkeypatch can replace it.
"""

class PlatformServices:
    def __init__(self, *args, **kwargs):
        pass

    def list_platforms(self):
        return []