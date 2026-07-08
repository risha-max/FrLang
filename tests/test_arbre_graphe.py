import pytest

from frlang.errors import ParseError
from frlang.interpreter import Interpreter


def run(source: str) -> tuple[object | None, list[str]]:
    interpreter = Interpreter(source)
    return interpreter.run(), interpreter.output


def test_arbre_genealogique() -> None:
    source = """
    soit Arbre famille = nouveau Arbre("Aïeul");
    soit Arbre pere = famille.ajouter_enfant("Père");
    pere.ajouter_enfant("Alice");
    pere.ajouter_enfant("Bob");
    afficher famille.taille();
    afficher famille.nombre_enfants();
    afficher famille.enfant(1).valeur();
    afficher famille.feuille();
    afficher pere.feuille();
    """
    _, output = run(source.strip())
    assert output == ["4", "1", "Père", "faux", "faux"]


def test_arbre_enfant_invalide() -> None:
    with pytest.raises(ParseError, match="n'existe pas"):
        run('soit Arbre a = nouveau Arbre("x"); a.enfant(1);')


def test_graphe_voisins() -> None:
    source = """
    soit Graphe carte = nouveau Graphe();
    carte.ajouter_sommet("Maison");
    carte.ajouter_sommet("École");
    carte.ajouter_sommet("Parc");
    carte.lier("Maison", "École");
    carte.lier("Maison", "Parc");
    afficher carte.nombre_sommets();
    afficher carte.nombre_aretes();
    afficher carte.voisins("Maison").contient("École");
    afficher carte.contient_sommet("Parc");
    """
    _, output = run(source.strip())
    assert output == ["3", "2", "vrai", "vrai"]


def test_graphe_sommet_inconnu() -> None:
    with pytest.raises(ParseError, match="n'est pas dans le graphe"):
        run("soit Graphe g = nouveau Graphe(); g.voisins(\"absent\");")


def test_graphe_constructeur_sans_argument() -> None:
    with pytest.raises(ParseError, match="ne prend pas 1 argument"):
        run("soit Graphe g = nouveau Graphe(1);")
