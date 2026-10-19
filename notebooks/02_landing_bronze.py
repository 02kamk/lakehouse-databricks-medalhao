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
import json
from pathlib import Path
counts=json.loads((Path(base)/'manifest.json').read_text())['tables']
for t in tables:
    raw=spark.read.option('header',True).option('inferSchema',False).option('mode','FAILFAST').csv(f'{base}/{t}.csv')
    assert raw.count()==counts[t], f'Contagem Landing: {t}'
    raw.withColumn('_ingestao',F.current_timestamp()).write.format('delta').mode('overwrite').option('overwriteSchema',True).saveAsTable(f'bronze.{t}')
    assert spark.table(f'bronze.{t}').count()==counts[t]
print('BRONZE OK: cinco tabelas Delta, conteúdo preservado como texto')
