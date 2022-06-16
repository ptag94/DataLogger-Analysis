# DataLogger-Analysis
---
Application pour tracer et analyser les données fournis par les deux data loggers.

Lancer à l'aide de Python le fichier ***main.py***

## Pré-requis

Cette application a été codé avec :
  * Python version 3.10.2
  * Pyside6 version 6.2.3
  * pyqtgraph version 0.12.3
  * pandas version 1.4.1
  * numpy version 1.22.2


## Interface générale et utilisation

L'interface est composé d'un encadré graphique où seront tracé les différentes courbes, de 3 boutons (*Load*, *Save* et *Timed Data*) et d'un espace entre les boutons *Save* et *Timed Date* où seront affiché les différentes expériences chargées.

---

### Bouton *Load*

Ce bouton ouvre une première fenêtre qui demande à l'utilisateur d'ouvrir les deux fichiers *.csv* correspondant aux deux jeux de données des deux data loggers.

Après avoir ouvert les deux fichiers, le programme nous demande le nom de l'expérience chargée. Ce nom n'a pas d'inscidence sur les fichiers, il n'est là qu'à titre indicatif pour l'affichage (comme une *étiquette*). Il n'y a pas de restriction sur le nombre de caractère mais je conseille de ne pas trop dépasser 20 caractères au risque de voir le nom coupé.

On observera alors l'apparition de deux bouttons dans l'espace prévu à cet effet :
  * Un bouton comportant le nom de l'expérience choisie
  * Un bouton *supprimer* qui efface l'expérience de l'application

A noter que l'on peut *charger* et *supprimer* autant de fois que l'on veut sans devoir delancer l'application. Les différentes expériences seront donc chargées et rangées dans une liste dans l'espace entre le bouton *Save* et *Timed Data*.

---

### Bouton *Save*

Sauvegarde l'aperçu du graphique dans un fichier *.png* où l'utilisateur pourra spécifier son emplacement.

---

### Bouton *Timed Data*

Switch entre le temps absolu en seconde fourni par les data loggers et une échelle d'une journée basée sur les heures.

---

### Bouton *<Nom de l'expérience>*

Affiche une fenêtre comportant deux tableaux, un pour chaque data loggers.

Dans chacun de ces tableaux on pourra retrouver:
  * Le nom du channel du data logger
  * Un bouton *Couleur*
  * Un bouton *Analyse*
  * Une case à cocher si l'on veut afficher sur le graphique la courbe correspondante au channel

#### Bouton *Couleur*

Initialement, une couleur aléatoire est affectée pour chaque courbe. Si l'utilisateur souhaite changer la couleur, il peut cliquer sur ce bouton et une fenêtre s'affichera pour choisir une nouvelle couleur à affectée.

#### Bouton *Analyse*

Analyse l'effet d'une chaufferette en enlevant une référence (typiquement cycle jour/nuit)

Utilisation:
  * Cliquer sur le bouton *Analyse* sur la ligne du channel voulu
  * Sélectionner l'expérience référente préalablement importée

Protocole :
  * Réalise un *fit* de la courbe référente
  * Soustrait ce *fit* à la courbe à analyser
  * Soustrait la valeur en 0 pour que la courbe affichée commence en 0

---

### Graphique

A l'aide de la souris, on peut décaler le graphique ou zoomer pour plus de clarté. On peut également seulement changer l'échelle d'un axe en zoomer sur celui ci.

La légende peut également être bougée.

Si l'on souhaite revenir à la vue initiale, un petit bouton *A* apparaît en bas à gauche de l'écran.

A noter que lorsqu'on appuie sur le bouton *Save*, on sauvegarde la vue actuelle du graphique (même si elle a changé) et non pas celle par défaut.
