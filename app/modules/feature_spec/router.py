from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.settings import settings
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.feature_spec.orchestrator import (
    generate_feature_spec,
    get_feature_spec_history,
)
from app.modules.feature_spec.schemas import (
    FeatureSpecGenerateRequest,
    FeatureSpecGenerateResponse,
    FeatureSpecHistoryResponse,
)

router = APIRouter(prefix="/feature-spec", tags=["feature-spec"])


@router.post("/generate", response_model=FeatureSpecGenerateResponse)
async def generate_feature_spec_endpoint(
    payload: FeatureSpecGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FeatureSpecGenerateResponse:
    try:
        return await generate_feature_spec(payload.feature_idea, db, current_user.id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.get("/history", response_model=FeatureSpecHistoryResponse)
async def get_feature_spec_history_endpoint(
    limit: int = settings.FEATURE_SPEC_HISTORY_DEFAULT_LIMIT,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FeatureSpecHistoryResponse:
    return get_feature_spec_history(db, current_user.id, limit)
