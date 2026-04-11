import json
import re


def extract_json(text: str) -> dict | list:
    """Extract the first JSON object or array from a raw LLM response."""
    match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in LLM response")
    return json.loads(match.group(1))


def strip_markdown(text: str) -> str:
    """Remove Markdown code fences and trim whitespace."""
    text = re.sub(r"```[\w]*\n?", "", text)
    return text.strip()


def extract_sections(text: str) -> dict[str, str]:
    """
    Split a Markdown-formatted LLM response into {heading: content} sections.

    Example input:
        ## Overview
        This is a spec...
        ## Requirements
        1. ...
    """
    sections: dict[str, str] = {}
    current_heading = "_preamble"
    current_lines: list[str] = []

    for line in text.splitlines():
        heading_match = re.match(r"^#{1,3}\s+(.+)", line)
        if heading_match:
            sections[current_heading] = "\n".join(current_lines).strip()
            current_heading = heading_match.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)

    sections[current_heading] = "\n".join(current_lines).strip()
    sections.pop("_preamble", None)
    return sections


def normalize_whitespace(text: str) -> str:
    """Collapse multiple blank lines to a single blank line."""
    return re.sub(r"\n{3,}", "\n\n", text).strip()
