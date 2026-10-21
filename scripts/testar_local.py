"""Validação offline dos CSVs e dos casos de qualidade. Não conecta ao Azure/Spark."""
import ast,csv,re,json
from collections import Counter
from decimal import Decimal,InvalidOperation
from datetime import date,datetime
from pathlib import Path
from contrato import COLUNAS,CHAVES,ORIGEM,SILVER,REJEITADOS,INVALIDOS

R=Path(__file__).resolve().parents[1]

def cast(value,kind):
    if value is None:return None
    try:
        if kind=='int':return int(value)
        if kind=='decimal':
            n=Decimal(value)
            return n if n.is_finite() else None
        if kind=='date':return date.fromisoformat(value)
        if kind=='timestamp':return datetime.strptime(value,'%Y-%m-%d %H:%M:%S')
        if kind=='boolean':return {'true':True,'false':False,'1':True,'0':False,'sim':True,'nao':False,'não':False}.get(value.lower())
    except (ValueError,InvalidOperation):return None
    raise ValueError(kind)

TYPES={
 'planos':{'id_plano':'int','valor_mensal':'decimal','duracao_meses':'int'},
 'unidades':{'id_unidade':'int','data_inauguracao':'date'},
 'alunos':{'id_aluno':'int','id_plano':'int','data_matricula':'date','ativo':'boolean'},
 'checkins':{'id_checkin':'int','id_aluno':'int','id_unidade':'int','data_hora':'timestamp'},
 'pagamentos':{'id_pagamento':'int','id_aluno':'int','competencia':'date','data_pagamento':'date','valor':'decimal'}}

def normalize(t,row):
    r={k:v.strip() or None for k,v in row.items()}
    if t=='alunos':
        if r['nome']:r['nome']=' '.join(r['nome'].split()).title()
        if r['email']:r['email']=r['email'].lower()
    if t=='pagamentos':
        for c in ['status','forma_pagamento']:
            if r[c]:r[c]=r[c].upper()
    for c,typ in TYPES[t].items():r[c]=cast(r[c],typ)
    return r

def valid(t,r,parents):
    pk=r[CHAVES[t]]
    if pk is None or pk<=0:return False
    if t=='planos':return bool(r['nome'] and r['valor_mensal'] is not None and r['valor_mensal']>0 and r['duracao_meses'] is not None and r['duracao_meses']>0)
    if t=='unidades':return bool(r['nome'] and r['cidade'] and r['data_inauguracao'])
    if t=='alunos':return bool(r['nome'] and r['email'] and re.fullmatch(r'[^ @]+@[^ @]+[.][^ @]+',r['email']) and r['data_matricula'] and r['ativo'] is not None and r['id_plano'] in parents['planos'])
    if t=='checkins':return bool(r['data_hora'] and r['id_aluno'] in parents['alunos'] and r['id_unidade'] in parents['unidades'])
    if t=='pagamentos':return bool(r['competencia'] and r['competencia'].day==1 and r['valor'] is not None and r['valor']>0 and r['forma_pagamento'] in {'PIX','CARTAO','BOLETO'} and r['status'] in {'PAGO','PENDENTE','ATRASADO'} and ((r['status']=='PAGO' and r['data_pagamento'] is not None) or (r['status']!='PAGO' and r['data_pagamento'] is None)) and r['id_aluno'] in parents['alunos'])
    raise ValueError(t)

def main():
    parents={};good={};audit=[]
    for t,cols in COLUNAS.items():
        with (R/f'data/{t}.csv').open(encoding='utf-8',newline='') as f:
            reader=csv.DictReader(f);assert reader.fieldnames==cols,t
            raw=list(reader)
        assert len(raw)==ORIGEM[t],t
        rows=[normalize(t,r) for r in raw]
        occurrences=Counter(r[CHAVES[t]] for r in rows)
        # PK física no SQL exige unicidade na origem, mas o classificador trata duplicatas.
        assert all(n==1 for n in occurrences.values()),'PK duplicada na origem SQL'
        good[t]=[r for r in rows if valid(t,r,parents) and occurrences[r[CHAVES[t]]]==1]
        rejected={r[CHAVES[t]] for r in rows if not valid(t,r,parents)}
        assert rejected==INVALIDOS[t],(t,rejected)
        assert len(good[t])==SILVER[t]
        assert len(raw)==len(good[t])+len(rejected)
        parents[t]={r[CHAVES[t]] for r in good[t]}
        audit.append({'tabela':t,'origem':len(raw),'silver_esperada':len(good[t]),'rejeitados_esperados':len(rejected)})
    joao=next(r for r in good['alunos'] if r['id_aluno']==301)
    assert (joao['nome'],joao['email'],joao['ativo'])==('João Da Silva','joao.silva@email.com',True)
    # Casos negativos independentes da base: email, datas, valores, domínio e FK.
    template=joao.copy()
    for field,value in [('email','errado'),('data_matricula',None),('id_plano',999),('ativo',None),('nome',None)]:
        candidate=template|{field:value};assert not valid('alunos',candidate,parents),field
    assert cast('2024-02-30','date') is None
    assert cast('abc','decimal') is None
    assert cast('false','boolean') is False
    received=sum((r['valor'] for r in good['pagamentos'] if r['status']=='PAGO'),Decimal('0'))
    for p in list((R/'scripts').glob('*.py'))+list((R/'notebooks').glob('*.py')):
        ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
    assert len(list((R/'notebooks').glob('*.py')))==7
    # Segurança do contrato: nenhum literal de senha real nem segredo em arquivo versionado.
    assert (R/'.env.example').exists() and '.env' in (R/'.gitignore').read_text()
    report={'ambiente':'offline: Python; não é execução no Azure ou Spark','contagens':audit,'receita_recebida_esperada':str(received),'visitas_esperadas':len(good['checkins']),'joao':{k:str(v) for k,v in joao.items()}}
    out=R/'evidencias/contrato-local.json';out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    print('PASSOU: CSVs, casos válidos/inválidos, normalização do João, reconciliação e sintaxe dos sete notebooks.')
    print('PENDENTE: conexão Azure SQL e execução real dos notebooks no Databricks.')

if __name__=='__main__':main()
