# Egeria Expert Multi-Model Deployment

We have successfully refactored the Egeria Expert agent to support multiple LLM backends via Ollama and deployed three separate instances.

## Changes

1.  **`src/queries/bee_qa_lib.py`**:
    *   Refactored `run_bee_agent` to accept a `model_name` argument.
    *   Dynamically initializes `OllamaChatModel` with the requested model.

2.  **`src/queries/server.py`**:
    *   Updated to read `AGENT_NAME` and `LLM_MODEL` from environment variables.
    *   Registers the agent with a unique name based on the environment variable, allowing distinguishable agents in the Bee Agent Stack.

3.  **`start_agents.sh`**:
    *   New script to automate the deployment of all three versions.
    *   Kills existing `server.py` processes.
    *   Launches three instances in the background.

## Deployed Agents

| Agent Name | Model | Port | URL |
| :--- | :--- | :--- | :--- |
| `egeria_expert_llama` | `llama3.1:latest` | 8010 | http://127.0.0.1:8010 |
| `egeria_expert_granite` | `granite3.3:8b` | 8011 | http://127.0.0.1:8011 |
| `egeria_expert_qwen` | `yasserrmd/Qwen2.5-7B-Instruct-1M:latest` | 8012 | http://127.0.0.1:8012 |

## Logs

Logs for each agent are captured in the root directory:
*   `llama.log`
*   `granite.log`
*   `qwen.log`

## Verification

The agents are currently running. You can interact with them via the Bee Agent Stack UI (configure it to point to these ports) or via API.

Example check:
```bash
curl http://127.0.0.1:8010/docs
```
