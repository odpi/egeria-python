from pyegeria.base_report_formats import select_report_spec


def test_select_default_formats():
    fmt = select_report_spec("Default", "DICT")
    assert isinstance(fmt, dict)
    assert "formats" in fmt


def test_select_terms_formats():
    fmt = select_report_spec("Terms", "LIST")
    # Fallback to some dict even if LIST specifics vary
    assert isinstance(fmt, dict)
    assert fmt.get("target_type") in ("Term", "Terms", None)
