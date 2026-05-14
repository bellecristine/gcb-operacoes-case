# Seção 5 — APIs REST, webhooks e segurança

## Questão 5.1 — Polling versus webhook

Polling é quando sua aplicação vai ativamente buscar dados na API em intervalos regulares, independente de ter novidade ou não. Webhook é o inverso a API te avisa quando algo acontece, sem você precisar perguntar.

Dois cenários onde polling ainda faz sentido mesmo havendo webhook disponível:

1. Quando o webhook do fornecedor não tem garantia de reentrega — polling ajuda a evitar perda de eventos, porque você controla o que já processou.

2. Reconciliação periódica — mesmo usando webhook no dia a dia, um polling diário pode validar se os eventos recebidos batem com o que realmente existe no sistema parceiro.

---

## Questão 5.2 — Recebendo webhooks de PSP

Validação de schema e tipos:
Antes de qualquer processamento, valido se o payload possui os campos esperados e se os tipos estão corretos. Payload inválido retorna erro 400 imediatamente.

Idempotência baseada em event_id:
Antes de processar o evento verifico se o event_id já existe no banco. Se já existir, retorno 200 sem reprocessar.

Autenticação por assinatura HMAC:
Recalculo a assinatura usando a chave secreta compartilhada e comparo com o valor enviado no header da requisição.

Retry com resposta rápida:
Responderia 200 rapidamente ao PSP e deixaria o processamento principal acontecer de forma assíncrona para evitar timeout e reenvio desnecessário.

Logs básicos:
Também adicionaria logs com event_id, tipo do evento e resultado do processamento para facilitar troubleshooting.

Eventos fora de ordem:
Em cenários financeiros pode acontecer de um evento chegar antes de outro. Nesse caso eu evitaria descartar o evento imediatamente e manteria ele pendente para tentativa posterior.

Premissa assumida:
Considerei uma arquitetura com fila assíncrona disponível para processamento posterior dos eventos.

---

## Questão 5.3 — Validação de assinatura HMAC

Código separado no arquivo `validacao_hmac.py`.

Cuidados considerados:

1. Chave secreta via variável de ambiente, evitando hardcode no código.

2. Validação feita usando o payload bruto em bytes, sem alteração prévia.

3. Uso de `hmac.compare_digest` para comparação mais segura da assinatura.

Premissa assumida:
Considerei que o PSP envia a assinatura como hexdigest puro no header.

---

## Questão 5.4 — Versionamento de API externa

Tentaria centralizar as chamadas da API em um único módulo para evitar regra espalhada pelo sistema inteiro. Quando a API mudar, apenas esse módulo precisaria ser atualizado.

Também manteria testes simples validando os campos consumidos da API para detectar mudanças antes de chegar em produção.

Quando possível, manteria suporte temporário a duas versões da API durante a migração para reduzir risco operacional.

Premissa assumida:
Considerei APIs com versionamento explícito via URL, como `/v1` e `/v2`.