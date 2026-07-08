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

Pour l'autocomplétion et les diagnostics (serveur LSP) :

```bash
pip install -e ".[lsp]"
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

`Arbre` modélise une structure parent → enfants (comme un arbre généalogique).

```text
soit Arbre famille = nouveau Arbre("Aïeul");
soit Arbre pere = famille.ajouter_enfant("Père");
pere.ajouter_enfant("Alice");
afficher famille.valeur();
afficher famille.nombre_enfants();
afficher famille.taille();
afficher famille.enfant(1).valeur();
afficher famille.feuille();
```

`Graphe` relie des lieux par des chemins (réseau non orienté).

```text
soit Graphe carte = nouveau Graphe();
carte.ajouter_sommet("Maison");
carte.ajouter_sommet("École");
carte.lier("Maison", "École");
afficher carte.contient_sommet("Maison");
afficher carte.voisins("Maison").taille();
afficher carte.nombre_sommets();
afficher carte.nombre_aretes();
```

`Fichier` permet de lire et d'écrire sur le disque (comme un fichier Java).

```text
soit Fichier journal = nouveau Fichier("notes.txt");
journal.ecrire("Hello world");
journal.ecrire(42);
journal.fermer();

soit Fichier lecture = nouveau Fichier("notes.txt");
afficher lecture.lire_ligne(1);
afficher lecture.existe();
```

Méthodes : `ecrire`, `lire`, `lire_ligne`, `fermer`, `existe`, `chemin`, `taille`. Voir `probleme/fichier_personne`.

Toutes les classes créées héritent de `Original`, qui fournit `afficher()` et `equals(...)`.

## Serveur LSP

FrLang expose un serveur [Language Server Protocol](https://microsoft.github.io/language-server-protocol/) réutilisable partout :

```bash
frlang-lsp                              # stdio : VS Code, Cursor (futur)
frlang-lsp --ws --host 127.0.0.1 --port 8765   # WebSocket : site web
frlang-lsp --tcp --port 8765            # TCP
```

Le serveur fournit :

- autocomplétion des mots-clés, sortes, builtins, variables, fonctions et classes
- méthodes après `.` (`mot.inverser`, `notes.ajouter`, ...)
- diagnostics en direct avec les messages d'erreur FrLang

Code dans `frlang/lsp/`. Pour le site web, connecter **Monaco Editor** au serveur via WebSocket (`monaco-languageclient`). Voir issue #3.

## Vérification

```bash
bash scripts/agent-check.sh
```

## Licence

À définir.
