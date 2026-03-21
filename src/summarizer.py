import json
from typing import Dict

import requests


class RouterSummarizer:
    def __init__(self, api_url: str, api_key: str, model: str, timeout_seconds: int = 30):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

    def summarize_email(self, email: Dict[str, str]) -> Dict[str, str]:
        prompt = (
            "Summarize this email in JSON with exactly two keys: "
            "summary (max 2 short sentences) and key_points (array of up to 4 bullets).\n\n"
            f"From: {email['from_name']} <{email['from_email']}>\n"
            f"Subject: {email['subject']}\n"
            f"Snippet: {email['snippet']}\n"
            f"Body: {email['body'][:6000]}"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an assistant that returns only valid JSON.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.2,
        }

        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = {
                "summary": content.strip()[:500],
                "key_points": ["Could not parse structured key points."],
            }

        summary = str(parsed.get("summary", "")).strip() or "No summary generated."
        key_points = parsed.get("key_points", [])

        if not isinstance(key_points, list):
            key_points = [str(key_points)]

        cleaned_points = [str(item).strip() for item in key_points if str(item).strip()]
        if not cleaned_points:
            cleaned_points = ["No key points generated."]

        return {
            "summary": summary,
            "key_points": "\n• " + "\n• ".join(cleaned_points),
        }
