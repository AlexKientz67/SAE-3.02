
#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Vérification root
if [ "$EUID" -ne 0 ]; then
    echo "Lance le script avec sudo."
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

echo "=== Installation des dépendances Python ==="
python3 -m pip install --break-system-packages \
    mysql-connector-python


echo ""
echo "================================"
echo "       INSTALLATION OK"
echo "================================"

