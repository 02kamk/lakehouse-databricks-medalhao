# Validações e resultados

## Critérios de validação

O pipeline compara contagens entre camadas, verifica unicidade das chaves, referências
entre tabelas e conservação dos valores financeiros. Esses controles indicam se as
transformações preservaram os eventos da origem sem perda ou multiplicação.

| Controle | Critério |
|---|---|
| Landing e Bronze | contagens iguais às da extração |
| Silver | bronze = silver + rejeitados |
| Chaves primárias | ausência de IDs duplicados nas tabelas válidas |
| Chaves estrangeiras | ausência de referências a dimensões inexistentes |
| Check-ins na Gold | uma linha por check-in e soma de quantidade igual ao total válido |
| Receita recebida | soma de valor_recebido igual à soma de pagamentos PAGO na Silver |
| Reexecução | conservação dos totais sobre o mesmo snapshot |

## Base original

| Tabela | Quantidade de registros |
|---|---:|
| planos | 4 |
| unidades | 4 |
| alunos | 300 |
| checkins | 7.684 |
| pagamentos | 2.156 |

O estudante confirmou zero rejeições nas cinco tabelas da Silver. Assim, na base
original, as contagens foram preservadas entre Bronze e Silver. Quarentena vazia
nesse conjunto não elimina a necessidade das regras: elas protegem o processamento
contra entradas inválidas futuras.

## Execução do Job

Uma captura compartilhada pelo estudante mostrou as tarefas extrair, bronze, silver,
gold e validar em sucesso. A validação dos notebooks e o teste de reexecução também
foram confirmados durante o acompanhamento.

O registro em evidencias/validacao-databricks.md, no repositório, distingue evidências
visuais e confirmações do estudante. Não houve execução remota independente pelo
assistente. Os totais numéricos das consultas não foram fornecidos na última confirmação,
portanto não são apresentados aqui como uma comparação independente.

## Análises disponibilizadas

- **Receita recebida por competência:** considera pagamentos com status PAGO e agrupa
  pela competência. Representa recebimentos associados ao mês da cobrança, não fluxo
  de caixa agrupado pela data efetiva de pagamento.
- **Visitas por unidade:** soma a medida quantidade da fato_checkin, relacionada à
  dimensão unidade, permitindo comparar a utilização das unidades da academia.

## Limites dos testes

As verificações locais cobrem integridade do SQLite, hash, contagens e sintaxe dos
notebooks. O build do MkDocs valida a documentação. Essas verificações são distintas
da execução do Spark e do Job no Databricks.

As regras implementadas encaminham dados inválidos para quarentena. O teste negativo
com registros deliberadamente inválidos não foi confirmado pelo estudante e não é
tratado como evidência de teste concluído.
