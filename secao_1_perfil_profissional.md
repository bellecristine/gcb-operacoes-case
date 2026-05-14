# Seção 1 — Perfil profissional e contexto técnico

## Questão 1.1 — Automação em produção

O fundo não tinha visibilidade confiável sobre sua composição de faturamento por categoria: os números existiam, mas estavam dispersos em planilhas despadronizadas e em um sistema interno sem integração, exigindo consolidação manual que levava cerca de um mês para ser concluída período em que decisões eram tomadas com dados defasados.

Assumi o processo de ponta a ponta: extração dos dados do sistema interno via SQL, tratamento e normalização das planilhas recebidas (que chegavam sem padrão de estrutura) em Excel avançado, e construção de um dashboard automatizado em Power BI com atualização incremental. A principal decisão de arquitetura foi centralizar a camada de transformação no SQL antes de carregar no Power BI, evitando lógica de negócio espalhada no próprio dashboard.

O ganho principal foi reduzir o ciclo de atualização dos KPIs de faturamento de ~30 dias para ~7 dias, um ganho de 75% no tempo de disponibilidade da informação, com eliminação dos erros de consolidação manual.

O que faria diferente hoje: investiria mais tempo na etapa de governança das fontes — as planilhas desestruturadas foram o maior gargalo e seguiram sendo um risco. Definiria um schema mínimo obrigatório de entrada e automatizaria a validação antes da ingestão, provavelmente com Python + Great Expectations ou uma validação simples em SQL.