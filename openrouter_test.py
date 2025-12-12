#!/usr/bin/env python3
"""
Quick OpenRouter connectivity check.

Usage:
  export OPENROUTER_API_KEY="your-key"
  python openrouter_test.py

Optional env vars:
  OPENROUTER_MODEL (default: mistralai/devstral-2512:free)
  OPENROUTER_BASE_URL (default: https://openrouter.ai/api/v1)
"""

import json
import os
import sys
import requests

API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/devstral-2512:free")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")


def main() -> int:
    if not API_KEY:
        print("❌ OPENROUTER_API_KEY not set. Set it and retry.")
        return 1

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",  # optional
        "X-Title": "Financial QA Bot",       # optional
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": "tell me about yourself in less than 10 words"}
        ],
        "temperature": 0.2,
    }

    try:
        resp = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            data=json.dumps(payload),
            timeout=30,
        )
        resp.raise_for_status()
    except Exception as exc:
        print(f"❌ Request failed: {exc}")
        resp_obj = getattr(exc, "response", None)
        if resp_obj is not None:
            print("Response text:", resp_obj.text)
        return 1

    data = resp.json()
    try:
        message = data["choices"][0]["message"]["content"].strip()
    except Exception:
        message = json.dumps(data, indent=2)

    print("✅ OpenRouter request succeeded")
    print("Model:", MODEL)
    print("Reply:", message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
