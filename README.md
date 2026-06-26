# 🍽️ AI Food Audit Assistant

> Um assistente inteligente para auditorias de Qualidade e Segurança de Alimentos utilizando Inteligência Artificial Local (Qwen GGUF) executando no Google Colab.

---

# Visão Geral

O **AI Food Audit Assistant** é um projeto demonstrativo que une **Ciência de Dados**, **Engenharia de IA**, **Large Language Models (LLMs)** e **Auditoria da Qualidade** para transformar planilhas de auditoria em análises inteligentes.

Ao invés de apenas calcular indicadores estatísticos, o sistema utiliza um modelo de linguagem **Qwen 2.5 GGUF** executado localmente para interpretar os resultados e produzir análises semelhantes às realizadas por um auditor experiente.

Todo o projeto pode ser executado no **Google Colab**, sem necessidade de serviços externos de IA.

---

# Objetivos

Este projeto demonstra como integrar um modelo de linguagem (LLM) a um fluxo tradicional de análise de dados.

O sistema é capaz de:

- Ler planilhas CSV de auditoria.
- Tratar e normalizar os dados.
- Calcular indicadores de desempenho.
- Identificar não conformidades.
- Encontrar padrões recorrentes.
- Detectar setores críticos.
- Detectar categorias críticas.
- Construir automaticamente o contexto da auditoria.
- Utilizar IA para interpretar os resultados.
- Gerar recomendações técnicas.
- Responder perguntas em linguagem natural.

---

# Arquitetura

```

CSV
│
▼

Pandas

│

├── Limpeza

├── Normalização

├── Estatísticas

├── Indicadores

└── Contexto

│
▼

Qwen 2.5 GGUF

(llama.cpp)

│

├── Resumo Executivo

├── Análise Técnica

├── Plano de Ação

├── Recomendações

└── Perguntas em linguagem natural

│
▼

Dashboard + Relatórios

```

---

# Fluxo de Execução

1. Upload do arquivo CSV.
2. Validação da estrutura da planilha.
3. Limpeza dos dados.
4. Conversão de datas.
5. Padronização de textos.
6. Cálculo dos indicadores.
7. Identificação de padrões.
8. Construção do contexto.
9. Envio do contexto para o Qwen.
10. Geração dos textos técnicos.
11. Criação do dashboard.
12. Exportação dos resultados.

---

# Recursos

## Estatísticas

- Percentual de conformidade
- Quantidade de não conformidades
- Setores mais críticos
- Categorias mais críticas
- Evolução mensal
- Ranking de ocorrências
- Itens recorrentes

---

## Inteligência Artificial

O projeto utiliza um modelo **Qwen GGUF** executado localmente através do **llama.cpp**.

A IA é utilizada para:

- Interpretar indicadores.
- Produzir resumo executivo.
- Gerar análise técnica.
- Priorizar riscos.
- Elaborar plano de ação.
- Responder perguntas sobre a auditoria.

Exemplos:

> Qual setor apresenta maior risco?

> Existe algum padrão de não conformidades?

> Qual ação corretiva deve ser priorizada?

> O índice de conformidade está aceitável?

> Quais tendências podem ser observadas?

---

# Tecnologias

## Linguagem

- Python 3

## Ciência de Dados

- Pandas

## Visualização

- Matplotlib
- Seaborn

## IA

- Qwen 2.5 GGUF
- llama-cpp-python

## Distribuição

- Google Colab

---

# Estrutura do Projeto

```

AI_Food_Audit_Assistant

│

├── data/

│

├── models/

│

├── outputs/

│ ├── dashboards/

│ ├── relatórios/

│ └── csv/

│

├── prompts.py

├── food_audit.py

├── config.py

├── utils.py

├── AI_Food_Audit_Assistant_Colab.ipynb

└── requirements.txt

```

---

# Exemplo de Pipeline de IA

```

Upload CSV

↓

Tratamento dos Dados

↓

Indicadores

↓

Contexto

↓

Qwen

↓

Resumo Executivo

↓

Análise Técnica

↓

Plano de Ação

↓

Dashboard

↓

Relatório

```

---

# Casos de Uso

Este projeto pode ser adaptado para:

- Segurança de Alimentos
- BPF
- HACCP
- ISO 22000
- FSSC 22000
- Auditorias Internas
- Auditorias de Fornecedores
- Auditorias Industriais
- Qualidade em Produção
- Controle Sanitário

---

# Possíveis Evoluções

O projeto foi desenvolvido de forma modular para facilitar futuras expansões.

Algumas possibilidades:

- RAG utilizando documentos internos.
- Consulta de procedimentos em PDF.
- Geração automática de planos CAPA.
- Exportação para PDF.
- Exportação para Word.
- Interface Web com Streamlit.
- API REST com FastAPI.
- Banco Vetorial (ChromaDB).
- Histórico de auditorias.
- Comparação entre auditorias.
- Dashboard em tempo real.
- Agente de IA para inspeções.
- Integração com Power BI.

---

# Objetivo do Projeto

Este projeto foi criado para demonstrar a integração entre **Ciência de Dados**, **Engenharia de IA** e **Modelos de Linguagem**, mostrando como um LLM pode atuar como um especialista capaz de interpretar resultados analíticos e gerar recomendações de alto valor para processos de auditoria da qualidade.

Ele serve como uma base para aplicações corporativas de inspeção, conformidade e suporte à decisão, podendo ser expandido para cenários reais em ambientes industriais.