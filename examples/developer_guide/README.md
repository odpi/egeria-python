<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# examples/developer_guide

Runnable examples for the
[Developer Guide: Building Egeria Applications in Python with pyegeria and Textual](../../docs/developer_guide_pyegeria_textual.md).
Each step builds on the previous one.

| File | Demonstrates |
|---|---|
| `common.py` | Reading connection settings from pyegeria's configuration; a glossary query that returns GUIDs. |
| `step1_hello_pyegeria.py` | pyegeria only: connect, log in, list glossaries, handle `PyegeriaException`. |
| `step2_glossary_browser.py` | A Textual app: `DataTable`, bindings, CSS, and a thread worker that loads data from Egeria. |
| `step3_glossary_comments.py` | Acting on the selected row: a `ModalScreen` pre-filled with the row's GUID, returning a result to a callback that adds a comment in Egeria. **Writes to Egeria.** |
| `capture_screenshots.py` | Regenerates the guide's screenshots in `docs/images/developer-guide/` by driving these examples and the My Profile app headlessly. Read-only. |

All of them need a running Egeria. The
[Egeria Workspaces quick start](https://egeria-project.org/egeria-workspaces/quick-start/overview/)
provides one with the defaults these examples assume (`https://localhost:9443`,
`qs-view-server`, user `garygeeke`). Override them with a `.env` file or environment
variables, as described in the guide.

```bash
python examples/developer_guide/step1_hello_pyegeria.py
python examples/developer_guide/step2_glossary_browser.py
python examples/developer_guide/step3_glossary_comments.py
python examples/developer_guide/capture_screenshots.py
```

The scripts import `common.py` from their own folder, and Python puts the script's folder on
the import path, so they can be run from any working directory.
