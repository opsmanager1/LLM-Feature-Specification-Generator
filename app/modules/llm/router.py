from fastapi import APIRouter, HTTPException, status

from app.core.settings import settings
from app.modules.llm.schemas import LlmGenerateRequest, LlmGenerateResponse
from app.modules.llm.service import generate_completion

router = APIRouter(prefix=settings.LLM_PREFIX, tags=[settings.LLM_TAG])


@router.post(settings.LLM_GENERATE_PATH, response_model=LlmGenerateResponse)
async def generate(payload: LlmGenerateRequest) -> LlmGenerateResponse:
    try:
        return await generate_completion(payload)
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