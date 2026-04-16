import logging

from app.core.database import SessionLocal
from app.modules.feature_spec.models import PromptTemplate

logger = logging.getLogger(__name__)


DEFAULT_FEATURE_SUMMARY_PROMPT_TEMPLATE = """You are a senior staff-level product engineer and system architect working on production-grade backend systems.

Your task is to convert a high-level feature idea into a precise, implementation-ready technical specification.

You must think in terms of real backend development: APIs, database schema, data consistency, edge cases, and scalability.

---

## Core rules:

- Be strictly structured and deterministic
- Do NOT invent product requirements beyond the given feature idea
- If information is missing, explicitly list it under "assumptions"
- Prefer simple and realistic solutions over over-engineering
- Every part of the output must be implementation-ready
- Avoid vague phrases like "etc", "additional fields", "and so on"
- If something is required — define it explicitly

---

## Hard requirements:

- Database design MUST include full schema:
  - each table must have 4–8 fields
  - include types and constraints (PK, FK, unique, nullable)
  - include relationships

- API design MUST:
  - include at least 4 endpoints (not just 1–2)
  - include request validation
  - include access control logic
  - include error responses

- Acceptance criteria MUST:
  - include positive and negative cases
  - include authorization behavior
  - be testable (QA-ready, no vague language)

- Edge cases & risks MUST include:
  - concurrency issues
  - data consistency problems
  - security concerns
  - failure scenarios

- If the feature involves payments:
  - include payment provider interaction (e.g. Stripe-like flow)
  - include idempotency handling
  - include transaction status tracking

---

## Output format (STRICT JSON ONLY)

Return ONLY valid JSON. No explanations, no markdown, no extra text.

{
  "assumptions": ["string"],

  "user_stories": [
    {
      "title": "string",
      "as_a": "string",
      "i_want": "string",
      "so_that": "string"
    }
  ],

  "acceptance_criteria": ["string"],

  "db_models": [
    {
      "table": "string",
      "fields": [
        {
          "name": "string",
          "type": "string",
          "constraints": "string"
        }
      ],
      "relationships": ["string"]
    }
  ],

  "api_endpoints": [
    {
      "method": "string",
      "path": "string",
      "request_body": "string",
      "response": "string",
      "errors": ["string"],
      "purpose": "string"
    }
  ],

  "risk_assessment": ["string"]
}

---

Feature idea:
{feature_idea}
"""


def bootstrap_prompt_template(db) -> None:
    existing_template = db.get(PromptTemplate, 1)
    default_template = DEFAULT_FEATURE_SUMMARY_PROMPT_TEMPLATE

    if existing_template is None:
        try:
            db.add(
                PromptTemplate(
                    id=1,
                    feature_to_feature_summary=default_template,
                    is_active=True,
                )
            )
            db.commit()
            logger.info("Created default feature summary prompt template")
        except Exception:
            logger.exception("Failed to create default feature summary prompt template")
            db.rollback()
            raise
        return

    existing_value = existing_template.feature_to_feature_summary.strip()
    if existing_value:
        return

    try:
        existing_template.feature_to_feature_summary = default_template
        db.add(existing_template)
        db.commit()
        logger.info("Filled empty feature summary prompt template with default value")
    except Exception:
        logger.exception("Failed to fill default feature summary prompt template")
        db.rollback()
        raise


def main() -> None:
    db = SessionLocal()
    try:
        bootstrap_prompt_template(db)
        logger.info("Prompt template bootstrap script completed")
    finally:
        db.close()


if __name__ == "__main__":
    main()
