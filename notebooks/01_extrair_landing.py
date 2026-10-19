# Databricks notebook source
dbutils.widgets.text("catalogo", "workspace")
catalogo = dbutils.widgets.get("catalogo")
import re
assert re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", catalogo), "Catálogo inválido"
spark.sql(f"USE CATALOG `{catalogo}`")
base = f"/Volumes/{catalogo}/landing/dados"
tables = ["planos", "unidades", "alunos", "checkins", "pagamentos"]
keys = {"planos":"id_plano", "unidades":"id_unidade", "alunos":"id_aluno", "checkins":"id_checkin", "pagamentos":"id_pagamento"}
from pyspark.sql import functions as F
# COMMAND ----------
import sqlite3, tempfile, shutil, csv, json, hashlib
from pathlib import Path
source=Path(f"/Volumes/{catalogo}/origem/arquivos")
expected=json.loads((source/'origem_manifest.json').read_text())
assert hashlib.sha256((source/'academia.db').read_bytes()).hexdigest()==expected['sha256'], 'Snapshot diferente do manifesto'
Path(base).mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    local=Path(tmp)/'academia.db'
    shutil.copyfile(source/'academia.db',local)
    with sqlite3.connect(local) as conn:
        found=[r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        assert set(found)==set(tables), f'Tabelas inesperadas: {found}'
        counts={}
        for t in found:
            cur=conn.execute(f'SELECT * FROM "{t}" ORDER BY "{keys[t]}"')
            rows=cur.fetchall()
            with (Path(base)/f'{t}.csv').open('w',encoding='utf-8',newline='') as f:
                w=csv.writer(f); w.writerow([d[0] for d in cur.description]); w.writerows(rows)
            counts[t]=len(rows)
        assert counts==expected['tables']
(Path(base)/'manifest.json').write_text(json.dumps({'tables':counts,'source_sha256':expected['sha256']},indent=2))
print(counts)
