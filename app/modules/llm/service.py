from app.modules.llm.parser import extract_json, extract_sections, normalize_whitespace, strip_markdown
from app.modules.llm.schemas import LlmGenerateRequest, LlmGenerateResponse
from app.modules.llm.providers.ollama import ollama_client


async def generate_completion(payload: LlmGenerateRequest) -> LlmGenerateResponse:
    raw_content = await ollama_client.generate(payload.prompt)
    normalized_content = normalize_whitespace(strip_markdown(raw_content))

    if payload.response_format == "json":
        return LlmGenerateResponse(
            raw_content=raw_content,
            data=extract_json(normalized_content),
        )

    if payload.response_format == "sections":
        return LlmGenerateResponse(
            raw_content=raw_content,
            sections=extract_sections(normalized_content),
        )

    return LlmGenerateResponse(
        raw_content=raw_content,
        content=normalized_content,
    )