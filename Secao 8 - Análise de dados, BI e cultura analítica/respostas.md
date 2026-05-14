## Questão 8.1 — Dashboard de saúde operacional

### Indicadores propostos

| Indicador | Fórmula resumida | Racional | Frequência |
|---|---|---|---|
| Volume de aportes | COUNT(aportes) | Queda pode indicar problema operacional ou integração | Diária |
| Taxa de liquidação | Liquidados / total × 100 | Mede efetividade do processamento | Diária |
| Ticket médio | SUM(valor) / COUNT(aportes) | Ajuda a identificar variações atípicas | Diária |
| Taxa de erro por meio de pagamento | Falhas / total × 100 | Identifica problemas por canal | Diária |
| Tempo médio de liquidação | AVG(data_liquidacao - data_aporte) | Mede SLA operacional | Semanal |
| Aportes pendentes >24h | COUNT(aportes pendentes) | Identifica fila represada | Diária |
| Volume por segmento | SUM(valor) por segmento | Mostra origem do volume financeiro | Semanal |
| Taxa de rejeição | Rejeitados / total × 100 | Detecta falha operacional ou no PSP | Diária |

---

### Alertas automáticos

#### Alerta 1 — Queda de volume

- Regra:
  volume diário abaixo de 70% da média dos últimos 7 dias.

- Canal:
  Slack — `#operacoes-pagamentos`

---

#### Alerta 2 — Aportes represados

- Regra:
  mais de 10 aportes pendentes há mais de 24h.

- Canal:
  Slack + e-mail para gestão.

---

#### Alerta 3 — Taxa de erro elevada

- Regra:
  taxa de erro acima de 5% em janela de 1 hora.

- Canal:
  Slack — `#operacoes-pagamentos`

Premissa assumida:
Metabase conectado ao banco transacional com permissão para alertas via Slack e e-mail.

---

## Questão 8.2 — Outliers e ruído

Usaria z-score para identificar dias muito fora do padrão histórico e média móvel de 7 dias para reduzir efeito de sazonalidade semanal. Meu critério para diferenciar ruído de incidente é o impacto: se a queda aparece só em um meio de pagamento ou segmento, tende a ser comportamento normal. Se a queda é transversal em vários recortes ao mesmo tempo, trato como incidente operacional e inicio investigação imediata.

---

## Questão 8.3 — Conflito com stakeholder

Não entregaria apenas o recorte distorcido. Explicaria que o filtro altera a leitura do indicador e pode gerar decisões erradas no futuro. Como alternativa, entregaria os dois cenários: o dado oficial e o recorte solicitado como visão complementar, deixando claro no dashboard o que cada um representa. Também registraria a decisão por escrito para manter rastreabilidade da solicitação.