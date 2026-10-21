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
for param in ['jdbc_host','jdbc_database','jdbc_user','jdbc_password']:
    dbutils.widgets.text(param,'')
host=dbutils.widgets.get('jdbc_host').strip()
database=dbutils.widgets.get('jdbc_database').strip()
user=dbutils.widgets.get('jdbc_user')
password=dbutils.widgets.get('jdbc_password')
# Opcional: jdbc_password pode ser secret:ESCOPO:CHAVE, sem gravar senha no Job.
if password.startswith('secret:'):
    _,scope,key=password.split(':',2)
    password=dbutils.secrets.get(scope=scope,key=key)
assert re.fullmatch(r'[A-Za-z0-9-]+\.database\.windows\.net',host), 'Preencha jdbc_host com FQDN Azure'
assert re.fullmatch(r'[A-Za-z0-9_-]+',database), 'Preencha jdbc_database'
assert user and password, 'Preencha jdbc_user e jdbc_password nas configurações privadas do Job'

def azure(query):
    # Conector SQLSERVER nativo, suportado em Serverless; não instala JARs via Maven.
    return (spark.read.format('sqlserver').option('host',host).option('port','1433')
        .option('database',database).option('user',user).option('password',password)
        .option('encrypt','true').option('trustServerCertificate','false')
        .option('query',query).load())

# O contrato exige um banco dedicado, contendo exatamente as cinco tabelas de origem.
inventory=azure("SELECT s.name AS schema_name,t.name AS table_name FROM sys.tables t JOIN sys.schemas s ON s.schema_id=t.schema_id WHERE t.is_ms_shipped=0").collect()
found={(r['schema_name'],r['table_name']) for r in inventory}
assert found=={('dbo',t) for t in tables}, f'Inventário de tabelas fora do contrato: {found}'

import json
from pathlib import Path
from datetime import datetime,timezone
manifest={'origem':'Azure SQL Database','tabelas':{},'extraido_em':datetime.now(timezone.utc).isoformat()}
for t in tables:
    raw=azure(f'SELECT * FROM [dbo].[{t}]')
    text=raw.select([F.col(c).cast('string').alias(c) for c in raw.columns])
    dest=f'{base}/{t}'
    text.coalesce(1).write.mode('overwrite').option('header',True).csv(dest)
    # CSV materializado: contagens e etapas posteriores leem a mesma extração.
    count=spark.read.option('header',True).csv(dest).count()
    assert count==expected_raw[t], f'Contagem de origem inesperada: {t}={count}'
    manifest['tabelas'][t]=count
(Path(base)/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('EXTRACAO AZURE PARA LANDING CONCLUIDA')
print(manifest['tabelas'])
# Não imprimir host, usuário ou senha em capturas de apresentação.
