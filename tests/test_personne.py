from frlang.interpreter import Interpreter


def test_personne_default_constructor() -> None:
    interpreter = Interpreter(
        """
        definir classe Personne {
            soit nombre age;
            soit Mots prenom;
            soit Mots nom_famille;
            constructeur() { }
            definir fonction afficher() {
                afficher prenom;
                afficher " ";
                afficher nom_famille;
                afficher ", ";
                afficher age;
            }
        }
        soit Personne p = nouveau Personne();
        p.afficher();
        """
    )
    interpreter.run()
    assert interpreter.output == ["", " ", "", ", ", "rien"]


def test_personne_equals_and_custom_afficher() -> None:
    interpreter = Interpreter(
        """
        definir classe Personne {
            soit nombre age;
            soit Mots prenom;
            soit Mots nom_famille;
            constructeur() { }
            constructeur(nombre un_age, Mots un_prenom, Mots un_nom) {
                age = un_age;
                prenom = un_prenom;
                nom_famille = un_nom;
            }
            definir fonction afficher() {
                afficher prenom;
                afficher " ";
                afficher nom_famille;
            }
            definir fonction equals(Personne autre) {
                si age != autre.age { retourne faux; }
                si prenom.equals(autre.prenom) == faux { retourne faux; }
                si nom_famille.equals(autre.nom_famille) == faux { retourne faux; }
                retourne vrai;
            } retourne logique
        }
        soit Personne a = nouveau Personne(20, "Léa", "Martin");
        soit Personne b = nouveau Personne(20, "Léa", "Martin");
        afficher a.equals(b);
        """
    )
    interpreter.run()
    assert interpreter.output == ["vrai"]


def test_etudiant_heritage_et_meilleur() -> None:
    interpreter = Interpreter(
        """
        definir classe Personne {
            soit nombre age;
            soit Mots prenom;
            soit Mots nom_famille;
            constructeur(nombre un_age, Mots un_prenom, Mots un_nom) {
                age = un_age;
                prenom = un_prenom;
                nom_famille = un_nom;
            }
        }
        definir classe Etudiant herite de Personne {
            soit nombre note;
            constructeur(nombre un_age, Mots un_prenom, Mots un_nom, nombre une_note) {
                age = un_age;
                prenom = un_prenom;
                nom_famille = un_nom;
                note = une_note;
            }
            definir fonction meilleur(Etudiant autre) {
                si note > autre.note { retourne vrai; }
                retourne faux;
            } retourne logique
        }
        soit Etudiant a = nouveau Etudiant(18, "A", "X", 90);
        soit Etudiant b = nouveau Etudiant(18, "B", "Y", 75);
        afficher a.meilleur(b);
        afficher b.meilleur(a);
        """
    )
    interpreter.run()
    assert interpreter.output == ["vrai", "faux"]
