# app/logger.py
"""
logger.py
Configuração de logging para o projeto de backup.

- Logs no console e em arquivo (backup.log por padrão).
- Níveis: INFO para operações normais e ERROR para falhas.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_logger(
    name: str = "backup_tool",
    log_file: str | Path = "backup.log",
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Retorna um logger configurado (console + arquivo).

    Args:
        name: Nome do logger.
        log_file: Caminho do arquivo de log.
        level: Nível de log (default: INFO).

    Returns:
        logging.Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Evita duplicar handlers se chamar get_logger várias vezes
    if logger.handlers:
        return logger

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(fmt)

    # Arquivo com rotação
    fh = RotatingFileHandler(
        filename=str(log_path),
        maxBytes=1_000_000,   # 1MB
        backupCount=3,
        encoding="utf-8",
    )
    fh.setLevel(level)
    fh.setFormatter(fmt)

    logger.addHandler(ch)
    logger.addHandler(fh)

    # Boa prática: não propagar para o root logger
    logger.propagate = False
    return logger
