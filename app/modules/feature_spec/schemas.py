from datetime import datetime
from typing import Any, Literal

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
    db_models: list[str | dict[str, Any]]
    api_endpoints: list[str | dict[str, Any]]


class FeatureSummaryResult(BaseModel):
    user_stories: list[FeatureSummaryItem]
    acceptance_criteria: list[str]
    db_models_and_api_endpoints: DbModelsAndApiEndpoints
    risk_assessment: list[str]

    @staticmethod
    def _is_missing(value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, str):
            return not value.strip()
        if isinstance(value, (list, dict)):
            return not value
        return False

    @staticmethod
    def _coerce_legacy_string_list(value: Any) -> list[str] | list[Any] | None:
        if isinstance(value, str):
            stripped = value.strip()
            return [stripped] if stripped else None
        if isinstance(value, list):
            return value
        return None

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_user_stories(cls, data):
        if not isinstance(data, dict):
            return data

        normalized = dict(data)

        if "user_stories" not in normalized and "feature_summary_items" in normalized:
            normalized["user_stories"] = normalized["feature_summary_items"]

        if cls._is_missing(normalized.get("acceptance_criteria")):
            legacy_acceptance = cls._coerce_legacy_string_list(normalized.get("acceptance"))
            if legacy_acceptance is not None:
                normalized["acceptance_criteria"] = legacy_acceptance

        if "db_models_and_api_endpoints" not in normalized:
            db_models = normalized.get("db_models", [])
            api_endpoints = normalized.get("api_endpoints", [])
            normalized["db_models_and_api_endpoints"] = DbModelsAndApiEndpoints(
                db_models=db_models,
                api_endpoints=api_endpoints,
            ).model_dump()

        if cls._is_missing(normalized.get("risk_assessment")) and "risks" in normalized:
            normalized["risk_assessment"] = normalized["risks"]

        return normalized


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
