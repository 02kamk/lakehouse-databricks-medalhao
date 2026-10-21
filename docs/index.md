# Lakehouse da Academia

**Trabalho 3 - Engenharia de Dados (SATC)**  
**Integrantes:** Kamily Hilário das Luzes · Kauã Lucas Alves Barbosa

## Objetivo

Construir um pipeline no Databricks que extrai todas as tabelas de um banco
**Azure SQL Database externo**, preserva a extração em CSV, aplica qualidade e
disponibiliza um modelo dimensional para análise de recebimentos e visitas.

## Arquitetura implementada

```mermaid
flowchart LR
    A["Azure SQL: cinco tabelas"] --> B["Landing: CSV"]
    B --> C["Bronze: Delta Lake"]
    C --> D["Silver: qualidade"]
    D --> E["Gold: dimensões e fatos"]
    D --> Q["Quarentena e auditoria"]
    E --> R["Receita e visitas"]
```

A origem fica fora do Databricks. O Ubuntu gera e carrega os dados no Azure; o Job
consulta o banco remoto por meio do conector SQLSERVER do Spark. Não há envio de
arquivo SQLite ou CSV como substituto da extração externa.

| Camada | Responsabilidade | Formato |
|---|---|---|
| Landing | preservar as cinco tabelas extraídas | CSV em volume |
| Bronze | registrar os dados recebidos e a ingestão | Delta |
| Silver | normalizar, validar e separar rejeições | Delta |
| Gold | organizar as análises por grãos e dimensões | Delta |

## Conteúdo

- [Cenário e dados](dados.md)
- [Pipeline e orquestração](pipeline.md)
- [Qualidade e exemplo de João](qualidade.md)
- [Modelo dimensional](modelagem.md)
- [Critérios e resultados esperados](testes.md)
- [Evidências da execução](evidencias.md)
- [Referências](referencias.md)

Tecnologias, criação do banco e instalação estão no
[README](https://github.com/02kamk/lakehouse-databricks-medalhao#readme).

## Estado da versão Azure

O grupo carregou as cinco tabelas no Azure SQL e forneceu uma captura do novo Job
com todas as tarefas em sucesso. O Run ID é 938325045572911, com duração exibida de
4min27s. A imagem está em [Evidências](evidencias.md). Os testes offline e o build
da documentação também passaram. As saídas detalhadas e a reexecução desta versão
serão registradas conforme as evidências forem fornecidas.
