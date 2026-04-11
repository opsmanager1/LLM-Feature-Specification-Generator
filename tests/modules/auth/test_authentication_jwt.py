from app.core.settings import settings
from app.modules.auth.infrastructure.fastapi_users_adapter import bearer_transport, get_jwt_strategy


def test_bearer_transport_token_url_matches_settings() -> None:
    assert (
        bearer_transport.scheme.model.flows.password.tokenUrl
        == f"{settings.API_V1_PREFIX}{settings.AUTH_PREFIX}/jwt/login"
    )


def test_get_jwt_strategy_uses_settings_secret_and_lifetime() -> None:
    strategy = get_jwt_strategy()

    assert strategy.secret == settings.SECRET_KEY
    assert (
        strategy.lifetime_seconds
        == settings.ACCESS_TOKEN_EXPIRE_MINUTES * settings.ACCESS_TOKEN_MINUTE_IN_SECONDS
    )
