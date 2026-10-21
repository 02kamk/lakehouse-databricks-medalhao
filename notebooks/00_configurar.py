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
for schema in ['landing','bronze','silver','gold']:
    spark.sql(f'CREATE SCHEMA IF NOT EXISTS `{catalogo}`.`{schema}`')
spark.sql('CREATE VOLUME IF NOT EXISTS landing.dados')
print('AMBIENTE CONFIGURADO. Não é necessário enviar banco ou CSV ao volume: o Job lê o Azure SQL.')
display(spark.sql(f'SHOW SCHEMAS IN `{catalogo}`'))
