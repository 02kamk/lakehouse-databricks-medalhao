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
for t in tables:
    b=spark.table(f'bronze.{t}').count(); s=spark.table(f'silver.{t}').count()
    q=spark.table(f'silver.quarentena_{t}').count()
    assert b==s+q, t
    assert spark.table(f'silver.{t}').groupBy(keys[t]).count().filter('count>1').count()==0
    assert q==0, f'{t}: há rejeições; revisar antes de apresentar'
for fact,src,pk in [('fato_checkin','checkins','id_checkin'),('fato_pagamento','pagamentos','id_pagamento')]:
    f=spark.table('gold.'+fact)
    assert f.count()==spark.table('silver.'+src).count(), 'Perda/multiplicação no join'
    assert f.select(pk).distinct().count()==f.count()
    for fk,dim,dk in [('sk_aluno','dim_aluno','sk_aluno'),('sk_plano','dim_plano','sk_plano')]:
        d=spark.table('gold.'+dim)
        assert f.join(d,f[fk]==d[dk],'left_anti').count()==0
assert spark.sql("SELECT sum(valor) FROM silver.pagamentos WHERE status='PAGO'").first()[0]==spark.sql('SELECT sum(valor_recebido) FROM gold.fato_pagamento').first()[0]
assert spark.sql('SELECT sum(quantidade) FROM gold.fato_checkin').first()[0]==spark.table('silver.checkins').count()
for fact,fk,dim,dk,nullable in [
    ('fato_checkin','sk_unidade','dim_unidade','sk_unidade',False),
    ('fato_checkin','sk_tempo','dim_tempo','sk_tempo',False),
    ('fato_pagamento','sk_competencia','dim_tempo','sk_tempo',False),
    ('fato_pagamento','sk_pagamento','dim_tempo','sk_tempo',True)]:
    f=spark.table('gold.'+fact)
    if nullable: f=f.filter(F.col(fk).isNotNull())
    else: assert f.filter(F.col(fk).isNull()).count()==0
    d=spark.table('gold.'+dim)
    assert f.join(d,f[fk]==d[dk],'left_anti').count()==0, f'FK inválida: {fact}.{fk}'
display(spark.sql("SELECT t.ano,t.mes,sum(f.valor_recebido) receita FROM gold.fato_pagamento f JOIN gold.dim_tempo t ON f.sk_competencia=t.sk_tempo GROUP BY t.ano,t.mes ORDER BY t.ano,t.mes"))
display(spark.sql("SELECT u.nome,sum(f.quantidade) visitas FROM gold.fato_checkin f JOIN gold.dim_unidade u ON f.sk_unidade=u.sk_unidade GROUP BY u.nome ORDER BY visitas DESC"))
print('TODAS AS VALIDACOES PASSARAM')
