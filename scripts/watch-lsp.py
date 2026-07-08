#!/usr/bin/env python3
"""Relance frlang-lsp-ws quand le code Python FrLang change."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WATCH_DIRS = [ROOT / "frlang"]


def main() -> int:
    try:
        from watchfiles import watch
    except ImportError:
        print(
            "watchfiles manquant — lance : pip install -e '.[web,lsp]'",
            file=sys.stderr,
        )
        return 1

    lsp_bin = ROOT / ".venv" / "bin" / "frlang-lsp-ws"
    if not lsp_bin.is_file():
        lsp_bin = Path(
            subprocess.check_output(["which", "frlang-lsp-ws"], text=True).strip()
        )

    host = "127.0.0.1"
    port = "8765"
    process: subprocess.Popen[bytes] | None = None

    def start() -> subprocess.Popen[bytes]:
        print(f"[lsp] démarrage sur ws://{host}:{port}", flush=True)
        return subprocess.Popen(
            [str(lsp_bin), "--host", host, "--port", port],
            cwd=ROOT,
        )

    def stop() -> None:
        nonlocal process
        if process is None:
            return
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
        print("[lsp] arrêté", flush=True)
        process = None

    process = start()
    try:
        for _changes in watch(*WATCH_DIRS, debounce=300, step=200):
            stop()
            time.sleep(0.2)
            process = start()
    except KeyboardInterrupt:
        pass
    finally:
        stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
