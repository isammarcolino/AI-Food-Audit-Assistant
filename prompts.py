"""
Templates de prompts para o modelo de IA local.
Usa Jinja2-style para injeção de dados.
"""

EXECUTIVE_SUMMARY_PROMPT = """
Você é um especialista em Qualidade e Segurança de Alimentos.
Analise os indicadores abaixo e gere um resumo executivo claro, técnico e direto.

INDICADORES:
- Conformidade Geral: {{ conformidade }}%
- Total de Não Conformidades: {{ nc_count }}
- Setor com mais NC: {{ top_sector }}
- Categoria com mais falhas: {{ top_category }}
- Itens recorrentes: {{ recorrentes }}

Escreva em português, em até 150 palavras.
Destaque riscos críticos e pontos positivos.
"""

TECHNICAL_ANALYSIS_PROMPT = """
Com base nos dados de auditoria, faça uma análise técnica detalhada.

PRINCIPAIS NC CRÍTICAS:
{{ critical_issues }}

RECOMENDAÇÕES:
- Ações imediatas
- Treinamentos necessários
- Melhorias estruturais

PLANO DE AÇÃO:
- Prioridades (1 a 3)
- Prazos sugeridos
- Responsáveis ideais

Use linguagem técnica, mas clara. Máximo 300 palavras.
"""

QA_CHAT_PROMPT = """
Você é um Auditor IA especialista em segurança de alimentos.
Responda à pergunta com base nos dados fornecidos.

PERGUNTA: {{ pergunta }}

DADOS:
{{ contexto }}

Responda com clareza, em português, em até 100 palavras.
"""
