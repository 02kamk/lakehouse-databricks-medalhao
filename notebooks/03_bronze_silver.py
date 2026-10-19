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
# try_cast evita abortar a leitura; regras encaminham inválidos para quarentena.
types={
 'planos':{'id_plano':'int','valor_mensal':'decimal(12,2)','duracao_meses':'int'},
 'unidades':{'id_unidade':'int','data_inauguracao':'date'},
 'alunos':{'id_aluno':'int','id_plano':'int','data_matricula':'date','ativo':'boolean'},
 'checkins':{'id_checkin':'int','id_aluno':'int','id_unidade':'int','data_hora':'timestamp'},
 'pagamentos':{'id_pagamento':'int','id_aluno':'int','competencia':'date','data_pagamento':'date','valor':'decimal(12,2)'}}
rules={
 'planos':"id_plano > 0 AND nome IS NOT NULL AND valor_mensal > 0 AND duracao_meses > 0",
 'unidades':"id_unidade > 0 AND nome IS NOT NULL AND cidade IS NOT NULL AND data_inauguracao IS NOT NULL",
 'alunos':"id_aluno > 0 AND nome IS NOT NULL AND email RLIKE '^[^ @]+@[^ @]+[.][^ @]+$' AND data_matricula IS NOT NULL AND ativo IS NOT NULL AND id_plano IN (SELECT id_plano FROM silver.planos)",
 'checkins':"id_checkin > 0 AND data_hora IS NOT NULL AND id_aluno IN (SELECT id_aluno FROM silver.alunos) AND id_unidade IN (SELECT id_unidade FROM silver.unidades)",
 'pagamentos':"id_pagamento > 0 AND competencia IS NOT NULL AND day(competencia)=1 AND valor > 0 AND forma_pagamento IN ('PIX','CARTAO','BOLETO') AND status IN ('PAGO','PENDENTE','ATRASADO') AND ((status='PAGO' AND data_pagamento IS NOT NULL) OR (status<>'PAGO' AND data_pagamento IS NULL)) AND id_aluno IN (SELECT id_aluno FROM silver.alunos)"}
audit=[]
for t in tables:
    raw=spark.table(f'bronze.{t}').drop('_ingestao')
    raw_json=F.to_json(F.struct(*[F.col(c) for c in raw.columns]))
    df=raw.withColumn('_raw_json',raw_json)
    for c in raw.columns:
        df=df.withColumn(c,F.when(F.length(F.trim(F.col(c)))==0,None).otherwise(F.trim(F.col(c))))
    if t=='alunos': df=df.withColumn('email',F.lower('email'))
    if t=='pagamentos':
        for c in ['status','forma_pagamento']: df=df.withColumn(c,F.upper(c))
    for c,typ in types[t].items(): df=df.withColumn(c,F.expr(f'try_cast(`{c}` AS {typ})'))
    # Rejeita TODAS as ocorrências de uma chave duplicada: não escolhe uma arbitrariamente.
    from pyspark.sql.window import Window
    df=df.withColumn('_n_pk',F.count('*').over(Window.partitionBy(keys[t])))
    df.createOrReplaceTempView('candidatos')
    checked=spark.sql(f"SELECT *, coalesce(({rules[t]}) AND _n_pk=1, false) AS _valido FROM candidatos")
    valid=checked.filter('_valido').drop('_n_pk','_valido','_raw_json')
    bad=checked.filter('NOT _valido').select(F.col('_raw_json').alias('registro_original')).withColumn('motivo',F.lit('TIPO_DOMINIO_FK_OU_PK_DUPLICADA'))
    n=raw.count(); v=valid.count(); q=bad.count()
    assert n==v+q
    valid.write.format('delta').mode('overwrite').option('overwriteSchema',True).saveAsTable(f'silver.{t}')
    bad.write.format('delta').mode('overwrite').option('overwriteSchema',True).saveAsTable(f'silver.quarentena_{t}')
    audit.append((t,n,v,q))
spark.createDataFrame(audit,'tabela string, bronze long, silver long, rejeitados long').write.format('delta').mode('overwrite').saveAsTable('silver.auditoria_qualidade')
display(spark.table('silver.auditoria_qualidade'))
