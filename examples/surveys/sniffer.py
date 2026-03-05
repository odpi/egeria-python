import json
import os
from typing import Optional, Dict, Any

class AIJsonInspector:
    """Inspects JSON artifacts to categorize them for Egeria annotations."""

    def __init__(self):
        # Define signatures for common AI/ML JSON structures
        self.signatures = {
            "tuning_params": {"keys": {"learning_rate", "batch_size", "epochs"}, "label": "Model Tuning Parameters"},
            "mlflow_run": {"keys": {"info", "data", "metrics", "params"}, "label": "MLflow Run Trace"},
            "qa_metrics": {"keys": {"accuracy", "f1_score", "precision", "recall"}, "label": "Model Quality Metrics"},
            "sagemaker_config": {"keys": {"TrainingJobName", "HyperParameters", "InputDataConfig"}, "label": "SageMaker Job Config"},
            "openai_finetune": {"keys": {"messages", "role", "content"}, "label": "ChatML Fine-tuning Data"}
        }

    def inspect(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Analyzes a JSON file and returns a summary dict if it matches a known 
        AI profile; otherwise returns None.
        """
        if not os.path.exists(file_path) or not file_path.endswith('.json'):
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # We only load the first bit or the whole thing if it's small
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

        # Handle both list-wrapped JSON (datasets) and dict-wrapped (configs)
        sample = data[0] if isinstance(data, list) and len(data) > 0 else data
        
        if not isinstance(sample, dict):
            return None

        found_keys = set(sample.keys())

        for profile, config in self.signatures.items():
            # If the intersection of keys matches the signature requirements
            if config["keys"].intersection(found_keys) == config["keys"]:
                return self._summarize(profile, config["label"], data)

        return None

    def _summarize(self, profile: str, label: str, data: Any) -> Dict[str, Any]:
        """Creates the summary dictionary for Egeria Annotation."""
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

# --- Airflow Task Example Usage ---
# def airflow_callable(**kwargs):
#     inspector = AIJsonInspector()
#     result = inspector.inspect(kwargs['file_to_check'])
#     if result:
#         # Code to push to Egeria OMAS or return for XCom
#         return result