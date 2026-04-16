import httpx
from celery.exceptions import MaxRetriesExceededError

from app.core.database import SessionLocal
from app.core.settings import settings
from app.infrastructure.celery_app import celery_app
from app.infrastructure.ollama_client import ollama_sync_client
from app.modules.feature_spec.models import FeatureSpecRun
from app.modules.feature_spec.prompts.feature_summary import (
    build_feature_summary_prompt_from_db,
    parse_feature_summary_response,
)
from app.modules.feature_spec.schemas import FeatureSummaryResult


@celery_app.task(bind=True, name="feature_spec.generate")
def generate_feature_spec_task(self, run_id: int, feature_idea: str, user_id: int) -> dict:
    db = SessionLocal()
    try:
        run = db.get(FeatureSpecRun, run_id)
        if run is None:
            return {"run_id": run_id, "status": "error", "message": "Run not found"}

        if run.status == "success" and run.response_json is not None:
            return {
                "run_id": run.id,
                "status": run.status,
                "feature_idea": run.feature_idea,
                "feature_summary": run.response_json,
            }

        try:
            prompt = build_feature_summary_prompt_from_db(feature_idea, db)
            feature_summary_raw = ollama_sync_client.generate(prompt)
            feature_summary_json = parse_feature_summary_response(feature_summary_raw)
            feature_summary_typed = FeatureSummaryResult.model_validate(feature_summary_json)

            run.status = "success"
            run.response_json = feature_summary_typed.model_dump(mode="json")
            run.error_message = None
            db.add(run)
            db.commit()

            return {
                "run_id": run.id,
                "status": run.status,
                "feature_idea": run.feature_idea,
                "feature_summary": run.response_json,
            }
        except (
            httpx.TimeoutException,
            httpx.RequestError,
            httpx.HTTPStatusError,
        ) as exc:
            retry_number = int(self.request.retries) + 1
            if retry_number <= settings.CELERY_TASK_MAX_RETRIES:
                delay_seconds = settings.CELERY_TASK_RETRY_BASE_SECONDS**retry_number
                try:
                    raise self.retry(exc=exc, countdown=delay_seconds)
                except MaxRetriesExceededError:
                    pass

            run.status = "error"
            run.error_message = "LLM provider request failed"
            db.add(run)
            db.commit()
            raise RuntimeError("LLM task failed after retries") from exc
        except Exception as exc:
            run.status = "error"
            run.error_message = "Failed to process feature specification"
            db.add(run)
            db.commit()
            raise RuntimeError("Feature specification task failed") from exc
    finally:
        db.close()
