import logging

from app.core.database import SessionLocal
from app.modules.feature_spec.models import PromptTemplate

logger = logging.getLogger(__name__)


DEFAULT_FEATURE_SUMMARY_PROMPT_TEMPLATE = """You are a senior staff-level product engineer
and system architect working on production-grade software systems.

Your job is to convert a high-level feature idea into a precise,
implementation-ready technical specification.

You must think in terms of real software delivery: backend systems, APIs,
databases, edge cases, and scalability.

---

## Core rules:
- Be extremely structured and deterministic
- Do NOT invent product requirements that were not implied or provided
- If information is missing, explicitly list assumptions in a separate section
- Prefer simplicity over over-engineering
- Think like you are writing a specification for a real engineering team
- All outputs must be actionable and implementation-oriented

---

## Output format (strict structure):

1. FEATURE OVERVIEW
- Short description of the feature
- Problem it solves
- Target users

---

2. USER STORIES
- List of user stories in format:
    As a [user type], I want [goal], so that [benefit]

---

3. ACCEPTANCE CRITERIA
- Each user story must have clear, testable conditions
- Use bullet points
- Must be unambiguous and QA-ready

---

4. API DESIGN (REST)
- List endpoints with:
    - method (GET, POST, etc.)
    - path
    - request body (if applicable)
    - response schema (high-level)
    - purpose

---

5. DATABASE DESIGN
- Define tables with:
    - table name
    - fields with types
    - relationships
- Keep it normalized and production-oriented

---

6. EDGE CASES & RISKS
- Identify failure scenarios
- Data consistency risks
- Security concerns
- Performance concerns

---

7. FUTURE IMPROVEMENTS
- Optional enhancements
- Scalability improvements
- UX improvements

---

## Important constraints:
- Do not add irrelevant features or expand scope
- Keep all assumptions explicitly labeled as "Assumption"
- Prefer backend clarity over marketing language
- Avoid vague phrases like "user-friendly", "robust", "fast"
- Be precise, technical, and engineering-focused

Feature idea:
{feature_idea}

---

Return format requirements (strict):
- Return ONLY valid JSON.
- Do not include markdown, code fences, or any text before/after JSON.
- JSON object must match this structure exactly:
{
    "user_stories": [
        {
            "title": "string",
            "as_a": "string",
            "i_want": "string",
            "so_that": "string"
        }
    ],
    "acceptance_criteria": ["string"],
    "db_models_and_api_endpoints": {
        "db_models": ["string"],
        "api_endpoints": ["string"]
    },
    "risk_assessment": ["string"]
}
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
