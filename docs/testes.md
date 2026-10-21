# Critérios e resultados esperados

## Reconciliação por tabela

| Tabela | Origem / Bronze | Silver válida | Quarentena |
|---|---:|---:|---:|
| planos | 4 | 4 | 0 |
| unidades | 4 | 4 | 0 |
| alunos | 303 | 301 | 2 |
| checkins | 7.686 | 7.685 | 1 |
| pagamentos | 2.160 | 2.157 | 3 |

O resultado offline de referência contém 7.685 visitas válidas e R$ 168.550,74 em
pagamentos PAGO. Esses valores foram calculados dos CSVs com Decimal no teste local;
o notebook 05 concluiu com sucesso na execução registrada e seus gráficos estão em [Evidências](evidencias.md). O total financeiro não está rotulado nas barras da captura.

## Verificações implementadas

- Contagens de todas as cinco tabelas de origem e comparação com Landing/Bronze.
- Reconciliação bronze = silver + quarentena e contagens exatas do contrato.
- Unicidade de PK e referências das fatos às dimensões.
- Conservação de eventos entre Silver e Gold.
- Soma de valor_recebido igual ao total PAGO da Silver.
- Soma de quantidade igual aos check-ins válidos.
- João normalizado e alunos 302/303 ausentes da dimensão válida.

## Consultas e gráficos

A análise financeira agrega receita recebida por competência da cobrança. A análise
de frequência agrega visitas por unidade. O notebook 05 apresenta as tabelas e gráficos
de barras correspondentes, separando os grãos das duas fatos.

## Estado das verificações

Os testes offline e a sintaxe dos sete notebooks foram verificados no ambiente de
preparação. Eles não comprovam conexão de rede, autenticação SQL, permissões do
workspace ou execução Spark. O grupo forneceu captura de um novo Job em sucesso, Run ID 938325045572911.
As saídas detalhadas serão incorporadas conforme recebidas. A reexecução da versão Azure
ainda precisa ser confirmada; as evidências do Job SQLite anterior permanecem distintas.
