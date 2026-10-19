# Testes para apresentar

## Etapa local

```bash
source .venv/bin/activate
bash scripts/testar.sh
```

O script usa set -euo pipefail: falha no primeiro erro e não imprime sucesso após falha. Verifica banco, FKs, hash do snapshot, contagens de todas as tabelas, sintaxe Python dos notebooks e documentação estrita. O relatório evidencias/testes-locais.txt contém o que foi executado no ambiente de preparação; repita no Ubuntu.

## Etapa Databricks obrigatória

1. Execute Job completo e salve o Run ID, data/hora e captura das cinco tarefas verdes.
2. Execute `SELECT * FROM silver.auditoria_qualidade`: cada linha deve satisfazer bronze=silver+rejeitados; os dados originais devem resultar em zero rejeições.
3. Execute `DESCRIBE DETAIL bronze.alunos`: format deve ser delta. Repita em silver.alunos e gold.fato_pagamento.
4. O notebook 05 verifica reconciliação de contagens, unicidade, FKs principais, conservação dos check-ins e soma exata dos valores recebidos. O Job falha se houver rejeições na base original.
5. Execute o Job de novo sem alterar o snapshot. Compare contagens por tabela, total de visitas e receita; devem ser iguais. Capture os dois Run IDs.
6. Confira ausência de órfãos da unidade: `SELECT count(*) FROM gold.fato_checkin f LEFT ANTI JOIN gold.dim_unidade d ON f.sk_unidade=d.sk_unidade`; esperado 0. Para o tempo, faça a mesma consulta com sk_tempo. Confira competência em fato_pagamento com sk_competencia=dim_tempo.sk_tempo.

## Teste negativo de qualidade em ambiente isolado

Não altere a origem usada na apresentação. Crie uma cópia do notebook 03 para teste e use outro catálogo/schema de laboratório ou restaure a Bronze executando 02 antes de voltar ao fluxo normal. Na Bronze de teste, insira uma linha de planos com ID novo e valor_mensal='abc'; outra com ID duplicado; e um aluno com id_plano inexistente. Execute 03. Esperado: registros inválidos na quarentena, nenhuma PK duplicada na Silver e conservação bronze=silver+quarentena. O notebook 05 deve falhar com rejeições: é a barreira de qualidade funcionando. Depois, execute o Job completo na base original e confirme zero rejeições. Registre os SQLs usados e capturas reais; não fabrique evidências.

## Checklist no dia

- Abrir a conta e confirmar disponibilidade da cota serverless antes da aula.
- Ter ZIP, PDF e documentação local acessíveis.
- Confirmar catálogo dos widgets e arquivos do snapshot no volume de origem.
- Rodar o Job com antecedência; manter a execução concluída aberta.
- Conferir README e MkDocs no novo repositório.
- Mostrar código, execução verde, qualidade e consultas Gold.
- Se o serviço estiver indisponível, mostrar evidências já coletadas e declarar a indisponibilidade. Um print não substitui teste novo.

## Problemas comuns

| Erro | Ação |
| --- | --- |
| CATALOG/SCHEMA_NOT_FOUND | Verificar catalogo e rodar 00 |
| PERMISSION_DENIED | Usar catálogo permitido e conferir privilégios |
| academia.db não encontrado | Enviar arquivo ao volume origem/arquivos correto |
| Snapshot diferente do manifesto | Enviar banco e manifesto da mesma geração |
| SQLITE error | Confirmar upload binário completo; reconstruir com preparar_origem.py |
| CSV faltando | Rodar 01; verificar se a tarefa terminou |
| Quarentena maior que zero | Abrir JSON original e corrigir a origem ou regra justificada |
| Quota serverless esgotada | Consultar limites na interface e aguardar liberação; ensaiar antes |
| MkDocs não encontrado | Ativar .venv e instalar requirements-docs.txt |
| Job não encontra notebook | Selecionar o caminho real no Workspace, sem copiar SEU_EMAIL |
