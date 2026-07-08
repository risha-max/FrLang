from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from frlang.web.executor import ExecutionResult, execute_source

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAIN_FILE = PROJECT_ROOT / "main.frlang"
WEB_DIST = PROJECT_ROOT / "web" / "dist"


class SourcePayload(BaseModel):
    source: str = Field(min_length=0)


class RunResponse(BaseModel):
    ok: bool
    stdout: list[str]
    result: str | None = None
    error: str | None = None


class MainResponse(BaseModel):
    source: str
    path: str


def create_app() -> FastAPI:
    app = FastAPI(title="FrLang Web", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/main", response_model=MainResponse)
    def get_main() -> MainResponse:
        if not MAIN_FILE.is_file():
            raise HTTPException(status_code=404, detail="main.frlang introuvable")
        return MainResponse(source=MAIN_FILE.read_text(encoding="utf-8"), path=str(MAIN_FILE))

    @app.put("/api/main", response_model=MainResponse)
    def put_main(payload: SourcePayload) -> MainResponse:
        MAIN_FILE.write_text(payload.source, encoding="utf-8")
        return MainResponse(source=payload.source, path=str(MAIN_FILE))

    @app.post("/api/run", response_model=RunResponse)
    def run_program(payload: SourcePayload) -> RunResponse:
        execution = execute_source(payload.source, MAIN_FILE)
        return _to_run_response(execution)

    if WEB_DIST.is_dir():
        app.mount("/", StaticFiles(directory=WEB_DIST, html=True), name="static")

    return app


def _to_run_response(execution: ExecutionResult) -> RunResponse:
    return RunResponse(
        ok=execution.ok,
        stdout=execution.stdout,
        result=execution.result,
        error=execution.error,
    )


app = create_app()
