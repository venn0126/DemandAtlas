from __future__ import annotations

from typing import Any
from uuid import uuid4


def build_success_response(data: Any, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "request_id": f"req_{uuid4().hex[:12]}",
        "data": data,
        "meta": meta or {},
        "error": None,
    }


def build_error_response(
    *,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "request_id": f"req_{uuid4().hex[:12]}",
        "data": None,
        "meta": meta or {},
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
    }
