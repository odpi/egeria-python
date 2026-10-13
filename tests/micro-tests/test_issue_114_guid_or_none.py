# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
ISSUE-114: get_guid_for_name signals a miss with a truthy sentinel string, so
`if not guid` reads a miss as found. guid_or_none turns a miss into None.
"""
import pytest

from pyegeria import guid_or_none
from pyegeria.core._globals import NO_ELEMENTS_FOUND, NO_ELEMENT_FOUND, NO_GUID_RETURNED


def test_guid_passes_through():
    g = "a7d4c3b2-1e0f-4a5b-9c8d-7e6f5a4b3c2d"
    assert guid_or_none(g) == g
    assert guid_or_none(f"  {g}\n") == g


@pytest.mark.parametrize("miss", [NO_ELEMENTS_FOUND, NO_ELEMENT_FOUND, NO_GUID_RETURNED,
                                  None, "", "   ", [], ["g1", "g2"], {"guid": "x"}])
def test_miss_is_none(miss):
    assert guid_or_none(miss) is None
