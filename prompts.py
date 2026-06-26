SYSTEM_PROMPT = """Você é um auditor especialista em qualidade e segurança de alimentos.
Analise os dados com objetividade, indique riscos, priorize ações e responda em português."""

EXEC_SUMMARY_PROMPT = """Gere um resumo executivo em até 120 palavras com base nos indicadores abaixo.

Conformidade geral: {conformidade}%
Total de não conformidades: {nc_count}
Setor com mais NC: {top_sector}
Categoria com mais falhas: {top_category}
Itens recorrentes: {recorrentes}

Inclua riscos e uma leitura executiva do cenário.
"""

TECH_PROMPT = """Gere uma análise técnica em até 180 palavras com foco em:
- riscos críticos
- provável causa raiz
- ações imediatas
- prevenção

Pontos críticos:
{critical_issues}
"""

ACTION_PROMPT = """Crie um plano de ação prático com prioridade 1, 2 e 3, em até 120 palavras.

Use como base:
- Conformidade: {conformidade}%
- Setor crítico: {top_sector}
- Categoria crítica: {top_category}
- Itens recorrentes: {recorrentes}
"""

QA_CHAT_PROMPT = """Responda à pergunta usando somente o contexto da auditoria.

Pergunta: {pergunta}

Contexto:
{contexto}

Responda em português, de forma objetiva e útil, até 90 palavras.
"""
