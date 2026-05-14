# Seção 3 — Python e Code Review

## Questão 3.1 — Merge com tolerância de data

A lógica usada foi conciliar aportes internos com transações PIX usando CPF + valor como chave principal, aplicando tolerância de D±1 na data para lidar com diferenças operacionais de liquidação.

Antes do merge:
- padronizei datas;
- removi duplicidades óbvias no lado PIX;
- e depois filtrei apenas os casos com diferença de até 1 dia.

Os registros conciliados e não conciliados foram separados para facilitar análise operacional posterior.

Premissa assumida:
Considerei CPF + valor suficientes para a conciliação operacional.

---

## Questão 3.2 — Consumo de API paginada

A estratégia foi consumir a API página por página com retry para erros temporários como timeout, conexão e status 5xx.

Também considerei:
- controle de rate limit;
- prevenção de duplicidade por ID;
- e encerramento da execução após muitas falhas consecutivas.

Os dados são salvos incrementalmente para evitar perda de progresso em caso de interrupção.

Premissa assumida:
Considerei que a API retorna IDs únicos e paginação estável.

---

## Questão 3.3 — Code Review

Os principais problemas identificados no código original foram:
- taxas hardcoded diretamente na lógica;
- ausência de tratamento de erro;
- excesso de if/elif;
- e falta de tipagem/documentação.

Na refatoração:
- centralizei as taxas em um dicionário;
- adicionei tratamento de exceções;
- simplifiquei a lógica;
- e incluí type hints e docstring para melhorar manutenção.

Premissa assumida:
Itens com classe desconhecida mantêm o valor original.