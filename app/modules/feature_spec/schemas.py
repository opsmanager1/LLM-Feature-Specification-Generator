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


class DbModelsAndApiEndpoints(BaseModel):
    db_models: list[str]
    api_endpoints: list[str]


class FeatureSummaryResult(BaseModel):
    user_stories: list[FeatureSummaryItem]
    acceptance_criteria: list[str]
    db_models_and_api_endpoints: DbModelsAndApiEndpoints
    risk_assessment: list[str]

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_user_stories(cls, data):
        if not isinstance(data, dict):
            return data

        normalized = dict(data)

        if "user_stories" not in normalized and "feature_summary_items" in normalized:
            normalized["user_stories"] = normalized["feature_summary_items"]

        if "acceptance_criteria" not in normalized:
            if "acceptance" in normalized:
                normalized["acceptance_criteria"] = normalized["acceptance"]

        if "db_models_and_api_endpoints" not in normalized:
            db_models = normalized.get("db_models", [])
            api_endpoints = normalized.get("api_endpoints", [])
            normalized["db_models_and_api_endpoints"] = {
                "db_models": db_models,
                "api_endpoints": api_endpoints,
            }

        if "risk_assessment" not in normalized and "risks" in normalized:
            normalized["risk_assessment"] = normalized["risks"]

        return normalized


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
