# Projet Carrefour - Priorité aux véhicules d'urgence

Projet de maquette en Python + PySide6 + sockets TCP + QThread.

## Architecture

- `server.py` : serveur central + interface de supervision + dessin du carrefour.
- `carrefour.py` : client représentant le contrôleur du carrefour.
- `ambulance.py` : client représentant une ambulance.
- `protocol.py` : protocole JSON commun aux programmes.

Architecture :

    Ambulance ──TCP──> Serveur <──TCP── Carrefour
                         │
                         └── Interface Qt

## Installation

```bash
python -m pip install PySide6
```

## Lancement

Ouvrir 3 terminaux.

Terminal 1 :
```bash
python server.py
```

Terminal 2 :
```bash
python carrefour.py
```

Terminal 3 :
```bash
python ambulance.py
```

Dans l'ambulance, choisir une direction puis cliquer sur « DEMANDER PRIORITÉ ».

Le serveur transmet alors une commande au carrefour. Le carrefour passe en mode priorité, attend quelques secondes, puis revient au cycle normal.

## Port

Le serveur écoute par défaut sur `127.0.0.1:5000`.

Pour utiliser plusieurs ordinateurs sur le réseau local, remplacer `HOST = "127.0.0.1"` par l'adresse IP du serveur et renseigner cette adresse dans les clients.
