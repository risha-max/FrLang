from pathlib import Path

import pytest

from frlang.errors import ParseError
from frlang.interpreter import Interpreter


def _run_in_dir(tmp_path: Path, source: str) -> Interpreter:
    main = tmp_path / "prog"
    main.write_text(source, encoding="utf-8")
    interpreter = Interpreter.session()
    interpreter._source_path = main.resolve()
    interpreter.execute(source)
    return interpreter


def test_fichier_ecrire_lire_ligne(tmp_path: Path) -> None:
    interpreter = _run_in_dir(
        tmp_path,
        """
        soit Fichier f = nouveau Fichier("out.txt");
        f.ecrire("Hello world");
        f.ecrire(42);
        f.fermer();
        soit Fichier lecture = nouveau Fichier("out.txt");
        afficher lecture.lire_ligne(1);
        afficher lecture.lire_ligne(2);
        """,
    )
    assert (tmp_path / "out.txt").read_text(encoding="utf-8") == "Hello world\n42\n"
    assert interpreter.output == ["Hello world", "42"]


def test_fichier_personne_program(tmp_path: Path) -> None:
    source = Path("probleme/fichier_personne").read_text(encoding="utf-8")
    interpreter = _run_in_dir(tmp_path, source)
    assert interpreter.output == ["Hello world", "Alice", " ", "Martin", ", ", "30", " ans"]


def test_fichier_existe(tmp_path: Path) -> None:
    interpreter = _run_in_dir(
        tmp_path,
        """
        soit Fichier f = nouveau Fichier("data.txt");
        f.ecrire("ok");
        afficher f.existe();
        """,
    )
    assert interpreter.output == ["vrai"]


def test_fichier_introuvable_sur_lire_ligne(tmp_path: Path) -> None:
    with pytest.raises(ParseError, match="ne trouve pas le fichier"):
        _run_in_dir(
            tmp_path,
            """
            soit Fichier f = nouveau Fichier("absent.txt");
            f.lire_ligne(1);
            """,
        )


def test_mots_en_nombre() -> None:
    assert Interpreter('nouveau Mots("42").en_nombre();').run() == 42
