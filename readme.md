# SAE 3.02 – Groupe ProxmoxVE
**Réalisé par Alexandre KIENTZ et Illia SITOVSKYI**

## Installation

```bash
su -
apt install sudo
sudo usermod -aG sudo toto
exit
```
Il faut peut-être redémarré la machine si le usermod ne s'applique pas.

**1. Installation de Git :**

```bash
sudo apt update
sudo apt install git
```

**2. Clonage du dépôt Git :**

```bash
git clone https://github.com/AlexKientz67/SAE-3.02.git
cd SAE-3.02
```

## Installation automatique

### Sur votre machine serveur

Lancer le script d'installation côté serveur :

```bash
chmod +x ./install_server.sh
sudo ./install_server.sh
```

### Sur votre machine cliente (carrefour)

Lancer le script d'installation côté carrefour :

```bash
chmod +x ./install_carrefour.sh
sudo ./install_carrefour.sh
```

Vous pouvez maintenant vous rendre à la fin du README, dans la section « Configuration ».

---

## Installation manuelle

L'installation manuelle consiste à installer les dépendances nécessaires, à configurer l'environnement Python et, dans le cas du serveur, à créer et initialiser la base de données MariaDB.

### Sur votre machine serveur

**1. Mise à jour du système :**

```bash
sudo apt update
sudo apt upgrade -y
```

**2. Installation des paquets nécessaires :**

```bash
sudo apt install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    mariadb-server \
    mariadb-client \
    openssl
```

**3. Création de l'environnement virtuel Python :**

Depuis la racine du projet, exécuter la commande suivante :

```bash
python3 -m venv venv
```

**4. Installation des dépendances Python :**

Activer l'environnement virtuel, mettre à jour `pip`, puis installer les dépendances du projet :

```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**5. Démarrage de MariaDB :**

Activer et démarrer le service MariaDB :

```bash
sudo systemctl enable --now mariadb
```

**6. Création de la base de données et de l'utilisateur :**

Ouvrir une console MariaDB :

```bash
sudo mariadb
```

Exécuter les commandes SQL suivantes :

```sql
CREATE DATABASE carrefour
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

CREATE USER 'carrefour'@'localhost'
IDENTIFIED BY 'carrefour';

CREATE USER 'carrefour'@'%'
IDENTIFIED BY 'carrefour';

GRANT ALL PRIVILEGES ON carrefour.* TO 'carrefour'@'localhost';
GRANT ALL PRIVILEGES ON carrefour.* TO 'carrefour'@'%';

FLUSH PRIVILEGES;

EXIT;
```

**7. Importation de la structure et des données SQL :**

Depuis la racine du projet, importer le fichier SQL :

```bash
sudo mariadb carrefour < src/urgences.sql
```

**8. Lancement du serveur :**

Activer l'environnement virtuel, puis démarrer le serveur :

```bash
source venv/bin/activate
python src/server.py
```

### Sur votre machine cliente (carrefour)

**1. Mise à jour du système :**

```bash
sudo apt update
sudo apt upgrade -y
```

**2. Installation des paquets nécessaires :**

```bash
sudo apt install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv
```

**3. Création de l'environnement virtuel Python :**

Depuis la racine du projet :

```bash
python3 -m venv venv
```

**4. Installation des dépendances Python :**

Activer l'environnement virtuel, mettre à jour `pip`, puis installer les dépendances :

```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**5. Lancement du carrefour :**

```bash
source venv/bin/activate
python src/carrefour.py
```

---

## Configuration

Avant de procéder à la configuration, il est nécessaire de distinguer les deux machines (serveur et carrefour) et de relever leurs adresses IPv4 respectives.

### Configuration du carrefour

Sur la machine cliente, il faut modifier l'adresse IP du serveur dans les fichiers suivants :

- `client.py`
- `client_urgence.py`
- `carrefour.py`

Au début de ces fichiers, remplacer :

```python
HOST = "127.0.0.1"
```

Pour retrouver l'adresse IPv4 de votre serveur
```bash
ip -4 addr
```

Et remplacer l'adresse du serveur par l'adresse de votre serveur
```python
HOST = "<Adresse IPv4 de votre serveur>"
```

### Configuration du serveur

### Configuration de SQL
**Ne pas faire si installation automatique**

Il faut modifier la ligne `bind-adress` dans le fichier `50-server.cnf`, voici la procédure
```bash
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
```
Il faut remplacer
```bash
bind-address        = 127.0.0.1
```
par
```bash
bind-address        = 0.0.0.0
```
Puis redémarrer le service MySQL
```bash
sudo systemctl restart mysql
```

## Lancement de l'application

Pour lancer l'application il faut d'abord rentrer dans le venv python

### Serveur
```bash
source venv/bin/activate
python src/server.py
```

### Carrefour
```bash
source venv/bin/activate
python src/carrefour.py
```

**Il faut lancer impérativement le serveur avant le carrefour !**