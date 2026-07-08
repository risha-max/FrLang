from pathlib import Path

from frlang.interpreter import Interpreter


def run(source: str) -> list[str]:
    interpreter = Interpreter(source)
    interpreter.run()
    return interpreter.output


def run_file(name: str) -> list[str]:
    source = Path(f"probleme/{name}").read_text(encoding="utf-8")
    return run(source)


def test_two_sum_program() -> None:
    assert run_file("two_sum") == ["Rangee [0, 1]", "Rangee [1, 2]"]


def test_parentheses_program() -> None:
    assert run_file("parentheses") == ["vrai", "faux", "faux", "vrai"]


def test_fizzbuzz_program() -> None:
    output = run_file("fizzbuzz")
    assert output == [
        "Rangee [1, 2, Fizz, 4, Buzz, Fizz, 7, 8, Fizz, Buzz, 11, Fizz, 13, 14, FizzBuzz]"
    ]


def test_doublon_program() -> None:
    assert run_file("doublon") == ["vrai", "faux", "vrai"]


def test_recherche_binaire_program() -> None:
    assert run_file("recherche_binaire") == ["4", "-1"]


def test_max_sous_tableau_program() -> None:
    assert run_file("max_sous_tableau") == ["6", "1", "23"]


def test_chemins_graphe_program() -> None:
    assert run_file("chemins_graphe") == ["2", "1", "0"]
