"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Tests for the pyegeria.core.json_inspector module.
"""

import json
import os
import pytest
from json_inspector import identify_file

def test_identify_mcp_server_config():
    """Test identifying the MCP server configuration file provided by the user."""
    filepath = "/Users/dwolfson/antigravity-pyegeria/egeria-python/docs/pyegeria-mcp.json"
    
    if not os.path.exists(filepath):
        pytest.skip(f"File {filepath} not found")
        
    summary = identify_file(filepath)
    assert summary is not None
    assert summary["artifact_type"] in ["mcp_server_config", "mcp_multi_server_config"]
    
    if summary["artifact_type"] == "mcp_server_config":
        assert summary["mcp_server_name"] == "pyegeria"
        assert "config" in summary
        assert "tools" in summary

def test_identify_mcp_tool_config(tmp_path):
    """Test identifying an MCP tool configuration with explicit tools."""
    p = tmp_path / "test_tools.json"
    
    tool_data = {
        "mcp_server_name": "TestServer",
        "tools": [
            {
                "name": "get_weather",
                "description": "Get the current weather",
                "inputSchema": {"type": "object", "properties": {"location": {"type": "string"}}}
            }
        ]
    }
    p.write_text(json.dumps(tool_data))
    
    summary = identify_file(str(p))
    assert summary is not None
    assert summary["artifact_type"] == "mcp_tool_config"
    assert summary["mcp_server_name"] == "TestServer"
    assert len(summary["tools"]) == 1

def test_identify_ai_tuning_params(tmp_path):
    """Test identifying AI tuning parameters profile."""
    p = tmp_path / "tuning.json"
    tuning_data = {
        "learning_rate": 0.001,
        "batch_size": 32,
        "epochs": 10,
        "optimizer": "adam"
    }
    p.write_text(json.dumps(tuning_data))
    
    summary = identify_file(str(p))
    assert summary is not None
    assert summary["artifact_type"] == "tuning_params"
    assert summary["display_label"] == "Model Tuning Parameters"
    assert "detected_fields" in summary

def test_identify_mlflow_run(tmp_path):
    """Test identifying MLflow run trace profile."""
    p = tmp_path / "mlflow.json"
    mlflow_data = {
        "info": {"run_id": "123"},
        "data": {"metrics": {"accuracy": 0.95}},
        "metrics": {"accuracy": 0.95},
        "params": {"lr": 0.01}
    }
    p.write_text(json.dumps(mlflow_data))
    
    summary = identify_file(str(p))
    assert summary is not None
    assert summary["artifact_type"] == "mlflow_run"

def test_identify_non_matching_json(tmp_path):
    """Test that non-matching JSON structures return None."""
    p = tmp_path / "other.json"
    p.write_text(json.dumps({"some_key": "some_value"}))
    
    summary = identify_file(str(p))
    assert summary is None

def test_identify_non_json_file(tmp_path):
    """Test that non-JSON files return None."""
    p = tmp_path / "test.txt"
    p.write_text("This is not JSON")
    
    summary = identify_file(str(p))
    assert summary is None
