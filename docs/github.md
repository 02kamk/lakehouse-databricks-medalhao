# Novo GitHub e MkDocs

O PDF exige repositório separado. Nome sugerido: lakehouse-databricks-medalhao. Não altere os repositórios dos trabalhos 1 e 2.

1. Acesse GitHub autenticado em 02kamk, New repository, nome lakehouse-databricks-medalhao. Não inicialize README, licença ou gitignore: os arquivos já estão no pacote.
2. No Ubuntu, dentro de lakehouse-academia:

```bash
git init -b main
git add .
git status
git commit -m "Implementa lakehouse academia com Databricks e Medalhao"
git remote add origin https://github.com/02kamk/lakehouse-databricks-medalhao.git
git push -u origin main
```

Se o Git pedir identidade, configure git config user.name e git config user.email com seus dados. Para autenticar, use o fluxo oficial do GitHub CLI (`gh auth login`, se instalado) ou credencial/token no gerenciador de credenciais; a senha comum do GitHub não autentica git push. Não cole tokens nos arquivos. Confira git status antes do commit: .venv e academia.db não devem entrar. Os CSVs fictícios e manifesto podem entrar; o banco é reconstruível.

3. O workflow incluído verifica origem e documentação a cada push/PR. Consulte a aba Actions e espere verde. Ele não executa o Job no Databricks.
4. Para ver o site local:

```bash
source .venv/bin/activate
mkdocs serve
```

Abra http://127.0.0.1:8000 no Windows. Para publicar:

```bash
mkdocs build --strict
mkdocs gh-deploy
```

5. No GitHub, Settings -> Pages -> Deploy from a branch -> gh-pages -> /(root). Aguarde a publicação e copie a URL realmente exibida. Adicione essa URL ao README. A URL esperada, somente após publicar, é https://02kamk.github.io/lakehouse-databricks-medalhao/.
6. Grave no README o Run ID final do Databricks e guarde capturas em evidencias/ sem dados de login. Não confunda Actions verde com validação do processamento remoto.

O repositório remoto e o site não foram publicados automaticamente por este pacote. Esses passos dependem da conta do estudante.
