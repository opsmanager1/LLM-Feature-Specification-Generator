from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.settings import settings
from app.modules.feature_spec.models import FeatureSpecRun
from app.modules.feature_spec.prompts.feature_summary import (
    build_feature_summary_prompt_from_db,
    parse_feature_summary_response,
)
from app.modules.feature_spec.providers.ollama import ollama_client
from app.modules.feature_spec.schemas import (
    FeatureSummaryResult,
    FeatureSpecGenerateResponse,
    FeatureSpecHistoryItem,
    FeatureSpecHistoryResponse,
)


class FeatureSpecOrchestrator:
    def __init__(self, llm_client) -> None:
        self.llm = llm_client

    async def generate(
        self,
        idea: str,
        db: Session,
        user_id: int,
    ) -> FeatureSpecGenerateResponse:
        run = FeatureSpecRun(
            user_id=user_id,
            feature_idea=idea,
            status="pending",
        )
        db.add(run)
        db.commit()
        db.refresh(run)

        feature_summary_prompt = build_feature_summary_prompt_from_db(idea, db)
        try:
            feature_summary_raw = await self.llm.generate(feature_summary_prompt)
            feature_summary_json = parse_feature_summary_response(feature_summary_raw)
            feature_summary_typed = FeatureSummaryResult.model_validate(
                feature_summary_json
            )

            run.status = "success"
            run.response_json = feature_summary_typed.model_dump(mode="json")
            run.error_message = None
            db.add(run)
            db.commit()
        except Exception as exc:
            run.status = "error"
            run.error_message = str(exc)
            db.add(run)
            db.commit()
            raise

        return FeatureSpecGenerateResponse(
            feature_idea=idea,
            feature_summary=feature_summary_typed,
        )


orchestrator = FeatureSpecOrchestrator(ollama_client)


async def generate_feature_spec(
    feature_idea: str,
    db: Session,
    user_id: int,
) -> FeatureSpecGenerateResponse:
    return await orchestrator.generate(feature_idea, db, user_id)


def get_feature_spec_history(
    db: Session,
    user_id: int,
    limit: int = settings.FEATURE_SPEC_HISTORY_DEFAULT_LIMIT,
) -> FeatureSpecHistoryResponse:
    safe_limit = max(1, min(limit, 100))
    statement = (
        select(FeatureSpecRun)
        .where(FeatureSpecRun.user_id == user_id)
        .order_by(FeatureSpecRun.created_at.desc())
        .limit(safe_limit)
    )
    rows = db.execute(statement).scalars().all()

    items = [
        FeatureSpecHistoryItem(
            id=row.id,
            feature_idea=row.feature_idea,
            status=row.status,
            response_json=(
                FeatureSummaryResult.model_validate(row.response_json)
                if row.response_json is not None
                else None
            ),
            error_message=row.error_message,
            created_at=row.created_at,
        )
        for row in rows
    ]
    return FeatureSpecHistoryResponse(items=items)
