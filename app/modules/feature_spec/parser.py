import json
import logging
import re
from typing import Any


logger = logging.getLogger(__name__)


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict)):
        return not value
    return False


def _normalize_acceptance_criteria(value: Any, *, strict: bool = False) -> list[str] | None:
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
        elif strict:
            raise ValueError("Invalid acceptance_criteria item")

    return normalized_items or None


def _normalize_risk_assessment(value: Any, *, strict: bool = False) -> list[str] | None:
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
        elif strict:
            raise ValueError("Invalid risk_assessment item")

    return normalized_items or None


def _normalize_mixed_items(value: Any, *, strict: bool = False) -> list[str | dict] | None:
    if value is None:
        return None

    items = value if isinstance(value, list) else [value]
    normalized_items: list[str | dict] = []

    for item in items:
        if isinstance(item, dict):
            normalized_items.append(item)
            continue

        text = str(item).strip()
        if text:
            normalized_items.append(text)
        elif strict:
            raise ValueError("Invalid db/api item")

    return normalized_items or None


def _first_non_empty(source: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = source.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _normalize_user_stories(value: Any, *, strict: bool = False) -> list[dict[str, str]] | None:
    if value is None:
        return None

    items = value if isinstance(value, list) else [value]
    normalized_items: list[dict] = []

    for index, item in enumerate(items, start=1):
        if isinstance(item, dict):
            title = _first_non_empty(item, "title", "name")
            as_a = _first_non_empty(item, "as_a", "as", "actor", "user")
            i_want = _first_non_empty(item, "i_want", "want", "goal", "objective")
            so_that = _first_non_empty(item, "so_that", "benefit", "because", "outcome")
            if not i_want:
                i_want = _first_non_empty(item, "description", "details", "text")
            if not so_that:
                so_that = i_want

            if not all([title, as_a, i_want, so_that]):
                if strict:
                    raise ValueError(f"Invalid user story at index {index}")
                logger.warning("Skipping invalid user story item at index %s", index)
                continue

            normalized_items.append(
                {
                    "title": title,
                    "as_a": as_a,
                    "i_want": i_want,
                    "so_that": so_that,
                }
            )
            continue

        if isinstance(item, str) and item.strip():
            text = item.strip()
            if strict:
                raise ValueError(
                    f"Invalid user story string item at index {index}; object expected"
                )
            normalized_items.append(
                {
                    "title": text,
                    "as_a": "User",
                    "i_want": text,
                    "so_that": text,
                }
            )
        elif strict:
            raise ValueError(f"Invalid user story item type at index {index}")

    return normalized_items or None


def normalize_feature_summary_payload(
    data: dict[str, Any] | list,
    *,
    strict: bool = False,
) -> dict[str, Any] | list:
    if not isinstance(data, dict):
        return data

    normalized = dict(data)

    if isinstance(normalized.get("feature_summary"), dict):
        nested = normalized["feature_summary"]
        logger.info("Using nested feature_summary payload")
        for key in (
            "user_stories",
            "feature_summary_items",
            "acceptance_criteria",
            "acceptance",
            "db_models_and_api_endpoints",
            "db_models",
            "api_endpoints",
            "risk_assessment",
            "risks",
        ):
            if key not in normalized and key in nested:
                normalized[key] = nested[key]

    user_stories_source = normalized.get("user_stories")
    if _is_missing(user_stories_source):
        user_stories_source = normalized.get("feature_summary_items")

    normalized_user_stories = _normalize_user_stories(user_stories_source, strict=strict)
    if normalized_user_stories is not None:
        normalized["user_stories"] = normalized_user_stories

    acceptance_source = normalized.get("acceptance_criteria")
    if _is_missing(acceptance_source):
        logger.info("Using legacy acceptance field")
        acceptance_source = normalized.get("acceptance")

    normalized_acceptance = _normalize_acceptance_criteria(
        acceptance_source,
        strict=strict,
    )
    if normalized_acceptance is not None:
        normalized["acceptance_criteria"] = normalized_acceptance

    db_api_source = normalized.get("db_models_and_api_endpoints")
    db_source = normalized.get("db_models")
    api_source = normalized.get("api_endpoints")

    if isinstance(db_api_source, dict):
        db_source = db_api_source.get("db_models", db_source)
        api_source = db_api_source.get("api_endpoints", api_source)

    normalized["db_models_and_api_endpoints"] = {
        "db_models": _normalize_mixed_items(db_source, strict=strict) or [],
        "api_endpoints": _normalize_mixed_items(api_source, strict=strict) or [],
    }

    risk_source = normalized.get("risk_assessment")
    if _is_missing(risk_source):
        logger.info("Using legacy risks field")
        risk_source = normalized.get("risks")

    normalized_risks = _normalize_risk_assessment(risk_source, strict=strict)
    if normalized_risks is not None:
        normalized["risk_assessment"] = normalized_risks

    return normalized


def extract_json(text: str) -> dict | list:
    stripped = text.strip()
    if stripped:
        try:
            parsed = json.loads(stripped)
            if isinstance(parsed, (dict, list)):
                return parsed
        except json.JSONDecodeError:
            pass

    fenced_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if fenced_match:
        candidate = fenced_match.group(1).strip()
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, (dict, list)):
                return parsed
        except json.JSONDecodeError:
            pass

    for candidate in re.findall(r"\{[\s\S]*?\}|\[[\s\S]*?\]", text):
        try:
            parsed = json.loads(candidate)
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
