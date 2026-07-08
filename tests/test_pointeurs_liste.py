from pathlib import Path

from frlang.interpreter import Interpreter


def test_afficher_pointer_with_offset() -> None:
    interpreter = Interpreter(
        """
        soit nombre[3] notes = [10, 20, 30];
        soit pointeur nombre p = adresse(notes);
        afficher p + 1;
        """
    )
    interpreter.run()
    assert len(interpreter.output) == 1
    assert interpreter.output[0].startswith("L'adresse hexadécimale de notes[1] est 0x")


def test_pointer_addresses_are_distinct_per_element() -> None:
    interpreter = Interpreter(
        """
        soit nombre[3] notes = [10, 20, 30];
        soit pointeur nombre p = adresse(notes);
        definir fonction montrer(pointeur nombre ptr) { afficher ptr; }
        montrer(p + 0);
        montrer(p + 1);
        montrer(p + 2);
        """
    )
    interpreter.run()
    assert len(interpreter.output) == 3
    assert interpreter.output[0].startswith("L'adresse hexadécimale de notes est ")
    assert interpreter.output[1].startswith("L'adresse hexadécimale de notes[1] est ")
    assert interpreter.output[2].startswith("L'adresse hexadécimale de notes[2] est ")
    addresses = [line.split(" est ")[1] for line in interpreter.output]
    assert len(set(addresses)) == 3


def test_pointeurs_liste_program() -> None:
    source = Path("probleme/pointeurs_liste").read_text(encoding="utf-8")
    interpreter = Interpreter(source)
    interpreter.run()
    assert interpreter.output[0] == "[10, 20, 5, 40, 50]"
    assert len(interpreter.output) == 6
    for line in interpreter.output[1:]:
        assert line.startswith("L'adresse hexadécimale de liste")
