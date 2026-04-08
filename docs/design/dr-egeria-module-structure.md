# Dr.Egeria — Module Structure & Processing Flow

This document provides a visual reference for the `md_processing` subsystem and its relationships to the `commands/` CLI layer and the `pyegeria` SDK.

---

## Module Dependency Map

```mermaid
graph TD
    subgraph CLI["CLI Layer  (commands/)"]
        CLI_ENTRY["commands/cat/dr_egeria.py\n@click process_markdown_file"]
    end

    subgraph CORE["Orchestrator  (md_processing/)"]
        DR["md_processing/dr_egeria.py\nprocess_md_file_v2()"]
    end

    subgraph V2["v2 Engine  (md_processing/v2/)"]
        EXT["extraction.py\nUniversalExtractor\nDrECommand"]
        PARSE["parsing.py\nAttributeFirstParser"]
        DISP["dispatcher.py\nV2Dispatcher"]
        BASE["processors.py\nAsyncBaseCommandProcessor"]
        CONST["md_processing_utils/\nmd_processing_constants.py\nCOMMAND_DEFINITIONS"]
        JSON["data/compact_commands/\ncommands_*.json"]

        subgraph PROC["Domain Processors"]
            GLOSS["glossary.py\nTermProcessor\nTermRelationshipProcessor"]
            DD["data_designer.py\nDataFieldProcessor\nDataClassProcessor\nDataValueSpecificationProcessor\n…"]
            SA["solution_architect.py\nBlueprintProcessor\nComponentProcessor\nSupplyChainProcessor\n…"]
            CM["collection_manager_processor.py\nCollectionManagerProcessor\nCSVElementProcessor\nCollectionLinkProcessor"]
            GOV["governance.py\nGovernanceProcessor\nGovernanceLinkProcessor\nGovernanceContextProcessor"]
            PROJ["project.py\nProjectProcessor\nProjectLinkProcessor"]
            FB["feedback.py\nFeedbackProcessor\nTagProcessor\nExternalReferenceProcessor\nFeedbackLinkProcessor"]
            VIEW["view.py\nViewProcessor"]
        end
    end

    subgraph SDK["pyegeria SDK"]
        TECH["egeria_tech_client.py\nEgeriaTech (lazy facade)"]
        OMVS["omvs/*\nDataDesigner\nGlossaryManager\nCollectionManager\n…"]
        BSC["core/_base_server_client.py\nBaseServerClient\n_async_make_request()"]
        SC["core/_server_client.py\nServerClient\n_async_new_relationship_request()\n…"]
    end

    EGERIA[("Egeria Server\n(HTTPS REST API)")]

    CLI_ENTRY -->|"asyncio.run()"| DR
    DR -->|"extract_commands()"| EXT
    DR -->|"dispatch_batch()"| DISP
    DR -.->|"monkey-patch\n(--debug only)"| BSC
    DISP -->|"dispatch()"| BASE
    BASE -->|"parse()"| PARSE
    BASE -->|"apply_changes()"| PROC
    PARSE -->|"resolve / validate"| TECH
    PROC -->|"_async_* SDK calls"| TECH
    CONST -->|"loads"| JSON
    PARSE -->|"get_command_spec()"| CONST
    DISP -->|"register / route"| CONST
    TECH -->|"delegates to"| OMVS
    OMVS -->|"inherits"| SC
    SC -->|"inherits"| BSC
    BSC -->|"HTTPS"| EGERIA
```

---

## Processing Flow (Sequence)

```mermaid
sequenceDiagram
    actor User
    participant CLI  as commands/cat/dr_egeria.py
    participant ORCH as md_processing/dr_egeria.py
    participant EXT  as UniversalExtractor
    participant DISP as V2Dispatcher
    participant PROC as AsyncBaseCommandProcessor
    participant PRSR as AttributeFirstParser
    participant SDK  as EgeriaTech / OMVS
    participant EGERIA as Egeria Server

    User->>CLI: hey_egeria cat process-markdown-file --input-file X.md [--validate|--process] [--advanced] [--debug]
    CLI->>ORCH: asyncio.run(process_md_file_v2(..., debug=...))

    opt debug=True
        ORCH->>SDK: monkey-patch BaseServerClient._async_make_request
        Note over ORCH,SDK: wrapper prints URL, call-chain, and body<br/>for every HTTP request
    end

    ORCH->>EXT: extract_commands(content)
    EXT-->>ORCH: List[DrECommand]

    ORCH->>DISP: register processors
    ORCH->>DISP: dispatch_batch(commands, context)

    loop for each DrECommand (sequential)
        DISP->>PROC: processor_cls(client, command, context)
        PROC->>PRSR: await parse()
        PRSR->>SDK: resolve valid-values / GUIDs
        SDK->>EGERIA: GET …
        EGERIA-->>SDK: response
        SDK-->>PRSR: resolved data
        PRSR-->>PROC: parsed_output

        PROC->>SDK: await fetch_as_is()
        SDK->>EGERIA: GET … (by QN or GUID)
        EGERIA-->>SDK: element or 404
        SDK-->>PROC: as_is_element (or None)

        alt directive == validate
            PROC-->>DISP: validation report (no Egeria writes)
        else directive == process
            opt debug=True
                PROC->>PROC: print "══ DEBUG CMD: Verb Object … ══"
            end
            PROC->>SDK: await apply_changes()  (create / update / link)
            SDK->>EGERIA: POST …
            opt debug=True
                Note over SDK,EGERIA: _debug_make_request intercepts:<br/>prints Method, URL, call-chain, body
            end
            EGERIA-->>SDK: GUID / 200 OK
            SDK-->>PROC: result
            PROC-->>DISP: result dict
        end
    end

    DISP-->>ORCH: List[result dicts]
    ORCH->>ORCH: build summary table + assemble output file
    ORCH->>User: Rich summary table + (optionally) output .md file

    opt debug=True
        ORCH->>SDK: restore original BaseServerClient._async_make_request
    end
```

---

## Key Data Structures

### `DrECommand` (extraction.py)

| Field | Type | Description |
|-------|------|-------------|
| `verb` | `str` | Canonical verb, e.g. `Create`, `Link` |
| `object_type` | `str` | Canonical object type, e.g. `Data Field` |
| `source_verb` | `str` | Verb exactly as written in the Markdown header |
| `source_object_type` | `str` | Object type exactly as written |
| `attributes` | `dict` | Raw `label → raw_value` mapping |
| `raw_block` | `str` | The complete original Markdown block |
| `is_command` | `bool` | `False` for non-command prose blocks |

### `parsed_output` (from `AttributeFirstParser.parse()`)

| Field | Type | Description |
|-------|------|-------------|
| `attributes` | `dict[str, AttrData]` | Parsed + validated attribute map |
| `qualified_name` | `str` | Resolved qualified name |
| `display_name` | `str` | Human-readable name |
| `guid` | `str \| None` | GUID if element already exists |
| `exists` | `bool` | Whether element was found in Egeria |
| `valid` | `bool` | Whether all required attributes parsed OK |
| `errors` | `list[str]` | Blocking errors (prevent execution) |
| `warnings` | `list[str]` | Non-blocking warnings |

### `context` dict (threaded through all processors)

| Key | Type | Description |
|-----|------|-------------|
| `directive` | `str` | `display`, `validate`, or `process` |
| `input_file` | `str` | Source file path |
| `request_id` | `str` | UUID for this run |
| `debug` | `bool` | Whether debug mode is active |
| `planned_elements` | `set[str]` | QNs of elements created earlier in the same document |

---

## Processor Hierarchy

```mermaid
classDiagram
    class AsyncBaseCommandProcessor {
        +client: EgeriaTech
        +command: DrECommand
        +context: dict
        +parsed_output: dict
        +execute() dict
        +apply_changes()* str
        +fetch_as_is()* dict
        +validate_only() str
        +render_result_markdown(guid) str
        +resolve_element_guid(name) str
    }

    AsyncBaseCommandProcessor <|-- TermProcessor
    AsyncBaseCommandProcessor <|-- TermRelationshipProcessor
    AsyncBaseCommandProcessor <|-- DataFieldProcessor
    AsyncBaseCommandProcessor <|-- DataClassProcessor
    AsyncBaseCommandProcessor <|-- DataValueSpecificationProcessor
    AsyncBaseCommandProcessor <|-- LinkDataFieldProcessor
    AsyncBaseCommandProcessor <|-- DataStructureProcessor
    AsyncBaseCommandProcessor <|-- DataCollectionProcessor
    AsyncBaseCommandProcessor <|-- BlueprintProcessor
    AsyncBaseCommandProcessor <|-- ComponentProcessor
    AsyncBaseCommandProcessor <|-- SupplyChainProcessor
    AsyncBaseCommandProcessor <|-- SolutionLinkProcessor
    AsyncBaseCommandProcessor <|-- CollectionManagerProcessor
    AsyncBaseCommandProcessor <|-- CollectionLinkProcessor
    AsyncBaseCommandProcessor <|-- ProjectProcessor
    AsyncBaseCommandProcessor <|-- GovernanceProcessor
    AsyncBaseCommandProcessor <|-- GovernanceLinkProcessor
    AsyncBaseCommandProcessor <|-- FeedbackProcessor
    AsyncBaseCommandProcessor <|-- ExternalReferenceProcessor
    AsyncBaseCommandProcessor <|-- FeedbackLinkProcessor
    AsyncBaseCommandProcessor <|-- ViewProcessor
```

---

## Compact Command JSON → Runtime Mapping

```mermaid
flowchart LR
    JSON["data/compact_commands/\ncommands_data_designer.json\n(attribute specs, valid_values,\ndefault_value, property_name…)"]

    subgraph RT["Runtime"]
        CONST["md_processing_constants.py\nCOMMAND_DEFINITIONS dict"]
        PARSE["AttributeFirstParser\n• valid_values validation\n• default injection\n• camelCase mapping"]
        DISP["V2Dispatcher\n• register() by command name\n• fuzzy preposition strip\n• verb-group alignment"]
        PROC["Processor.apply_changes()\n• reads parsed_output.attributes\n• builds SDK request body"]
    end

    SDK["pyegeria OMVS methods\n_async_create_*\n_async_link_*\netc."]

    JSON -->|"load_commands()"| CONST
    CONST --> PARSE
    CONST --> DISP
    PARSE --> PROC
    PROC --> SDK
```

---

## File Reference

| File | Role |
|------|------|
| `commands/cat/dr_egeria.py` | Click CLI entry-point; `--validate` / `--process` shortcut flags, `--advanced`, `--debug` |
| `md_processing/dr_egeria.py` | Async orchestrator: extraction → dispatch → output; owns debug patch/restore |
| `md_processing/v2/extraction.py` | `UniversalExtractor` — produces `DrECommand` list from raw Markdown |
| `md_processing/v2/parsing.py` | `AttributeFirstParser` — async, spec-driven, with server-side validation cache |
| `md_processing/v2/dispatcher.py` | `V2Dispatcher` — sequential batch dispatch; fuzzy matching; planned-element tracking |
| `md_processing/v2/processors.py` | `AsyncBaseCommandProcessor` — base class: parse → validate → fetch → apply |
| `md_processing/v2/data_designer.py` | Data Designer domain processors (Data Field, Data Class, Data Value Specification, …) |
| `md_processing/v2/glossary.py` | Glossary / Term processors |
| `md_processing/v2/solution_architect.py` | Blueprint, Component, Supply-Chain processors |
| `md_processing/v2/collection_manager_processor.py` | Collection, Product, Agreement processors |
| `md_processing/v2/governance.py` | Governance definition processors |
| `md_processing/v2/project.py` | Project / Campaign / Task processors |
| `md_processing/v2/feedback.py` | Comment, Tag, External Reference, Like, Rating processors |
| `md_processing/v2/view.py` | `ViewProcessor` — runs pyegeria report engine |
| `md_processing/v2/rewriters.py` | `CommandRewriter` — upsert / verb-normalisation pre-pass |
| `md_processing/md_processing_utils/md_processing_constants.py` | `COMMAND_DEFINITIONS` registry; `load_commands()` |
| `md_processing/data/compact_commands/` | JSON specs driving parsing, validation and SDK call routing |
| `pyegeria/egeria_tech_client.py` | `EgeriaTech` lazy facade over all OMVS subclients |
| `pyegeria/core/_base_server_client.py` | `BaseServerClient._async_make_request` — HTTP transport layer; target of debug patch |

