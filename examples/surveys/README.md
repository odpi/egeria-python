# JSON Inspector

This directory contains the `json_inspector.py` module, which is used to identify and parse JSON files for Egeria surveyors.

## Purpose

The `json_inspector.py` module provides a way to:

1. **Identify** if a JSON file matches a known type (e.g., discovery or configuration files).
2. **Summarize** the contents of the file if identified, providing key information like server names, tool names, parameters, or AI/ML metadata.

## Files

- [json_inspector.py](file:///Users/dwolfson/antigravity-pyegeria/egeria-python/examples/surveys/json_inspector.py): The core implementation of the file identification and parsing logic.
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

## Running Tests

To run the tests for the inspector:

```bash
pytest examples/surveys/test_json_inspector.py
```
