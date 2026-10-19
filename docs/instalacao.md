# Instalação no Ubuntu / WSL

## 1. Conferir o Ubuntu existente

Você já tem Ubuntu: não precisa reinstalá-lo. No PowerShell do Windows:

```powershell
wsl --list --verbose
```

Confira VERSION 2. Se sua distribuição se chama Ubuntu e aparece como versão 1: `wsl --set-version Ubuntu 2`. Use o nome exato exibido. Para uma máquina nova, o comando administrativo é `wsl --install -d Ubuntu-24.04`, seguido de reinicialização e criação de usuário Linux.

## 2. Instalar utilitários no Ubuntu

Todos os comandos seguintes, salvo indicação, são no terminal Ubuntu.

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git sqlite3 unzip
python3 --version
git --version
sqlite3 --version
mkdir -p ~/projetos
```

Este projeto usa a biblioteca sqlite3 que já vem no Python. Não precisa de Java, MinIO, Docker ou instalação local do Spark para o trabalho 3. Mantenha os ambientes dos trabalhos anteriores separados.

## 3. Colocar o projeto no Linux

Baixe o ZIP entregue no chat para Downloads. No Ubuntu, ajuste o caminho se necessário:

```bash
cd ~/projetos
unzip /mnt/c/Users/kamil/Downloads/lakehouse-academia.zip
cd lakehouse-academia
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-docs.txt
python scripts/gerar_dados.py
python scripts/preparar_origem.py
python scripts/testar_local.py
sqlite3 data/academia.db '.tables'
mkdocs build --strict
```

Se o ZIP estiver em outra pasta, ajuste apenas o argumento do unzip. Não execute comandos Python no PowerShell usando os caminhos do Ubuntu. Preserve a saída de preparar_origem.py: é a contagem exata de cada tabela.

## 4. Criar a conta Databricks

1. Abra https://www.databricks.com/learn/free-edition no navegador do Windows.
2. Escolha Free Edition, faça seu cadastro e verifique o e-mail. Escolha a oferta gratuita, conferindo as condições apresentadas na tela.
3. Entre no workspace. A Free Edition usa compute serverless e possui cotas; não procure criar um cluster Spark local ou configurar Java.
4. Abra um notebook Python e execute `spark.sql('SELECT current_catalog()').show()` e `spark.sql('SHOW CATALOGS').show()`.
5. Anote o catálogo que permite criar schemas. O valor padrão dos notebooks é workspace; altere o widget catalogo se o nome da sua conta for outro.

Não compartilhe senha, token ou código de autenticação. Login e aceite de termos devem ser realizados por você.

## 5. Importar notebooks e criar volumes

1. Em Workspace, crie a pasta lakehouse-academia/notebooks na sua área de usuário.
2. Use Import e selecione os arquivos notebooks/00_configurar.py a 05_validar.py. São notebooks no formato SOURCE Databricks, com separadores COMMAND.
3. Abra 00_configurar, conecte ao compute Serverless, ajuste catalogo e clique Run all.
4. Confirme no Catalog Explorer os schemas origem, landing, bronze, silver e gold. Em origem deve existir o volume arquivos, e em landing o volume dados.
5. Pelo Ubuntu, rode `explorer.exe .` para abrir a pasta do projeto no Windows. Em data, localize academia.db e origem_manifest.json.
6. No Databricks, New -> Add or upload data -> Upload files to a volume. Escolha /Volumes/SEU_CATALOGO/origem/arquivos e envie somente academia.db e origem_manifest.json.
7. Não use a opção Create table para o banco: ele deve ser um arquivo no volume. Não envie os CSVs diretamente à Bronze. O notebook 01 fará a extração.

Permissões necessárias: USE CATALOG, USE SCHEMA, CREATE SCHEMA quando aplicável, CREATE TABLE, CREATE VOLUME, READ VOLUME e WRITE VOLUME. Se houver erro de permissão, escolha seu catálogo permitido e confira o proprietário; não troque para DBFS root como atalho.
