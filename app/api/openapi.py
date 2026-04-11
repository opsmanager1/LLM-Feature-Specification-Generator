from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def configure_openapi_bearer_auth(app: FastAPI) -> None:
    def custom_openapi() -> dict:
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version=app.version,
            routes=app.routes,
        )

        components = schema.setdefault("components", {})
        security_schemes = components.setdefault("securitySchemes", {})
        if "OAuth2PasswordBearer" in security_schemes:
            security_schemes.pop("OAuth2PasswordBearer", None)
            security_schemes["BearerAuth"] = {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }

            for path_item in schema.get("paths", {}).values():
                for operation in path_item.values():
                    if not isinstance(operation, dict):
                        continue
                    security = operation.get("security")
                    if not security:
                        continue
                    operation["security"] = [
                        (
                            {"BearerAuth": item.get("OAuth2PasswordBearer", [])}
                            if "OAuth2PasswordBearer" in item
                            else item
                        )
                        for item in security
                    ]

        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi
