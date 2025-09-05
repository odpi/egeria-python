from pyegeria._output_formats import select_output_format_set


def test_select_default_formats():
    fmt = select_output_format_set("Default", "DICT")
    assert isinstance(fmt, dict)
    assert "formats" in fmt


def test_select_terms_formats():
    fmt = select_output_format_set("Terms", "LIST")
    # Fallback to some dict even if LIST specifics vary
    assert isinstance(fmt, dict)
    assert fmt.get("target_type") in ("Term", "Terms", None)
