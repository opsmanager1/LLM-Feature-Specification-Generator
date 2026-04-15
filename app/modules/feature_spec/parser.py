import json
import re


def extract_json(text: str) -> dict | list:
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char not in "[{":
            continue
        try:
            parsed, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, (dict, list)):
            return parsed
    raise ValueError("No JSON found in LLM response")


def strip_markdown(text: str) -> str:
    text = re.sub(r"```[\w]*\n?", "", text)
    return text.strip()


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text).strip()
