# Roteiro de apresentação e perguntas

## Roteiro de 8 a 10 minutos

1. Contexto (1 min): "Nos trabalhos anteriores usamos academia, Spark e formatos de tabela. Agora implementamos uma arquitetura Medalhão no Databricks Free Edition. O serviço gerencia o processamento e o Ubuntu prepara a origem."
2. Origem e Landing (1 min): mostrar .tables, manifesto e CSV. "SQLite é o banco relacional escolhido; extraímos todas as cinco tabelas. O Job copia o snapshot para temporário e consulta cada tabela. Landing preserva CSV em um volume."
3. Bronze (1 min): mostrar Delta e _ingestao. "Bronze mantém conteúdo textual da origem. Delta adiciona transações e metadados sobre os arquivos de dados."
4. Silver (2 min): mostrar regras e auditoria. "Convertemos tipos com try_cast, validamos PK/FK e domínios. Rejeições ficam em quarentena com o registro original. bronze=silver+rejeitados comprova que não descartamos linhas sem registro."
5. Gold (2 min): explicar grão, dimensões, medidas e papéis de data. "Visita e pagamento são eventos diferentes; por isso há duas fatos. Somamos valor_recebido, não todas as cobranças. O plano representa a situação atual, pois não temos histórico."
6. Job e testes (1-2 min): mostrar dependências e execução real. "Cada tarefa só inicia após sucesso da anterior. A validação final interrompe a entrega caso apareçam inconsistências. Reexecutamos o mesmo snapshot e comparamos totais."

Use essas falas como guia de entendimento. Só diga "executamos", "passou" ou "publicamos" quando tiver feito a etapa e coletado evidência real.

## Perguntas prováveis

**Por que SQLite?** O PDF permite escolher o banco. Reutilizamos o modelo e o gerador do trabalho 2, com banco relacional simples e FKs verificadas. SQL Server não é usado nesta implementação.

**Isso ainda complementa os anteriores?** Sim: preserva cenário, dados e Delta; acrescenta plataforma gerenciada, qualidade, dimensão e Job. A mudança de origem está declarada.

**Por que upload do banco?** O workspace remoto não acessa localhost do WSL. Enviamos um snapshot consistente. A extração de todas as tabelas ocorre na tarefa 01; não afirmamos conexão ao banco local em tempo real.

**O que é PaaS?** Usamos uma plataforma gerenciada para notebooks, armazenamento governado e orquestração. Não administramos a instalação do Spark nos servidores.

**Schema e volume são a mesma coisa?** Não. Schema organiza tabelas e volumes; o volume dados dentro de landing guarda os CSVs.

**Por que Delta na Bronze?** É um formato de tabela com log transacional, suporte a operações consistentes e evolução/histórico; Parquet sozinho não fornece esse gerenciamento.

**Qual é o grão?** Um check-in em fato_checkin e um pagamento em fato_pagamento. Dimensões descrevem esses eventos.

**Por que não uma tabela única?** Misturar visitas e pagamentos multiplica linhas e pode inflar receitas. Grãos separados evitam esse erro.

**Como tratam duplicadas?** Rejeitamos todas as linhas com PK repetida para evitar escolher um registro conflitante sem critério de negócio.

**Há SCD2?** Não. Dimensões tipo 1 são reconstruídas. Para histórico contratual seria preciso acrescentar vigência, chave substituta por versão e ligação temporal dos fatos.

**As chaves são substitutas independentes?** Aqui são técnicas derivadas dos IDs da origem única; é uma simplificação. Múltiplas origens exigiriam mapeamento independente para evitar colisões.

**Como provam que nada se perdeu?** Reconciliação de contagens em cada camada, quarentena, unicidade, FKs e conservação dos valores financeiros e visitas.

**O Job é incremental?** Não. É carga completa por snapshot e overwrite, adequada ao pequeno conjunto acadêmico. Uma evolução seria CDC/MERGE, controle de lotes e dimensões históricas.

**ACID garante o pipeline inteiro?** Não. Cada escrita Delta é transacional; não há transação única para todas as tabelas. Falha parcial requer corrigir e reexecutar.

**Qual a diferença entre competência e pagamento?** Competência identifica o mês da cobrança. Data de pagamento identifica quando houve recebimento e pode estar ausente. A consulta de receita do notebook agrupa por competência, não por fluxo de caixa do dia pago.

**Jobs & Pipelines exige Delta Live Tables?** O enunciado pede notebooks encadeados por Job. Esta solução usa Job com dependências, sem afirmar que implementa um pipeline declarativo Lakeflow.

**O que falta validar?** Antes de concluir a execução remota: permissões, compatibilidade serverless, Job, consultas e reexecução. Depois, responder com os Run IDs e resultados reais coletados.
