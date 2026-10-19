# Lakehouse com Databricks e arquitetura Medalhão

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Databricks](https://img.shields.io/badge/Databricks-Free%20Edition-FF3621?logo=databricks&logoColor=white)
![MkDocs](https://img.shields.io/badge/MkDocs-Material-526CFE?logo=materialformkdocs&logoColor=white)

📘 **Documentação do trabalho:** https://02kamk.github.io/lakehouse-databricks-medalhao/

👥 **Integrantes:** Kamily Hilário das Luzes · Kauã Lucas Alves Barbosa

Este README contém as instruções para instalar, configurar e executar o projeto.

---

## Sumário

- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração do Databricks](#configuração-do-databricks)
- [Execução](#execução)
- [Problemas comuns](#problemas-comuns)

---

## Pré-requisitos

| Requisito | Versão / configuração |
|---|---|
| Ubuntu | 24.04 LTS, nativo ou no WSL2 |
| Python | 3.10 ou superior, com suporte a venv |
| Git | versão recente |
| Databricks | conta Free Edition com acesso a Serverless |
| Catálogo | permissão para criar schemas, volumes e tabelas e ler/gravar arquivos |

> [!NOTE]
> Execute os comandos deste README no terminal do **Ubuntu**.
> Não é necessário instalar Spark, Java, Docker ou Databricks no computador.

---

## Instalação

### 1. Instalar os pacotes do sistema

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git sqlite3
```

### 2. Clonar o repositório

```bash
mkdir -p ~/projetos
cd ~/projetos
git clone https://github.com/02kamk/lakehouse-databricks-medalhao.git lakehouse-academia
cd lakehouse-academia
```

Se já possui o projeto, entre na pasta existente:

```bash
cd ~/projetos/lakehouse-academia
```

### 3. Criar e ativar o ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-docs.txt
```

### 4. Gerar o banco de origem

Execute na primeira instalação:

```bash
python scripts/gerar_dados.py
python scripts/preparar_origem.py
python scripts/testar_local.py
```

Confira se foram criados `data/academia.db` e `data/origem_manifest.json`.

> [!IMPORTANT]
> Se reconstruir o banco, envie novamente os dois arquivos ao Databricks.
> Para atualizar apenas README ou MkDocs, não é necessário executar os geradores.

---

## Configuração do Databricks

1. Entre no Databricks Free Edition pelo navegador.
2. Em **Workspace**, crie a pasta `lakehouse-academia/notebooks` na sua área de usuário.
3. Importe os seis arquivos `.py` de `notebooks/` como notebooks Python.
4. Abra `00_configurar`, selecione **Serverless** e informe `workspace` no parâmetro `catalogo`.
5. Execute **Run all**. Se seu catálogo tiver outro nome, use esse nome em todos os notebooks e tarefas.
6. Em **Catalog**, abra `workspace → origem → Volumes → arquivos`.
7. Clique em **Upload to this volume** e envie `academia.db` e `origem_manifest.json` da pasta `data/`.

Destino padrão:

```text
/Volumes/workspace/origem/arquivos/
```

Para abrir a pasta pelo Ubuntu no WSL:

```bash
cd ~/projetos/lakehouse-academia/data
explorer.exe .
```

---

## Execução

### Execução manual

Após configurar o ambiente e enviar os arquivos, execute **Run all** em cada notebook nesta ordem:

1. `01_extrair_landing`
2. `02_landing_bronze`
3. `03_bronze_silver`
4. `04_silver_gold`
5. `05_validar`

Confira o mesmo valor de `catalogo` em todos os notebooks.

### Execução pelo Job

Em **Jobs & Pipelines**, crie o Job `academia-medalhao` e adicione:

| Task name | Notebook | Depends on |
|---|---|---|
| `extrair` | `01_extrair_landing` | nenhuma |
| `bronze` | `02_landing_bronze` | `extrair` |
| `silver` | `03_bronze_silver` | `bronze` |
| `gold` | `04_silver_gold` | `silver` |
| `validar` | `05_validar` | `gold` |

Em todas as tarefas, use **Serverless**, **Run if: All succeeded** e o parâmetro
`catalogo` com valor `workspace` (ou seu catálogo). Configure uma execução simultânea do Job.

Clique em **Run now**. O notebook `00_configurar` não entra no Job.

> [!WARNING]
> A execução substitui as tabelas do projeto no catálogo informado.
> Use um ambiente dedicado e não inicie execuções simultâneas.

---

## Problemas comuns

| Erro | Como resolver |
|---|---|
| `No module named mkdocs` | ative `.venv` e instale `requirements-docs.txt` |
| Volume ou schema não encontrado | confira `catalogo` e execute `00_configurar` |
| `academia.db` não encontrado | confira o upload no volume `origem.arquivos` |
| Hash diferente do manifesto | envie o banco e o manifesto da mesma geração |
| Tarefas em `Blocked` | confira se a tarefa anterior terminou com sucesso |
| Falha na validação | abra a saída da tarefa que falhou e siga o roteiro de testes no MkDocs |
| Falha de autenticação Git | confira sua autenticação e acesso ao repositório |
