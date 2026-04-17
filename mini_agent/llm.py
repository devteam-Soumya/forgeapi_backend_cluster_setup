import json
import os
from pathlib import Path
from typing import Any, Dict

import requests
from dotenv import load_dotenv


class LLMError(Exception):
    pass


# Load .env from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH)


class OpenRouterLLM:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENROUTER_API_KEY", "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").strip()
        self.base_url = os.getenv(
            "OPENROUTER_BASE_URL",
            "https://openrouter.ai/api/v1",
        ).rstrip("/")
        self.model = os.getenv(
            "OPENROUTER_MODEL",
            "anthropic/claude-opus-4.6",
        )

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def generate_spec(self, prompt: str) -> Dict[str, Any]:
        if not self.enabled:
            raise LLMError(
                f"OPENROUTER_API_KEY is not configured. Expected it in {ENV_PATH}"
            )

        system_prompt = """
Return ONLY valid JSON.
Do not use markdown.

{
  "framework": "fastapi",
  "database": "mongodb",
  "fields": [
    {
      "name": "name",
      "type": "str",
      "required": true,
      "unique": false,
      "description": ""
    }
  ],
  "operations": ["create", "read", "update", "delete"],
  "tenant_aware": true,
  "route_base": "/resources",
  "description": "short description"
}
""".strip()

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "max_tokens": 400,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=45,
        )

        if response.status_code != 200:
            raise LLMError(f"OpenRouter error {response.status_code}: {response.text}")

        try:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)
        except Exception as exc:
            raise LLMError(f"Invalid LLM response: {exc}") from exc