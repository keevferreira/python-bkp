# Backup Tool (Python + Pytest + Docker)

## O software foi desenvolvido pensando somente em ambientes Linux.

## Rodar localmente
```bash
pip install -r requirements.txt
python -m app.main --source ./origem --dest ./backups --versioning folder
docker run --rm -v "$PWD":/work -w /work backup-tool --source ./origem --dest ./backups --versioning folder