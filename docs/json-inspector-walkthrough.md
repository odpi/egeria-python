# Walkthrough: Unified JSON Inspector for Egeria Surveyors

I have merged the `sniffer.py` and `inspector.py` logic into a single, unified module: `json_inspector.py`. This module provides a one-stop-shop for identifying various JSON file types for Egeria surveyors.

## Changes Made

### Unified Core Logic

- Created [json_inspector.py](file:///Users/dwolfson/antigravity-pyegeria/egeria-python/examples/surveys/json_inspector.py):
  - **MCP Support**: Detects and parses MCP tool and server configurations.
  - **AI/ML Support**: Detects AI profiles like Model Tuning, MLflow, and SageMaker jobs using key-based signatures.
  - **Functional Design**: Uses a clean `identify_file` entry point.

### Verification

- Created [test_json_inspector.py](file:///Users/dwolfson/antigravity-pyegeria/egeria-python/examples/surveys/test_json_inspector.py):
  - Combined and expanded tests for both MCP and AI profiles.
  - All tests passed.

### Documentation & Cleanup

- Updated [README.md](file:///Users/dwolfson/antigravity-pyegeria/egeria-python/examples/surveys/README.md) with the new module name and detailed AI profile documentation.
- Cleanup: Deleted the old `sniffer.py`, `inspector.py`, and `test_inspector.py` files.

### Enhanced Survey Crawler

- Modified [survey_crawler.py](file:///Users/dwolfson/antigravity-pyegeria/egeria-python/examples/surveys/survey_crawler.py):
  - **CSV Output**: Added `--csv` flag to save results to a CSV file.
  - **Egeria Integration**: Added `--egeria` flag to automatically create `SurveyReport` elements in Egeria.
  - **Directory Linking**: Uses `AssetMaker` to find the `FileFolder` GUID and links the report using the `ReportSubject` relationship.

## Test Results

### Unit Tests

Ran `pytest examples/surveys/test_json_inspector.py`:

```
examples/surveys/test_json_inspector.py ......                                                                            [100%]
6 passed in 0.53s
```

### CSV Verification

Ran `python examples/surveys/survey_crawler.py test_scan --csv test_results.csv`:

```
           Survey Identification Results for: test_scan            
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ File Name   ┃ Relative Path ┃ Artifact Type     ┃ Display Label ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ server.json │ server.json   │ mcp_server_config │ N/A           │
│ tools.json  │ tools.json    │ mcp_tool_config   │ N/A           │
└─────────────┴───────────────┴───────────────────┴───────────────┘
Successfully wrote results to test_results.csv
```

The CSV content was verified:

```csv
name,path,type,label
server.json,server.json,mcp_server_config,N/A
tools.json,tools.json,mcp_tool_config,N/A
```

## How to Use

### Inspector Library

```python
from json_inspector import identify_file

# Identify an MCP config
summary = identify_file("docs/pyegeria-mcp.json")
```

### Visualization & Reporting

- Modified [survey_crawler.py](file:///Users/dwolfson/antigravity-pyegeria/egeria-python/examples/surveys/survey_crawler.py):
  - **Markdown Table**: Added `--markdown` flag to output results as a clean markdown table.
  - **Vega-Lite Integration**: Added `--report` flag to generate a comprehensive markdown report with embedded Vega-Lite charts.
  - **File Breakdown Chart**: Displays a donut chart comparing identified JSON files to other files.
  - **Artifact Histogram**: Displays a bar chart showing the distribution of identified JSON types.

## Verification

### Markdown Table

Ran `python examples/surveys/survey_crawler.py test_scan --markdown`:

```markdown
| File Name | Relative Path | Artifact Type | Display Label |
| :--- | :--- | :--- | :--- |
| server.json | server.json | mcp_server_config | N/A |
| tools.json | tools.json | mcp_tool_config | N/A |
```

### Full Report (Vega-Lite)

Ran `python examples/surveys/survey_crawler.py test_scan --report test_report.md`:

- Generated a file with:
  - Summary statistics (Total Files vs. JSON Identified).
  - A `vega-lite` block for the File Breakdown chart.
  - A `vega-lite` block for the Artifact Type Histogram.
  - The detailed findings table.

## How to Use

### Basic scan

```bash
python examples/surveys/survey_crawler.py examples
```

### Generate Visual Report

```bash
python examples/surveys/survey_crawler.py [path] --report survey_report.md
```
