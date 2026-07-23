from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from frlang.web.auth import authenticate, public_eleves
from frlang.web.curriculum import get_lesson, load_curriculum
from frlang.web.devoirs import (
    assign_devoir,
    get_devoir,
    list_for_user,
    public_devoir,
    run_devoir,
)
from frlang.web.executor import ExecutionResult, execute_source
from frlang.web.progress import (
    end_session,
    heartbeat,
    load_progress,
    record_run,
    start_session,
    submit_lesson_attempt,
    summarize_progress,
)
from frlang.web.unlock import is_lesson_unlocked


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAIN_FILE = PROJECT_ROOT / "main.frlang"
WEB_DIST = PROJECT_ROOT / "web" / "dist"


class SourcePayload(BaseModel):
    source: str = Field(min_length=0)
    username: str | None = None
    context: str = "free"


class LoginPayload(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    username: str
    display_name: str
    session_id: str
    role: str = "eleve"


class SessionPayload(BaseModel):
    username: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    path: str | None = None


class LessonAttemptPayload(BaseModel):
    username: str = Field(min_length=1)
    source: str = Field(min_length=0)


class DevoirRunPayload(BaseModel):
    username: str = Field(min_length=1)
    source: str = Field(min_length=0)
    mode: str = "test"


class DevoirAssignPayload(BaseModel):
    usernames: list[str]


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

    @app.post("/api/login", response_model=LoginResponse)
    def login(payload: LoginPayload) -> LoginResponse:
        eleve = authenticate(payload.username, payload.password)
        if eleve is None:
            raise HTTPException(
                status_code=401,
                detail="Identifiant ou mot de passe incorrect.",
            )
        progress = start_session(eleve.username, path="/accueil")
        session = progress.get("active_session") or {}
        return LoginResponse(
            username=eleve.username,
            display_name=eleve.display_name,
            session_id=str(session.get("id") or ""),
            role=eleve.role,
        )

    @app.get("/api/eleves")
    def list_eleves() -> list[dict[str, str]]:
        return public_eleves()

    @app.post("/api/session/heartbeat")
    def session_heartbeat(payload: SessionPayload) -> dict[str, Any]:
        try:
            data = heartbeat(payload.username, payload.session_id, payload.path)
        except ValueError:
            raise HTTPException(status_code=400, detail="Session invalide.") from None
        return {"ok": True, "active_session": data.get("active_session")}

    @app.post("/api/session/end")
    def session_end(payload: SessionPayload) -> dict[str, Any]:
        data = end_session(payload.username, payload.session_id)
        return {"ok": True, "stats": data.get("stats")}

    @app.get("/api/curriculum")
    def curriculum() -> dict[str, Any]:
        return load_curriculum()

    @app.get("/api/curriculum/lessons/{lesson_id}")
    def curriculum_lesson(lesson_id: str) -> dict[str, Any]:
        lesson = get_lesson(lesson_id)
        if lesson is None:
            raise HTTPException(status_code=404, detail="Leçon introuvable.")
        return lesson

    @app.get("/api/progress/{username}")
    def progress(username: str) -> dict[str, Any]:
        return summarize_progress(username)

    @app.post("/api/lessons/{lesson_id}/attempt")
    def lesson_attempt(lesson_id: str, payload: LessonAttemptPayload) -> dict[str, Any]:
        progress = summarize_progress(payload.username)
        if not is_lesson_unlocked(lesson_id, progress.get("lessons") or {}):
            raise HTTPException(
                status_code=403,
                detail="Cette leçon est verrouillée. Termine d'abord le module précédent.",
            )
        try:
            return submit_lesson_attempt(payload.username, lesson_id, payload.source)
        except KeyError:
            raise HTTPException(status_code=404, detail="Leçon introuvable.") from None

    @app.get("/api/devoirs")
    def devoirs_list(username: str, role: str = "eleve") -> list[dict[str, Any]]:
        return list_for_user(username, role=role)

    @app.get("/api/devoirs/{devoir_id}")
    def devoir_detail(devoir_id: str, username: str, role: str = "eleve") -> dict[str, Any]:
        devoir = get_devoir(devoir_id)
        if devoir is None:
            raise HTTPException(status_code=404, detail="Devoir introuvable.")
        if role != "admin" and not any(
            a == "*" or str(a).casefold() == username.casefold()
            for a in (devoir.get("assignees") or [])
        ):
            raise HTTPException(status_code=403, detail="Devoir non assigné.")
        progress = load_progress(username)
        state = (progress.get("devoirs") or {}).get(devoir_id) or {}
        body = public_devoir(devoir)
        body["status"] = state.get("status", "todo")
        body["attempts"] = state.get("attempts", 0)
        body["last_source"] = state.get("last_source") or devoir.get("starter_code", "")
        return body

    @app.post("/api/devoirs/{devoir_id}/run")
    def devoir_run(devoir_id: str, payload: DevoirRunPayload) -> dict[str, Any]:
        mode = payload.mode if payload.mode in {"test", "attempt"} else "test"
        try:
            return run_devoir(payload.username, devoir_id, payload.source, mode=mode)
        except KeyError:
            raise HTTPException(status_code=404, detail="Devoir introuvable.") from None
        except PermissionError:
            raise HTTPException(status_code=403, detail="Devoir non assigné.") from None

    @app.put("/api/devoirs/{devoir_id}/assign")
    def devoir_assign(devoir_id: str, payload: DevoirAssignPayload) -> dict[str, Any]:
        try:
            devoir = assign_devoir(devoir_id, payload.usernames)
        except KeyError:
            raise HTTPException(status_code=404, detail="Devoir introuvable.") from None
        return public_devoir(devoir)

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
        if payload.username:
            record_run(payload.username, execution.ok, payload.context)
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
