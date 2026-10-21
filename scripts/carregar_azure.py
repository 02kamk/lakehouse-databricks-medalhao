"""Cria e carrega as cinco tabelas dbo em um Azure SQL Database já provisionado.

Sem DROP DATABASE, sem apagar tabelas externas e com transação única da carga.
Colunas de negócio são texto para preservar os casos inválidos da demonstração.
"""
import argparse,csv,os,sys
from pathlib import Path
from contrato import COLUNAS,CHAVES,ORIGEM

def brace(value):
    return '{'+str(value).replace('}','}}')+'}'

def main():
    import pyodbc
    from dotenv import load_dotenv
    parser=argparse.ArgumentParser()
    parser.add_argument('--somente-testar',action='store_true')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    load_dotenv(root/'.env',override=False,interpolate=False)
    def env(k):
        v=os.getenv(k,'').strip()
        if not v or 'SEU_' in v or v=='PREENCHA_LOCALMENTE': raise ValueError(f'Preencha {k} no .env')
        return v
    host=env('AZURE_SQL_HOST');db=env('AZURE_SQL_DATABASE');user=env('AZURE_SQL_USER')
    password=os.getenv('AZURE_SQL_PASSWORD','')
    if not password or password=='PREENCHA_LOCALMENTE': raise ValueError('Preencha AZURE_SQL_PASSWORD no .env')
    import re
    if not re.fullmatch(r'[A-Za-z0-9-]+\.database\.windows\.net',host): raise ValueError('Host deve ser o FQDN do Azure, sem https://')
    port=int(os.getenv('AZURE_SQL_PORT','1433'))
    connstr='DRIVER={ODBC Driver 18 for SQL Server};SERVER='+brace(f'tcp:{host},{port}')+';DATABASE='+brace(db)+';UID='+brace(user)+';PWD='+brace(password)+';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    batches={}
    if not args.somente_testar:
        for t,cols in COLUNAS.items():
            with (root/f'data/{t}.csv').open(encoding='utf-8',newline='') as f:
                reader=csv.DictReader(f)
                if reader.fieldnames!=cols: raise ValueError(f'Colunas diferentes do contrato: {t}')
                rows=[tuple(r[c] for c in cols) for r in reader]
            if len(rows)!=ORIGEM[t]: raise ValueError(f'Contagem inválida: {t}; gere e teste os CSVs primeiro')
            batches[t]=rows
    with pyodbc.connect(connstr,autocommit=False) as conn:
        cur=conn.cursor()
        name=cur.execute('SELECT DB_NAME()').fetchone()[0]
        if name.lower()!=db.lower(): raise RuntimeError('Banco conectado diferente do solicitado')
        print('CONEXAO AZURE SQL OK')
        if args.somente_testar:return
        existing={(r[0],r[1]) for r in cur.execute("SELECT s.name,t.name FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id WHERE t.is_ms_shipped=0")}
        allowed={('dbo',t) for t in COLUNAS}
        if existing-allowed: raise RuntimeError('Use banco dedicado: há tabelas fora das cinco tabelas acadêmicas')
        if existing:
            if input('As cinco tabelas acadêmicas serão recarregadas. Digite SIM: ').strip()!='SIM':
                raise RuntimeError('Carga cancelada')
        for t,cols in COLUNAS.items():
            pk=CHAVES[t]
            defs=[f'[{c}] INT NOT NULL PRIMARY KEY' if c==pk else f'[{c}] NVARCHAR(500) NULL' for c in cols]
            cur.execute(f"IF OBJECT_ID(N'dbo.{t}',N'U') IS NULL CREATE TABLE [dbo].[{t}] ("+','.join(defs)+')')
            actual=[r[0] for r in cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='dbo' AND TABLE_NAME=? ORDER BY ORDINAL_POSITION",t)]
            if actual!=cols: raise RuntimeError(f'Estrutura incompatível na tabela {t}')
        for t in reversed(COLUNAS):cur.execute(f'DELETE FROM [dbo].[{t}]')
        for t,cols in COLUNAS.items():
            cur.executemany(f'INSERT INTO [dbo].[{t}] ('+','.join(f'[{c}]' for c in cols)+') VALUES ('+','.join('?' for _ in cols)+')',batches[t])
            n=cur.execute(f'SELECT COUNT(*) FROM [dbo].[{t}]').fetchone()[0]
            if n!=ORIGEM[t]: raise RuntimeError(f'Contagem divergente em {t}')
            print(f'{t}: {n}')
        conn.commit()
    print('CARGA AZURE CONCLUIDA. A origem permanece disponível após a limpeza do Databricks.')

if __name__=='__main__':
    try:main()
    except Exception as exc:
        # Não imprimir connection strings/credenciais em logs ou capturas.
        msg=str(exc)
        pw=os.getenv('AZURE_SQL_PASSWORD','')
        if pw:msg=msg.replace(pw,'[REDACTED]')
        print(type(exc).__name__+': '+msg,file=sys.stderr)
        sys.exit(1)
