from frlang.interpreter import Interpreter


def test_inverse_mot_manuel() -> None:
    interpreter = Interpreter(
        """
        definir fonction inverser_manuel(Mots mot) {
            soit Mots resultat = nouveau Mots("");
            pourchaque i dans range(mot.taille(), 0, -1) {
                resultat = resultat.concatener(mot.caractere(i));
            }
            retourne resultat;
        } retourne Mots
        afficher inverser_manuel(nouveau Mots("bonjour"));
        afficher inverser_manuel(nouveau Mots("radar"));
        """
    )
    interpreter.run()
    assert interpreter.output == ["ruojnob", "radar"]


def test_mots_caractere_taille_concatener() -> None:
    from frlang.objects import Mots

    value = Interpreter(
        """
        soit Mots mot = nouveau Mots("abc");
        mot.caractere(1).concatener(mot.caractere(2));
        """
    ).run()
    assert isinstance(value, Mots)
    assert value.text == "ab"
    assert Interpreter('nouveau Mots("abc").taille();').run() == 3
