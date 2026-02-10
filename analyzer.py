import os
import json
import requests

from perplexity import Perplexity  # pip-installed via requirements if you prefer; here we’ll just use requests to the API directly

HA_URL = os.environ.get("HA_URL", "http://supervisor/core")
SUPERVISOR_TOKEN = os.environ["SUPERVISOR_TOKEN"]
PPLX_API_KEY = os.environ["PPLX_API_KEY"]
LOG_MAX_CHARS = int(os.environ.get("LOG_MAX_CHARS", "30000"))

def ha_get(path: str) -> requests.Response:
    headers = {"Authorization": f"Bearer {SUPERVISOR_TOKEN}"}
    url = f"{HA_URL}{path}"
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp

def ha_post(path: str, payload: dict) -> requests.Response:
    headers = {
        "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
        "Content-Type": "application/json",
    }
    url = f"{HA_URL}{path}"
    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
    resp.raise_for_status()
    return resp

def get_error_log() -> str:
    # /api/error_log returns text with recent errors/warnings
    resp = ha_get("/api/error_log")
    return resp.text

def call_sonar(log_text: str) -> str:
    # Trim to limit token usage
    log_snippet = log_text[:LOG_MAX_CHARS]

    prompt = (
        "You are a Home Assistant expert. I will give you a Home Assistant error log.\n"
        "Tasks:\n"
        "1) Identify the main recurring errors and warnings.\n"
        "2) Explain likely causes in clear language.\n"
        "3) Suggest concrete steps to fix or mitigate them, including any configuration.yaml "
        "changes, integration options, or known issues.\n"
        "Only base your answer on the log content.\n\n"
        f"Here is the log:\n\n{log_snippet}"
    )

    url = "https://api.perplexity.ai/chat/completions"  # from Sonar API docs[web:55]
    headers = {
        "Authorization": f"Bearer {PPLX_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": "sonar-pro",
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }

    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]

def create_notification(message: str) -> None:
    payload = {
        "title": "Sonar log analysis",
        "message": message,
    }
    ha_post("/api/services/persistent_notification/create", payload)

def main():
    log_text = get_error_log()
    if not log_text.strip():
        create_notification("No error log content found to analyze.")
        return

    try:
        summary = call_sonar(log_text)
        create_notification(summary)
    except Exception as e:
        create_notification(f"Sonar log analyzer failed: {e}")

if __name__ == "__main__":
    main()
