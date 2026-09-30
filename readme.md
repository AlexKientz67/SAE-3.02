# Carrefour et véhicules

Prérequis : Python et PyQt6 (`python3 -m pip install PyQt6`).
Depuis la racine du projet, lancer chaque programme dans un terminal séparé, dans cet ordre :

```sh
python3 src/server.py
```

```sh
python3 src/carrefour.py
```

Cliquer sur **Générer une voiture** dans le carrefour : chaque clic crée un véhicule
dans son propre thread, avec sa propre connexion socket au serveur.
Les véhicules générés s'arrêtent à la fermeture du carrefour.
La direction de chaque voiture générée est choisie au hasard.

Il reste possible de lancer un véhicule séparément avec `python3 src/car.py`.
Chaque véhicule calcule sa position et envoie `x,y,direction\n` au serveur TCP sur
`127.0.0.1:5500` avec la bibliothèque Python `socket`.
Le carrefour s'abonne au serveur en envoyant `carrefour\n` et reçoit les positions
avec un identifiant par véhicule (`position,id,x,y,direction\n`).
Il affiche un dessin distinct par véhicule et le retire à sa déconnexion.
Le carrefour envoie aussi `feux,vertical,horizontal\n` au serveur.
Le serveur gère seul les feux et les distances ; les véhicules proposent leur déplacement. Au rouge et à l’orange, ils attendent avant l’intersection ; une voiture déjà
engagée poursuit sa route. Sans carrefour, les feux
restent rouges. Les voitures horizontales sont dessinées en 40 × 20 pixels.

Le serveur valide chaque position et répond `accord,x,y\n`.
Il garde au moins 10 pixels entre les voitures, espace les créations et laisse
finir les voitures engagées avant de faire entrer l’autre axe. Au rouge et à l’orange, le bord
avant des voitures s’arrête 10 pixels avant le feu. Arrêter les programmes en terminal avec
`Ctrl+C`. Si le serveur est redémarré, relancer le carrefour et les véhicules.
