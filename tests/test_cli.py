import io
from pathlib import Path

import pytest

from frlang.cli import frlang_main, run_file
from frlang.interpreter import Interpreter
from frlang.repl import InteractiveConsole, source_needs_continuation


def test_session_execute_preserves_state() -> None:
    interpreter = Interpreter.session()
    interpreter.execute("soit nombre x = 5;")
    assert interpreter.execute("x;") == 5


def test_session_execute_afficher() -> None:
    interpreter = Interpreter.session()
    interpreter.execute('soit Mots nom = "Léa";')
    interpreter.execute("afficher nom;")
    assert interpreter.output == ["Léa"]


def test_run_file(tmp_path: Path) -> None:
    program = tmp_path / "demo.fr"
    program.write_text("soit nombre x = 3; x + 4;", encoding="utf-8")
    assert run_file(program) == 0


def test_run_file_missing(tmp_path: Path) -> None:
    assert run_file(tmp_path / "absent.fr") == 1


def test_frlang_main_help() -> None:
    assert frlang_main(["--help"]) == 0


def test_frlang_main_missing_file() -> None:
    assert frlang_main(["inexistant.fr"]) == 1


def test_frlang_main_too_many_args() -> None:
    assert frlang_main(["a.fr", "b.fr"]) == 1


def test_source_needs_continuation() -> None:
    assert source_needs_continuation('definir fonction f() {')
    assert source_needs_continuation('afficher("a')
    assert source_needs_continuation("2 + (3")
    assert not source_needs_continuation("2 + 3")
    assert not source_needs_continuation("definir fonction f() { retourne 1; } retourne nombre")


def test_interactive_console_multiline_function() -> None:
    input_stream = io.StringIO(
        "\n".join(
            [
                "definir fonction double(nombre n) {",
                "    retourne n * 2;",
                "} retourne nombre",
                "double(4);",
                "quitter",
                "",
            ]
        )
    )
    output_stream = io.StringIO()
    InteractiveConsole(input_stream=input_stream, output_stream=output_stream).run()
    assert "8" in output_stream.getvalue()


def test_interactive_console_error_continues() -> None:
    input_stream = io.StringIO("inconnu;\n2 + 2;\nquitter\n")
    output_stream = io.StringIO()
    InteractiveConsole(input_stream=input_stream, output_stream=output_stream).run()
    assert "4" in output_stream.getvalue()


def test_interactive_console_help() -> None:
    input_stream = io.StringIO("aide\nquitter\n")
    output_stream = io.StringIO()
    InteractiveConsole(input_stream=input_stream, output_stream=output_stream).run()
    assert "Commandes spéciales" in output_stream.getvalue()


def test_run_file_syntax_error(tmp_path: Path) -> None:
    program = tmp_path / "bad.fr"
    program.write_text("soit nombre x = ;", encoding="utf-8")
    assert run_file(program) == 1


def test_run_file_with_afficher(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    program = tmp_path / "afficher.fr"
    program.write_text('afficher "Salut";', encoding="utf-8")
    assert run_file(program) == 0
    assert capsys.readouterr().out.strip() == "Salut"
