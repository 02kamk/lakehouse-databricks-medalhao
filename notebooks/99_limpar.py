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
dbutils.widgets.text('confirmar','NAO')
assert dbutils.widgets.get('confirmar')=='SIM', 'Limpeza não executada. Para apagar saídas acadêmicas, digite SIM em confirmar.'
# Lista fechada: não apaga catálogo, schemas, conexões, origem Azure ou tabelas externas.
targets={
 'gold':['fato_checkin','fato_pagamento','dim_aluno','dim_plano','dim_unidade','dim_tempo'],
 'silver':tables+['quarentena_'+t for t in tables]+['auditoria_qualidade'],
 'bronze':tables}
for schema,names in targets.items():
    for name in names:spark.sql(f'DROP TABLE IF EXISTS `{catalogo}`.`{schema}`.`{name}`')
assert base==f'/Volumes/{catalogo}/landing/dados'
for t in tables:dbutils.fs.rm(f'{base}/{t}',True)
# Arquivos de extração da versão antiga, se ainda existirem no mesmo volume.
for t in tables:dbutils.fs.rm(f'{base}/{t}.csv',False)
dbutils.fs.rm(f'{base}/manifest.json',False)
print('SAIDAS LIMPAS. Azure SQL preservado. O Job pode reconstruir Landing, Bronze, Silver e Gold.')
