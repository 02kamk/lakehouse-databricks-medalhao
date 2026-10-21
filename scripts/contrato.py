"""Contrato da base acadêmica. Sem credenciais ou dependências externas."""
COLUNAS={
 'planos':['id_plano','nome','valor_mensal','duracao_meses'],
 'unidades':['id_unidade','nome','cidade','bairro','data_inauguracao'],
 'alunos':['id_aluno','nome','email','cidade','id_plano','data_matricula','ativo'],
 'checkins':['id_checkin','id_aluno','id_unidade','data_hora'],
 'pagamentos':['id_pagamento','id_aluno','competencia','data_pagamento','valor','forma_pagamento','status']}
CHAVES={t:cols[0] for t,cols in COLUNAS.items()}
ORIGEM={'planos':4,'unidades':4,'alunos':303,'checkins':7686,'pagamentos':2160}
SILVER={'planos':4,'unidades':4,'alunos':301,'checkins':7685,'pagamentos':2157}
REJEITADOS={t:ORIGEM[t]-SILVER[t] for t in COLUNAS}
INVALIDOS={'planos':set(),'unidades':set(),'alunos':{302,303},'checkins':{7686},'pagamentos':{2158,2159,2160}}
