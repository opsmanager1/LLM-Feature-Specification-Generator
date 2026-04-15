from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

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


class FeatureSummaryResult(BaseModel):
    feature_summary: str
    feature_summary_items: list[FeatureSummaryItem]

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_user_stories(cls, data):
        if isinstance(data, dict) and "feature_summary_items" not in data:
            if "user_stories" in data:
                data = {**data, "feature_summary_items": data["user_stories"]}
        return data


class FeatureSpecGenerateResponse(BaseModel):
    feature_idea: str
    feature_summary: FeatureSummaryResult


class FeatureSpecHistoryItem(BaseModel):
    id: int
    feature_idea: str
    status: Literal["pending", "success", "error"]
    response_json: FeatureSummaryResult | None = None
    error_message: str | None = None
    created_at: datetime


class FeatureSpecHistoryResponse(BaseModel):
    items: list[FeatureSpecHistoryItem]
