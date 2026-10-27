"""
A Create that Dr.Egeria rewrites to Update (the element already exists) must not carry the
spec defaults the parser filled in for the Create. A merge update would send them over the
stored values -- e.g. isNullable: true over a stored false. Egeria 6.3 keeps an omitted number
or flag (odpi/egeria#9389), so dropping the defaults is what preserves the current value.
"""
from md_processing.v2.extraction import DrECommand
from md_processing.v2.processors import AsyncBaseCommandProcessor


class _Processor(AsyncBaseCommandProcessor):
    async def apply_changes(self) -> str:
        return ""


def _processor(attributes: dict) -> _Processor:
    proc = _Processor(object(), DrECommand(verb="Create", object_type="Data Field", attributes={},
                                           raw_block="## Create Data Field\n"))
    proc.parsed_output = {"attributes": attributes}
    return proc


def test_defaults_dropped_but_user_values_and_control_flags_kept():
    attributes = {
        "Display Name": {"value": "Customer Id"},
        "Is Nullable": {"value": True, "is_default": True},
        "Position": {"value": 0, "is_default": True},
        "Length": {"value": 12},
        "Merge Update": {"value": True, "is_default": True},
    }
    _processor(attributes)._drop_create_defaults()
    assert set(attributes) == {"Display Name", "Length", "Merge Update"}


def test_no_attributes_is_a_no_op():
    proc = _processor({})
    proc._drop_create_defaults()
    assert proc.parsed_output["attributes"] == {}
