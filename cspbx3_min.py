#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cspbx3_min.py
=============

Búsqueda del mínimo en una superficie de energía 2D obtenida por DFT
para perovskitas de haluro de cesio y plomo del tipo CsPbX3 (X = Cl, Br, I).

La superficie de energía se construye sobre una grilla discreta de 21x21
puntos correspondientes a dos ángulos de rotación (θ, φ) de los octaedros
[PbX6] dentro de la celda unitaria. Para cada par (θ_i, φ_j) el archivo de
entrada contiene la energía total E(θ_i, φ_j) (en unidades de la salida del
código DFT, típicamente eV o Ry).

Fuentes de datos soportadas
---------------------------
* `--source local`  : lee el archivo desde disco (default).
* `--source github` : descarga el archivo desde el repositorio configurado en
  `.env` (variables GITHUB_OWNER, GITHUB_REPO, GITHUB_BRANCH,
  GITHUB_INPUT_PATH), usando la URL raw.githubusercontent.com.
  Si el repo es privado se manda el header Authorization con el token.

Subida automática de resultados
-------------------------------
Con `--upload`, después de generar las figuras y resultados.json el script
los publica en `data/salida/...` del repo a través de la API contents de
GitHub (módulo `github_sync`).

Uso
---
    python3 cspbx3_min.py                              # local, no sube
    python3 cspbx3_min.py --source github              # lee desde GitHub
    python3 cspbx3_min.py --source github --upload     # lee y sube

Autor: Trabajo final del curso "Herramientas Computacionales para Científicos"
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
from pathlib import Path
from typing import Tuple

import numpy as np
import matplotlib

# Backend no interactivo si la variable de entorno DISPLAY no está
# disponible (típico al correr en un servidor o en CI). Debe configurarse
# ANTES de importar pyplot.
if not os.environ.get("DISPLAY") and sys.platform.startswith("linux"):
    matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401,E402
from scipy.interpolate import RectBivariateSpline  # noqa: E402

# Carga .env si python-dotenv está disponible (no es obligatorio).
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:  # pragma: no cover
    pass


# ---------------------------------------------------------------------------
# Constantes del problema
# ---------------------------------------------------------------------------

GRID_SIZE = 21
#: Tamaño (en puntos de la grilla) de la ventana 2D que se interpola
#: alrededor del mínimo discreto. Por defecto 5x5 centrada en el mínimo.
SUBREGION_SIZE = 5
REFINED_STEP = 0.1


def auto_subregion(
    energies: np.ndarray, size: int = SUBREGION_SIZE,
) -> tuple[slice, slice]:
    """Devuelve un slice 2D centrado en el mínimo discreto de ``energies``.

    Si el mínimo está cerca de un borde se desplaza la ventana hacia adentro
    para que siempre encierre ``size``×``size`` puntos válidos.
    """
    n = energies.shape[0]
    half = size // 2
    i, j = np.unravel_index(int(np.argmin(energies)), energies.shape)
    i0 = max(0, min(i - half, n - size))
    j0 = max(0, min(j - half, n - size))
    return slice(i0, i0 + size), slice(j0, j0 + size)


# ---------------------------------------------------------------------------
# Lectura de datos
# ---------------------------------------------------------------------------

def _load_from_text(text: str) -> np.ndarray:
    """Parsea el contenido de un archivo de grilla en una matriz 21x21."""
    raw = np.loadtxt(io.StringIO(text))
    expected = GRID_SIZE * GRID_SIZE
    if raw.shape[0] != expected:
        raise ValueError(
            f"Se esperaban {expected} filas, llegaron {raw.shape[0]}."
        )
    return raw[:, 2].reshape((GRID_SIZE, GRID_SIZE))


def load_energy_grid_local(path: Path) -> np.ndarray:
    """Carga la grilla desde un archivo en disco."""
    return _load_from_text(path.read_text())


def load_energy_grid_github(
    owner: str,
    repo: str,
    path: str,
    branch: str = "main",
    token: str | None = None,
) -> np.ndarray:
    """Descarga la grilla desde un repo GitHub vía URL raw.

    Si `token` es None se intenta sin autenticación (sirve para repos
    públicos). Para repos privados se pasa el token en el header
    Authorization.
    """
    import requests  # import perezoso para no exigir requests en modo local

    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    headers = {"Accept": "text/plain"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(
            f"No se pudo descargar {url} (HTTP {resp.status_code}): "
            f"{resp.text[:200]}"
        )
    return _load_from_text(resp.text)


# ---------------------------------------------------------------------------
# Funciones de cálculo
# ---------------------------------------------------------------------------

def relative_energy_meV(energies: np.ndarray) -> Tuple[np.ndarray, float]:
    """Resta el mínimo discreto y multiplica por 1000 (eV -> meV)."""
    e_min = float(np.min(energies))
    return 1000.0 * (energies - e_min), e_min


def interpolate_subregion(
    sub: np.ndarray,
    theta_indices: np.ndarray,
    phi_indices: np.ndarray,
    step: float = REFINED_STEP,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Interpolación spline bicúbica sobre una sub-grilla."""
    spline = RectBivariateSpline(theta_indices, phi_indices, sub)
    theta_fine = np.arange(theta_indices[0], theta_indices[-1] + step / 2, step)
    phi_fine = np.arange(phi_indices[0], phi_indices[-1] + step / 2, step)
    return theta_fine, phi_fine, spline(theta_fine, phi_fine)


def find_minimum(
    z_fine: np.ndarray,
    theta_fine: np.ndarray,
    phi_fine: np.ndarray,
    e_min_disc: float,
) -> Tuple[float, float, float, float]:
    """Mínimo continuo: (theta*, phi*, z_min_meV, E0 absoluta)."""
    z_min_meV = float(np.min(z_fine))
    i, j = np.unravel_index(np.argmin(z_fine), z_fine.shape)
    return float(theta_fine[i]), float(phi_fine[j]), z_min_meV, z_min_meV / 1000.0 + e_min_disc


# ---------------------------------------------------------------------------
# Graficación
# ---------------------------------------------------------------------------

def _plot_surface(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    title: str,
    outpath: Path | None = None,
) -> plt.Figure:
    fig = plt.figure(figsize=(7, 5))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(x, y, z, cmap="jet", edgecolor="none")
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label="E - E_min (meV)")
    ax.set_title(title)
    ax.set_xlabel(r"$\theta$ (índice)")
    ax.set_ylabel(r"$\phi$ (índice)")
    ax.set_zlabel("E - E_min (meV)")
    fig.tight_layout()
    if outpath is not None:
        fig.savefig(outpath, dpi=150)
    return fig


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Mínimo de la superficie de energía DFT de CsPbX3."
    )
    parser.add_argument(
        "--source", choices=("local", "github"), default="local",
        help="De dónde leer el archivo de entrada (default: %(default)s).",
    )
    parser.add_argument(
        "-i", "--input", type=Path, default=here / "CsPbBr3_AA_AA.txt",
        help="Path local (solo si --source local). Default: %(default)s.",
    )
    parser.add_argument(
        "-o", "--outdir", type=Path, default=here / "figs",
        help="Directorio de salida para las figuras (default: %(default)s).",
    )
    parser.add_argument(
        "--no-show", action="store_true",
        help="No abrir ventanas interactivas (servidores).",
    )
    parser.add_argument(
        "--upload", action="store_true",
        help="Subir figuras y resultados.json al repo GitHub (data/salida/).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    # --- Carga de datos ---
    if args.source == "local":
        if not args.input.exists():
            print(f"ERROR: no se encuentra {args.input}", file=sys.stderr)
            return 1
        print(f"Leyendo datos locales de {args.input}")
        energies = load_energy_grid_local(args.input)
    else:
        owner = os.environ.get("GITHUB_OWNER")
        repo = os.environ.get("GITHUB_REPO")
        branch = os.environ.get("GITHUB_BRANCH", "main")
        gh_path = os.environ.get("GITHUB_INPUT_PATH", "data/entrada/CsPbBr3_AA_AA.txt")
        token = os.environ.get("GITHUB_TOKEN")
        if not (owner and repo):
            print("ERROR: faltan GITHUB_OWNER y/o GITHUB_REPO en el entorno/.env",
                  file=sys.stderr)
            return 2
        print(f"Descargando datos de github.com/{owner}/{repo}@{branch}:{gh_path}")
        energies = load_energy_grid_github(owner, repo, gh_path, branch, token)

    # --- Procesamiento ---
    rel_full, e_min_disc = relative_energy_meV(energies)
    args.outdir.mkdir(parents=True, exist_ok=True)

    theta_full = np.arange(GRID_SIZE)
    phi_full = np.arange(GRID_SIZE)
    th_full, ph_full = np.meshgrid(theta_full, phi_full, indexing="ij")
    _plot_surface(th_full, ph_full, rel_full,
                  title="Superficie de energía completa (21×21)",
                  outpath=args.outdir / "01_surface_full.png")

    theta_slice, phi_slice = auto_subregion(rel_full, size=SUBREGION_SIZE)
    sub = rel_full[theta_slice, phi_slice]
    theta_sub = np.arange(theta_slice.start, theta_slice.stop)
    phi_sub = np.arange(phi_slice.start, phi_slice.stop)
    print(f"Sub-región auto-detectada: θ[{theta_slice.start}:{theta_slice.stop}] φ[{phi_slice.start}:{phi_slice.stop}]")
    th_sub, ph_sub = np.meshgrid(theta_sub, phi_sub, indexing="ij")
    _plot_surface(th_sub, ph_sub, sub,
                  title="Sub-región 5×5 alrededor del mínimo",
                  outpath=args.outdir / "02_surface_sub.png")

    theta_fine, phi_fine, z_fine = interpolate_subregion(sub, theta_sub, phi_sub)
    th_fine, ph_fine = np.meshgrid(theta_fine, phi_fine, indexing="ij")
    _plot_surface(th_fine, ph_fine, z_fine,
                  title="Interpolación spline bicúbica de la sub-región",
                  outpath=args.outdir / "03_surface_spline.png")

    theta_star, phi_star, z_min_meV, e0 = find_minimum(z_fine, theta_fine, phi_fine, e_min_disc)

    # --- Reporte por consola ---
    print("=" * 60)
    print("Resultados")
    print("=" * 60)
    print(f"Fuente             : {args.source}")
    print(f"Mínimo discreto    : {e_min_disc:.6f} (unid. orig.)")
    print(f"Mínimo interpolado : {z_min_meV:.4f} meV")
    print(f"E0 absoluta        : {e0:.6f} (unid. orig.)")
    print(f"θ* (índice)        : {theta_star:.3f}")
    print(f"φ* (índice)        : {phi_star:.3f}")
    print(f"Figuras en         : {args.outdir}")
    print("=" * 60)

    # --- Resultados estructurados ---
    results = {
        "source": args.source,
        "e_min_discreto": e_min_disc,
        "min_interpolado_meV": z_min_meV,
        "E0_absoluta": e0,
        "theta_star_idx": theta_star,
        "phi_star_idx": phi_star,
    }
    results_path = args.outdir.parent / "resultados.json"
    results_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"resultados.json en : {results_path}")

    # --- Subida opcional a GitHub ---
    if args.upload:
        from github_sync import upload_run  # import perezoso
        try:
            uploaded = upload_run(args.outdir, results_path)
            print(f"Subidos {len(uploaded)} archivos a GitHub:")
            for u in uploaded:
                print(f"  - {u}")
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR al subir a GitHub: {exc}", file=sys.stderr)
            return 3

    if not args.no_show:
        plt.show()
    else:
        plt.close("all")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
