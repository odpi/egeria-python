# JSON Inspector

This directory contains the `json_inspector.py` module, which is used to identify and parse JSON files for Egeria surveyors.

## Purpose

The `json_inspector.py` module provides a way to:

1. **Identify** if a JSON file matches a known type (e.g., discovery or configuration files).
2. **Summarize** the contents of the file if identified, providing key information like server names, tool names, parameters, or AI/ML metadata.

## Files

- [json_inspector.py](file:///Users/dwolfson/antigravity-pyegeria/egeria-python/examples/surveys/json_inspector.py): The core implementation of the file identification and parsing logic.
- [survey_crawler.py](file:///Users/dwolfson/antigravity-pyegeria/egeria-python/examples/surveys/survey_crawler.py): A CLI script to recursively scan directories and report JSON file types.
- [test_json_inspector.py](file:///Users/dwolfson/antigravity-pyegeria/egeria-python/examples/surveys/test_json_inspector.py): Unit tests for the inspector.

## Supported File Types

### MCP Tool Configuration

Detected by the presence of a top-level `tools` key (list). The summary includes:

- `mcp_server_name`
- `tools`: A list of tools with their purpose and parameters.

### AI/ML Profiles

Detected by specific signatures (key patterns) in the JSON structure. Supported profiles include:

- **Model Tuning Parameters**: Detected by `learning_rate`, `batch_size`, `epochs`.
- **MLflow Run Trace**: Detected by `info`, `data`, `metrics`, `params`.
- **Model Quality Metrics**: Detected by `accuracy`, `f1_score`, `precision`, `recall`.
- **SageMaker Job Config**: Detected by `TrainingJobName`, `HyperParameters`, `InputDataConfig`.
- **ChatML Fine-tuning Data**: Detected by `messages`, `role`, `content`.

The summary for AI profiles includes:

- `artifact_type` (e.g., `mlflow_run`)
- `display_label`
- `element_count`
- `detected_fields`
- `preview`: A short snippet of the raw data.

## Usage Example

```python
from json_inspector import identify_file

# Identify a file
filepath = "path/to/your/file.json"
summary = identify_file(filepath)

if summary:
    print(f"Identified Type: {summary.get('artifact_type')}")
    print(f"Label: {summary.get('display_label', 'N/A')}")
else:
    print("File type not recognized.")
```

## Survey Crawler Usage

The `survey_crawler.py` script recursively scans a directory for JSON files and identifies their types. It can optionally write results to a CSV file and integrate with Egeria to create Survey Reports.

### Basic Usage

```bash
# Basic scan with beautiful terminal output
python examples/surveys/survey_crawler.py [path_to_scan]

# Scan and save results to CSV
python examples/surveys/survey_crawler.py [path_to_scan] --csv results.csv

# Display results as a markdown table
python examples/surveys/survey_crawler.py [path_to_scan] --markdown

# Generate a full markdown report with Vega-Lite charts
python examples/surveys/survey_crawler.py [path_to_scan] --report survey_report.md

# Scan and integrate with Egeria (creates SurveyReports)
python examples/surveys/survey_crawler.py [path_to_scan] --egeria --url https://egeria:9443 --user pete
```

### Egeria Integration Options

- `--egeria`: Enable integration.
- `--url`: Egeria platform URL (default: `https://localhost:9443`).
- `--server`: View server name (default: `view-server`).
- `--user`: User ID for authentication (default: `pete`).

### Reporting Options

- `--markdown`: Prints the findings as a clean markdown table in the console.
- `--report <path>`: Generates a comprehensive markdown report that includes:
  - Summary statistics.
  - **Vega-Lite Graphical Breakdown**: A donut chart showing the ratio of identified JSON files to others.
  - **Vega-Lite Histogram**: A bar chart showing the distribution of identified artifact types.
  - Detailed findings table.

**Environment Variables:**
The script also honors environment variables: `EGERIA_PLATFORM_URL`, `EGERIA_VIEW_SERVER`, and `EGERIA_USER_ID`.

## Running Tests

To run the tests for the inspector:

```bash
pytest examples/surveys/test_json_inspector.py
```
