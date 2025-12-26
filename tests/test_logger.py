# tests/test_logger.py
from __future__ import annotations

from pathlib import Path

from app.logger import get_logger
from app.backup import run_backup


def test_logger_writes_to_file(tmp_path: Path):
    log_file = tmp_path / "backup.log"
    logger = get_logger(name="test_logger", log_file=log_file)

    src = tmp_path / "src"
    dest = tmp_path / "dest"

    src.mkdir()
    (src / "a.txt").write_text("hello", encoding="utf-8")

    run_backup(source_dir=src, destination_dir=dest, versioning="none", logger=logger)

    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "Arquivo copiado" in content
    assert "Backup finalizado com sucesso" in content


def test_logger_error_on_missing_source(tmp_path: Path):
    log_file = tmp_path / "backup.log"
    logger = get_logger(name="test_logger_error", log_file=log_file)

    src = tmp_path / "missing"
    dest = tmp_path / "dest"

    try:
        run_backup(source_dir=src, destination_dir=dest, versioning="folder", logger=logger)
    except FileNotFoundError:
        pass

    content = log_file.read_text(encoding="utf-8")
    assert "Diretório de origem não existe" in content
