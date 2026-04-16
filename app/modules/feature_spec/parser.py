import json
import re


def _is_missing(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict)):
        return not value
    return False


def _normalize_acceptance_criteria(value) -> list[str] | None:
    if value is None:
        return None

    items = value if isinstance(value, list) else [value]
    normalized_items: list[str] = []

    for item in items:
        if isinstance(item, str):
            text = item.strip()
        elif isinstance(item, dict):
            text = next(
                (
                    candidate.strip()
                    for key in (
                        "title",
                        "description",
                        "details",
                        "criterion",
                        "text",
                        "message",
                    )
                    if isinstance((candidate := item.get(key)), str)
                    and candidate.strip()
                ),
                str(item).strip(),
            )
        else:
            text = str(item).strip()

        if text:
            normalized_items.append(text)

    return normalized_items or None


def _normalize_risk_assessment(value) -> list[str] | None:
    if value is None:
        return None

    items = value if isinstance(value, list) else [value]
    normalized_items: list[str] = []

    for item in items:
        if isinstance(item, str):
            text = item.strip()
        elif isinstance(item, dict):
            text = next(
                (
                    candidate.strip()
                    for key in ("title", "risk", "description", "details", "message")
                    if isinstance((candidate := item.get(key)), str)
                    and candidate.strip()
                ),
                str(item).strip(),
            )
        else:
            text = str(item).strip()

        if text:
            normalized_items.append(text)

    return normalized_items or None


def normalize_feature_summary_payload(data: dict | list) -> dict | list:
    if not isinstance(data, dict):
        return data

    normalized = dict(data)

    if "user_stories" not in normalized and "feature_summary_items" in normalized:
        normalized["user_stories"] = normalized["feature_summary_items"]

    acceptance_source = normalized.get("acceptance_criteria")
    if _is_missing(acceptance_source):
        acceptance_source = normalized.get("acceptance")

    normalized_acceptance = _normalize_acceptance_criteria(acceptance_source)
    if normalized_acceptance is not None:
        normalized["acceptance_criteria"] = normalized_acceptance

    if "db_models_and_api_endpoints" not in normalized:
        normalized["db_models_and_api_endpoints"] = {
            "db_models": normalized.get("db_models", []),
            "api_endpoints": normalized.get("api_endpoints", []),
        }

    risk_source = normalized.get("risk_assessment")
    if _is_missing(risk_source):
        risk_source = normalized.get("risks")

    normalized_risks = _normalize_risk_assessment(risk_source)
    if normalized_risks is not None:
        normalized["risk_assessment"] = normalized_risks

    return normalized


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
