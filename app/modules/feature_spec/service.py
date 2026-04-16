from celery.result import AsyncResult
from sqlalchemy.orm import Session

from app.infrastructure.celery_app import celery_app
from app.infrastructure.tasks.feature_spec_tasks import generate_feature_spec_task
from app.modules.feature_spec.models import FeatureSpecRun
from app.modules.feature_spec.schemas import (
    FeatureSpecTaskStatusResponse,
    FeatureSpecTaskSubmitResponse,
)


TERMINAL_STATES = {"SUCCESS", "FAILURE"}


def submit_feature_spec_generation(
    feature_idea: str,
    db: Session,
    user_id: int,
) -> FeatureSpecTaskSubmitResponse:
    run = FeatureSpecRun(
        user_id=user_id,
        feature_idea=feature_idea,
        status="pending",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    task = generate_feature_spec_task.delay(run.id, feature_idea, user_id)
    return FeatureSpecTaskSubmitResponse(task_id=task.id, status="processing")


def get_feature_spec_task_status(task_id: str) -> FeatureSpecTaskStatusResponse:
    async_result = AsyncResult(task_id, app=celery_app)
    state = async_result.state

    if state == "SUCCESS":
        payload = async_result.result if isinstance(async_result.result, dict) else None
        return FeatureSpecTaskStatusResponse(
            task_id=task_id,
            status="SUCCESS",
            result=payload,
        )

    if state == "FAILURE":
        return FeatureSpecTaskStatusResponse(
            task_id=task_id,
            status="FAILURE",
            error="Task execution failed",
        )

    if state == "STARTED":
        return FeatureSpecTaskStatusResponse(task_id=task_id, status="STARTED")

    return FeatureSpecTaskStatusResponse(task_id=task_id, status="PENDING")
