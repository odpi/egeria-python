# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
ISSUE-134: with PYEGERIA_ENABLE_LOGGER_CATCH on, @dynamic_catch wrapped methods
in loguru's logger.catch, whose default reraise=False logged the exception and
returned None -- a failed read looked like an empty one. The exception must
still reach the caller, sync and async.
"""
import pytest

from pyegeria.core import utils


@pytest.fixture
def logger_catch_on(monkeypatch):
    monkeypatch.setattr(utils.app_settings.Debug, "enable_logger_catch", True)


def test_sync_failure_still_raises(logger_catch_on):
    @utils.dynamic_catch
    def boom():
        raise ValueError("server said no")

    with pytest.raises(ValueError, match="server said no"):
        boom()


@pytest.mark.asyncio
async def test_async_failure_still_raises(logger_catch_on):
    @utils.dynamic_catch
    async def boom():
        raise ValueError("server said no")

    with pytest.raises(ValueError, match="server said no"):
        await boom()


def test_success_value_unchanged(logger_catch_on):
    @utils.dynamic_catch
    def ok():
        return "value"

    assert ok() == "value"
