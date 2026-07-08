# FrLang

Langage de programmation en français pour apprendre la programmation (primaire / secondaire).

FrLang utilise des mots du quotidien (`soit`, `afficher`, `definir`, `Sac`, `Rangee`, `Carnet`...) plutôt que du jargon anglais.

## Exemple

```text
soit nombre x = 5;
afficher x;

definir fonction double(nombre n) {
    retourne n * 2;
} retourne nombre

double(3) + 4;
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Utilisation

```bash
python main.py "2 + 3 * 4"
python main.py
frlang probleme/ecole/main
```

Les fichiers FrLang n'ont pas besoin d'extension. Pour séparer un projet en plusieurs fichiers, utilise `import` :

```text
import utilitaires;
import utilitaires as u;
from utilitaires import doubler;
from "entites/etudiant" import Etudiant;
```

`import module;` donne accès à `module.fonction()` et `module.variable`. `from module import nom;` met directement `nom` dans le fichier courant.

## Objets Integrés

`Mots` représente du texte.

```text
soit Mots mot = "bonjour";
afficher mot.inverser();        // ruojnob
afficher mot.taille();          // 7
afficher mot.caractere(1);      // b
afficher mot.concatener(nouveau Mots("!"));   // bonjour!
afficher mot.equals(nouveau Mots("bonjour")); // vrai
```

`Rangee` est une liste ordonnée. Les positions commencent à 1.

```text
soit Rangee notes = nouveau Rangee(10, 20);
notes.ajouter(30);
afficher notes.element(1);
afficher notes.premier();
afficher notes.dernier();
afficher notes.taille();
afficher notes.contient(20);
notes.vider();
```

`Sac` garde une seule copie de chaque élément, sans ordre.

```text
soit Sac fruits = nouveau Sac();
fruits.ajouter("pomme");
fruits.retirer("pomme");
afficher fruits.contient("pomme");
afficher fruits.taille();
fruits.vider();
```

`Carnet` associe une étiquette à une valeur.

```text
soit Carnet ages = nouveau Carnet();
ages.etiqueter("Alice", 17);
afficher ages.element("Alice");
afficher ages.contient("Alice");
afficher ages.etiquettes();
afficher ages.taille();
ages.vider();
```

`Tas` fonctionne comme une pile : le dernier ajouté sort en premier.

```text
soit Tas pile = nouveau Tas();
pile.empiler(1);
pile.empiler(2);
afficher pile.depiler(); // 2
afficher pile.vide();
afficher pile.taille();
```

`File` fonctionne comme une file d'attente : le premier ajouté sort en premier.

```text
soit File attente = nouveau File();
attente.enfiler("A");
attente.enfiler("B");
afficher attente.defiler(); // A
afficher attente.vide();
afficher attente.taille();
```

Toutes les classes créées héritent de `Original`, qui fournit `afficher()` et `equals(...)`.

## Vérification

```bash
bash scripts/agent-check.sh
```

## Licence

À définir.
