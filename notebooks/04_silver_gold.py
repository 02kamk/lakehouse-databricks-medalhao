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
# Full refresh, dimensões tipo 1. Chaves estáveis derivadas das chaves da origem única.
for t,singular in [('alunos','aluno'),('planos','plano'),('unidades','unidade')]:
    pk=keys[t]
    df=spark.table(f'silver.{t}').withColumn(f'sk_{singular}',F.col(pk).cast('long'))
    df.write.format('delta').mode('overwrite').option('overwriteSchema',True).saveAsTable(f'gold.dim_{singular}')
spark.sql("""CREATE OR REPLACE TABLE gold.dim_tempo USING DELTA AS
WITH limites AS (
 SELECT min(d) mi, max(d) ma FROM (
 SELECT to_date(data_hora) d FROM silver.checkins UNION ALL
 SELECT competencia d FROM silver.pagamentos UNION ALL
 SELECT data_pagamento d FROM silver.pagamentos WHERE data_pagamento IS NOT NULL))
SELECT cast(date_format(d,'yyyyMMdd') AS INT) sk_tempo, d data,
year(d) ano, month(d) mes, day(d) dia, quarter(d) trimestre
FROM limites LATERAL VIEW explode(sequence(mi,ma,interval 1 day)) e AS d""")
spark.sql("""CREATE OR REPLACE TABLE gold.fato_checkin USING DELTA AS
SELECT c.id_checkin, a.sk_aluno, p.sk_plano, u.sk_unidade, t.sk_tempo,
c.data_hora, 1 quantidade
FROM silver.checkins c JOIN gold.dim_aluno a ON c.id_aluno=a.id_aluno
JOIN gold.dim_plano p ON a.id_plano=p.id_plano
JOIN gold.dim_unidade u ON c.id_unidade=u.id_unidade
JOIN gold.dim_tempo t ON to_date(c.data_hora)=t.data""")
spark.sql("""CREATE OR REPLACE TABLE gold.fato_pagamento USING DELTA AS
SELECT f.id_pagamento, a.sk_aluno, p.sk_plano, t.sk_tempo sk_competencia,
dt.sk_tempo sk_pagamento, f.valor, f.status, f.forma_pagamento,
CASE WHEN f.status='PAGO' THEN f.valor ELSE cast(0 AS DECIMAL(12,2)) END valor_recebido
FROM silver.pagamentos f JOIN gold.dim_aluno a ON f.id_aluno=a.id_aluno
JOIN gold.dim_plano p ON a.id_plano=p.id_plano
JOIN gold.dim_tempo t ON f.competencia=t.data
LEFT JOIN gold.dim_tempo dt ON f.data_pagamento=dt.data""")
print('GOLD OK: quatro dimensões e duas fatos')
