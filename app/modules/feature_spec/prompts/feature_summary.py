import html

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.feature_spec.models import PromptTemplate
from app.modules.feature_spec.parser import extract_json, normalize_whitespace, strip_markdown


def build_feature_summary_prompt_from_template(template: str, feature_idea: str) -> str:
    safe_template = template.strip()
    escaped_feature_idea = html.escape(feature_idea.strip(), quote=True)
    try:
        return safe_template.format(
            feature_idea=escaped_feature_idea,
            input=escaped_feature_idea,
        )
    except KeyError as exc:
        missing_key = exc.args[0] if exc.args else "unknown"
        raise ValueError(
            f"Prompt template error: missing placeholder '{missing_key}'"
        ) from exc


def load_feature_summary_template(db: Session) -> str:
    statement = (
        select(PromptTemplate.feature_to_feature_summary)
        .where(PromptTemplate.is_active.is_(True))
        .order_by(PromptTemplate.updated_at.desc())
        .limit(1)
    )
    template = db.execute(statement).scalar_one_or_none()
    if template and template.strip():
        return template
    raise ValueError(
        "Active feature summary prompt template is not configured in database"
    )


def build_feature_summary_prompt_from_db(feature_idea: str, db: Session) -> str:
    template = load_feature_summary_template(db)
    return build_feature_summary_prompt_from_template(template, feature_idea)


def parse_feature_summary_response(raw_response: str) -> dict | list:
    normalized_content = normalize_whitespace(strip_markdown(raw_response))
    return extract_json(normalized_content)
