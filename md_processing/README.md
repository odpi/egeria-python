<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# md_processing

Dr.Egeria: the markdown-driven command pipeline for automating Egeria
operations via markdown files.

| File/folder | Role |
|---|---|
| `dr_egeria.py` | Entry point; `setup_dispatcher()` (wires every command to its processor); `process_md_file_v2()`. |
| `v2/` | The v2 pipeline itself — extraction, dispatch, and per-family processors (own `README.md`). |
| `md_processing_utils/` | Shared parsing/body-building utilities used by `v2/` (own `README.md`). |
| `data/` | Compact command JSON specs and the generated report-spec registry (own `README.md`). |

Full pipeline for one `process_md_file_v2()` call:

```
Markdown file
  -> UniversalExtractor (v2/extraction.py): splits on ## headers/horizontal rules -> DrECommand objects
  -> setup_dispatcher() (dr_egeria.py): loads COMMAND_DEFINITIONS, registers {command_key -> ProcessorClass}
  -> V2Dispatcher.dispatch_batch() (v2/dispatcher.py): alias resolution -> fuzzy verb-stripping -> subtype fallbacks
  -> AsyncBaseCommandProcessor.execute() (v2/processors.py): parse -> derive qualified name -> fetch_as_is
     -> CommandRewriter-style Create<->Update transition -> resolve reference GUIDs -> validate_only()
     -> apply_changes() (abstract, per processor) -> render_result_markdown(guid)
  -> dr_egeria.py: assemble final_output, write processed-*.md
```

CLI usage and the full command reference live in `docs/dr_egeria_manual.md`
and the root `CLAUDE.md`/`AGENTS.md`. Design-history documents (not
necessarily current) are in `docs/design/`.
