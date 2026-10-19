# Qualidade e modelo dimensional

## Bronze

Cinco tabelas Delta: planos, unidades, alunos, checkins e pagamentos. Colunas recebidas como texto para preservar os valores de origem, mais _ingestao. Não há limpeza silenciosa nessa camada.

## Silver

trim remove espaços nas extremidades; vazios viram nulos; email fica em minúsculas; status e forma de pagamento ficam em maiúsculas. try_cast converte IDs para inteiros, valores para decimal(12,2), datas, timestamps e booleanos. Datas inválidas viram nulos e são rejeitadas quando obrigatórias.

Regras: IDs positivos e únicos; todas as ocorrências de PK duplicada são rejeitadas; nomes essenciais preenchidos; email com formato básico; valor e duração positivos; datas obrigatórias válidas; domínios de pagamento limitados; pagamento PAGO requer data, PENDENTE/ATRASADO requerem ausência de data; FKs precisam existir nos pais válidos. Pais são processados antes dos filhos. Aluno inválido pode causar rejeição dos seus fatos: isso é propagação de qualidade, não exclusão arbitrária.

Cada tabela gera silver.quarentena_NOME com o JSON original e motivo geral. silver.auditoria_qualidade registra bronze = silver + rejeitados. Uma evolução útil é detalhar qual regra falhou. Não se alega validação universal de e-mail ou regra temporal de matrícula: alguns registros herdados do gerador acadêmico podem ter eventos anteriores à matrícula. Esse caso deve ser discutido antes de adicionar uma regra nova.

## Gold: estrelas Kimball

| Tabela | Grão e papel |
| --- | --- |
| dim_aluno | Uma linha por aluno; nome, cidade, email, situação e plano atual |
| dim_plano | Uma linha por plano |
| dim_unidade | Uma linha por unidade |
| dim_tempo | Uma linha por dia, calendário contínuo entre menor e maior data dos fatos |
| fato_checkin | Uma linha por check-in; aluno, plano atual, unidade, dia; medida quantidade=1 |
| fato_pagamento | Uma linha por pagamento; aluno, plano atual, competência e data de pagamento; valor e valor_recebido |

Relacionamentos: dim_aluno 1:N para as duas fatos; dim_plano 1:N para as duas fatos; dim_unidade 1:N para fato_checkin; dim_tempo 1:N para as datas das duas fatos. Em pagamentos a dimensão tempo exerce dois papéis: competência e pagamento. sk_pagamento pode ser nulo para pendentes e atrasados.

As chaves sk_aluno, sk_plano e sk_unidade são chaves técnicas long derivadas dos IDs da única origem. Não são sequências independentes; isso é uma simplificação explícita do laboratório. A dimensão tempo usa YYYYMMDD. IDs do evento são dimensões degeneradas nas fatos. Dimensões são tipo 1 e carga completa: alterações substituem atributos, sem histórico SCD2. O plano é o plano atual do aluno, pois a origem não contém histórico contratual. Não atribua a receita a um plano histórico que não existe na origem.

Não unir as duas fatos diretamente por aluno para somar dinheiro: várias visitas multiplicariam pagamentos. Agregue cada fato separadamente antes de cruzar resultados. A medida receita recebida considera apenas status PAGO; valor dos demais registros representa cobrança, não recebimento.

## Relação com trabalhos 1 e 2

Trabalho 1 comparou Delta e Iceberg e demonstrou DML. Trabalho 2 adicionou SQL Server, MinIO, CSV e Delta. Trabalho 3 mantém academia e gerador, muda a origem para SQLite e leva o processamento ao serviço gerenciado Databricks, com qualidade, modelo dimensional e orquestração. Não é necessário reproduzir os comandos DML do trabalho 1 no pipeline novo.
