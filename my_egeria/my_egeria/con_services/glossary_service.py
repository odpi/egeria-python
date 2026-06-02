# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Shim module to support tests that monkeypatch:
    services.glossary_service.GlossaryAuthorView

The tests only need this symbol to exist so monkeypatch can replace it.
"""

# Provide a very permissive placeholder that accepts any args and does nothing.
class GlossaryAuthorView:
    def __init__(self, *args, **kwargs):
        pass
