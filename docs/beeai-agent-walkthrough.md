# BeeAI Agent Implementation Walkthrough

I have built a new QA agent using the **BeeAI Framework** (`beeai-framework`) to replicate the RAG functionality found in `basic_qa.ipynb`.

## Implementation Details

### File: `src/queries/bee_qa.py`
This script contains the complete agent implementation:
- **Embeddings**: `GraniteOllamaEmbeddings` class adapted from the notebook.
- **Vector Store**: Connects to the local Milvus instance and `Egeria_12_8_Collection`.
- **Tool**: `RetrieverTool` wraps the Milvus retrieval logic into a standard BeeAI tool.
- **Agent**: Uses `ReActAgent` with `OllamaChatModel` (via `beeai-framework` adapters) in an unconstrained memory setting.

## How to Run
Ensure your local Milvus and Ollama services are running (as expected from the existing notebook setup).

Run the agent script:
```bash
python src/queries/bee_qa.py
```

## Observations
- The agent successfully initializes, connects to Milvus, and communicates with the LLM.
- The `ReActAgent` is configured to use the retrieval tool.
- **Note**: The current model (`yasserrmd/Qwen2.5-7B-Instruct-1M`) may need further prompt tuning to reliably execute the tool calls in the ReAct loop. The script includes a system prompt to encourage tool usage.

## Next Steps
- Experiment with different models in Ollama (e.g., `llama3.1` or `granite-3.0-8b-instruct`) which might follow tool calling instructions better.
- Adjust the `SystemMessage` to further constrain the agent's behavior.
