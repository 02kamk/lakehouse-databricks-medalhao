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
    df=raw.withColumn('_raw_json',F.to_json(F.struct(*[F.col(c) for c in raw.columns])))
    for c in raw.columns:
        df=df.withColumn(c,F.when(F.length(F.trim(F.col(c)))==0,None).otherwise(F.trim(F.col(c))))
    if t=='alunos':
        df=df.withColumn('nome',F.initcap(F.regexp_replace('nome',r'\s+',' ')))
        df=df.withColumn('email',F.lower('email'))
        active=F.lower(F.col('ativo'))
        df=df.withColumn('ativo',F.when(active.isin('true','1','sim'),F.lit('true')).when(active.isin('false','0','nao','não'),F.lit('false')).otherwise(F.col('ativo')))
    if t=='pagamentos':
        for c in ['status','forma_pagamento']:df=df.withColumn(c,F.upper(c))
    for c,typ in types[t].items():df=df.withColumn(c,F.expr(f'try_cast(`{c}` AS {typ})'))
    from pyspark.sql.window import Window
    df=df.withColumn('_n_pk',F.count('*').over(Window.partitionBy(keys[t])))
    df.createOrReplaceTempView('candidatos')
    checked=spark.sql(f"SELECT *,coalesce(({rules[t]}) AND _n_pk=1,false) AS _valido FROM candidatos")
    valid=checked.filter('_valido').drop('_n_pk','_valido','_raw_json')
    # Registro original + motivo identificável, sem descartar silenciosamente.
    if t=='alunos':
        reason=F.when(F.col('nome').isNull(),'NOME_OBRIGATORIO').when(~F.col('email').rlike(r'^[^ @]+@[^ @]+[.][^ @]+$'),'EMAIL_INVALIDO').when(~F.col('id_plano').isin([r[0] for r in spark.table('silver.planos').select('id_plano').collect()]),'PLANO_INEXISTENTE').otherwise('TIPO_DOMINIO_OU_PK')
    elif t=='checkins':reason=F.lit('ALUNO_OU_UNIDADE_INEXISTENTE_OU_DATA_INVALIDA')
    elif t=='pagamentos':reason=F.when(F.col('valor')<=0,'VALOR_NAO_POSITIVO').when(~F.col('status').isin('PAGO','PENDENTE','ATRASADO'),'STATUS_INVALIDO').otherwise('ALUNO_INEXISTENTE_OU_DOMINIO_INVALIDO')
    else:reason=F.lit('TIPO_DOMINIO_OU_PK')
    bad=checked.filter('NOT _valido').withColumn('motivo',reason).select(F.col('_raw_json').alias('registro_original'),'motivo')
    n=raw.count();v=valid.count();q=bad.count()
    assert n==v+q
    valid.write.format('delta').mode('overwrite').option('overwriteSchema',True).saveAsTable(f'silver.{t}')
    bad.write.format('delta').mode('overwrite').option('overwriteSchema',True).saveAsTable(f'silver.quarentena_{t}')
    audit.append((t,n,v,q))
spark.createDataFrame(audit,'tabela string, bronze long, silver long, rejeitados long').write.format('delta').mode('overwrite').saveAsTable('silver.auditoria_qualidade')
display(spark.table('silver.auditoria_qualidade').orderBy('tabela'))
# COMMAND ----------
# Evidência: antes/depois do João, sem alterar o dado original da Bronze.
print('ANTES: JOAO NA BRONZE')
display(spark.table('bronze.alunos').filter("try_cast(id_aluno AS INT)=301").drop('_ingestao'))
print('DEPOIS: JOAO NA SILVER')
display(spark.table('silver.alunos').filter('id_aluno=301'))
for t in ['alunos','checkins','pagamentos']:
    print('QUARENTENA: '+t)
    display(spark.table(f'silver.quarentena_{t}'))
