from pathlib import Path

import pytest

from frlang.errors import ParseError
from frlang.interpreter import Interpreter


def _run_with_module(main_source: str, module_name: str, module_source: str, tmp_path: Path) -> Interpreter:
    module_path = tmp_path / module_name
    module_path.write_text(module_source, encoding="utf-8")
    main_path = tmp_path / "principal"
    main_path.write_text(main_source, encoding="utf-8")
    interpreter = Interpreter.session()
    interpreter._source_path = main_path.resolve()
    interpreter.execute(main_source)
    return interpreter


def test_from_import_function(tmp_path: Path) -> None:
    interpreter = _run_with_module(
        """
        from utilitaires import doubler;
        afficher doubler(4);
        """,
        "utilitaires",
        """
        definir fonction doubler(nombre n) {
            retourne n * 2;
        } retourne nombre
        """,
        tmp_path,
    )
    assert interpreter.output == ["8"]


def test_import_module_namespace_call(tmp_path: Path) -> None:
    interpreter = _run_with_module(
        """
        import utilitaires;
        afficher utilitaires.saluer();
        """,
        "utilitaires",
        """
        definir fonction saluer() {
            retourne nouveau Mots("bonjour");
        } retourne Mots
        """,
        tmp_path,
    )
    assert interpreter.output == ["bonjour"]


def test_import_as_alias(tmp_path: Path) -> None:
    interpreter = _run_with_module(
        """
        import utilitaires as u;
        afficher u.trois();
        """,
        "utilitaires",
        """
        definir fonction trois() {
            retourne 3;
        } retourne nombre
        """,
        tmp_path,
    )
    assert interpreter.output == ["3"]


def test_from_import_variable(tmp_path: Path) -> None:
    interpreter = _run_with_module(
        """
        from config import limite;
        afficher limite;
        """,
        "config",
        """
        soit nombre limite = 42;
        """,
        tmp_path,
    )
    assert interpreter.output == ["42"]


def test_from_import_multiple_names(tmp_path: Path) -> None:
    interpreter = _run_with_module(
        """
        from utilitaires import doubler, tripler;
        afficher doubler(2);
        afficher tripler(2);
        """,
        "utilitaires",
        """
        definir fonction doubler(nombre n) { retourne n * 2; } retourne nombre
        definir fonction tripler(nombre n) { retourne n * 3; } retourne nombre
        """,
        tmp_path,
    )
    assert interpreter.output == ["4", "6"]


def test_from_import_alias(tmp_path: Path) -> None:
    interpreter = _run_with_module(
        """
        from utilitaires import doubler as fois2;
        afficher fois2(5);
        """,
        "utilitaires",
        """
        definir fonction doubler(nombre n) { retourne n * 2; } retourne nombre
        """,
        tmp_path,
    )
    assert interpreter.output == ["10"]


def test_import_runs_module_side_effects(tmp_path: Path) -> None:
    interpreter = _run_with_module(
        """
        import utilitaires;
        """,
        "utilitaires",
        """
        afficher "charge";
        """,
        tmp_path,
    )
    assert interpreter.output == ["charge"]


def test_import_cached_second_time(tmp_path: Path) -> None:
    interpreter = _run_with_module(
        """
        import utilitaires;
        import utilitaires;
        """,
        "utilitaires",
        """
        afficher "une fois";
        """,
        tmp_path,
    )
    assert interpreter.output == ["une fois"]


def test_import_file_not_found(tmp_path: Path) -> None:
    main_path = tmp_path / "principal"
    main_path.write_text("import absent;", encoding="utf-8")
    interpreter = Interpreter.session()
    interpreter._source_path = main_path.resolve()
    with pytest.raises(ParseError, match="Je ne trouve pas le fichier"):
        interpreter.execute("import absent;")


def test_from_import_name_not_found(tmp_path: Path) -> None:
    with pytest.raises(ParseError, match="n'existe pas"):
        _run_with_module(
            "from utilitaires import inconnu;",
            "utilitaires",
            "soit nombre x = 1;",
            tmp_path,
        )


def test_circular_import(tmp_path: Path) -> None:
    (tmp_path / "a").write_text("import b;", encoding="utf-8")
    (tmp_path / "b").write_text("import a;", encoding="utf-8")
    main_path = tmp_path / "principal"
    main_path.write_text("import a;", encoding="utf-8")
    interpreter = Interpreter.session()
    interpreter._source_path = main_path.resolve()
    with pytest.raises(ParseError, match="Import circulaire"):
        interpreter.execute("import a;")


def test_import_error_in_module(tmp_path: Path) -> None:
    with pytest.raises(ParseError, match="fichier importé"):
        _run_with_module(
            "import utilitaires;",
            "utilitaires",
            "soit nombre x = ;",
            tmp_path,
        )


def test_import_module_attribute_not_found(tmp_path: Path) -> None:
    with pytest.raises(ParseError, match="n'existe pas"):
        _run_with_module(
            """
            import utilitaires;
            afficher utilitaires.inconnu;
            """,
            "utilitaires",
            "soit nombre x = 1;",
            tmp_path,
        )


def test_from_import_class(tmp_path: Path) -> None:
    interpreter = _run_with_module(
        """
        from formes import Point;
        soit Point p = nouveau Point(1, 2);
        afficher p;
        """,
        "formes",
        """
        definir classe Point {
            soit nombre x = 0;
            soit nombre y = 0;
            constructeur(nombre un_x, nombre un_y) {
                x = un_x;
                y = un_y;
            }
        }
        """,
        tmp_path,
    )
    assert interpreter.output == ["Point { x=1, y=2 }"]


def test_import_text_path(tmp_path: Path) -> None:
    module_path = tmp_path / "mon_module"
    module_path.write_text(
        """
        definir fonction saluer() { retourne nouveau Mots("ok"); } retourne Mots
        """,
        encoding="utf-8",
    )
    main_path = tmp_path / "principal"
    main_path.write_text(
        """
        from "mon_module" import saluer;
        afficher saluer();
        """,
        encoding="utf-8",
    )
    interpreter = Interpreter.session()
    interpreter._source_path = main_path.resolve()
    interpreter.execute(main_path.read_text(encoding="utf-8"))
    assert interpreter.output == ["ok"]
