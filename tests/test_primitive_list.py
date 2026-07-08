import pytest

from frlang.errors import ParseError
from frlang.interpreter import Interpreter


def test_nombre_array_declaration() -> None:
    interpreter = Interpreter(
        """
        soit nombre[3] notes = [10, 20, 30];
        afficher notes;
        """
    )
    interpreter.run()
    assert interpreter.output == ["[10, 20, 30]"]


def test_logique_array_declaration() -> None:
    interpreter = Interpreter(
        """
        soit logique[3] flags = [vrai, faux, vrai];
        afficher flags;
        """
    )
    interpreter.run()
    assert interpreter.output == ["[vrai, faux, vrai]"]


def test_array_pads_with_rien() -> None:
    interpreter = Interpreter(
        """
        soit nombre[5] notes = [10, 20];
        afficher notes;
        """
    )
    interpreter.run()
    assert interpreter.output == ["[10, 20, rien, rien, rien]"]


def test_array_default_all_rien() -> None:
    interpreter = Interpreter(
        """
        soit nombre[3] notes;
        afficher notes;
        """
    )
    interpreter.run()
    assert interpreter.output == ["[rien, rien, rien]"]


def test_type_builtin_array() -> None:
    assert (
        Interpreter("soit nombre[2] notes = [1, 2]; type(notes);").run()
        == "nombre[2]"
    )


def test_array_pointer_first_element() -> None:
    result = Interpreter(
        """
        soit nombre[3] notes = [10, 20, 30];
        soit pointeur nombre p = adresse(notes);
        valeur(p);
        """
    ).run()
    assert result == 10


def test_array_pointer_offset_read() -> None:
    result = Interpreter(
        """
        soit nombre[3] notes = [10, 20, 30];
        soit pointeur nombre p = adresse(notes);
        valeur(p + 2);
        """
    ).run()
    assert result == 30


def test_array_pointer_offset_write() -> None:
    interpreter = Interpreter(
        """
        soit nombre[3] notes = [10, 20, 30];
        soit pointeur nombre p = adresse(notes);
        valeur(p + 1) = 99;
        afficher notes;
        """
    )
    interpreter.run()
    assert interpreter.output == ["[10, 99, 30]"]


def test_array_pass_by_value_copies() -> None:
    result = Interpreter(
        """
        definir fonction essayer(nombre[3] source) {
            valeur(adresse(source)) = 99;
        }
        soit nombre[3] notes = [1, 2, 3];
        essayer(notes);
        valeur(adresse(notes));
        """
    ).run()
    assert result == 1


def test_pointer_to_array_type_rejected() -> None:
    with pytest.raises(ParseError, match="ne peut pas viser directement un tableau"):
        Interpreter("soit pointeur nombre[3] p = adresse(notes);").run()


def test_object_array_type_rejected() -> None:
    with pytest.raises(ParseError, match="tableau primitif"):
        Interpreter('soit Mots[3] mots = ["a"];').run()


def test_array_size_required() -> None:
    with pytest.raises(ParseError, match="besoin d'une taille"):
        Interpreter("soit nombre[] notes = [10];").run()


def test_array_size_must_be_constant() -> None:
    with pytest.raises(ParseError, match="nombre connu à l'avance"):
        Interpreter(
            """
            soit nombre taille = 3;
            soit nombre[taille] notes = [1, 2, 3];
            """
        ).run()


def test_array_size_invalid() -> None:
    with pytest.raises(ParseError, match="entier positif"):
        Interpreter("soit nombre[0] notes = [];").run()


def test_array_too_many_elements() -> None:
    with pytest.raises(ParseError, match="ne peut en contenir que"):
        Interpreter("soit nombre[2] notes = [1, 2, 3];").run()


def test_array_index_out_of_bounds() -> None:
    with pytest.raises(ParseError, match="hors limites"):
        Interpreter(
            """
            soit nombre[2] notes = [10, 20];
            soit pointeur nombre p = adresse(notes);
            valeur(p + 5);
            """
        ).run()


def test_pointer_arithmetic_requires_array() -> None:
    with pytest.raises(ParseError, match="tableau primitif"):
        Interpreter(
            """
            soit nombre x = 1;
            soit pointeur nombre p = adresse(x);
            valeur(p + 1);
            """
        ).run()
