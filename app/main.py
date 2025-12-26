# app/main.py
"""
main.py
Script principal que integra logger + backup e permite execução via CLI.

Exemplos:
  python -m app.main --source ./origem --dest ./backups --versioning folder
  python -m app.main --source ./origem --dest ./backups --versioning filename
  python -m app.main --source ./origem --dest ./backups --simulate-missing-source
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.backup import run_backup
from app.logger import get_logger


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ferramenta de Backup Automatizado (Python + Docker + Pytest)")
    parser.add_argument("--source", required=True, help="Diretório de origem (source)")
    parser.add_argument("--dest", required=True, help="Diretório de destino (destination)")
    parser.add_argument(
        "--versioning",
        choices=["none", "folder", "filename"],
        default="folder",
        help="Modo de versionamento: none | folder | filename",
    )
    parser.add_argument(
        "--log-file",
        default="backup.log",
        help="Arquivo de log (default: backup.log)",
    )

    # Simulações/erros
    parser.add_argument(
        "--simulate-missing-source",
        action="store_true",
        help="Simula falha definindo uma origem inexistente",
    )
    parser.add_argument(
        "--no-create-dest",
        action="store_true",
        help="Se passado, falha caso o destino não exista (não cria diretórios).",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    args = parse_args(argv)

    logger = get_logger(log_file=args.log_file)

    source = Path(args.source)
    dest = Path(args.dest)

    if args.simulate_missing_source:
        source = Path(str(source) + "__MISSING__")

    try:
        run_backup(
            source_dir=source,
            destination_dir=dest,
            versioning=args.versioning,
            create_destination=not args.no_create_dest,
            logger=logger,
        )
        return 0
    except Exception as exc:
        # Loga erro e retorna código != 0 (bom para CI/Docker)
        logger.error("Falha ao executar backup: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
