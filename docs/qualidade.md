# Qualidade dos dados

## Normalização

A Silver remove espaços nas extremidades, converte vazios em nulos, padroniza email
para minúsculas, nome de aluno para capitalização de palavras e status/forma de
pagamento para maiúsculas. true, false, 1, 0, sim, nao e não são tratados como
representações de atividade antes da conversão booleana.

IDs são convertidos para inteiros; valores financeiros para decimal(12,2); datas e
timestamps para seus tipos correspondentes. try_cast transforma entradas incompatíveis
em nulos que são avaliados pelas regras de validade.

## Antes e depois de João

| Campo | Bronze | Silver |
|---|---|---|
| id_aluno | texto 301 | inteiro 301 |
| nome | `  João   da SILVA  ` | João Da Silva |
| email | `  JOAO.SILVA@EMAIL.COM  ` | joao.silva@email.com |
| cidade | `  Criciúma  ` | Criciúma |
| id_plano | ` 1 ` | inteiro 1 |
| ativo | sim | booleano true |

João permanece na Silver. Correção de formato é distinta de exclusão por violação
de regra. Seu check-in e pagamento também permanecem nas fatos.

## Regras

| Tabela | Regras principais |
|---|---|
| planos | ID único e positivo, nome, valor e duração positivos |
| unidades | ID único e positivo, nome, cidade e data de inauguração |
| alunos | ID único e positivo, nome, email sintático, matrícula, atividade e plano válido |
| checkins | ID único e positivo, data/hora, aluno e unidade válidos |
| pagamentos | ID único e positivo, competência no primeiro dia, valor positivo, domínios e aluno válidos |

Pagamentos PAGO requerem data; PENDENTE e ATRASADO requerem ausência dela.
Formas permitidas: PIX, CARTAO e BOLETO. Todas as ocorrências de uma PK duplicada
são rejeitadas. As referências são verificadas contra pais válidos, propagando
rejeições para filhos órfãos.

## Quarentena e auditoria

As rejeições conservam o registro original em JSON e um motivo. As tabelas
quarentena_alunos, quarentena_checkins e quarentena_pagamentos terão registros na
base de demonstração; quarentena vazia não é o objetivo desta versão.

**bronze = silver + rejeitados**

O notebook 05 aceita somente as quantidades de rejeição previstas no contrato.
Rejeições adicionais, perdas e multiplicações causam falha na validação.
