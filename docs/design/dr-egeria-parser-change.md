# Proposal: Shift Dr.Egeria Markdown Syntax Hierarchy

This plan outlines the changes required to adjust the Dr.Egeria parsing and generation syntax so that:
- **`#` (Single Hash)**: Ignored by the parser; treated as standard Markdown document headers or comments.
- **`##` (Double Hash)**: Defines a Dr.Egeria Command.
- **`###` (Triple Hash)**: Defines a Command Attribute.

## Motivation
This change will allow users to comfortably use single-hash `#` headers to title their overarching Markdown documents or sections, reserving the `##` and `###` headers strictly for Dr.Egeria execution contexts.

## Proposed Changes

### 1. Update the Extraction Logic (`md_processing/v2/extraction.py`)
The `UniversalExtractor` determines how markdown text is split into command blocks and attributes.
- **Command Header Matching**: 
  - Update `self.cmd_header_rx` to match `## <Verb> <Object>`. 
  - Update `_split_into_blocks()` so that it looks for `line.startswith("## ")` instead of `line.startswith("# ")` when identifying block boundaries.
- **Attribute Header Matching**:
  - Update `_extract_attributes_from_block()` to use `^###\s+` in its regular expression instead of `^##\s+`.

### 2. Update Template Generation (`commands/tech/generate_md_cmd_templates.py`)
The generator needs to produce templates in the new syntax.
- **Command Titles**: Update `_generate_md_file_content()` and the console output equivalent to prefix commands with `## ` instead of `# `.
- **Attribute Titles**: Update `_write_attr_block()` and `_print_attr()` to prefix attributes with `### ` instead of `## `.

### 3. Documentation & Sample Data Migration
Existing Markdown files (smoke tests, templates, inbox documentation) will no longer parse correctly.
- Run `uv run gen_md_cmd_templates --usage-level Basic` and `--usage-level Advanced` to forcefully regenerate all built-in template files in the new syntax.
- Manually (or via script) update `sample-data/smoke_test_gov_officer.md` and `sample-data/smoke_test_terms_and_conditions.md` to shift all hashes down one level.
- Any Markdown files provided to users in the inbox (e.g. `dr_egeria_intro_*.md`) may need an update to reflect the new expected format.

## Verification Plan

### Automated Verification
- Re-run Pytest unit tests. Many tests under `tests/micro-tests/` that feed string literals to `UniversalExtractor` will fail and need to be updated to the new `##` and `###` syntax.
- Specifically, the parser tests in `tests/micro-tests/md_processing/v2/test_extraction.py` will serve as our primary validation that the single hash `#` is ignored and `##`/`###` parse correctly.

### Manual Verification
- Re-run validation on the smoke tests: `dr_egeria sample-data/smoke_test_gov_officer.md --validate` to ensure it parses successfully.

> [!WARNING] 
> **Breaking Change**: This is a breaking change for any existing user Markdown scripts. Users who have created their own `dr_egeria` markdown documents will need to run a quick search-and-replace to shift their headers down one level. 

Does this approach and scope of changes align with what you had in mind?
