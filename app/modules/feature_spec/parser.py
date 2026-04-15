import json
import re


def extract_json(text: str) -> dict | list:
    match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in LLM response")
    return json.loads(match.group(1))


def strip_markdown(text: str) -> str:
    text = re.sub(r"```[\w]*\n?", "", text)
    return text.strip()


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text).strip()
