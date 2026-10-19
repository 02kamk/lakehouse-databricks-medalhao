# Qualidade dos dados

## Objetivo

A Silver separa dados válidos de registros que violam o contrato da base.
O processamento mantém uma trilha das rejeições para que a qualidade seja mensurável.

## Padronização e tipos

Espaços nas extremidades são removidos e textos vazios tornam-se nulos. Emails são
normalizados para minúsculas; status e formas de pagamento para maiúsculas.

| Informação | Tipo na Silver |
|---|---|
| Identificadores | inteiro |
| Valores financeiros | decimal(12,2) |
| Datas de cadastro e pagamento | date |
| Data e hora de visita | timestamp |
| Situação de atividade | boolean |

As conversões usam try_cast. Um valor incompatível torna-se nulo e é avaliado pelas
regras de obrigatoriedade e domínio, em vez de interromper a leitura inteira.

## Regras por tabela

| Tabela | Regras principais |
|---|---|
| planos | ID positivo e único, nome preenchido, valor e duração positivos |
| unidades | ID positivo e único, nome e cidade preenchidos, inauguração válida |
| alunos | ID positivo e único, nome e email válidos, matrícula e atividade válidas, plano existente |
| checkins | ID positivo e único, data/hora válida, aluno e unidade existentes |
| pagamentos | ID positivo e único, competência no primeiro dia do mês, valor positivo, aluno existente e domínios permitidos |

Em pagamentos, PAGO requer data de pagamento válida. PENDENTE e ATRASADO requerem
ausência dessa data. As formas permitidas são PIX, CARTAO e BOLETO.

## Duplicidade e referências

Todas as ocorrências de uma chave primária duplicada são rejeitadas. A regra evita
escolher arbitrariamente entre registros conflitantes. A verificação de email é
sintática básica; não comprova que o endereço existe.

Referências são verificadas contra os pais válidos. Um aluno rejeitado pode provocar
a rejeição de seus pagamentos e visitas por ausência de referência válida.

## Quarentena e auditoria

Cada tabela tem uma quarentena correspondente na Silver. Ela conserva o registro
original em JSON e um motivo geral de rejeição. A tabela auditoria_qualidade registra
as contagens da Bronze, da Silver e das rejeições.

**bronze = silver + rejeitados**

Essa igualdade garante a reconciliação das linhas processadas. O motivo armazenado
é geral; detalhar cada regra violada é uma possibilidade de evolução.

## Barreira final

A carga original teve zero rejeições, conforme confirmação do grupo. O notebook de
validação exige esse resultado para a base de referência. Em uma carga com rejeições,
a quarentena e a auditoria são gravadas, mas a validação final falha, sinalizando
necessidade de análise antes de aceitar os resultados.
