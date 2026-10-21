# Validação da versão Azure

Evidências fornecidas pelo grupo em 21/10/2026.

- Origem Azure carregada: planos=4, unidades=4, alunos=303, checkins=7686, pagamentos=2160.
- Job ID: 609219804361760.
- Run ID: 938325045572911.
- Todas as cinco tarefas em Succeeded; duração exibida de 4min27s.
- Auditoria: planos 4/4/0, unidades 4/4/0, alunos 303/301/2,
  checkins 7686/7685/1, pagamentos 2160/2157/3 (Bronze/Silver/rejeitados).
- Capturas: job.png, catalogo.png, auditoria.png, quarentena.png, joao.png,
  receita.png e visitas.png, em docs/assets/evidencias/.
- Capturas dos gráficos mostram a tarefa validar em sucesso.
- Nome e tipos de João visíveis; email Silver truncado e ativo fora da captura.

Os registros são baseados nas saídas e capturas do estudante. O assistente não
executou a conexão remotamente. Não há captura numérica do total financeiro;
R$ 168.550,74 é o valor de referência calculado offline, reconciliado pelo código
do notebook que concluiu com sucesso, não um número lido das barras.

Pendente: confirmar reexecução da versão Azure e limpeza 99 seguida de reconstrução.
