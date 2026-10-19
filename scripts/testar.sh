#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/gerar_dados.py
python3 scripts/preparar_origem.py
python3 scripts/testar_local.py
.venv/bin/mkdocs build --strict
echo 'TESTES LOCAIS PASSARAM; execute também o Job no Databricks.'
