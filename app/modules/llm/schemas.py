from typing import Literal

from pydantic import BaseModel, Field


class LlmGenerateRequest(BaseModel):
    prompt: str = Field(min_length=1)
    response_format: Literal["text", "sections", "json"] = "text"


class LlmGenerateResponse(BaseModel):
    raw_content: str
    content: str | None = None
    sections: dict[str, str] | None = None
    data: dict | list | None = None