import json
from pyegeria._output_format_models import Column, Format, FormatSet, FormatSetDict, save_format_sets_to_json, load_format_sets_from_json
from tempfile import NamedTemporaryFile


def test_build_format_set_dict_roundtrip():
    cols = [
        Column(name="Name", key="display_name"),
        Column(name="GUID", key="guid"),
    ]
    fmt = Format(types=["DICT", "LIST"], columns=cols)
    fset = FormatSet(target_type="Term", heading="Test", description="Test FS", formats=[fmt])
    fsd = FormatSetDict(**{"TestFS": fset})

    # Save and load through JSON
    with NamedTemporaryFile(mode="w+", suffix=".json", delete=True) as tf:
        save_format_sets_to_json(fsd, tf.name)
        tf.flush()
        reloaded = load_format_sets_from_json(tf.name)
        assert "TestFS" in reloaded
        assert reloaded["TestFS"].target_type == "Term"
        # Verify columns preserved
        first_cols = reloaded["TestFS"].formats[0].columns
        assert any(c.key == "display_name" for c in first_cols)
