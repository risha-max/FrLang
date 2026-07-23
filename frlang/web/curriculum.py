from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CURRICULUM_PATH = PROJECT_ROOT / "data" / "curriculum.json"


def curriculum_path() -> Path:
    override = os.environ.get("FRLANG_CURRICULUM_PATH")
    if override:
        return Path(override)
    return DEFAULT_CURRICULUM_PATH


def load_curriculum(path: Path | None = None) -> dict[str, Any]:
    file_path = path or curriculum_path()
    if not file_path.is_file():
        return {"title": "Parcours FrLang", "description": "", "modules": []}
    return json.loads(file_path.read_text(encoding="utf-8"))


def iter_lessons(curriculum: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    data = curriculum or load_curriculum()
    lessons: list[dict[str, Any]] = []
    for module in data.get("modules", []):
        for lesson in module.get("lessons", []):
            lessons.append(
                {
                    **lesson,
                    "module_id": module.get("id"),
                    "module_title": module.get("title"),
                }
            )
    return lessons


def get_lesson(lesson_id: str, curriculum: dict[str, Any] | None = None) -> dict[str, Any] | None:
    for lesson in iter_lessons(curriculum):
        if lesson.get("id") == lesson_id:
            return lesson
    return None


def lesson_count(curriculum: dict[str, Any] | None = None) -> int:
    return len(iter_lessons(curriculum))
