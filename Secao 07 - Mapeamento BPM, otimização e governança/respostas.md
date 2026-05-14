# Seção 7 — BPM e Governança

## Questão 7.1 — Fluxo AS-IS

Fluxo atual representado no arquivo:
-  `fluxo_as_is.png`

### Principais gargalos
- Pendência documental depende do tempo de resposta do cliente;
- Consulta manual de CPF aumenta tempo operacional;
- Planilha manual gera retrabalho por erro de digitação.

### Pontos de falha
- Documento ilegível;
- Erro manual na Receita Federal;
- Critério subjetivo na validação;
- Erro de preenchimento na planilha.

### Quebra do SLA

O SLA de 24h quebra principalmente:
- quando o cliente demora a responder pendências;
- e quando retrabalhos manuais acumulam fila operacional.

### Capacidade operacional estimada

- Tempo médio: 25 min/cadastro
- Analistas: 3
- Capacidade estimada:
  `~57 cadastros/dia`
- Volume recebido:
  `~80 cadastros/dia`

Gap operacional:
`~23 cadastros/dia`

Premissa assumida:
Considerei jornada de 8h por analista.

---

## Questão 7.2 — Fluxo TO-BE e business case

Fluxo futuro representado no arquivo:
- `fluxo to be.png`

### Otimização 1 — Formulário estruturado

| Item | Valor |
|---|---|
| Ferramenta | Typeform ou formulário integrado |
| Ganho | Redução de retrabalho na entrada |
| Economia estimada | ~R$ 413/mês |
| Esforço | ~20h-pessoa |
| Risco | Resistência do cliente |

---

### Otimização 2 — Consulta automática de CPF

| Item | Valor |
|---|---|
| Ferramenta | API Receita Federal / Serpro |
| Ganho | Redução de ~5 min/cadastro |
| Economia estimada | ~R$ 1.800/mês |
| Esforço | ~40h-pessoa |
| Risco | Dependência de fornecedor |

---

### Otimização 3 — Integração automática

| Item | Valor |
|---|---|
| Ferramenta | n8n ou integração via API |
| Ganho | Eliminação de digitação manual |
| Economia estimada | ~R$ 825/mês |
| Esforço | ~60h-pessoa |
| Risco | Dependência de Engenharia |

---

## Resumo financeiro

| Item | Valor |
|---|---|
| Ganho mensal estimado | R$ 3.038/mês |
| Custo estimado | R$ 9.600 |
| Payback estimado | ~3,2 meses |

Premissa assumida:
Ganhos calculados de forma conservadora.

---

## Questão 7.3 — Governança e KPIs

| KPI | Meta | Frequência |
|---|---|---|
| SLA cumprido | ≥ 95% | Diária |
| Taxa de retrabalho | ≤ 1% | Diária |
| Tempo médio de triagem | ≤ 15 min | Semanal |
| Pendências respondidas em 24h | ≥ 70% | Semanal |

### Ritual de governança

Revisão semanal de 30 minutos acompanhando KPIs e gargalos operacionais.

Gatilhos de revisão:
- SLA abaixo de 90%;
- retrabalho acima de 3%.

Responsável:
analista sênior da operação com reporte mensal para liderança.