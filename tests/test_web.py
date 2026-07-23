from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from frlang.web.app import create_app
from frlang.web.auth import authenticate, load_eleves
from frlang.web.executor import execute_source
from frlang.web.progress import start_session, submit_lesson_attempt, summarize_progress


def test_execute_main_example(tmp_path: Path) -> None:
    main = tmp_path / "main.frlang"
    main.write_text(
        """
        soit nombre x = 2;
        afficher x;
        """,
        encoding="utf-8",
    )
    result = execute_source(main.read_text(encoding="utf-8"), main)
    assert result.ok is True
    assert result.stdout == ["2"]
    assert result.error is None


def test_execute_reports_error(tmp_path: Path) -> None:
    main = tmp_path / "main.frlang"
    main.write_text("soit nombre x = ;", encoding="utf-8")
    result = execute_source(main.read_text(encoding="utf-8"), main)
    assert result.ok is False
    assert result.error is not None


def test_authenticate_plain_credentials(tmp_path: Path) -> None:
    eleves = tmp_path / "eleves.json"
    eleves.write_text(
        json.dumps(
            {
                "eleves": [
                    {
                        "username": "Marie",
                        "password": "secret",
                        "display_name": "Marie Tremblay",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    assert load_eleves(eleves)[0].username == "Marie"
    ok = authenticate("marie", "secret", eleves)
    assert ok is not None
    assert ok.display_name == "Marie Tremblay"
    assert authenticate("marie", "wrong", eleves) is None


def test_login_endpoint(tmp_path: Path, monkeypatch) -> None:
    eleves = tmp_path / "eleves.json"
    eleves.write_text(
        json.dumps(
            {
                "eleves": [
                    {"username": "leo", "password": "abc", "display_name": "Léo"}
                ]
            }
        ),
        encoding="utf-8",
    )
    progress_dir = tmp_path / "progress"
    monkeypatch.setenv("FRLANG_ELEVES_PATH", str(eleves))
    monkeypatch.setenv("FRLANG_PROGRESS_DIR", str(progress_dir))
    client = TestClient(create_app())

    bad = client.post("/api/login", json={"username": "leo", "password": "nope"})
    assert bad.status_code == 401

    good = client.post("/api/login", json={"username": "Leo", "password": "abc"})
    assert good.status_code == 200
    body = good.json()
    assert body["username"] == "leo"
    assert body["display_name"] == "Léo"
    assert body["session_id"]
    assert body["role"] == "eleve"


def test_module_lock_blocks_later_lesson(tmp_path: Path, monkeypatch) -> None:
    from frlang.web.unlock import is_lesson_unlocked

    assert is_lesson_unlocked("bonjour", {}) is True
    assert is_lesson_unlocked("variables", {}) is False
    assert (
        is_lesson_unlocked(
            "variables",
            {"bonjour": {"status": "completed"}},
        )
        is True
    )
    assert (
        is_lesson_unlocked(
            "arithmetique",
            {"bonjour": {"status": "completed"}, "variables": {"status": "completed"}},
        )
        is True
    )
    assert (
        is_lesson_unlocked(
            "conditions",
            {
                "bonjour": {"status": "completed"},
                "variables": {"status": "completed"},
                "arithmetique": {"status": "completed"},
            },
        )
        is False
    )


def test_progress_and_lesson_attempt(tmp_path: Path, monkeypatch) -> None:
    progress_dir = tmp_path / "progress"
    monkeypatch.setenv("FRLANG_PROGRESS_DIR", str(progress_dir))
    start_session("demo", path="/lecons/bonjour")
    result = submit_lesson_attempt(
        "demo",
        "bonjour",
        'afficher "Bonjour FrLang!";',
    )
    assert result["passed"] is True
    summary = summarize_progress("demo")
    assert summary["completed_lessons"] >= 1
    assert summary["login_count"] >= 1
    assert "bonjour" in summary["lessons"]


def test_devoir_attempt_and_assign(tmp_path: Path, monkeypatch) -> None:
    from frlang.web.devoirs import assign_devoir, run_devoir

    progress_dir = tmp_path / "progress"
    devoirs_file = tmp_path / "devoirs.json"
    devoirs_file.write_text(
        json.dumps(
            {
                "devoirs": [
                    {
                        "id": "mini",
                        "title": "Mini",
                        "difficulty": "facile",
                        "points": 10,
                        "tags": ["TEST"],
                        "summary": "Affiche 1",
                        "instructions": "Utilise `afficher`.",
                        "starter_code": "",
                        "sample_tests": "// 1",
                        "checks": [
                            {"type": "runs_ok"},
                            {"type": "stdout_contains", "value": "1"},
                        ],
                        "assignees": ["demo"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("FRLANG_PROGRESS_DIR", str(progress_dir))
    monkeypatch.setenv("FRLANG_DEVOIRS_PATH", str(devoirs_file))

    bad = run_devoir("demo", "mini", 'afficher "0";', mode="attempt")
    assert bad["passed"] is False

    good = run_devoir("demo", "mini", "afficher 1;", mode="attempt")
    assert good["passed"] is True

    assign_devoir("mini", ["encours"])
    try:
        run_devoir("demo", "mini", "afficher 1;", mode="test")
        assert False, "expected PermissionError"
    except PermissionError:
        pass
