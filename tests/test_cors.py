from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Settings
from app.cors import configure_cors, parse_origins

ORIGIN = "http://localhost:3000"


def make_client(cors_origins: str) -> TestClient:
    app = FastAPI()

    @app.get("/ping")
    def ping():
        return {"ok": True}

    configure_cors(app, Settings(cors_origins=cors_origins))
    return TestClient(app)


def test_parse_origins_trims_and_drops_empty_and_duplicates():
    assert parse_origins(" http://a.com ,http://b.com/, ,http://a.com") == [
        "http://a.com",
        "http://b.com",
    ]


def test_parse_origins_empty_string_gives_empty_list():
    assert parse_origins("") == []


def test_allowed_origin_gets_cors_header():
    res = make_client(ORIGIN).get("/ping", headers={"Origin": ORIGIN})
    assert res.headers["access-control-allow-origin"] == ORIGIN


def test_unlisted_origin_gets_no_cors_header():
    res = make_client(ORIGIN).get("/ping", headers={"Origin": "http://evil.test"})
    assert "access-control-allow-origin" not in res.headers


def test_no_origins_configured_sends_no_cors_headers():
    res = make_client("").get("/ping", headers={"Origin": ORIGIN})
    assert res.status_code == 200
    assert "access-control-allow-origin" not in res.headers


def test_preflight_allows_api_key_header():
    res = make_client(ORIGIN).options(
        "/ping",
        headers={
            "Origin": ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "x-api-key",
        },
    )
    assert res.status_code == 200
    assert res.headers["access-control-allow-origin"] == ORIGIN
    assert "x-api-key" in res.headers["access-control-allow-headers"].lower()


def test_preflight_from_unlisted_origin_is_rejected():
    res = make_client(ORIGIN).options(
        "/ping",
        headers={
            "Origin": "http://evil.test",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert res.status_code == 400


def test_wildcard_is_never_used():
    res = make_client(ORIGIN).get("/ping", headers={"Origin": ORIGIN})
    assert res.headers["access-control-allow-origin"] != "*"
