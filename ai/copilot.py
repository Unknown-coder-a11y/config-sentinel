import requests
import json

class ConfigCopilot:
    def __init__(self, model_name="qwen2.5-coder:1.5b", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = f"{base_url}/api/generate"

    def analyze_subgraph(self, target_service: str, subgraph_nodes: set, system_status: str = "degraded") -> str:
        prompt = f"""You are ConfigSentinel, an autonomous SRE copilot.
Target Service: {target_service}
Current State: {system_status}
Active Topology Dependencies: {list(subgraph_nodes)}

Task: Provide a concise diagnosis (max 2 sentences) and propose the exact configuration verification command or patch needed. Keep response concise and structured.
"""
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }

        try:
            # Bumping timeout from 15 to 60 seconds for cold starts
            response = requests.post(self.base_url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "No response received from model.")
        except requests.exceptions.RequestException as e:
            return f"[AI Copilot Error] Could not connect to Ollama: {e}"