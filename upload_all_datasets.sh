#!/usr/bin/env bash
# ===========================================================================
# upload_all_datasets.sh
# ---------------------------------------------------------------------------
# Sube TODOS los archivos .dat de ~/Desktop/Minimos rotaciones/datosderotaciones/
# a data/entrada/ del repo HarryBsaltos/cspbx3-min via la API de GitHub.
#
# Uso (desde Terminal):
#   bash upload_all_datasets.sh
#
# Te va a pedir el GITHUB_TOKEN. Despues sube todo y borra el .env temporal.
# ===========================================================================
set -euo pipefail

PROJECT_DIR="$HOME/Desktop/cspbx3-min"
SOURCE_DIR="$HOME/Desktop/Minimos rotaciones/datosderotaciones"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "ERROR: no encuentro el repo clonado en $PROJECT_DIR"
    echo "Antes corre: bash setup_local.sh"
    exit 1
fi
if [ ! -d "$SOURCE_DIR" ]; then
    echo "ERROR: no encuentro $SOURCE_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

# Activar venv y asegurar que las dependencias estan
# shellcheck source=/dev/null
source .venv/bin/activate
pip install --quiet -r requirements.txt

# Pedir token si .env no existe
if [ ! -f .env ]; then
    echo "Pega tu GITHUB_TOKEN (no se va a mostrar):"
    read -rsp "  GITHUB_TOKEN: " GH_TOKEN
    echo
    cat > .env <<EOF
GITHUB_TOKEN=$GH_TOKEN
GITHUB_OWNER=HarryBsaltos
GITHUB_REPO=cspbx3-min
GITHUB_BRANCH=main
EOF
    chmod 600 .env
    unset GH_TOKEN
fi

# Listar y subir cada .dat
echo
echo "Buscando archivos en $SOURCE_DIR ..."
count=0
for f in "$SOURCE_DIR"/*.dat "$SOURCE_DIR"/*.txt; do
    [ -f "$f" ] || continue
    name="$(basename "$f")"
    echo "  -> data/entrada/$name"
    python3 github_sync.py "$f" "data/entrada/$name" -m "data: add $name" || {
        echo "     FALLO al subir $name (sigo con los demas)"
    }
    count=$((count + 1))
done

echo
echo "=========================================="
echo "Subidos $count archivos a data/entrada/"
echo "Ver en: https://github.com/HarryBsaltos/cspbx3-min/tree/main/data/entrada"
echo "=========================================="
