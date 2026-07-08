import pytest

from frlang.errors import ParseError
from frlang.interpreter import Interpreter


def run(source: str) -> tuple[object | None, list[str]]:
    interpreter = Interpreter(source)
    return interpreter.run(), interpreter.output


def test_rangee_zero_based_element() -> None:
    _, output = run(
        """
        soit Rangee notes = nouveau Rangee(10, 20, 30);
        afficher notes.element(0);
        afficher notes.element(2);
        """
    )
    assert output == ["10", "30"]


def test_rangee_constructor_and_methods() -> None:
    source = """
    soit Rangee notes = nouveau Rangee(10, 20);
    notes.ajouter(30);
    afficher notes.taille();
    afficher notes.premier();
    """
    _, output = run(source.strip())
    assert output == ["3", "10"]


def test_sac_no_duplicates() -> None:
    source = """
    soit Sac fruits = nouveau Sac("pomme");
    fruits.ajouter("pomme");
    fruits.ajouter("banane");
    afficher fruits.taille();
    """
    _, output = run(source.strip())
    assert output == ["2"]


def test_sac_premier_error() -> None:
    with pytest.raises(ParseError, match="ne peut pas utiliser « premier »"):
        run("soit Sac s = nouveau Sac(); s.premier();")


def test_carnet_constructor_and_element() -> None:
    source = """
    soit Carnet eleve = nouveau Carnet(nom: "Léa", score: 10);
    eleve.etiqueter("bonus", 5);
    afficher eleve.element("score");
    """
    _, output = run(source.strip())
    assert output == ["10"]


def test_carnet_missing_key() -> None:
    with pytest.raises(ParseError, match="n'est pas dans le carnet"):
        run('soit Carnet c = nouveau Carnet(); c.element("absent");')


def test_rangee_index_out_of_bounds() -> None:
    with pytest.raises(ParseError, match="n'existe pas"):
        run("soit Rangee r = nouveau Rangee(1); r.element(5);")


def test_tas_depiler_empty() -> None:
    with pytest.raises(ParseError, match="est vide"):
        run("soit Tas t = nouveau Tas(); t.depiler();")


def test_file_fifo() -> None:
    source = """
    soit File attente = nouveau File();
    attente.enfiler(1);
    attente.enfiler(2);
    afficher attente.defiler();
    afficher attente.defiler();
    """
    _, output = run(source.strip())
    assert output == ["1", "2"]


def test_unknown_object_method() -> None:
    with pytest.raises(ParseError, match="ne connaît pas"):
        run("soit Rangee r = nouveau Rangee(); r.trier();")


def test_wrong_method_argument_count() -> None:
    with pytest.raises(ParseError, match="a besoin d'une valeur"):
        run("soit Rangee r = nouveau Rangee(); r.ajouter();")


def test_object_in_numeric_expression() -> None:
    with pytest.raises(ParseError, match="ne peut pas faire de calcul avec un Rangee"):
        run("soit Rangee r = nouveau Rangee(1); r + 1;")


def test_type_mismatch_declaration() -> None:
    with pytest.raises(ParseError, match="il faut un Rangee"):
        run("soit Rangee r = nouveau Sac();")


def test_afficher_object() -> None:
    _, output = run('soit Sac fruits = nouveau Sac("pomme", "banane"); afficher fruits;')
    assert output == ['Sac [pomme, banane]']


def test_deprecated_bracket_literal() -> None:
    with pytest.raises(ParseError, match="ne crée plus"):
        run("soit Rangee r = Rangee [1];")


def test_use_nouveau_for_class() -> None:
    with pytest.raises(ParseError, match="nouveau Personne"):
        Interpreter(
            'definir classe Personne { soit Mots nom = "Léa"; } soit Personne p = Personne();'
        ).run()
