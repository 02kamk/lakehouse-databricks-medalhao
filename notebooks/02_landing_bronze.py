# Databricks notebook source
dbutils.widgets.text("catalogo", "workspace")
catalogo=dbutils.widgets.get("catalogo")
import re
assert re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*",catalogo), "Catálogo inválido"
spark.sql(f"USE CATALOG `{catalogo}`")
base=f"/Volumes/{catalogo}/landing/dados"
tables=["planos","unidades","alunos","checkins","pagamentos"]
keys={"planos":"id_plano","unidades":"id_unidade","alunos":"id_aluno","checkins":"id_checkin","pagamentos":"id_pagamento"}
expected_raw={"planos":4,"unidades":4,"alunos":303,"checkins":7686,"pagamentos":2160}
expected_silver={"planos":4,"unidades":4,"alunos":301,"checkins":7685,"pagamentos":2157}
from pyspark.sql import functions as F
# COMMAND ----------
import json
from pathlib import Path
manifest=json.loads((Path(base)/'manifest.json').read_text(encoding='utf-8'))
for t in tables:
    raw=spark.read.option('header',True).option('inferSchema',False).option('mode','FAILFAST').csv(f'{base}/{t}')
    assert raw.count()==manifest['tabelas'][t]==expected_raw[t]
    raw.withColumn('_ingestao',F.current_timestamp()).write.format('delta').mode('overwrite').option('overwriteSchema',True).saveAsTable(f'bronze.{t}')
print('BRONZE OK: cinco tabelas Delta e conteúdo da extração preservado')
