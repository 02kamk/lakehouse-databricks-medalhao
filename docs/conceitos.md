# Fundamentos do trabalho

## Contexto

Trabalho 3 de Engenharia de Dados (SATC), continuidade dos trabalhos 1 e 2.
O cenário é uma academia com planos, unidades, alunos, check-ins e pagamentos.
O gerador e o modelo de origem vêm do trabalho 2. A origem escolhida aqui é SQLite,
permitida pelo enunciado. SQL Server e MinIO permanecem no projeto anterior.

## Lakehouse

Um Lakehouse combina armazenamento de dados em arquivos com recursos de gerenciamento
de tabelas e processamento analítico. Neste projeto, o Databricks fornece o ambiente
de processamento e governança; Delta Lake organiza as tabelas das camadas tratadas.

## Databricks e a experiência de plataforma gerenciada

O Ubuntu prepara a origem e a documentação. O processamento Spark acontece no Databricks,
em compute Serverless. O grupo usa notebooks, catálogo, volumes e orquestração sem
administrar a instalação do Spark nos servidores. Esse uso corresponde à experiência
de plataforma gerenciada solicitada no enunciado.

## Arquitetura Medalhão

- **Landing:** preserva a extração em CSV no volume landing.dados.
- **Bronze:** registra o conteúdo recebido em tabelas Delta, inicialmente textual, com data de ingestão.
- **Silver:** converte tipos e valida chaves, domínios e campos obrigatórios; conserva rejeições em quarentena.
- **Gold:** disponibiliza dimensões e fatos para consultas analíticas.

Essas responsabilidades ajudam a localizar erros e permitem comparar a origem com
os resultados tratados. As regras específicas estão em [Qualidade e modelagem](modelagem.md).

## Delta Lake e transações

Delta Lake utiliza arquivos de dados e um log transacional para gerenciar versões e
escritas consistentes em uma tabela. Cada escrita Delta tem sua própria transação;
isso não torna todas as tabelas e etapas do Job uma transação única. Em caso de falha
parcial, é preciso corrigir a causa e reexecutar o fluxo.

## Modelo dimensional

O projeto separa check-ins e pagamentos em duas fatos porque são eventos com grãos
distintos. Aluno, plano, unidade e tempo são dimensões. Há quatro dimensões e duas
fatos na Gold. O calendário tem papéis de competência e pagamento na fato financeira.

As dimensões são tipo 1 e as chaves técnicas derivam dos IDs da origem única.
O plano associado ao aluno é o plano atual, pois a origem não possui histórico contratual.
Essas simplificações e as medidas estão detalhadas em [Qualidade e modelagem](modelagem.md).

## Qualidade e resultados

O controle de qualidade deve explicar o destino de cada linha: bronze = silver + rejeitados.
O grupo confirmou zero rejeições na base original. A base contém quatro planos,
quatro unidades, 300 alunos, 7.684 check-ins e 2.156 pagamentos.

O Job completo foi executado pelo estudante, e uma captura mostrou as cinco tarefas
em sucesso. O estudante também confirmou o teste de reexecução. Os registros e limites
da evidência estão em evidencias/validacao-databricks.md no repositório.

## Limites

A solução usa carga completa por snapshot, não CDC ou carga incremental. O envio do
banco é manual, e não existe conexão em tempo real entre o workspace e o SQLite no WSL.
Receita recebida considera apenas pagamentos com status PAGO. Não se deve juntar
as duas fatos por aluno antes de somar receitas, pois as visitas poderiam multiplicar os valores.

## Referências

Consulte as [fontes e créditos](referencias.md).
