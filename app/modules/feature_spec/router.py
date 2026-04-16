from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.settings import settings
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.feature_spec.orchestrator import get_feature_spec_history
from app.modules.feature_spec.schemas import (
    FeatureSpecGenerateRequest,
    FeatureSpecHistoryResponse,
    FeatureSpecTaskStatusResponse,
    FeatureSpecTaskSubmitResponse,
)
from app.modules.feature_spec.service import (
    get_feature_spec_task_status,
    submit_feature_spec_generation,
)

router = APIRouter(prefix="/feature-spec", tags=["feature-spec"])


@router.post("/generate", response_model=FeatureSpecTaskSubmitResponse)
async def generate_feature_spec_endpoint(
    payload: FeatureSpecGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FeatureSpecTaskSubmitResponse:
    return submit_feature_spec_generation(payload.feature_idea, db, current_user.id)


@router.get("/tasks/{task_id}", response_model=FeatureSpecTaskStatusResponse)
async def get_feature_spec_task_status_endpoint(task_id: str) -> FeatureSpecTaskStatusResponse:
    return get_feature_spec_task_status(task_id)


@router.get("/history", response_model=FeatureSpecHistoryResponse)
async def get_feature_spec_history_endpoint(
    limit: int = settings.FEATURE_SPEC_HISTORY_DEFAULT_LIMIT,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FeatureSpecHistoryResponse:
    return get_feature_spec_history(db, current_user.id, limit)
