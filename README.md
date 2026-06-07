# cspbx3-min

Trabajo final del curso **Herramientas Computacionales para Científicos (HCC)**.

Programa en Python para post-procesar superficies de energía DFT 2D obtenidas
sobre una grilla de 21×21 ángulos (θ, φ) de rotación de los octaedros
[PbX₆] en perovskitas de cesio y plomo CsPbX₃ (X = Cl, Br, I).

El programa puede leer los datos **desde disco local o directamente desde
este repositorio en GitHub**, y opcionalmente subir las figuras y los
resultados a `data/salida/` del repo usando la API REST de GitHub.

## Estructura del repositorio

```
.
├── cspbx3_min.py          # Script principal (lee + procesa + opcionalmente sube)
├── github_sync.py         # Módulo de subida de archivos via GitHub API
├── build_report.py        # Genera el informe PDF a partir de las figuras
├── informe_HCC.pdf        # Informe final del curso (5 páginas A4)
├── requirements.txt       # Dependencias Python
├── .env.example           # Plantilla de variables de entorno
├── .gitignore             # Excluye .env, figs/, __pycache__, etc.
├── data/
│   ├── entrada/
│   │   └── CsPbBr3_AA_AA.txt   # Datos DFT de entrada
│   └── salida/                  # Figuras y resultados.json subidos por el script
└── README.md
```

## Requisitos

- Python ≥ 3.9
- Las dependencias de `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Configuración del Personal Access Token (PAT)

Para que el script lea y/o suba archivos al repo necesitás un PAT con permiso
mínimo. Estos pasos sirven para repos **públicos** (no hace falta PAT para
leer, pero sí para escribir) y para **privados** (PAT obligatorio).

1. Andá a **https://github.com/settings/personal-access-tokens/new**
2. **Token name**: `cspbx3-min upload PAT`
3. **Expiration**: 30 días (o lo que prefieras; al vencer generás otro).
4. **Repository access** → "Only select repositories" → elegí `cspbx3-min`.
5. **Permissions** → Repository permissions:
   - **Contents**: Read and write
   - Metadata: Read-only (se agrega solo, es obligatorio)
6. Click **Generate token**. Copialo (se ve **una sola vez**).

Para revocar un token después, andá a la misma pantalla, click en el
nombre del token y "Delete".

## Configuración local

```bash
git clone https://github.com/TU-USUARIO/cspbx3-min.git
cd cspbx3-min

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Editá .env con tu editor favorito y pegá el token + tu usuario.
```

El archivo `.env` queda fuera del repo gracias a `.gitignore`.

## Uso

### Lectura local (sin GitHub)

```bash
python3 cspbx3_min.py
```

Lee `CsPbBr3_AA_AA.txt` del directorio del script y guarda figuras en `./figs/`.

### Lectura desde GitHub

```bash
python3 cspbx3_min.py --source github
```

Descarga el archivo desde
`https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}/{INPUT_PATH}`.

### Lectura desde GitHub + subida automática de resultados

```bash
python3 cspbx3_min.py --source github --upload
```

Lee de GitHub, procesa, y publica:

- `data/salida/figs/01_surface_full.png`
- `data/salida/figs/02_surface_sub.png`
- `data/salida/figs/03_surface_spline.png`
- `data/salida/resultados.json`

Cada subida es un commit independiente. Si los archivos ya existen, se
actualizan (la API maneja el SHA automáticamente).

### Subir un archivo arbitrario

```bash
python3 github_sync.py /ruta/local/archivo.txt data/destino/archivo.txt
```

### Opciones del script principal

| Opción            | Descripción                                                |
|-------------------|------------------------------------------------------------|
| `--source`        | `local` (default) o `github`.                              |
| `-i, --input`     | Path local (solo si `--source local`).                     |
| `-o, --outdir`    | Directorio de salida para las figuras.                     |
| `--no-show`       | No abrir ventanas interactivas (servidores headless).      |
| `--upload`        | Subir figuras + resultados.json al repo configurado.       |

## Aplicar a otra composición (CsPbCl₃, CsPbI₃)

Subí el archivo de datos a `data/entrada/CsPbCl3_AA_AA.txt` (o I) y corré:

```bash
GITHUB_INPUT_PATH=data/entrada/CsPbCl3_AA_AA.txt \
  python3 cspbx3_min.py --source github -o figs_Cl
```

## Regenerar el informe PDF

```bash
python3 build_report.py
```

Genera `informe_HCC.pdf` (5 páginas A4) a partir de las figuras de `./figs/`.

## Seguridad

- **Nunca commitees `.env`**. Está en `.gitignore`.
- Si el token se filtra (por screenshot, copy-paste en chat, etc.) andá a
  https://github.com/settings/personal-access-tokens y borralo. Generá uno
  nuevo y actualizá `.env`.
- El token está scopeado a este único repo; si alguien lo obtiene, lo peor
  que puede hacer es vandalizar este repo, no tocar otros.

## Licencia

MIT — ver archivo `LICENSE` si está presente.

## Autor

Trabajo final del curso *Herramientas Computacionales para Científicos* (HCC).
