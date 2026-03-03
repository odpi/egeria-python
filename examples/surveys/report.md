# Egeria Survey Scan Report
Generated on: 2026-02-22 19:37:30
Root Path: `/Users/dwolfson/localGit/dw`

## Summary
- **Total Files Scanned:** 176691
- **JSON Files Identified:** 62

## File Breakdown
```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "description": "File Breakdown: Identified JSON vs Other Files",
  "data": {
    "values": [
      {
        "Category": "Identified JSON",
        "Count": 62
      },
      {
        "Category": "Other Files",
        "Count": 176629
      }
    ]
  },
  "mark": {
    "type": "arc",
    "innerRadius": 50
  },
  "encoding": {
    "theta": {
      "field": "Count",
      "type": "quantitative"
    },
    "color": {
      "field": "Category",
      "type": "nominal",
      "scale": {
        "range": [
          "#673ab7",
          "#e0e0e0"
        ]
      }
    }
  },
  "title": "File Structure Breakdown"
}
```

## Artifact Type Distribution
```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "description": "Histogram of Identified JSON Artifact Types",
  "data": {
    "values": [
      {
        "Type": "mcp_tool_config",
        "Count": 62
      }
    ]
  },
  "mark": "bar",
  "encoding": {
    "y": {
      "field": "Type",
      "type": "nominal",
      "sort": "-x",
      "title": "Artifact Type"
    },
    "x": {
      "field": "Count",
      "type": "quantitative",
      "title": "Count"
    },
    "color": {
      "field": "Type",
      "type": "nominal",
      "legend": null
    }
  },
  "title": "JSON Artifact Type Distribution"
}
```

## Detailed Findings
| File Name | Relative Path | Artifact Type | Display Label |
| :--- | :--- | :--- | :--- |
| agentstack.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/agentstack.json | mcp_tool_config | N/A |
| example_config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/example_config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/ftp/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/open_interpreter/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/agentmail/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/agent_connect/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/agentql/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/firecrawl/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/hyperspell/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/exa/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/browserbase/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/dappier/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/vision/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/perplexity/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/neon/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/mem0/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/payman/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/composio/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/hyperbrowser/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/weaviate/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/file_read/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/code_interpreter/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/directory_search/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/stripe/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/_tools/sql/config.json | mcp_tool_config | N/A |
| hello_alex.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/templates/hello_alex.json | mcp_tool_config | N/A |
| content_creator.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/templates/content_creator.json | mcp_tool_config | N/A |
| reasoning.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/templates/reasoning.json | mcp_tool_config | N/A |
| research.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/templates/research.json | mcp_tool_config | N/A |
| hola_alex.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/templates/hola_alex.json | mcp_tool_config | N/A |
| system_analyzer.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/.venv/lib/python3.12/site-packages/agentstack/templates/system_analyzer.json | mcp_tool_config | N/A |
| agentstack.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/agentstack.json | mcp_tool_config | N/A |
| example_config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/example_config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/ftp/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/open_interpreter/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/agentmail/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/agent_connect/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/agentql/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/firecrawl/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/hyperspell/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/exa/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/browserbase/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/dappier/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/vision/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/perplexity/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/neon/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/mem0/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/payman/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/composio/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/hyperbrowser/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/weaviate/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/file_read/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/code_interpreter/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/directory_search/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/stripe/config.json | mcp_tool_config | N/A |
| config.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/_tools/sql/config.json | mcp_tool_config | N/A |
| hello_alex.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/templates/hello_alex.json | mcp_tool_config | N/A |
| content_creator.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/templates/content_creator.json | mcp_tool_config | N/A |
| reasoning.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/templates/reasoning.json | mcp_tool_config | N/A |
| research.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/templates/research.json | mcp_tool_config | N/A |
| hola_alex.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/templates/hola_alex.json | mcp_tool_config | N/A |
| system_analyzer.json | egeria-workspaces/exchange/loading-bay/EgeriaExpert-Demo/src/queries/egeria_agent_stack/egeria_expert/.venv/lib/python3.12/site-packages/agentstack/templates/system_analyzer.json | mcp_tool_config | N/A |
