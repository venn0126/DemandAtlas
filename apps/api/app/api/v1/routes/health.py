from fastapi import APIRouter


router = APIRouter(tags=["Health"])


@router.get("/healthz")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
