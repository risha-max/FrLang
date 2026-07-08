from __future__ import annotations

import sys
from pathlib import Path

from frlang.errors import FrLangError, LexerError, ParseError
from frlang.interpreter import Interpreter
from frlang.repl import InteractiveConsole, print_execution_result


def run_file(path: Path) -> int:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as error:
        print(f"frlang: impossible d'ouvrir « {path} » : {error}", file=sys.stderr)
        return 1

    interpreter = Interpreter.session()
    interpreter._source_path = path.resolve()
    try:
        result = interpreter.execute(source)
    except (LexerError, ParseError, FrLangError) as error:
        print(error, file=sys.stderr)
        return 1

    print_execution_result(interpreter, result)
    return 0


def frlang_main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])

    if not args or args[0] in {"-h", "--help"}:
        print("Usage : frlang <fichier>", file=sys.stderr)
        print("Exécute un programme FrLang.", file=sys.stderr)
        return 0 if args and args[0] in {"-h", "--help"} else 1

    if len(args) > 1:
        print("frlang: un seul fichier attendu", file=sys.stderr)
        print("Usage : frlang <fichier>", file=sys.stderr)
        return 1

    path = Path(args[0])
    if not path.is_file():
        print(f"frlang: fichier introuvable : {path}", file=sys.stderr)
        return 1

    return run_file(path)


def ifrlang_main() -> int:
    try:
        import readline  # noqa: F401
    except ImportError:
        pass

    InteractiveConsole().run()
    return 0


def main() -> int:
    program = Path(sys.argv[0]).name
    if program == "ifrlang":
        return ifrlang_main()
    return frlang_main()
