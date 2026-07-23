from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from frlang.web.curriculum import get_lesson, iter_lessons, lesson_count, load_curriculum
from frlang.web.executor import ExecutionResult, execute_source

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROGRESS_DIR = PROJECT_ROOT / "data" / "progress"


def progress_dir() -> Path:
    override = os.environ.get("FRLANG_PROGRESS_DIR")
    if override:
        return Path(override)
    return DEFAULT_PROGRESS_DIR


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_username(username: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "_", username.strip())
    return cleaned or "eleve"


def progress_path(username: str) -> Path:
    return progress_dir() / f"{_safe_username(username)}.json"


def empty_progress(username: str) -> dict[str, Any]:
    return {
        "username": username,
        "lessons": {},
        "sessions": [],
        "events": [],
        "stats": {
            "login_count": 0,
            "total_seconds": 0,
            "guided_seconds": 0,
            "free_seconds": 0,
            "runs_count": 0,
            "lessons_completed": 0,
        },
        "devoirs": {},
        "active_session": None,
    }


def load_progress(username: str) -> dict[str, Any]:
    path = progress_path(username)
    if not path.is_file():
        return empty_progress(username)
    data = json.loads(path.read_text(encoding="utf-8"))
    base = empty_progress(username)
    base.update(data)
    base["stats"] = {**empty_progress(username)["stats"], **(data.get("stats") or {})}
    base["lessons"] = data.get("lessons") or {}
    base["devoirs"] = data.get("devoirs") or {}
    base["sessions"] = data.get("sessions") or []
    base["events"] = data.get("events") or []
    return base


def save_progress(data: dict[str, Any]) -> None:
    directory = progress_dir()
    directory.mkdir(parents=True, exist_ok=True)
    path = progress_path(str(data["username"]))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _append_event(data: dict[str, Any], kind: str, detail: dict[str, Any] | None = None) -> None:
    events = data.setdefault("events", [])
    events.append({"at": _now(), "kind": kind, **(detail or {})})
    data["events"] = events[-200:]


def _path_kind(path: str | None) -> str:
    if not path:
        return "other"
    if path.startswith("/lecons"):
        return "guided"
    return "other"


def start_session(username: str, path: str = "/accueil") -> dict[str, Any]:
    data = load_progress(username)
    if data.get("active_session"):
        _close_active(data)
    session_id = str(uuid.uuid4())
    now = _now()
    data["active_session"] = {
        "id": session_id,
        "started_at": now,
        "last_heartbeat": now,
        "path": path,
        "seconds": 0,
    }
    data["stats"]["login_count"] = int(data["stats"].get("login_count", 0)) + 1
    _append_event(data, "login", {"session_id": session_id, "path": path})
    save_progress(data)
    return data


def heartbeat(username: str, session_id: str, path: str | None = None) -> dict[str, Any]:
    data = load_progress(username)
    active = data.get("active_session")
    if not active or active.get("id") != session_id:
        raise ValueError("session_invalide")

    now = datetime.now(timezone.utc)
    last = datetime.fromisoformat(active["last_heartbeat"])
    delta = max(0, min(int((now - last).total_seconds()), 120))
    active["seconds"] = int(active.get("seconds", 0)) + delta
    active["last_heartbeat"] = now.isoformat()
    if path:
        active["path"] = path
        kind = _path_kind(path)
        if kind == "guided":
            data["stats"]["guided_seconds"] = int(data["stats"].get("guided_seconds", 0)) + delta
        elif kind == "free":
            data["stats"]["free_seconds"] = int(data["stats"].get("free_seconds", 0)) + delta
    data["stats"]["total_seconds"] = int(data["stats"].get("total_seconds", 0)) + delta
    data["active_session"] = active
    save_progress(data)
    return data


def end_session(username: str, session_id: str | None = None) -> dict[str, Any]:
    data = load_progress(username)
    active = data.get("active_session")
    if active and (session_id is None or active.get("id") == session_id):
        _close_active(data)
        _append_event(data, "logout", {"session_id": active.get("id")})
        save_progress(data)
    return data


def _close_active(data: dict[str, Any]) -> None:
    active = data.get("active_session")
    if not active:
        return
    now = datetime.now(timezone.utc)
    last = datetime.fromisoformat(active["last_heartbeat"])
    delta = max(0, min(int((now - last).total_seconds()), 120))
    active["seconds"] = int(active.get("seconds", 0)) + delta
    active["ended_at"] = now.isoformat()
    data["stats"]["total_seconds"] = int(data["stats"].get("total_seconds", 0)) + delta
    kind = _path_kind(active.get("path"))
    if kind == "guided":
        data["stats"]["guided_seconds"] = int(data["stats"].get("guided_seconds", 0)) + delta
    elif kind == "free":
        data["stats"]["free_seconds"] = int(data["stats"].get("free_seconds", 0)) + delta
    sessions = data.setdefault("sessions", [])
    sessions.append(active)
    data["sessions"] = sessions[-100:]
    data["active_session"] = None


def record_run(username: str, ok: bool, context: str = "free") -> dict[str, Any]:
    data = load_progress(username)
    data["stats"]["runs_count"] = int(data["stats"].get("runs_count", 0)) + 1
    _append_event(data, "run", {"ok": ok, "context": context})
    save_progress(data)
    return data


def evaluate_checks(checks: list[dict[str, Any]], execution: ExecutionResult) -> tuple[bool, list[str]]:
    messages: list[str] = []
    passed = True
    stdout_text = "\n".join(execution.stdout)
    for check in checks:
        kind = check.get("type")
        if kind == "runs_ok":
            if not execution.ok:
                passed = False
                messages.append(execution.error or "Le programme doit s'exécuter sans erreur.")
        elif kind == "stdout_contains":
            value = str(check.get("value", ""))
            if value not in stdout_text:
                passed = False
                messages.append(f"La sortie doit contenir « {value} ».")
        elif kind == "stdout_equals":
            value = str(check.get("value", ""))
            if stdout_text.strip() != value.strip():
                passed = False
                messages.append("La sortie ne correspond pas exactement à l'attendu.")
        else:
            messages.append(f"Vérification inconnue: {kind}")
            passed = False
    if passed and not messages:
        messages.append("Bravo — objectifs atteints.")
    return passed, messages


def submit_lesson_attempt(
    username: str,
    lesson_id: str,
    source: str,
    *,
    mark_complete_if_pass: bool = True,
) -> dict[str, Any]:
    lesson = get_lesson(lesson_id)
    if lesson is None:
        raise KeyError(lesson_id)

    execution = execute_source(source, PROJECT_ROOT / "main.frlang")
    passed, messages = evaluate_checks(lesson.get("checks") or [], execution)

    data = load_progress(username)
    entry = data["lessons"].get(lesson_id) or {
        "status": "in_progress",
        "attempts": 0,
        "completed_at": None,
        "last_source": "",
        "last_messages": [],
    }
    entry["attempts"] = int(entry.get("attempts", 0)) + 1
    entry["last_source"] = source
    entry["last_messages"] = messages
    entry["last_ok"] = passed
    entry["updated_at"] = _now()
    if entry.get("status") != "completed":
        entry["status"] = "completed" if (passed and mark_complete_if_pass) else "in_progress"
    if passed and mark_complete_if_pass and not entry.get("completed_at"):
        entry["completed_at"] = _now()
        data["stats"]["lessons_completed"] = sum(
            1 for item in {**data["lessons"], lesson_id: entry}.values() if item.get("status") == "completed"
        )
        _append_event(data, "lesson_completed", {"lesson_id": lesson_id})
    else:
        _append_event(data, "lesson_attempt", {"lesson_id": lesson_id, "ok": passed})

    data["lessons"][lesson_id] = entry
    data["stats"]["runs_count"] = int(data["stats"].get("runs_count", 0)) + 1
    save_progress(data)

    return {
        "passed": passed,
        "messages": messages,
        "execution": {
            "ok": execution.ok,
            "stdout": execution.stdout,
            "result": execution.result,
            "error": execution.error,
        },
        "progress": summarize_progress(username, data),
        "lesson": entry,
    }


def summarize_progress(username: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    progress = data or load_progress(username)
    curriculum = load_curriculum()
    total = lesson_count(curriculum)
    lessons_state = progress.get("lessons") or {}
    completed_ids = [
        lesson_id
        for lesson_id, state in lessons_state.items()
        if state.get("status") == "completed"
    ]
    completed = len(completed_ids)
    next_lesson = None
    for lesson in iter_lessons(curriculum):
        if lesson["id"] not in completed_ids:
            next_lesson = {
                "id": lesson["id"],
                "title": lesson.get("title"),
                "module_title": lesson.get("module_title"),
            }
            break

    stats = progress.get("stats") or {}
    return {
        "username": username,
        "total_lessons": total,
        "completed_lessons": completed,
        "completion_ratio": (completed / total) if total else 0.0,
        "next_lesson": next_lesson,
        "login_count": int(stats.get("login_count", 0)),
        "total_seconds": int(stats.get("total_seconds", 0)),
        "guided_seconds": int(stats.get("guided_seconds", 0)),
        "free_seconds": int(stats.get("free_seconds", 0)),
        "runs_count": int(stats.get("runs_count", 0)),
        "active_session": progress.get("active_session"),
        "lessons": lessons_state,
        "recent_sessions": list(reversed(progress.get("sessions") or []))[:10],
        "recent_events": list(reversed(progress.get("events") or []))[:20],
    }
