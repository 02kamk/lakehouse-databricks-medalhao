# Execução e Job sequencial

## Primeiro ensaio

Depois do setup 00 e do upload, execute 01, 02, 03, 04 e 05 nessa ordem. Configure o mesmo catálogo em todos. O notebook 00 é preparação única e fica fora do Job. O notebook 01 extrai o snapshot SQLite enviado: se o banco local mudar, envie novamente o banco e seu manifesto antes da execução.

## Criar o Job pela interface

1. Abra Jobs & Pipelines (o nome atual pode aparecer como Lakeflow Jobs) e Create job. Nome: academia-medalhao.
2. Adicione a tarefa extrair, tipo Notebook, apontando para 01_extrair_landing. Use compute Serverless e parâmetro catalogo com seu catálogo.
3. Adicione bronze apontando para 02_landing_bronze, com Depends on: extrair.
4. Adicione silver apontando para 03_bronze_silver, com Depends on: bronze.
5. Adicione gold apontando para 04_silver_gold, com Depends on: silver.
6. Adicione validar apontando para 05_validar, com Depends on: gold.
7. Em cada tarefa, configure catalogo com o mesmo valor e Run if: All succeeded. Configure uma execução simultânea do Job. Não adicione agendamento para este laboratório.
8. Salve e clique Run now. Abra a execução e espere todas as cinco tarefas ficarem Succeeded. Se uma falhar, abra o erro e corrija a causa; tarefas posteriores devem permanecer bloqueadas.
9. Abra validar e confira TODAS AS VALIDACOES PASSARAM e as consultas analíticas.

jobs/job.template.json é referência estrutural: contém SEU_EMAIL e caminhos que precisam ser substituídos. A criação pela interface é o caminho explicado e evita depender de configuração de CLI. Não envie esse template sem ajustes à API.

## Reexecução

O projeto usa carga completa com overwrite das suas tabelas acadêmicas. Não reutilize os mesmos schemas com dados de outro projeto. Não há DELETE ou DROP de schemas, mas tabelas de mesmo nome são substituídas. Execute o Job com concorrência 1 e mantenha o snapshot de origem estável durante a execução. Não há transação única abrangendo todas as tabelas: uma falha pode deixar camadas parcialmente atualizadas. Corrija a falha e execute o Job completo.

O manifesto identifica a origem por SHA-256 e contagens. Regere o manifesto sempre que reconstruir o banco. Reexecutar o Job sobre o mesmo snapshot deve manter contagens e valores analíticos; timestamps de ingestão e versões Delta podem mudar.
