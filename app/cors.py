from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings


def parse_origins(value: str) -> list[str]:
    """Turn 'https://a.com, https://b.com/' into a clean list of origins."""
    origins = []
    for item in value.split(","):
        origin = item.strip().rstrip("/")
        if origin and origin not in origins:
            origins.append(origin)
    return origins


def configure_cors(app: FastAPI, settings: Settings) -> None:
    """Allow browser calls from the configured origins. No origins, no CORS."""
    origins = parse_origins(settings.cors_origins)
    if not origins:
        return
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["X-API-Key", "Content-Type"],
        max_age=600,
    )
