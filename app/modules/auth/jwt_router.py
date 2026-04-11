from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.core.settings import settings
from app.modules.auth.infrastructure.fastapi_users_adapter import (
    get_jwt_strategy,
    get_refresh_jwt_strategy,
    get_user_manager,
)
from app.modules.auth.service import AuthSessionService

router = APIRouter(prefix="/jwt")


def _build_refresh_cookie_path() -> str:
    return f"{settings.API_V1_PREFIX}{settings.AUTH_PREFIX}/jwt"


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.AUTH_REFRESH_COOKIE_SECURE,
        samesite=settings.AUTH_REFRESH_COOKIE_SAMESITE,
        max_age=settings.AUTH_REFRESH_TOKEN_EXPIRE_SECONDS,
        path=_build_refresh_cookie_path(),
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        path=_build_refresh_cookie_path(),
    )


async def get_auth_session_service(
    user_manager=Depends(get_user_manager),
) -> AuthSessionService:
    return AuthSessionService(
        user_authentication=user_manager,
        access_token_strategy=get_jwt_strategy(),
        refresh_token_strategy=get_refresh_jwt_strategy(),
    )


@router.post("/login", name="auth:jwt.login")
async def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    auth_session_service: AuthSessionService = Depends(get_auth_session_service),
) -> JSONResponse:
    tokens = await auth_session_service.login(credentials)
    if tokens is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LOGIN_BAD_CREDENTIALS",
        )

    response = JSONResponse(
        {"access_token": tokens.access_token, "token_type": "bearer"}
    )
    _set_refresh_cookie(response, tokens.refresh_token)
    return response


@router.post("/refresh", name="auth:jwt.refresh")
async def refresh(
    request: Request,
    auth_session_service: AuthSessionService = Depends(get_auth_session_service),
) -> JSONResponse:
    refresh_token = request.cookies.get(settings.AUTH_REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    tokens = await auth_session_service.refresh(refresh_token)
    if tokens is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    response = JSONResponse(
        {"access_token": tokens.access_token, "token_type": "bearer"}
    )
    _set_refresh_cookie(response, tokens.refresh_token)
    return response


@router.post("/logout", name="auth:jwt.logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    auth_session_service: AuthSessionService = Depends(get_auth_session_service),
) -> Response:
    await auth_session_service.logout(request.cookies.get(settings.AUTH_REFRESH_COOKIE_NAME))

    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    _clear_refresh_cookie(response)
    return response
