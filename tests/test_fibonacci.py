from pathlib import Path

from frlang.interpreter import Interpreter


def test_fib_naive() -> None:
    interpreter = Interpreter(
        """
        definir fonction fib(nombre n) {
            si n <= 1 { retourne n; }
            retourne fib(n - 1) + fib(n - 2);
        } retourne nombre
        afficher fib(10);
        """
    )
    interpreter.run()
    assert interpreter.output == ["55"]


def test_fib_cache() -> None:
    interpreter = Interpreter(
        """
        soit Carnet memo = nouveau Carnet();
        definir fonction fib_cache(nombre n) {
            si memo.contient(n) { retourne memo.element(n); }
            si n <= 1 {
                memo.etiqueter(n, n);
                retourne n;
            }
            soit nombre r = fib_cache(n - 1) + fib_cache(n - 2);
            memo.etiqueter(n, r);
            retourne r;
        } retourne nombre
        afficher fib_cache(10);
        afficher fib_cache(35);
        """
    )
    interpreter.run()
    assert interpreter.output == ["55", "9227465"]


def test_fibonacci_program() -> None:
    source = Path("probleme/fibonacci").read_text(encoding="utf-8")
    interpreter = Interpreter(source)
    interpreter.run()
    assert interpreter.output == ["55", "55", "6765", "6765", "9227465"]
