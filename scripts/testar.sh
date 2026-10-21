#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python scripts/gerar_dados.py
python scripts/testar_local.py
python -m mkdocs build --strict
echo 'TESTES LOCAIS PASSARAM. Azure e Databricks exigem testes remotos separados.'
