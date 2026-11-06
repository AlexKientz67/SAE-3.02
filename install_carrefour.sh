
#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
VENV_DIR="$SCRIPT_DIR/venv"

# Vérification root
if [ "$EUID" -ne 0 ]; then
    echo "Lance le script avec sudo."
    exit 1
fi

# Vérification du fichier requirements
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "Fichier introuvable : $REQUIREMENTS_FILE"
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
    python3-venv

echo "=== Création de l'environnement virtuel ==="
python3 -m venv "$VENV_DIR"

echo "=== Installation des dépendances Python ==="
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$REQUIREMENTS_FILE"

echo ""
echo "================================"
echo "       INSTALLATION OK"
echo "================================"
echo "Venv : $VENV_DIR"
echo ""
echo "Pour lancer le projet côté carrefour :"
echo "source venv/bin/activate"
echo "python src/carrefour.py"
echo "================================"