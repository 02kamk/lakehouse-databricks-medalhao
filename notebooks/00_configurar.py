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
for schema in ["origem", "landing", "bronze", "silver", "gold"]:
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{catalogo}`.`{schema}`")
spark.sql("CREATE VOLUME IF NOT EXISTS origem.arquivos")
spark.sql("CREATE VOLUME IF NOT EXISTS landing.dados")
print(f"Enviar academia.db e origem_manifest.json para /Volumes/{catalogo}/origem/arquivos/")
