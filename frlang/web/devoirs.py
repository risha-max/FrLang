from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from frlang.web.executor import execute_source
from frlang.web.progress import (
    PROJECT_ROOT,
    _append_event,
    _now,
    evaluate_checks,
    load_progress,
    save_progress,
    summarize_progress,
)

DEFAULT_DEVOIRS_PATH = PROJECT_ROOT / "data" / "devoirs.json"


def devoirs_path() -> Path:
    override = os.environ.get("FRLANG_DEVOIRS_PATH")
    if override:
        return Path(override)
    return DEFAULT_DEVOIRS_PATH


def load_devoirs(path: Path | None = None) -> list[dict[str, Any]]:
    file_path = path or devoirs_path()
    if not file_path.is_file():
        return []
    raw = json.loads(file_path.read_text(encoding="utf-8"))
    entries = raw.get("devoirs", raw) if isinstance(raw, dict) else raw
    if not isinstance(entries, list):
        raise ValueError("devoirs.json: attendu une liste")
    return [entry for entry in entries if isinstance(entry, dict) and entry.get("id")]


def save_devoirs(devoirs: list[dict[str, Any]], path: Path | None = None) -> None:
    file_path = path or devoirs_path()
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        json.dumps({"devoirs": devoirs}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def get_devoir(devoir_id: str, path: Path | None = None) -> dict[str, Any] | None:
    for devoir in load_devoirs(path):
        if devoir.get("id") == devoir_id:
            return devoir
    return None


def is_assigned(devoir: dict[str, Any], username: str) -> bool:
    assignees = devoir.get("assignees") or []
    if "*" in assignees:
        return True
    needle = username.casefold()
    return any(str(name).casefold() == needle for name in assignees)


def list_for_user(username: str, *, role: str = "eleve") -> list[dict[str, Any]]:
    progress = load_progress(username)
    states = progress.get("devoirs") or {}
    out: list[dict[str, Any]] = []
    for devoir in load_devoirs():
        if role != "admin" and not is_assigned(devoir, username):
            continue
        state = states.get(devoir["id"]) or {}
        out.append(
            {
                "id": devoir["id"],
                "title": devoir.get("title"),
                "difficulty": devoir.get("difficulty"),
                "points": devoir.get("points", 0),
                "tags": devoir.get("tags") or [],
                "summary": devoir.get("summary"),
                "assignees": devoir.get("assignees") or [],
                "status": state.get("status", "todo"),
                "attempts": state.get("attempts", 0),
                "completed_at": state.get("completed_at"),
            }
        )
    return out


def public_devoir(devoir: dict[str, Any]) -> dict[str, Any]:
    """Sans les checks secrets (pour l’élève)."""
    return {
        "id": devoir["id"],
        "title": devoir.get("title"),
        "difficulty": devoir.get("difficulty"),
        "points": devoir.get("points", 0),
        "tags": devoir.get("tags") or [],
        "summary": devoir.get("summary"),
        "instructions": devoir.get("instructions"),
        "starter_code": devoir.get("starter_code", ""),
        "sample_tests": devoir.get("sample_tests", ""),
        "assignees": devoir.get("assignees") or [],
    }


def assign_devoir(devoir_id: str, usernames: list[str]) -> dict[str, Any]:
    devoirs = load_devoirs()
    found = None
    for devoir in devoirs:
        if devoir.get("id") == devoir_id:
            devoir["assignees"] = usernames
            found = devoir
            break
    if found is None:
        raise KeyError(devoir_id)
    save_devoirs(devoirs)
    return found


def run_devoir(
    username: str,
    devoir_id: str,
    source: str,
    *,
    mode: str = "test",
) -> dict[str, Any]:
    devoir = get_devoir(devoir_id)
    if devoir is None:
        raise KeyError(devoir_id)
    if not is_assigned(devoir, username):
        raise PermissionError(devoir_id)

    execution = execute_source(source, PROJECT_ROOT / "main.frlang")
    checks = devoir.get("checks") or []
    if mode == "test":
        # Test = exécution libre + rappel des exemples (pas de validation secrète stricte)
        passed = execution.ok
        messages = (
            ["Exécution OK — compare avec les exemples."]
            if passed
            else [execution.error or "Erreur d’exécution."]
        )
        if passed and checks:
            soft_ok, soft_msgs = evaluate_checks(checks, execution)
            if soft_ok:
                messages = ["Les exemples semblent passés."]
            else:
                messages = ["Exécution OK, mais les exemples ne matchent pas encore."] + soft_msgs
                passed = False
    else:
        passed, messages = evaluate_checks(checks, execution)

    data = load_progress(username)
    devoirs_state = data.setdefault("devoirs", {})
    entry = devoirs_state.get(devoir_id) or {
        "status": "in_progress",
        "attempts": 0,
        "completed_at": None,
        "last_source": "",
        "last_messages": [],
    }
    entry["last_source"] = source
    entry["last_messages"] = messages
    entry["last_ok"] = passed
    entry["updated_at"] = _now()
    if mode == "attempt":
        entry["attempts"] = int(entry.get("attempts", 0)) + 1
        if passed:
            entry["status"] = "completed"
            if not entry.get("completed_at"):
                entry["completed_at"] = _now()
            _append_event(data, "devoir_completed", {"devoir_id": devoir_id})
        elif entry.get("status") != "completed":
            entry["status"] = "in_progress"
            _append_event(data, "devoir_attempt", {"devoir_id": devoir_id, "ok": False})
    else:
        if entry.get("status") != "completed":
            entry["status"] = "in_progress"
        _append_event(data, "devoir_test", {"devoir_id": devoir_id, "ok": passed})

    devoirs_state[devoir_id] = entry
    data["stats"]["runs_count"] = int(data["stats"].get("runs_count", 0)) + 1
    save_progress(data)

    return {
        "passed": passed,
        "mode": mode,
        "messages": messages,
        "execution": {
            "ok": execution.ok,
            "stdout": execution.stdout,
            "result": execution.result,
            "error": execution.error,
        },
        "devoir": entry,
        "progress": summarize_progress(username, data),
    }
