"""
PY-30: a Dr.Egeria block whose headings are one level off ran less than its author meant, with no word why.
`# Delete Instance` (H1) was kept as prose, so the document ran 0 commands; `## Delete Method` (an attribute written
as H2) matched the command pattern and became a command of its own. UniversalExtractor.diagnose() now names both.
"""
from md_processing.v2.extraction import UniversalExtractor, _load_command_attributes

ATTRS = {"Delete Instance": ["Metadata Element GUID", "Delete Method", "Confirm Delete GUID"]}


def test_h1_command_heading_is_named():
    hints = UniversalExtractor("# Delete Instance\n\n## Metadata Element GUID\nabc\n").diagnose(ATTRS)
    assert any("'# Delete Instance' is an H1 heading" in h and "'## Delete Instance'" in h for h in hints)
    assert any("No Dr.Egeria command was found" in h for h in hints)


def test_attribute_written_as_h2_is_named():
    text = "## Delete Instance\n\n### Metadata Element GUID\nabc\n\n## Delete Method\nSOFT_DELETE\n"
    hints = UniversalExtractor(text).diagnose(ATTRS)
    assert hints == ["line 6: '## Delete Method' is an attribute of 'Delete Instance' written as a command heading. "
                     "Write it as '### Delete Method'."]


def test_a_correct_block_has_no_hints():
    text = "## Delete Instance\n### Metadata Element GUID\nabc\n### Delete Method\nSOFT_DELETE\n"
    assert UniversalExtractor(text).diagnose(ATTRS) == []


def test_two_real_commands_are_not_mistaken_for_attributes():
    text = "## Create Glossary\n### Display Name\nG\n\n## Create Term\n### Display Name\nT\n"
    attrs = {"Create Glossary": ["Display Name"], "Create Term": ["Display Name"]}
    assert UniversalExtractor(text).diagnose(attrs) == []


def test_prose_only_document_says_no_command():
    hints = UniversalExtractor("Some notes.\n\nMore notes.\n").diagnose({})
    assert hints == ["No Dr.Egeria command was found. A command is an H2 heading '## <Verb> <Object>' "
                     "followed by '### <Attribute>' lines."]


def test_without_specs_the_attribute_check_is_skipped_quietly():
    text = "## Delete Instance\n### Metadata Element GUID\nabc\n\n## Delete Method\nX\n"
    assert UniversalExtractor(text).diagnose({}) == []


def test_real_specs_load_and_carry_attribute_labels():
    attrs = _load_command_attributes()
    assert "Delete Method" in attrs.get("Delete Instance", [])
    assert "name" not in attrs.get("Delete Instance", [])


def test_a_shell_comment_in_a_code_fence_is_not_a_heading():
    text = "Set up:\n\n```bash\n# Create a virtual environment\npython -m venv .venv\n```\n\n## Create Glossary\n### Display Name\nG\n"
    attrs = {"Create Glossary": ["Display Name"]}
    assert UniversalExtractor(text).diagnose(attrs) == []


def test_tilde_fence_is_skipped_too():
    text = "~~~\n# Delete Instance\n~~~\n\n## Create Glossary\n### Display Name\nG\n"
    assert UniversalExtractor(text).diagnose({"Create Glossary": ["Display Name"], "Delete Instance": []}) == []


def test_h1_that_is_not_a_known_command_gets_no_hint_when_specs_are_loaded():
    text = "# Create Fantasy Thing\n\n## Create Glossary\n### Display Name\nG\n"
    assert UniversalExtractor(text).diagnose({"Create Glossary": ["Display Name"]}) == []


def test_real_specs_do_not_flag_a_tutorial_comment():
    text = "```bash\n# Create a virtual environment\n```\n# Create a virtual environment\n"
    hints = UniversalExtractor(text).diagnose()
    assert not any("Create a virtual environment" in h for h in hints)
