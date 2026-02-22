"""
Mock target API for predictable scanner results.
"""

from __future__ import annotations

import os
import time
from typing import Any

from fastapi import FastAPI, Header, Query
from fastapi.responses import JSONResponse, PlainTextResponse


app = FastAPI(title="Mock Target API", version="1.0.0")

MODE = os.getenv("MOCK_MODE", "vulnerable").strip().lower()
SECURE_MODE = MODE == "secure"
EXPECTED_TOKEN = os.getenv("MOCK_AUTH_TOKEN", "mock-token")
RATE_LIMIT = int(os.getenv("MOCK_RATE_LIMIT", "10"))
RATE_WINDOW_SECONDS = int(os.getenv("MOCK_RATE_WINDOW", "60"))

_rate_limit_state = {
    "start": time.time(),
    "count": 0,
}

ITEMS = [
    {
        "id": 1,
        "uuid": "11111111-1111-1111-1111-111111111111",
        "name": "alpha",
    },
    {
        "id": 2,
        "uuid": "22222222-2222-2222-2222-222222222222",
        "name": "beta",
    },
]

USERS = [
    {
        "id": 1,
        "email": "alice@example.com",
        "name": "Alice",
        "role": "user",
    },
    {
        "id": 2,
        "email": "bob@example.com",
        "name": "Bob",
        "role": "admin",
    },
]

ORDERS = [
    {
        "id": 1001,
        "user_id": 1,
        "total": 42.5,
        "status": "paid",
    },
    {
        "id": 1002,
        "user_id": 2,
        "total": 13.0,
        "status": "pending",
    },
]


def _is_authorized(authorization: str | None) -> bool:
    if not authorization:
        return False
    return authorization == f"Bearer {EXPECTED_TOKEN}"


def _rate_limit_headers(remaining: int) -> dict[str, str]:
    reset_in = int(max(0, RATE_WINDOW_SECONDS - (time.time() - _rate_limit_state["start"])))
    return {
        "X-RateLimit-Limit": str(RATE_LIMIT),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(reset_in),
    }


def _check_rate_limit() -> tuple[bool, dict[str, str]]:
    now = time.time()
    if now - _rate_limit_state["start"] >= RATE_WINDOW_SECONDS:
        _rate_limit_state["start"] = now
        _rate_limit_state["count"] = 0

    _rate_limit_state["count"] += 1
    remaining = max(RATE_LIMIT - _rate_limit_state["count"], 0)
    headers = _rate_limit_headers(remaining)

    if _rate_limit_state["count"] > RATE_LIMIT:
        headers["Retry-After"] = str(max(1, RATE_WINDOW_SECONDS - int(now - _rate_limit_state["start"])) )
        return True, headers

    return False, headers


def _sqli_response(id_value: str, secure_mode: bool) -> JSONResponse | PlainTextResponse:
    if secure_mode:
        return JSONResponse(
            {
                "status": "ok",
                "id": id_value,
                "items": ITEMS,
            }
        )

    lower_value = id_value.lower()

    if "sleep" in lower_value or "pg_sleep" in lower_value or "waitfor" in lower_value:
        time.sleep(5)
        return JSONResponse(
            {
                "status": "delayed",
                "id": id_value,
                "items": ITEMS,
            }
        )

    if "and 1=1" in lower_value or "and '1'='1" in lower_value:
        return JSONResponse(
            {
                "status": "true",
                "data": "A" * 1200,
            }
        )

    if "and 1=2" in lower_value or "and '1'='2" in lower_value or "and 1=0" in lower_value:
        return JSONResponse(
            {
                "status": "false",
                "data": "A" * 10,
            }
        )

    if "'" in id_value or "union" in lower_value or "select" in lower_value or " or " in lower_value:
        return PlainTextResponse("SQL syntax error near '...'", status_code=500)

    return JSONResponse(
        {
            "status": "ok",
            "id": id_value,
            "items": ITEMS,
        }
    )


def _require_api_auth(authorization: str | None) -> JSONResponse | None:
    if not _is_authorized(authorization):
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)
    return None


@app.get("/", response_model=None)
def root(
    id: str | None = Query(default=None),
    authorization: str | None = Header(default=None, alias="Authorization"),
):
    if SECURE_MODE and not _is_authorized(authorization):
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)

    if SECURE_MODE:
        limited, headers = _check_rate_limit()
        if limited:
            return JSONResponse({"detail": "Too Many Requests"}, status_code=429, headers=headers)

    if id:
        response = _sqli_response(id, SECURE_MODE)
        if SECURE_MODE and isinstance(response, JSONResponse):
            response.headers.update(_rate_limit_headers(max(0, RATE_LIMIT - _rate_limit_state["count"])))
        return response

    response = JSONResponse(
        {
            "items": ITEMS,
            "count": len(ITEMS),
        }
    )
    if SECURE_MODE:
        response.headers.update(_rate_limit_headers(max(0, RATE_LIMIT - _rate_limit_state["count"])))
    return response


@app.get("/{item_id}")
def get_item(
    item_id: str,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> JSONResponse:
    if SECURE_MODE and not _is_authorized(authorization):
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)

    if SECURE_MODE and item_id != "1":
        return JSONResponse({"detail": "Forbidden"}, status_code=403)

    return JSONResponse(
        {
            "id": item_id,
            "owner_id": 1,
            "details": "public item details",
        }
    )


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
    }


@app.post("/api/auth/login")
def api_login() -> dict[str, str]:
    return {
        "access_token": EXPECTED_TOKEN,
        "token_type": "bearer",
    }


@app.get("/api/users")
def list_users(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> JSONResponse:
    unauthorized = _require_api_auth(authorization)
    if unauthorized:
        return unauthorized

    return JSONResponse(
        {
            "items": USERS,
            "count": len(USERS),
        }
    )


@app.get("/api/users/{user_id}")
def get_user(
    user_id: int,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> JSONResponse:
    unauthorized = _require_api_auth(authorization)
    if unauthorized:
        return unauthorized

    for user in USERS:
        if user["id"] == user_id:
            return JSONResponse(user)

    return JSONResponse({"detail": "Not Found"}, status_code=404)


@app.get("/api/orders")
def list_orders(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> JSONResponse:
    unauthorized = _require_api_auth(authorization)
    if unauthorized:
        return unauthorized

    return JSONResponse(
        {
            "items": ORDERS,
            "count": len(ORDERS),
        }
    )


@app.get("/api/orders/{order_id}")
def get_order(
    order_id: int,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> JSONResponse:
    unauthorized = _require_api_auth(authorization)
    if unauthorized:
        return unauthorized

    for order in ORDERS:
        if order["id"] == order_id:
            return JSONResponse(order)

    return JSONResponse({"detail": "Not Found"}, status_code=404)
