import requests
from pcos.config import get_env


class LLMClient:
    def __init__(self):
        self.api_key = get_env("OPENAI_API_KEY")
        self.endpoint = "https://api.openai.com/v1/chat/completions"

    def generate(self, prompt: str) -> str:
        payload = {
            "model": "gpt-4.1-mini",
            "messages": [
                {"role": "system", "content": "You are a precise system."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        r = requests.post(self.endpoint, json=payload, headers=headers)
        r.raise_for_status()

        return r.json()["choices"][0]["message"]["content"]
