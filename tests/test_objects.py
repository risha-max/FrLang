import pytest

from sac.errors import ParseError
from sac.interpreter import Interpreter


def run(source: str) -> tuple[object | None, list[str]]:
    interpreter = Interpreter(source)
    return interpreter.run(), interpreter.output


def test_rangee_literal_and_methods() -> None:
    source = """
    soit rangée notes = rangée [10, 20];
    notes.ajouter(30);
    afficher notes.taille();
    afficher notes.premier();
    """
    _, output = run(source.strip())
    assert output == ["3", "10"]


def test_sac_no_duplicates() -> None:
    source = """
    soit sac fruits = sac ["pomme"];
    fruits.ajouter("pomme");
    fruits.ajouter("banane");
    afficher fruits.taille();
    """
    _, output = run(source.strip())
    assert output == ["2"]


def test_sac_premier_error() -> None:
    with pytest.raises(ParseError, match="ne peut pas utiliser « premier »"):
        run("soit sac s = sac []; s.premier();")


def test_carnet_etiqueter_and_element() -> None:
    source = """
    soit carnet eleve = carnet [nom: "Léa", score: 10];
    eleve.etiqueter("bonus", 5);
    afficher eleve.element("score");
    """
    _, output = run(source.strip())
    assert output == ["10"]


def test_carnet_missing_key() -> None:
    with pytest.raises(ParseError, match="n'est pas dans le carnet"):
        run('soit carnet c = carnet []; c.element("absent");')


def test_rangee_index_out_of_bounds() -> None:
    with pytest.raises(ParseError, match="n'existe pas"):
        run("soit rangée r = rangée [1]; r.element(5);")


def test_tas_depiler_empty() -> None:
    with pytest.raises(ParseError, match="est vide"):
        run("soit tas t = tas []; t.depiler();")


def test_file_fifo() -> None:
    source = """
    soit file attente = file [];
    attente.enfiler(1);
    attente.enfiler(2);
    afficher attente.defiler();
    afficher attente.defiler();
    """
    _, output = run(source.strip())
    assert output == ["1", "2"]


def test_unknown_object_method() -> None:
    with pytest.raises(ParseError, match="ne connaît pas"):
        run("soit rangée r = rangée []; r.trier();")


def test_wrong_method_argument_count() -> None:
    with pytest.raises(ParseError, match="a besoin d'une valeur"):
        run("soit rangée r = rangée []; r.ajouter();")


def test_object_in_numeric_expression() -> None:
    with pytest.raises(ParseError, match="ne peut pas faire de calcul avec un rangée"):
        run("soit rangée r = rangée [1]; r + 1;")


def test_type_mismatch_declaration() -> None:
    with pytest.raises(ParseError, match="il faut un rangée"):
        run("soit rangée r = 5;")


def test_afficher_object() -> None:
    _, output = run('soit sac fruits = sac ["pomme", "banane"]; afficher fruits;')
    assert output == ['sac [pomme, banane]']
