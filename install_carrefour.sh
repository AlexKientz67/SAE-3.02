
#!/bin/bash

set -e

# Configuration
DB_NAME="carrefour"
DB_USER="carrefour"
DB_PASSWORD="carrefour"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SQL_FILE="$SCRIPT_DIR/src/urgences.sql"

# Vérification root
if [ "$EUID" -ne 0 ]; then
    echo "Lance le script avec sudo."
    exit 1
fi

# Vérification du fichier SQL
if [ ! -f "$SQL_FILE" ]; then
    echo "Fichier introuvable : $SQL_FILE"
    exit 1
fi

echo "=== Mise à jour ==="
apt-get update
apt-get upgrade -y

echo "=== Installation des paquets ==="
apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    mariadb-server \
    mariadb-client \
    openssl

echo "=== Installation des dépendances Python ==="
python3 -m pip install --break-system-packages \
    mysql-connector-python

echo "=== Démarrage de MariaDB ==="
systemctl enable --now mariadb

echo "=== Création de la base et de l'utilisateur ==="

mariadb <<EOF
CREATE DATABASE IF NOT EXISTS \`$DB_NAME\`
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS '$DB_USER'@'localhost'
IDENTIFIED BY '$DB_PASSWORD';

CREATE USER IF NOT EXISTS '$DB_USER'@'%'
IDENTIFIED BY '$DB_PASSWORD';

ALTER USER '$DB_USER'@'localhost'
IDENTIFIED BY '$DB_PASSWORD';

ALTER USER '$DB_USER'@'%'
IDENTIFIED BY '$DB_PASSWORD';

GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_USER'@'localhost';
GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_USER'@'%';

FLUSH PRIVILEGES;
EOF

echo "=== Import du fichier SQL ==="
mariadb "$DB_NAME" < "$SQL_FILE"

echo ""
echo "================================"
echo "       INSTALLATION OK"
echo "================================"
echo "Database : $DB_NAME"
echo "Username : $DB_USER"
echo "Password : $DB_PASSWORD"
echo "SQL      : $SQL_FILE"
echo "================================"

