## Questão 9.1 — Cenário ao vivo

Primeiro verificaria no banco se os três aportes foram registrados no sistema. Isso ajuda a identificar rapidamente se o problema é de recebimento ou de processamento.

Em paralelo, validaria se existem outros aportes do domingo na mesma situação. Meu critério para considerar incidente sistêmico seria encontrar mais de 5 aportes pendentes de clientes distintos.

Se confirmar problema sistêmico, acionaria:
1. Engenharia — para validar o job de conciliação;
2. Liderança — para alinhamento operacional;
3. Time de Pagamentos — para validar recebimento junto ao PSP.

Também responderia imediatamente os clientes informando que o aporte está seguro e em investigação.

Escalaria para aprovação apenas ações com impacto amplo, como reprocessamento em lote ou comunicação massiva.

Premissa assumida:
Possuo acesso de leitura ao banco para investigação inicial sem depender da Engenharia.

---

## Questão 9.2 — 5 Whys

### Problema inicial
Job de conciliação do domingo falhou silenciosamente.

### 5 Whys

1. O job falhou sem notificação.
2. Não existia alerta configurado.
3. O monitoramento não foi definido antes do deploy.
4. O processo de deploy não exigia validação de observabilidade.
5. Não existia checklist mínimo de monitoramento para produção.

### Ação corretiva
Reprocessar os aportes afetados e confirmar liquidação para os clientes.

### Ação preventiva
Criar checklist obrigatório de deploy incluindo monitoramento e alerta de falha.

Premissa assumida:
A falha silenciosa indica ausência de alerta operacional, não ausência total de logs técnicos.

---

## Questão 9.3 — Post mortem blameless

Post mortem blameless é uma análise pós-incidente focada em entender quais falhas de processo, sistema ou monitoramento permitiram o problema acontecer, sem buscar culpados individuais.

### Elementos principais
- linha do tempo;
- impacto operacional;
- causa raiz;
- ação corretiva;
- ação preventiva.

Faria post mortem formal quando houver impacto direto ao cliente, quebra de SLA, risco financeiro ou possibilidade de recorrência do problema.

Premissa assumida:
A cultura blameless depende de apoio da liderança para funcionar de forma correta.