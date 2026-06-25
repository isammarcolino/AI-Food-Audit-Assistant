"""
Módulo principal do AI Food Audit Assistant.
Orquestra análise de dados, geração de gráficos, relatórios e IA local.
"""
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
from typing import Dict, List
import logging

from config import *
from utils import logger, download_file
from llama_cpp import Llama
from prompts import EXECUTIVE_SUMMARY_PROMPT, TECHNICAL_ANALYSIS_PROMPT, QA_CHAT_PROMPT

# Inicializa o logger
logger = logging.getLogger(__name__)

class FoodAuditAnalyzer:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df: pd.DataFrame = None
        self.indicadores: Dict = {}

    def carregar_dados(self) -> bool:
        """Carrega e valida o CSV."""
        try:
            self.df = pd.read_csv(self.csv_path, encoding='utf-8')
            logger.info(f"Dados carregados: {len(self.df)} linhas")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar CSV: {e}")
            return False

    def limpar_dados(self):
        """Padroniza e limpa o DataFrame."""
        df = self.df.copy()

        # Normalização de texto
        for col in ['Setor', 'Auditor', 'Item auditado', 'Categoria', 'Observação', 'Ação corretiva', 'Responsável']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.title()

        # Tratamento de 'Conforme'
        df['Conforme'] = df['Conforme'].str.strip()
        df['Conforme_Numerico'] = df['Conforme'].apply(
            lambda x: 1 if x in CONFORME_VALUES else 0
        )

        # Prazo para datetime
        if 'Prazo' in df.columns:
            df['Prazo'] = pd.to_datetime(df['Prazo'], errors='coerce')

        self.df = df
        logger.info("Dados limpos e normalizados.")

    def gerar_indicadores(self):
        """Calcula métricas-chave."""
        df = self.df
        total = len(df)
        nc_count = len(df[df['Conforme_Numerico'] == 0])
        conformidade = ((total - nc_count) / total) * 100

        # Rankings
        setor_nc = df[df['Conforme_Numerico'] == 0]['Setor'].value_counts()
        categoria_nc = df[df['Conforme_Numerico'] == 0]['Categoria'].value_counts()

        # Itens recorrentes
        itens_recorrentes = df[df['Conforme_Numerico'] == 0]['Item auditado'].value_counts()
        recorrentes = itens_recorrentes[itens_recorrentes > 1].to_dict()

        # Histórico mensal
        df['Mes'] = pd.to_datetime(df['Data']).dt.to_period('M')
        evolucao = df.groupby('Mes')['Conforme_Numerico'].agg(['count', 'sum'])
        evolucao['nc_mensal'] = evolucao['count'] - evolucao['sum']

        self.indicadores = {
            "conformidade": round(conformidade, 2),
            "nc_count": nc_count,
            "total": total,
            "top_sector": setor_nc.index[0] if len(setor_nc) > 0 else "N/A",
            "top_category": categoria_nc.index[0] if len(categoria_nc) > 0 else "N/A",
            "recorrentes": recorrentes,
            "evolucao": evolucao,
            "setor_nc": setor_nc.to_dict(),
            "categoria_nc": categoria_nc.to_dict()
        }
        logger.info("Indicadores gerados.")

    def gerar_graficos(self):
        """Gera e salva gráficos em outputs/graficos/"""
        plt.style.use('seaborn-v0_8')

        # 1. Conformidade
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

        # Gráfico 1: Pizza de conformidade
        labels = ['Conforme', 'Não Conforme']
        sizes = [self.indicadores['conformidade'], 100 - self.indicadores['conformidade']]
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['#5cb85c', '#d9534f'])
        ax1.set_title('Percentual de Conformidade')

        # Gráfico 2: Setores com mais NC
        setor_data = list(self.indicadores['setor_nc'].items())[:5]
        if setor_data:
            setores, counts = zip(*setor_data)
            ax2.bar(setores, counts, color='orange')
            ax2.set_title('Top 5 Setores com NC')
            ax2.tick_params(axis='x', rotation=45)

        # Gráfico 3: Categorias com mais NC
        cat_data = list(self.indicadores['categoria_nc'].items())[:5]
        if cat_data:
            cats, counts = zip(*cat_data)
            ax3.bar(cats, counts, color='red')
            ax3.set_title('Top 5 Categorias com NC')
            ax3.tick_params(axis='x', rotation=45)

        # Gráfico 4: Evolução mensal de NC
        evol = self.indicadores['evolucao']
        ax4.plot(evol.index.astype(str), evol['nc_mensal'], marker='o', color='purple')
        ax4.set_title('Evolução Mensal de Não Conformidades')
        ax4.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        path = GRAPHICS_DIR / "dashboard_conformidade.png"
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Gráficos salvos em {path}")

    def exportar_csv(self):
        """Exporta DataFrame tratado."""
        path = OUTPUTS_DIR / "auditoria_tratada.csv"
        self.df.to_csv(path, index=False, encoding='utf-8')
        logger.info(f"Dados exportados para {path}")

    def gerar_relatorio_executivo(self):
        """Gera relatório em texto com análise simples."""
        rep = f"""
RELATÓRIO EXECUTIVO - AI FOOD AUDIT ASSISTANT
Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}

📌 RESUMO DA AUDITORIA
- Conformidade: {self.indicadores['conformidade']}%
- Total de NC: {self.indicadores['nc_count']}

🏆 PONTOS FORTES
- Alta conformidade geral.
- Setores como Embalagem e Expedição apresentam bom desempenho.

⚠️ PRINCIPAIS PROBLEMAS
- Setor: {self.indicadores['top_sector']}
- Categoria crítica: {self.indicadores['top_category']}
- Itens recorrentes: {list(self.indicadores['recorrentes'].keys())[:3]}

💡 SUGESTÕES
- Revisar procedimentos no setor {self.indicadores['top_sector']}.
- Treinamento específico em {self.indicadores['top_category']}.

"""
        path = REPORTS_DIR / "relatorio_executivo.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(rep)
        logger.info(f"Relatório executivo salvo em {path}")

    def _carregar_modelo_ia(self) -> Llama:
        """Baixa e carrega o modelo GGUF localmente."""
        if not MODEL_PATH.exists():
            if not download_file(MODEL_URL, MODEL_PATH):
                raise RuntimeError("Falha ao baixar o modelo.")
        return Llama(**LLM_PARAMS)

    def gerar_relatorio_ia(self):
        """Usa IA local para gerar análise avançada."""
        llm = self._carregar_modelo_ia()

        # Preenche prompt de resumo
        prompt_sumario = EXECUTIVE_SUMMARY_PROMPT.replace(
            "{{ conformidade }}", str(self.indicadores['conformidade'])
        ).replace(
            "{{ nc_count }}", str(self.indicadores['nc_count'])
        ).replace(
            "{{ top_sector }}", str(self.indicadores['top_sector'])
        ).replace(
            "{{ top_category }}", str(self.indicadores['top_category'])
        ).replace(
            "{{ recorrentes }}", str(list(self.indicadores['recorrentes'].keys())[:5])
        )

        output = llm(
            prompt_sumario,
            max_tokens=300,
            stop=["\n\n"],
            temperature=0.3
        )
        resumo = output['choices'][0]['text'].strip()

        # Preenche análise técnica
        critical = "\n".join([
            f"- {item} ({count} ocorrências)" for item, count in self.indicadores['recorrentes'].items()
        ])
        prompt_tecnico = TECHNICAL_ANALYSIS_PROMPT.replace("{{ critical_issues }}", critical)

        output2 = llm(
            prompt_tecnico,
            max_tokens=400,
            temperature=0.4
        )
        analise = output2['choices'][0]['text'].strip()

        # Salva relatório completo
        full_report = f"""
# RELATÓRIO DE AUDITORIA COM IA LOCAL

## Resumo Executivo
{resumo}

## Análise Técnica
{analise}

--- 
Gerado por: AI Food Audit Assistant (Qwen2.5-3B-Instruct)
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""
        path = REPORTS_DIR / "relatorio_ia.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(full_report)
        logger.info(f"Relatório com IA salvo em {path}")

    def auditor_ia(self, pergunta: str) -> str:
        """Responde perguntas com base nos dados."""
        llm = self._carregar_modelo_ia()
        contexto = str(self.indicadores)
        prompt = QA_CHAT_PROMPT.replace("{{ pergunta }}", pergunta).replace("{{ contexto }}", contexto[:2000])

        output = llm(prompt, max_tokens=200, temperature=0.5)
        return output['choices'][0]['text'].strip()
