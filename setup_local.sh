#!/usr/bin/env bash
# ===========================================================================
# setup_local.sh — instala el proyecto cspbx3-min en tu Mac
# ---------------------------------------------------------------------------
# Lo que hace:
#   1. Clona el repo HarryBsaltos/cspbx3-min en ~/Desktop/cspbx3-min
#   2. Crea un entorno virtual de Python e instala las dependencias
#   3. Te pide pegar tu Personal Access Token y escribe .env localmente
#   4. Hace una prueba: corre el script en modo --source github
#
# Uso:
#   bash setup_local.sh
# ===========================================================================
set -euo pipefail

PROJECT_DIR="$HOME/Desktop/cspbx3-min"
REPO_URL="https://github.com/HarryBsaltos/cspbx3-min.git"

echo "=========================================="
echo "  Instalacion cspbx3-min"
echo "=========================================="
echo

# 1. Clonar (o actualizar) el repo
if [ -d "$PROJECT_DIR/.git" ]; then
    echo "[1/4] El repo ya esta clonado en $PROJECT_DIR — actualizando..."
    git -C "$PROJECT_DIR" pull --rebase --autostash
else
    echo "[1/4] Clonando $REPO_URL en $PROJECT_DIR ..."
    git clone "$REPO_URL" "$PROJECT_DIR"
fi
cd "$PROJECT_DIR"

# 2. Entorno virtual + dependencias
echo
echo "[2/4] Creando entorno virtual e instalando dependencias..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
# shellcheck source=/dev/null
source .venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# 3. Configurar .env si no existe
echo
if [ -f ".env" ]; then
    echo "[3/4] Ya existe un .env — no lo toco."
else
    echo "[3/4] Configurando .env"
    echo "      Pega tu Personal Access Token (no se va a mostrar en pantalla)."
    echo "      Para crear uno nuevo: https://github.com/settings/personal-access-tokens/new"
    echo
    read -rsp "      GITHUB_TOKEN: " GH_TOKEN
    echo
    if [ -z "$GH_TOKEN" ]; then
        echo "ERROR: no se pego ningun token. Abortando."
        exit 1
    fi
    cat > .env <<EOF
GITHUB_TOKEN=$GH_TOKEN
GITHUB_OWNER=HarryBsaltos
GITHUB_REPO=cspbx3-min
GITHUB_BRANCH=main
GITHUB_INPUT_PATH=data/entrada/CsPbBr3_AA_AA.txt
EOF
    chmod 600 .env
    unset GH_TOKEN
    echo "      .env creado (permisos 600)."
fi

# 4. Smoke test
echo
echo "[4/4] Probando el flujo completo (--source github --upload)..."
python3 cspbx3_min.py --source github --upload --no-show

echo
echo "=========================================="
echo "  Listo. El proyecto esta en:"
echo "  $PROJECT_DIR"
echo "=========================================="
