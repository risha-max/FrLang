from __future__ import annotations

from typing import Any

from frlang.web.curriculum import load_curriculum


def is_lesson_completed(lessons_state: dict[str, Any], lesson_id: str) -> bool:
    entry = lessons_state.get(lesson_id) or {}
    return entry.get("status") == "completed"


def is_module_complete(
    module: dict[str, Any], lessons_state: dict[str, Any]
) -> bool:
    lessons = module.get("lessons") or []
    if not lessons:
        return True
    return all(is_lesson_completed(lessons_state, lesson["id"]) for lesson in lessons)


def is_module_unlocked(
    modules: list[dict[str, Any]], module_index: int, lessons_state: dict[str, Any]
) -> bool:
    if module_index <= 0:
        return True
    return is_module_complete(modules[module_index - 1], lessons_state)


def is_lesson_unlocked(lesson_id: str, lessons_state: dict[str, Any] | None = None) -> bool:
    curriculum = load_curriculum()
    modules = curriculum.get("modules") or []
    state = lessons_state or {}
    for module_index, module in enumerate(modules):
        lessons = module.get("lessons") or []
        for lesson_index, lesson in enumerate(lessons):
            if lesson.get("id") != lesson_id:
                continue
            if not is_module_unlocked(modules, module_index, state):
                return False
            # Dans un module ouvert : les leçons se débloquent dans l'ordre.
            for previous in lessons[:lesson_index]:
                if not is_lesson_completed(state, previous["id"]):
                    return False
            return True
    return False
