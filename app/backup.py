# app/backup.py
"""
backup.py
Funções principais para realizar backup (cópia) de arquivos.

Suporta versionamento:
- none: copia direto para destino preservando estrutura
- folder: cria uma subpasta timestamp no destino e copia dentro
- filename: adiciona sufixo _backup_<timestamp> no nome de cada arquivo

Também possui tratamento de exceções para cenários comuns (origem inexistente etc.).
"""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Literal


VersioningMode = Literal["none", "folder", "filename"]


@dataclass(frozen=True)
class BackupResult:
    """Resultado do backup."""
    files_copied: int
    bytes_copied: int
    destination_used: Path
    timestamp_str: str


def _timestamp_str(now: datetime | None = None) -> str:
    """
    Retorna timestamp no formato YYYYMMDD_HHMMSS.
    """
    now = now or datetime.now()
    return now.strftime("%Y%m%d_%H%M%S")


def _ensure_dir_exists(path: Path) -> None:
    """
    Garante que o diretório existe.
    """
    path.mkdir(parents=True, exist_ok=True)


def _compute_destination_root(dest: Path, versioning: VersioningMode, ts: str) -> Path:
    """
    Decide o diretório base onde os arquivos serão copiados, dependendo do versionamento.
    """
    if versioning == "folder":
        return dest / ts
    return dest


def _destination_for_file(
    dest_root: Path,
    rel_path: Path,
    versioning: VersioningMode,
    ts: str,
) -> Path:
    """
    Gera o caminho destino para um arquivo individual, preservando subpastas.

    - none/folder: mantém o nome do arquivo.
    - filename: adiciona _backup_<ts> antes da extensão.
    """
    if versioning != "filename":
        return dest_root / rel_path

    # rel_path pode conter subpastas, então precisamos tratar só o nome
    parent = rel_path.parent
    stem = rel_path.stem
    suffix = rel_path.suffix  # inclui o ponto (ex: .txt)
    new_name = f"{stem}_backup_{ts}{suffix}"
    return dest_root / parent / new_name


def run_backup(
    source_dir: str | Path,
    destination_dir: str | Path,
    versioning: VersioningMode = "folder",
    create_destination: bool = True,
    logger: logging.Logger | None = None,
    now_fn: Callable[[], datetime] | None = None,
) -> BackupResult:
    """
    Executa o backup copiando arquivos de source_dir para destination_dir.

    Args:
        source_dir: Diretório de origem.
        destination_dir: Diretório de destino.
        versioning: "none" | "folder" | "filename".
        create_destination: Se True, cria diretórios de destino quando necessário.
                            Se False, falha caso destino não exista.
        logger: Logger opcional.
        now_fn: Função opcional para fornecer datetime (útil em testes).

    Returns:
        BackupResult

    Raises:
        FileNotFoundError: Se origem não existir ou destino não existir (quando create_destination=False).
        NotADirectoryError: Se source_dir não for diretório.
        ValueError: Se versioning inválido.
    """
    if versioning not in ("none", "folder", "filename"):
        raise ValueError(f"versioning inválido: {versioning}")

    log = logger or logging.getLogger("backup_tool")
    src = Path(source_dir)
    dest = Path(destination_dir)

    if not src.exists():
        log.error("Diretório de origem não existe: %s", src)
        raise FileNotFoundError(f"Diretório de origem não existe: {src}")
    if not src.is_dir():
        log.error("Origem não é um diretório: %s", src)
        raise NotADirectoryError(f"Origem não é um diretório: {src}")

    if not dest.exists():
        if create_destination:
            _ensure_dir_exists(dest)
            log.info("Diretório de destino criado: %s", dest)
        else:
            log.error("Diretório de destino não existe (create_destination=False): %s", dest)
            raise FileNotFoundError(f"Diretório de destino não existe: {dest}")

    now = (now_fn or datetime.now)()
    ts = _timestamp_str(now)
    dest_root = _compute_destination_root(dest, versioning, ts)

    if not dest_root.exists():
        _ensure_dir_exists(dest_root)
        log.info("Diretório de backup (versionado) criado: %s", dest_root)

    files_copied = 0
    bytes_copied = 0

    # Caminha recursivamente
    for path in src.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(src)
        target = _destination_for_file(dest_root, rel, versioning, ts)

        # Garante subpastas
        target.parent.mkdir(parents=True, exist_ok=True)

        # Copia (preserva metadata básica com copy2)
        shutil.copy2(path, target)

        size = target.stat().st_size
        files_copied += 1
        bytes_copied += size

        log.info("Arquivo copiado: %s -> %s (%d bytes)", path, target, size)

    log.info(
        "Backup finalizado com sucesso. Arquivos: %d | Bytes: %d | Destino: %s",
        files_copied,
        bytes_copied,
        dest_root,
    )

    return BackupResult(
        files_copied=files_copied,
        bytes_copied=bytes_copied,
        destination_used=dest_root,
        timestamp_str=ts,
    )
