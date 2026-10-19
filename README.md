# Lakehouse com Databricks e arquitetura Medalhão

Trabalho 3 - Academia. Ubuntu no WSL2 + Databricks Free Edition.

Complementa [Trabalho 1](https://github.com/02kamk/apachespark) e [Trabalho 2](https://github.com/02kamk/spark-minio-delta-lake). Este projeto deve ter um **novo repositório**.

## O que faz

SQLite (cinco tabelas) -> CSV no volume landing.dados -> tabelas Delta bronze -> qualidade e quarentena silver -> quatro dimensões e duas fatos gold -> testes. Notebooks encadeados em um Job sequencial. Os dados e gerador vêm do trabalho 2; SQLite é a nova origem, permitida no PDF.

## Instalar e testar no Ubuntu

```bash
sudo apt update
sudo apt install -y python3 python3-venv git sqlite3 unzip
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-docs.txt
bash scripts/testar.sh
mkdocs serve
```

Execute na raiz do projeto. Consulte o [passo a passo](docs/instalacao.md) para WSL, extração do ZIP e cadastro na Free Edition.

## Databricks

1. Crie sua conta Free Edition.
2. Importe notebooks/00_configurar.py a 05_validar.py como notebooks SOURCE Python.
3. Configure catalogo (padrão workspace), rode 00 e envie data/academia.db e data/origem_manifest.json para o volume origem.arquivos.
4. Crie o Job 01 -> 02 -> 03 -> 04 -> 05 em compute Serverless.
5. Rode e confira todas as tarefas Succeeded e as validações. Repita e compare os totais.

Guia completo: [execução](docs/execucao.md), [testes](docs/testes.md), [modelo](docs/modelagem.md), [falas e perguntas](docs/apresentacao.md), [publicação no GitHub](docs/github.md).

## Estrutura

- scripts/: gerador, construção do banco e testes locais.
- notebooks/: setup e cinco tarefas do Job.
- data/: CSVs fictícios e manifesto; banco gerado localmente, ignorado no Git.
- docs/ e mkdocs.yml: documentação completa.
- jobs/job.template.json: estrutura de referência, com caminhos para ajustar.
- .github/workflows/docs.yml: validação local e build estrito em Actions.
- evidencias/: resultados locais e espaço para evidências reais do Databricks.

## Limites e estado

Carga completa, dimensões tipo 1, chaves técnicas derivadas e snapshot enviado manualmente. Cada escrita substitui a tabela acadêmica correspondente; não use schemas com dados de outro projeto. O notebook 05 não autoriza publicar resultados incorretos: falha quando há rejeições na base original. A execução Databricks e a publicação remota precisam ser feitas com sua conta. Não há alegação de Job executado neste pacote.

Consulte [referências e créditos](docs/referencias.md). Após concluir, registre aqui a URL real do site, Run ID do Job e data/hora da execução.
