# Walkthrough - Performance Testing of `find_processes`

I have refactored `tests/action_perf.py` to systematically measure the performance impact of varying `include_only_relationships`, `relationship_page_size`, `graph_query_depth`, and `metadata_element_subtypes` in the `a_client.find_processes` method.

> [!NOTE]
> The tests were run using the `erinoverview` user and `activity_status_list=[]` to ensure a representative data set was retrieved. A total of 10 processes were used for these measurements.

## Test Results

### 1. Varying `include_only_relationships`

| Relationship Set | Latency (s) | Size (bytes) | Count |
| :--- | :---: | :---: | :---: |
| `[]` | 1.0965 | 17094 | 10 |
| `['Actions']` | 1.0543 | 54518 | 10 |
| `['AssignmentScope']` | 1.4812 | 54518 | 10 |
| `['ActionRequestor']` | 1.1335 | 37014 | 10 |
| `['Actions', 'AssignmentScope']` | 1.0856 | 91936 | 10 |
| `['Actions', 'AssignmentScope', 'ActionRequestor']` | 1.0063 | 91936 | 10 |

#### Vega-Lite Visualization

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "width": 600,
  "height": 300,
  "title": "Latency by Relationship Set",
  "data": {
    "values": [
      {"Scenario": "[]", "Latency": 1.0965},
      {"Scenario": "Actions", "Latency": 1.0543},
      {"Scenario": "AssignScope", "Latency": 1.4812},
      {"Scenario": "Req", "Latency": 1.1335},
      {"Scenario": "Actions+Scope", "Latency": 1.0856},
      {"Scenario": "All", "Latency": 1.0063}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {"field": "Scenario", "type": "nominal", "axis": {"labelAngle": 0}},
    "y": {"field": "Latency", "type": "quantitative", "title": "Latency (s)"}
  }
}
```

### 2. Varying `relationship_page_size`

| `relationship_page_size` | Latency (s) | Size (bytes) | Count |
| :--- | :---: | :---: | :---: |
| 1 | 1.0349 | 156747 | 10 |
| 2 | 1.3347 | 156747 | 10 |
| 5 | 1.2111 | 156747 | 10 |

#### Vega-Lite Visualization

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "width": 600,
  "height": 300,
  "title": "Latency by Relationship Page Size",
  "data": {
    "values": [
      {"PageSize": "1", "Latency": 1.0349},
      {"PageSize": "2", "Latency": 1.3347},
      {"PageSize": "5", "Latency": 1.2111}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {"field": "PageSize", "type": "nominal", "axis": {"labelAngle": 0}},
    "y": {"field": "Latency", "type": "quantitative", "title": "Latency (s)"}
  }
}
```

### 3. Varying `graph_query_depth`

| `graph_query_depth` | Latency (s) | Size (bytes) | Count |
| :--- | :---: | :---: | :---: |
| 0 | 1.3963 | 156747 | 10 |
| 1 | 1.4542 | 156747 | 10 |
| 2 | 1.1335 | 156747 | 10 |
| 3 | 1.5857 | 156747 | 10 |
| 4 | 1.3588 | 156747 | 10 |
| 5 | 1.2409 | 156747 | 10 |

#### Vega-Lite Visualization

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "width": 600,
  "height": 300,
  "title": "Latency by Graph Query Depth",
  "data": {
    "values": [
      {"Depth": "0", "Latency": 1.3963},
      {"Depth": "1", "Latency": 1.4542},
      {"Depth": "2", "Latency": 1.1335},
      {"Depth": "3", "Latency": 1.5857},
      {"Depth": "4", "Latency": 1.3588},
      {"Depth": "5", "Latency": 1.2409}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {"field": "Depth", "type": "nominal", "axis": {"labelAngle": 0}},
    "y": {"field": "Latency", "type": "quantitative", "title": "Latency (s)"}
  }
}
```

### 4. Varying `metadata_element_subtypes`

| Subtypes Set | Latency (s) | Size (bytes) | Count |
| :--- | :---: | :---: | :---: |
| `['Action']` | 1.2812 | 156747 | 10 |
| `['ToDo']` | 0.1541 | 2 | 0 |
| `['Action', 'ToDo']` | 1.3349 | 156771 | 10 |
| `[]` | 0.1719 | 2 | 0 |
| `['Process']` | 1.1959 | 156747 | 10 |

#### Vega-Lite Visualization

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "width": 600,
  "height": 300,
  "title": "Latency by Metadata Element Subtypes",
  "data": {
    "values": [
      {"Subtypes": "Action", "Latency": 1.2812},
      {"Subtypes": "ToDo", "Latency": 0.1541},
      {"Subtypes": "Action+ToDo", "Latency": 1.3349},
      {"Subtypes": "[]", "Latency": 0.1719},
      {"Subtypes": "Process", "Latency": 1.1959}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {"field": "Subtypes", "type": "nominal", "axis": {"labelAngle": 0}},
    "y": {"field": "Latency", "type": "quantitative", "title": "Latency (s)"}
  }
}
```

## Implementation Details

The updated [action_perf.py](file:///Users/dwolfson/antigravity-pyegeria/egeria-python/tests/action_perf.py) script systematically tests all four parameter sets and outputs JSON data for easy visualization.
