from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.core.settings import settings


class FeatureSpecGenerateRequest(BaseModel):
    feature_idea: str = Field(min_length=1, max_length=settings.LLM_PROMPT_MAX_LENGTH)

    @field_validator("feature_idea")
    @classmethod
    def validate_feature_idea(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Feature idea must not be empty")
        return normalized


class FeatureSummaryItem(BaseModel):
    title: str
    as_a: str
    i_want: str
    so_that: str


class DbModelsAndApiEndpoints(BaseModel):
    db_models: list[str | dict[str, Any]]
    api_endpoints: list[str | dict[str, Any]]


class FeatureSummaryResult(BaseModel):
    user_stories: list[FeatureSummaryItem]
    acceptance_criteria: list[str]
    db_models_and_api_endpoints: DbModelsAndApiEndpoints
    risk_assessment: list[str]


class FeatureSpecGenerateResponse(BaseModel):
    feature_idea: str
    feature_summary: FeatureSummaryResult


class FeatureSpecTaskSubmitResponse(BaseModel):
    task_id: str
    status: Literal["processing"]


class FeatureSpecTaskStatusResponse(BaseModel):
    task_id: str
    status: Literal["PENDING", "STARTED", "SUCCESS", "FAILURE"]
    result: dict[str, Any] | None = None
    error: str | None = None


class FeatureSpecHistoryItem(BaseModel):
    id: int
    feature_idea: str
    status: Literal["pending", "success", "error"]
    response_json: FeatureSummaryResult | None = None
    error_message: str | None = None
    created_at: datetime


class FeatureSpecHistoryResponse(BaseModel):
    items: list[FeatureSpecHistoryItem]
