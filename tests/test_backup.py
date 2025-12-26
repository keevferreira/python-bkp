# tests/test_backup.py
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from app.backup import run_backup


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_backup_success_folder_versioning(tmp_path: Path):
    src = tmp_path / "src"
    dest = tmp_path / "dest"

    write_file(src / "a.txt", "hello")
    write_file(src / "sub" / "b.txt", "world")

    fixed_now = datetime(2025, 12, 26, 10, 20, 30)

    result = run_backup(
        source_dir=src,
        destination_dir=dest,
        versioning="folder",
        now_fn=lambda: fixed_now,
    )

    assert result.timestamp_str == "20251226_102030"
    version_folder = dest / "20251226_102030"
    assert version_folder.exists()

    assert (version_folder / "a.txt").read_text(encoding="utf-8") == "hello"
    assert (version_folder / "sub" / "b.txt").read_text(encoding="utf-8") == "world"
    assert result.files_copied == 2


def test_backup_success_filename_versioning(tmp_path: Path):
    src = tmp_path / "src"
    dest = tmp_path / "dest"
    dest.mkdir(parents=True, exist_ok=True)

    write_file(src / "a.txt", "hello")
    write_file(src / "sub" / "b.log", "world")

    fixed_now = datetime(2025, 12, 26, 11, 0, 0)

    result = run_backup(
        source_dir=src,
        destination_dir=dest,
        versioning="filename",
        now_fn=lambda: fixed_now,
    )

    assert (dest / "a_backup_20251226_110000.txt").exists()
    assert (dest / "sub" / "b_backup_20251226_110000.log").exists()
    assert result.files_copied == 2


def test_backup_missing_source_raises(tmp_path: Path):
    src = tmp_path / "src_missing"
    dest = tmp_path / "dest"
    with pytest.raises(FileNotFoundError):
        run_backup(source_dir=src, destination_dir=dest, versioning="folder")


def test_backup_no_create_dest_fails(tmp_path: Path):
    src = tmp_path / "src"
    dest = tmp_path / "dest_missing"

    write_file(src / "a.txt", "x")

    with pytest.raises(FileNotFoundError):
        run_backup(
            source_dir=src,
            destination_dir=dest,
            versioning="none",
            create_destination=False,
        )
