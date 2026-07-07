from frlang.interpreter import Interpreter


def test_palindrome_gagner() -> None:
    interpreter = Interpreter(
        """
        definir fonction verifier(Mots mot) {
            soit Mots inverse = mot.inverser();
            si mot.equals(inverse) {
                retourne nouveau Mots("GAGNER");
            }
            retourne nouveau Mots("");
        } retourne Mots
        afficher verifier(nouveau Mots("radar"));
        """
    )
    interpreter.run()
    assert interpreter.output == ["GAGNER"]


def test_palindrome_pas_gagner() -> None:
    interpreter = Interpreter(
        """
        definir fonction verifier(Mots mot) {
            soit Mots inverse = mot.inverser();
            si mot.equals(inverse) {
                retourne nouveau Mots("GAGNER");
            }
            retourne nouveau Mots("");
        } retourne Mots
        afficher verifier(nouveau Mots("bonjour"));
        """
    )
    interpreter.run()
    assert interpreter.output == [""]


def test_mots_inverser() -> None:
    from frlang.objects import Mots

    value = Interpreter('soit Mots mot = nouveau Mots("abc"); mot.inverser();').run()
    assert isinstance(value, Mots)
    assert value.text == "cba"
