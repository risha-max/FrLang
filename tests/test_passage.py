from pathlib import Path

from frlang.interpreter import Interpreter


def test_passage_program() -> None:
    source = Path("probleme/passage").read_text(encoding="utf-8")
    interpreter = Interpreter(source)
    interpreter.run()
    assert interpreter.output == ["5", "15", "1", "2", "100", "150"]


def test_pass_by_value_custom_class() -> None:
    result = Interpreter(
        """
        definir classe Compte {
            soit nombre solde;
            constructeur(nombre montant) { solde = montant; }
            definir fonction crediter(nombre montant) { solde = solde + montant; }
            definir fonction lire() { retourne solde; } retourne nombre
        }
        definir fonction crediter_valeur(Compte c) { c.crediter(50); }
        soit Compte wallet = nouveau Compte(100);
        crediter_valeur(wallet);
        wallet.lire();
        """
    ).run()
    assert result == 100


def test_pass_by_pointer_custom_class() -> None:
    result = Interpreter(
        """
        definir classe Compte {
            soit nombre solde;
            constructeur(nombre montant) { solde = montant; }
            definir fonction crediter(nombre montant) { solde = solde + montant; }
            definir fonction lire() { retourne solde; } retourne nombre
        }
        definir fonction crediter_ref(pointeur Compte p) { valeur(p).crediter(50); }
        soit Compte wallet = nouveau Compte(100);
        crediter_ref(adresse(wallet));
        wallet.lire();
        """
    ).run()
    assert result == 150
