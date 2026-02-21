"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides methods to identify and parse JSON files for Egeria surveyors.
It supports:
- MCP Tool Configuration
- MCP Server Configuration
- AI/ML Profiles (Tuning params, MLFlow, SageMaker, etc.)
"""

import json
import os
from typing import Any, Dict, Optional, List

# AI Signatures from sniffer.py
AI_SIGNATURES = {
    "tuning_params": {"keys": {"learning_rate", "batch_size", "epochs"}, "label": "Model Tuning Parameters"},
    "mlflow_run": {"keys": {"info", "data", "metrics", "params"}, "label": "MLflow Run Trace"},
    "qa_metrics": {"keys": {"accuracy", "f1_score", "precision", "recall"}, "label": "Model Quality Metrics"},
    "sagemaker_config": {"keys": {"TrainingJobName", "HyperParameters", "InputDataConfig"}, "label": "SageMaker Job Config"},
    "openai_finetune": {"keys": {"messages", "role", "content"}, "label": "ChatML Fine-tuning Data"}
}


def identify_file(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Identifies a JSON file based on its contents and returns a summary if it matches a known type.
    
    Args:
        filepath: The path to the JSON file to analyze.
        
    Returns:
        A dictionary summarizing the file contents if it matches a known type, or None otherwise.
    """
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        return None
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError, IOError):
        return None
        
    # 1. Check for MCP formats (standard dict structures)
    if isinstance(data, dict):
        if "tools" in data and isinstance(data["tools"], list):
            return _summarize_mcp_tool_config(data)
        if "mcpServers" in data and isinstance(data["mcpServers"], dict):
            return _summarize_mcp_server_config(data)

    # 2. Check for AI Profiles
    ai_summary = _check_ai_profiles(data)
    if ai_summary:
        return ai_summary
        
    return None


def _summarize_mcp_tool_config(data: Dict[str, Any]) -> Dict[str, Any]:
    """Summarizes an MCP tool configuration file."""
    server_name = data.get("mcp_server_name", "Unknown MCP Server")
    tools = []
    
    for tool_data in data.get("tools", []):
        if not isinstance(tool_data, dict):
            continue
            
        tool_entry = {
            "tool_name": tool_data.get("name") or tool_data.get("tool_name"),
            "purpose": tool_data.get("description") or tool_data.get("purpose"),
            "input_parameters": tool_data.get("inputSchema") or tool_data.get("input_parameters") or tool_data.get("parameters"),
            "output_parameters": tool_data.get("output_parameters")
        }
        tools.append(tool_entry)
        
    return {
        "artifact_type": "mcp_tool_config",
        "mcp_server_name": server_name,
        "tools": tools
    }


def _summarize_mcp_server_config(data: Dict[str, Any]) -> Dict[str, Any]:
    """Summarizes an MCP server configuration file."""
    mcp_servers = data.get("mcpServers", {})
    server_summaries = []
    
    for server_name, config in mcp_servers.items():
        if not isinstance(config, dict):
            continue
        
        server_summaries.append({
            "mcp_server_name": server_name,
            "config": config
        })
    
    if len(server_summaries) == 1:
        summary = server_summaries[0]
        summary["artifact_type"] = "mcp_server_config"
        summary["tools"] = []
        return summary
        
    return {
        "artifact_type": "mcp_multi_server_config",
        "mcp_server_configs": server_summaries
    }


def _check_ai_profiles(data: Any) -> Optional[Dict[str, Any]]:
    """Analyzes data for AI/ML profile signatures."""
    # Handle both list-wrapped JSON and dict-wrapped
    sample = data[0] if isinstance(data, list) and len(data) > 0 else data
    
    if not isinstance(sample, dict):
        return None

    found_keys = set(sample.keys())

    for profile, config in AI_SIGNATURES.items():
        # If the intersection of keys matches the signature requirements
        if config["keys"].intersection(found_keys) == config["keys"]:
            return _summarize_ai_profile(profile, config["label"], data)

    return None


def _summarize_ai_profile(profile: str, label: str, data: Any) -> Dict[str, Any]:
    """Creates the summary dictionary for Egeria Annotation for AI profiles."""
    summary = {
        "artifact_type": profile,
        "display_label": label,
        "is_collection": isinstance(data, list),
        "element_count": len(data) if isinstance(data, list) else 1,
        "detected_fields": list(data[0].keys()) if isinstance(data, list) else list(data.keys())
    }
    
    # Add a snippet of the actual data for the Egeria Annotation 'Summary' field
    summary["preview"] = str(data)[:500] + "..."
    return summary
