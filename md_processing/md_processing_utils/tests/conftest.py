import csv
import json
from pathlib import Path

import pytest

from md_processing.md_processing_utils.common_md_utils import clear_element_dictionary
from md_processing.md_processing_utils.md_processing_constants import COMMAND_DEFINITIONS, load_commands


@pytest.fixture(autouse=True, scope="session")
def load_command_definitions():
    load_commands("commands.json")
    command_specs = COMMAND_DEFINITIONS.setdefault("Command Specifications", {})
    commands_dir = Path("md_processing/data/commands")
    for path in commands_dir.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        specs = data.get("Command Specifications", {})
        command_specs.update(specs)


@pytest.fixture(autouse=True)
def reset_element_dictionary():
    clear_element_dictionary()


_SKIP_REPORT = []
_MISSING_SPEC_REPORT = []
_FAILURE_REPORT = []


@pytest.fixture
def skip_reporter(request):
    test_file = str(request.fspath)
    test_name = request.node.name

    def _skip(command: str, reason: str) -> None:
        _SKIP_REPORT.append((command, reason, test_file, test_name))
        pytest.skip(f"{command}: {reason}")

    return _skip


@pytest.fixture
def missing_spec_reporter(request):
    test_file = str(request.fspath)
    test_name = request.node.name

    def _record(command: str) -> None:
        _MISSING_SPEC_REPORT.append((command, test_file, test_name))
    return _record


def pytest_runtest_logreport(report):
    if report.when != "call" or not report.failed:
        return
    test_file = report.location[0] if report.location else ""
    test_name = report.location[2] if report.location else report.nodeid
    details = str(report.longrepr).splitlines()[0] if report.longrepr else ""
    _FAILURE_REPORT.append((test_file, test_name, report.nodeid, details))


def pytest_sessionfinish(session, exitstatus):
    if _SKIP_REPORT:
        report_path = Path("md_processing/md_processing_utils/tests/skip_report.csv")
        with report_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["command", "reason", "test_file", "test_name"])
            for command, reason, test_file, test_name in sorted(_SKIP_REPORT):
                writer.writerow([command, reason, test_file, test_name])

    if _MISSING_SPEC_REPORT:
        missing_path = Path("md_processing/md_processing_utils/tests/missing_spec_report.csv")
        with missing_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["command", "test_file", "test_name"])
            for command, test_file, test_name in sorted(set(_MISSING_SPEC_REPORT)):
                writer.writerow([command, test_file, test_name])

    if _FAILURE_REPORT:
        failures_path = Path("md_processing/md_processing_utils/tests/failure_report.csv")
        with failures_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["test_file", "test_name", "nodeid", "details"])
            for test_file, test_name, nodeid, details in _FAILURE_REPORT:
                writer.writerow([test_file, test_name, nodeid, details])
