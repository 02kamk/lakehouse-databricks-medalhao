# Lakehouse com Databricks e Azure SQL Database

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Azure SQL](https://img.shields.io/badge/Azure_SQL-origem_externa-0078D4)
![Databricks](https://img.shields.io/badge/Databricks-Free_Edition-FF3621?logo=databricks&logoColor=white)

> 📘 **[Documentação do trabalho (MkDocs)](https://02kamk.github.io/lakehouse-databricks-medalhao/)**

**Integrantes:** Kamily Hilário das Luzes · Kauã Lucas Alves Barbosa

Instruções de instalação, criação do banco externo, configuração e execução.

## Tecnologias e requisitos

| Componente | Uso / requisito |
|---|---|
| Ubuntu 24.04 no WSL2 | comandos locais; outras versões suportadas exigem o repositório Microsoft correspondente |
| Python 3.10+ e venv | geração e carga dos CSVs |
| ODBC Driver 18 + pyodbc 5.2.0 | conexão local ao Azure SQL com TLS |
| python-dotenv 1.1.1 | configuração local ignorada pelo Git |
| Azure SQL Database | banco relacional externo, com autenticação SQL |
| Databricks Free Edition | Spark Serverless, volumes, Delta e Job |
| Conector SQLSERVER | leitura externa nativa do Spark; usa parâmetros jdbc_*; sem Maven no Serverless |
| Matplotlib | gráficos no notebook 05; normalmente disponível no ambiente Databricks |
| MkDocs 1.6.1 + Material 9.7.7 | documentação do trabalho |

## 1. Aplicar a atualização

Os comandos são no Ubuntu, na raiz do projeto. Salve alterações locais antes do pull.

```bash
cd ~/projetos/lakehouse-academia
git status
git pull --ff-only
unzip -o /mnt/c/Users/kamil/Downloads/ajustes-final.zip
git rm --ignore-unmatch scripts/preparar_origem.py data/origem_manifest.json
git rm --ignore-unmatch docs/apresentacao.md docs/instalacao.md docs/execucao.md docs/github.md docs/conceitos.md
```

O ZIP tem os arquivos na raiz para sobrepor o projeto. Ajuste apenas o caminho do
ZIP caso tenha sido salvo em outra pasta. O banco SQLite local antigo deixa de ser
usado; não é preciso apagá-lo para aplicar a migração. Não envie .env ao GitHub.

## 2. Criar um Azure SQL Database externo

### Conta e assinatura

1. Entre em https://portal.azure.com com sua conta Microsoft.
2. Pesquise **Assinaturas / Subscriptions** e confira se existe uma assinatura ativa.
3. Se não houver, ative uma oferta elegível da sua conta ou use o banco liberado pelo professor.
   O banco não é criado apenas por ter conta Microsoft. Não é necessário comprar uma VM.

### Recurso SQL Database

1. Abra https://aka.ms/azuresqlhub e procure **Start free / Iniciar gratuitamente**, quando disponível.
2. Em **Create SQL Database**, confirme **Free offer applied / Oferta gratuita aplicada**.
3. Selecione a assinatura e crie o grupo de recursos `rg-academia-trabalho3`.
4. Nome do banco: `academia_lakehouse`. Use um banco dedicado, vazio, sem tabelas de outros projetos.
5. Em **Server / Servidor**, clique em **Create new**. Escolha um nome globalmente único,
   por exemplo `academia-kamily-<sufixo>`, e uma região disponível próxima ao seu uso.
6. Escolha autenticação SQL ou SQL + Microsoft Entra. Defina login `academiaadmin` e uma senha forte própria.
7. Na opção de limite gratuito, escolha **Auto-pause the database until next month**.
   Confira custo estimado zero e a oferta aplicada antes de clicar em **Review + create → Create**.
   Se a oferta não estiver disponível, confira o preço e a assinatura antes de provisionar.
8. Depois da implantação, anote o FQDN do servidor (`NOME.database.windows.net`), o banco e o usuário.
   A senha será preenchida apenas no .env local e na configuração privada da conexão/Job.

O script de carga cria as tabelas e insere os dados; não é necessário criar tabelas
manualmente no portal. A carga não cria a assinatura ou o recurso SQL Database.

### Networking

1. No recurso do servidor SQL, abra **Networking → Public access**.
2. Permita acesso público por redes selecionadas e use **Add your client IPv4 address** para o Ubuntu.
3. Se o laboratório exigir a regra temporária para o Databricks sem IP fixo, adicione uma regra
   como `DatabricksLaboratorio`, início `0.0.0.0`, fim `255.255.255.255` e salve.
4. Essa faixa permite tentativas de conexão de qualquer IPv4. Utilize somente o banco fictício,
   autenticação SQL e remova a regra ampla ao terminar a atividade.
5. **Allow Azure services** é outra regra: `0.0.0.0 → 0.0.0.0`; não é equivalente à faixa acima.
6. O firewall Azure não remove restrições de saída da Free Edition. A conexão deve ser
   testada no notebook 01 antes de executar o Job inteiro. Se houver bloqueio do workspace,
   use um workspace permitido pelo professor; não substitua silenciosamente a extração por upload manual.

## 3. Instalar as dependências no Ubuntu

```bash
sudo apt update
sudo apt install -y git curl ca-certificates unzip python3 python3-venv python3-pip unixodbc unixodbc-dev
```

Se o ODBC Driver 18 ainda não estiver instalado, no Ubuntu 24.04:

```bash
curl -fsSL https://packages.microsoft.com/config/ubuntu/24.04/packages-microsoft-prod.deb -o /tmp/packages-microsoft-prod.deb
sudo dpkg -i /tmp/packages-microsoft-prod.deb
sudo apt update
sudo ACCEPT_EULA=Y apt install -y msodbcsql18
odbcinst -q -d
```

Confira a presença de `[ODBC Driver 18 for SQL Server]`.

```bash
cd ~/projetos/lakehouse-academia
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-docs.txt -r requirements-origem.txt
```

## 4. Configurar e carregar a origem externa

```bash
cp -n .env.example .env
nano .env
```

Preencha somente no arquivo local:

```dotenv
AZURE_SQL_HOST=SEU_SERVIDOR.database.windows.net
AZURE_SQL_DATABASE=academia_lakehouse
AZURE_SQL_USER=academiaadmin
AZURE_SQL_PASSWORD="SUA_SENHA"
AZURE_SQL_PORT=1433
```

No nano: Ctrl+O, Enter, Ctrl+X. Não publique a senha nem fotografe a tela de configuração.
Depois:

```bash
python scripts/gerar_dados.py
python scripts/testar_local.py
python scripts/carregar_azure.py --somente-testar
python scripts/carregar_azure.py
```

Se já houver tabelas acadêmicas, o script pedirá SIM antes de recarregá-las.
Ele rejeita bancos com outras tabelas de usuário e usa transação para a carga.

Saída final esperada:

```text
planos: 4
unidades: 4
alunos: 303
checkins: 7686
pagamentos: 2160
```

No **Query editor** do Azure, conectado ao seu banco, pode conferir:

```sql
SELECT 'planos' tabela, COUNT(*) linhas FROM dbo.planos
UNION ALL SELECT 'unidades',COUNT(*) FROM dbo.unidades
UNION ALL SELECT 'alunos',COUNT(*) FROM dbo.alunos
UNION ALL SELECT 'checkins',COUNT(*) FROM dbo.checkins
UNION ALL SELECT 'pagamentos',COUNT(*) FROM dbo.pagamentos;
```

## 5. Atualizar os notebooks e o Job

1. Exporte ou guarde os notebooks anteriores se quiser preservar o ensaio SQLite.
2. Substitua os notebooks da pasta do projeto pelos **sete** da pasta notebooks deste pacote.
3. Execute `00_configurar` com o mesmo catálogo do Job.
4. No Job `academia-medalhao`, confira os caminhos dos notebooks importados.
5. Em **Job parameters**, configure:

| Chave | Valor |
|---|---|
| catalogo | workspace, ou seu catálogo |
| jdbc_host | FQDN do servidor Azure, sem https:// |
| jdbc_database | academia_lakehouse |
| jdbc_user | usuário SQL |
| jdbc_password | senha na configuração privada, ou secret:ESCOPO:CHAVE |

Parâmetros comuns de Job são texto, não um cofre. Se houver Secret Scope disponível,
o formato secret:ESCOPO:CHAVE faz o notebook buscar a senha com dbutils.secrets.
Não coloque credenciais no JSON versionado, código ou capturas. Os notebooks não imprimem a senha.

Teste primeiro `01_extrair_landing` com esses parâmetros. O conector é SQLSERVER nativo,
sem upload de banco ou CSV. Se receber erro de rede, permissões ou conector, guarde o erro
sem credenciais. A conexão remota ainda precisa ser validada na sua conta.

Mantenha a sequência do Job:

| Tarefa | Notebook | Depends on |
|---|---|---|
| extrair | 01_extrair_landing | nenhuma |
| bronze | 02_landing_bronze | extrair |
| silver | 03_bronze_silver | bronze |
| gold | 04_silver_gold | silver |
| validar | 05_validar | gold |

Use Serverless, Run if All succeeded e concorrência 1. O setup 00 e a limpeza 99 ficam fora do Job.
Em caso de ModuleNotFoundError de matplotlib no 05, adicione `matplotlib==3.9.2` às dependências
do ambiente Serverless usado pelo notebook/tarefa e repita o ensaio.

## 6. Evidências e publicação pelo grupo

Guarde os prints em `docs/assets/evidencias/` com estes nomes, se quiser exibi-los no site:
`job.png`, `catalogo.png`, `auditoria.png`, `quarentena.png`, `receita.png`, `visitas.png`, `joao.png`.
O notebook 03 exibe antes/depois de João e as quarentenas; o 05 exibe as tabelas e gráficos.
Não capture Job parameters com a senha visível. A documentação inicialmente mostra links
para os locais das evidências, sem fingir que capturas reais já existem.

Depois de adicionar suas imagens, acrescente os embeds no arquivo docs/evidencias.md,
conforme os comentários internos, e publique:

```bash
python -m mkdocs build --strict
git add -A
git status
git commit -m "Banco de origem no Azure SQL, data quality e notebook de limpeza"
git push origin main
python -m mkdocs gh-deploy --strict
```

Confira que .env não aparece entre os arquivos preparados para commit.

## 7. Limpeza antes da apresentação

Depois de testar o novo Job completo, abra `99_limpar`, confira o catálogo e coloque
**SIM** em `confirmar`. Execute tudo. A limpeza apaga apenas as saídas acadêmicas
enumeradas em Bronze, Silver e Gold e os CSVs/manifesto da Landing. Ela preserva os
schemas e **não conecta, altera ou apaga o banco Azure**.

Na apresentação, execute o Job para reconstruir as camadas a partir do banco externo.
Não inclua 99 como tarefa automática. Os prints e o último ensaio devem ser guardados antes da limpeza.

## Problemas comuns

| Erro | Verificação |
|---|---|
| assinatura não encontrada | recurso Assinaturas no portal; conta/tenant e status da assinatura |
| ODBC Driver 18 não encontrado | odbcinst -q -d e instalação Microsoft compatível com seu Ubuntu |
| login failed | autenticação SQL habilitada, usuário e banco corretos |
| timeout/firewall | FQDN, TCP 1433, regra do cliente e conectividade de saída do Databricks |
| inventário fora do contrato | usar banco dedicado com exatamente as cinco tabelas |
| .env sem valores | preencher host, banco, usuário e senha localmente |
| Secret Scope não encontrado | conferir escopo/chave ou configurar autenticação privada disponível no laboratório |
| antiga validação exige zero rejeitados | reimportar o novo notebook 05; a nova base possui rejeições intencionais |
| task aponta para notebook antigo | corrigir Path nas cinco tarefas |
| confirmar diferente de SIM | limpeza não é executada |
