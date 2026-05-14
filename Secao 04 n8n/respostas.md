# Seção 4 — n8n

## Questão 4.1 — Fluxo de solicitação de estorno

Optei por descrever o fluxo em formato textual porque não tenho ambiente n8n configurado atualmente. A ideia foi mostrar a lógica ponta a ponta do processo e os principais tratamentos de erro.

```text
FLUXO PONTA A PONTA — SOLICITAÇÃO DE ESTORNO

[1] TRIGGER
    Google Sheets — nova linha adicionada com "Solicitação de Estorno"

[2] CHECAR IDEMPOTÊNCIA
    Verificar se a linha já tem ID de card preenchido no Sheets
    → Se sim: encerrar fluxo sem reprocessar
    → Se não: continuar

[3] VALIDAR CPF
    HTTP Request → API interna de validação de CPF
    Timeout: 10s

    Em erro 5xx:
    → retry até 3x com intervalo de 5s

    Se timeout estourar:
    → atualizar linha com status "erro_validacao"
    → notificar canal #operacoes-estornos-erro

[4a] CPF INVÁLIDO
    → Atualizar linha no Sheets com status "invalido"
    → Enviar mensagem no Slack → canal #operacoes-invalidos
    → Encerrar fluxo

[4b] CPF VÁLIDO
    → Criar card no Pipefy na fase "Triagem"
    → Salvar ID retornado

[5] ATUALIZAR SHEETS
    → Gravar ID do card e status "triagem"

[6] NOTIFICAR SLACK
    → Canal #operacoes-estornos
    → Mensagem com link do card + resumo da solicitação

[FIM]
```

Premissa assumida:
Considerei que o trigger do Sheets dispara automaticamente quando a linha é salva e que a API retorna apenas um booleano indicando validade do CPF.

---

## Questão 4.2 — Idempotência e tolerância a falhas

### Cenário 1 — Trigger duplicado pelo Sheets

A primeira validação do fluxo verifica se a linha já possui ID de card preenchido. Se já existir, o fluxo encerra sem reprocessar.

Impacto residual:
Baixo. A checagem acontece antes das chamadas externas.

---

### Cenário 2 — Falha entre Pipefy e Sheets

Pode acontecer de o card ser criado mas o Sheets não ser atualizado.

Para reduzir risco de duplicidade, antes de criar um novo card eu consultaria o Pipefy usando o identificador da solicitação.

Se já existir card:
- não recria;
- apenas atualiza o Sheets.

Impacto residual:
Baixo, desde que a consulta exista antes da criação.

---

### Cenário 3 — Falha do Slack

Nesse caso a etapa operacional já foi concluída porque o card existe no Pipefy.

O Slack foi tratado como notificação acessória.

Uma rotina separada poderia reenviar notificações pendentes posteriormente.

Impacto residual:
Possível atraso na comunicação do time.

---

## Questão 4.3 — Limites e alternativas do n8n

Meu contato com n8n foi mais exploratório do que operacional em produção, então considerei limitações mais gerais que observei em testes e documentação.

### Limitação 1 — Concorrência

Fluxos muito grandes ou muitas execuções simultâneas podem acumular e deixar workers lentos.

Em cenários maiores eu avaliaria ferramentas com controle de fila mais robusto.

---

### Limitação 2 — Observabilidade

Os logs ajudam, mas senti falta de métricas mais estruturadas para acompanhar falhas e volume de execução em tempo real.

---

### Limitação 3 — Processamento pesado

Manipular arquivos grandes ou muitas transformações dentro do fluxo pode deixar o n8n lento e instável.

Nesses casos eu deixaria o n8n apenas para orquestração simples e moveria o processamento para Python.

Premissa assumida:
Considerei ambiente self-hosted e uso operacional básico do n8n.

---

## Observações

Meu contato com n8n foi mais focado em testes e estudos de automação simples, não em operações grandes em produção.

Algumas decisões descritas acima foram baseadas em documentação e conceitos gerais de integração/eventos.

Dúvidas que ficaram em aberto:
- Melhor estratégia de monitoramento em fluxos muito grandes;
- Limites práticos de concorrência;
- Estratégias mais robustas de fila e retry.