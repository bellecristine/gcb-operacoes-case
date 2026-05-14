# Seção 2 — SQL avançado aplicado a dados operacionais

## Questão 2.1 — Volume por meio de pagamento

```sql
SELECT
    meio_pagamento,
    SUM(valor) AS volume_total,
    ROUND(
        100.0 * SUM(valor) / SUM(SUM(valor)) OVER (),
        2
    ) AS pct_participacao
FROM aportes
WHERE status = 'LIQUIDADO'
  AND DATE_TRUNC('month', data_aporte) = DATE_TRUNC('month', CURRENT_DATE)
GROUP BY meio_pagamento
ORDER BY volume_total DESC;

## Lógica

A window function SUM(SUM(valor)) OVER () calcula o total geral do mês sem necessidade de uma subquery separada, permitindo obter o percentual de participação de cada meio de pagamento de forma mais simples. O DATE_TRUNC garante que apenas registros do mês corrente sejam considerados.

## Questão 2.2 — Aportistas sem investimento

'''sql 
WITH aportes_recentes AS (
    SELECT
        a.id_aporte,
        a.id_cliente,
        a.data_aporte,
        a.valor AS valor_aporte
    FROM aportes a
    WHERE a.data_aporte >= CURRENT_DATE - INTERVAL '30 days'
),
sem_investimento AS (
    SELECT
        ar.id_aporte,
        ar.id_cliente,
        ar.data_aporte,
        ar.valor_aporte
    FROM aportes_recentes ar
    WHERE NOT EXISTS (
        SELECT 1
        FROM investimentos i
        WHERE i.id_cliente = ar.id_cliente
          AND i.data_investimento BETWEEN ar.data_aporte
                                      AND ar.data_aporte + INTERVAL '7 days'
    )
)
SELECT
    si.id_cliente,
    c.nome,
    si.data_aporte,
    si.valor_aporte,
    CURRENT_DATE - si.data_aporte AS dias_decorridos_desde_aporte
FROM sem_investimento si
JOIN clientes c
    ON c.id_cliente = si.id_cliente
ORDER BY si.data_aporte DESC;WITH aportes_recentes AS (
    SELECT
        a.id_aporte,
        a.id_cliente,
        a.data_aporte,
        a.valor AS valor_aporte
    FROM aportes a
    WHERE a.data_aporte >= CURRENT_DATE - INTERVAL '30 days'
),
sem_investimento AS (
    SELECT
        ar.id_aporte,
        ar.id_cliente,
        ar.data_aporte,
        ar.valor_aporte
    FROM aportes_recentes ar
    WHERE NOT EXISTS (
        SELECT 1
        FROM investimentos i
        WHERE i.id_cliente = ar.id_cliente
          AND i.data_investimento BETWEEN ar.data_aporte
                                      AND ar.data_aporte + INTERVAL '7 days'
    )
)
SELECT
    si.id_cliente,
    c.nome,
    si.data_aporte,
    si.valor_aporte,
    CURRENT_DATE - si.data_aporte AS dias_decorridos_desde_aporte
FROM sem_investimento si
JOIN clientes c
    ON c.id_cliente = si.id_cliente
ORDER BY si.data_aporte DESC;

##Lógica
Utilizei CTEs para separar a leitura dos aportes recentes da regra principal de negócio. O NOT EXISTS foi escolhido por ser uma abordagem boa para identificar ausência de registros relacionados sem risco de duplicidade.

## Questão 2.3 — Cohort de retenção

'''sql
WITH primeiro_aporte AS (
    SELECT
        id_cliente,
        MIN(data_aporte) AS data_primeiro_aporte,
        DATE_TRUNC('month', MIN(data_aporte)) AS cohort
    FROM aportes
    GROUP BY id_cliente
),
segundo_aporte AS (
    SELECT
        a.id_cliente,
        MIN(a.data_aporte) AS data_segundo_aporte
    FROM aportes a
    JOIN primeiro_aporte p
        ON p.id_cliente = a.id_cliente
    WHERE a.data_aporte > p.data_primeiro_aporte
    GROUP BY a.id_cliente
),
base AS (
    SELECT
        p.cohort,
        p.id_cliente,
        p.data_primeiro_aporte,
        s.data_segundo_aporte,
        s.data_segundo_aporte - p.data_primeiro_aporte AS dias_ate_segundo
    FROM primeiro_aporte p
    LEFT JOIN segundo_aporte s
        ON s.id_cliente = p.id_cliente
)
SELECT
    TO_CHAR(cohort, 'YYYY-MM') AS cohort,
    COUNT(*) AS total_clientes,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE dias_ate_segundo <= 30) / COUNT(*),
        1
    ) AS pct_retorno_30d,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE dias_ate_segundo <= 60) / COUNT(*),
        1
    ) AS pct_retorno_60d,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE dias_ate_segundo <= 90) / COUNT(*),
        1
    ) AS pct_retorno_90d
FROM base
GROUP BY cohort
ORDER BY cohort;

##Lógica

A consulta foi dividida em etapas usando CTEs para facilitar leitura e manutenção. A cláusula FILTER (WHERE ...) deixou os cálculos percentuais mais claros e legíveis do que múltiplos CASE WHEN dentro das agregações.

## Questão 2.4 — Análise de queda atípica

Começaria validando se a queda é real ou causada por atraso na ingestão de dados, comparando os horários esperados de entrada dos registros com os timestamps efetivamente recebidos.

Se os dados estiverem imparcial, investigaria as hipóteses em ordem de probabilidade:

Problema em um meio de pagamento específico, quebra por meio_pagamento.
Problema concentrado em determinado segmento de clientes, quebra por segmento e status_kyc.
Sazonalidade, comparação com médias das últimas semanas.
Queda concentrada em uma categoria de produto — quebra por classe.

Usaria SQL para validar rapidamente os volumes e o Metabase para visualizar tendências e desvios.

Como critério inicial, compararia o volume atual com o comportamento médio das últimas semanas para entender se está muito fora do padrão esperado. Em um cenário mais estruturado, utilizaria desvio-padrão para definir limites objetivos de alerta.

Escalaria para IT caso a queda aparecesse simultaneamente em múltiplos segmentos e meios de pagamento, indicando possível falha sistêmica.


##Questão 2.5 — Otimização de query

Principais problemas identificados
Uso de subqueries correlacionadas, gerando múltiplas leituras da tabela aportes.
Repetição de scans na mesma tabela para calcular métricas diferentes.
Possível custo elevado de ordenação devido a valores nulos em volume_total.
Versão otimizada

'''sql

SELECT
    c.nome,
    c.cpf,
    COALESCE(a.qtd_aportes, 0) AS qtd_aportes,
    COALESCE(a.volume_total, 0) AS volume_total,
    a.ultimo_aporte
FROM clientes c
LEFT JOIN (
    SELECT
        id_cliente,
        COUNT(*) AS qtd_aportes,
        SUM(
            CASE
                WHEN status = 'LIQUIDADO' THEN valor
                ELSE 0
            END
        ) AS volume_total,
        MAX(data_aporte) AS ultimo_aporte
    FROM aportes
    GROUP BY id_cliente
) a
    ON a.id_cliente = c.id_cliente
WHERE c.status_kyc = 'APROVADO'
ORDER BY volume_total DESC NULLS LAST;