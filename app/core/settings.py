from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Specification Generator"
    ENV: str = "development"
    DEBUG: bool = False
    VERSION: str = "1.0.0"

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ACCESS_TOKEN_MINUTE_IN_SECONDS: int = 60

    AUTH_PREFIX: str = "/auth"
    AUTH_ME_PATH: str = "/me"
    AUTH_TAG: str = "auth"
    AUTH_BOOTSTRAP_ENABLED: bool = False
    AUTH_BOOTSTRAP_SUPERUSER: bool = True

    AUTH_USERNAME: str | None = None
    AUTH_EMAIL: str | None = None
    AUTH_PASSWORD: str | None = None
    AUTH_PASSWORD_HASH: str | None = None

    ALLOWED_ORIGINS: list[str] = ["*"]
    SECURITY_TRUSTED_HOSTS: list[str] = ["*"]
    SECURITY_ENABLE_HTTPS_REDIRECT: bool = False
    SECURITY_CSP: str = ""
    SECURITY_REFERRER_POLICY: str = "strict-origin-when-cross-origin"
    SECURITY_CORS_ALLOW_METHODS: list[str] = [
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ]
    SECURITY_CORS_ALLOW_HEADERS: list[str] = [
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-Request-ID",
    ]
    SECURITY_REQUEST_ID_HEADER: str = "X-Request-ID"
    SECURITY_LOG_SUSPICIOUS: bool = True
    SECURITY_RATE_LIMIT_ENABLED: bool = True
    SECURITY_RATE_LIMIT_REQUESTS: int = 120
    SECURITY_RATE_LIMIT_WINDOW_SECONDS: int = 60
    SECURITY_RATE_LIMIT_PATHS: list[str] = ["/api/v1/auth"]

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"
    OLLAMA_TIMEOUT: int = 120
    OLLAMA_SYSTEM_PROMPT: str = (
        "You are a helpful assistant that generates software specifications."
    )
    LLM_PREFIX: str = "/llm"
    LLM_GENERATE_PATH: str = "/generate"
    LLM_TAG: str = "llm"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
