#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
github_sync.py
==============

Subida (create-or-update) de archivos a un repositorio GitHub vía la API
REST `contents`. Permite que `cspbx3_min.py` publique automáticamente las
figuras y los resultados en `data/salida/...` del repo configurado en
`.env`.

Variables de entorno requeridas
-------------------------------
* ``GITHUB_TOKEN``  : Personal Access Token con permiso Contents: Read/Write.
* ``GITHUB_OWNER``  : nombre del usuario o de la organización dueña del repo.
* ``GITHUB_REPO``   : nombre del repositorio.
* ``GITHUB_BRANCH`` : (opcional, default ``main``).

Endpoint usado
--------------
``PUT https://api.github.com/repos/{owner}/{repo}/contents/{path}``

Documentación oficial:
https://docs.github.com/en/rest/repos/contents#create-or-update-file-contents
"""

from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Iterable, List

import requests

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:  # pragma: no cover
    pass


API_BASE = "https://api.github.com"


# ---------------------------------------------------------------------------
# Configuración desde entorno
# ---------------------------------------------------------------------------

def _env_or_raise(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"La variable de entorno {name} no está definida. "
            f"Configurala en .env o exportala en la shell."
        )
    return value


def _config() -> dict:
    return {
        "owner": _env_or_raise("GITHUB_OWNER"),
        "repo": _env_or_raise("GITHUB_REPO"),
        "branch": os.environ.get("GITHUB_BRANCH", "main"),
        "token": _env_or_raise("GITHUB_TOKEN"),
    }


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


# ---------------------------------------------------------------------------
# Operaciones de la API
# ---------------------------------------------------------------------------

def _get_existing_sha(
    owner: str, repo: str, path: str, branch: str, token: str,
) -> str | None:
    """Devuelve el SHA de un archivo si ya existe en el repo, sino None.

    El SHA es obligatorio cuando la operación PUT es un update; sin él
    GitHub devuelve 422 (file already exists).
    """
    url = f"{API_BASE}/repos/{owner}/{repo}/contents/{path}"
    resp = requests.get(
        url, params={"ref": branch}, headers=_headers(token), timeout=30,
    )
    if resp.status_code == 200:
        return resp.json().get("sha")
    if resp.status_code == 404:
        return None
    raise RuntimeError(
        f"GET {url} devolvió {resp.status_code}: {resp.text[:200]}"
    )


def put_file(
    local_path: Path,
    remote_path: str,
    message: str | None = None,
) -> str:
    """Sube (o actualiza) un archivo individual al repo.

    Parameters
    ----------
    local_path : Path
        Archivo en disco a leer.
    remote_path : str
        Ruta destino en el repo (ej. ``data/salida/figs/01_surface_full.png``).
    message : str
        Mensaje del commit (default autogenerado).

    Returns
    -------
    str
        URL HTML del archivo en GitHub tras el upload.
    """
    cfg = _config()
    if message is None:
        message = f"auto: update {remote_path}"

    content_b64 = base64.b64encode(local_path.read_bytes()).decode("ascii")

    sha = _get_existing_sha(
        cfg["owner"], cfg["repo"], remote_path, cfg["branch"], cfg["token"],
    )

    payload = {
        "message": message,
        "content": content_b64,
        "branch": cfg["branch"],
    }
    if sha is not None:
        payload["sha"] = sha

    url = f"{API_BASE}/repos/{cfg['owner']}/{cfg['repo']}/contents/{remote_path}"
    resp = requests.put(url, json=payload, headers=_headers(cfg["token"]), timeout=60)
    if resp.status_code not in (200, 201):
        raise RuntimeError(
            f"PUT {url} devolvió {resp.status_code}: {resp.text[:400]}"
        )
    return resp.json()["content"]["html_url"]


def upload_run(
    figs_dir: Path,
    results_path: Path,
    remote_base: str = "data/salida",
) -> List[str]:
    """Sube una corrida completa: todas las figuras + resultados.json.

    Returns
    -------
    list[str]
        URLs HTML de los archivos subidos.
    """
    urls: List[str] = []

    # Figuras
    for fig in sorted(figs_dir.glob("*.png")):
        remote = f"{remote_base}/figs/{fig.name}"
        urls.append(put_file(fig, remote))

    # Resultados estructurados
    if results_path.exists():
        urls.append(put_file(results_path, f"{remote_base}/{results_path.name}"))

    return urls


# ---------------------------------------------------------------------------
# CLI auxiliar (subir un archivo arbitrario)
# ---------------------------------------------------------------------------

def _cli(argv: Iterable[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="Sube un archivo local al repositorio GitHub configurado."
    )
    parser.add_argument("local", type=Path, help="Archivo local a subir.")
    parser.add_argument("remote", help="Ruta destino dentro del repo.")
    parser.add_argument(
        "-m", "--message", default=None, help="Mensaje de commit.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)
    if not args.local.exists():
        print(f"ERROR: {args.local} no existe")
        return 1
    url = put_file(args.local, args.remote, args.message)
    print(f"OK: {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
