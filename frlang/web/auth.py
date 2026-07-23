from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ELEVES_PATH = PROJECT_ROOT / "data" / "eleves.json"


@dataclass(frozen=True)
class Eleve:
    username: str
    password: str
    display_name: str
    role: str = "eleve"


def eleves_path() -> Path:
    override = os.environ.get("FRLANG_ELEVES_PATH")
    if override:
        return Path(override)
    return DEFAULT_ELEVES_PATH


def load_eleves(path: Path | None = None) -> list[Eleve]:
    file_path = path or eleves_path()
    if not file_path.is_file():
        return []
    raw = json.loads(file_path.read_text(encoding="utf-8"))
    entries = raw.get("eleves", raw) if isinstance(raw, dict) else raw
    if not isinstance(entries, list):
        raise ValueError("eleves.json: attendu une liste d'élèves")

    eleves: list[Eleve] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        username = str(entry.get("username", "")).strip()
        password = str(entry.get("password", ""))
        display_name = str(entry.get("display_name") or username).strip()
        role = str(entry.get("role") or "eleve").strip().casefold()
        if role not in {"eleve", "admin"}:
            role = "eleve"
        if not username:
            continue
        eleves.append(
            Eleve(
                username=username,
                password=password,
                display_name=display_name,
                role=role,
            )
        )
    return eleves


def authenticate(username: str, password: str, path: Path | None = None) -> Eleve | None:
    needle = username.strip().casefold()
    if not needle:
        return None
    for eleve in load_eleves(path):
        if eleve.username.casefold() == needle and eleve.password == password:
            return eleve
    return None


def public_eleves(path: Path | None = None) -> list[dict[str, str]]:
    """Liste sans mots de passe — pour le tableau admin."""
    return [
        {
            "username": eleve.username,
            "display_name": eleve.display_name,
            "role": eleve.role,
        }
        for eleve in load_eleves(path)
        if eleve.role == "eleve"
    ]
