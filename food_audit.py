from dataclasses import dataclass
from pathlib import Path
from typing import Dict
import pandas as pd

from config import CONFORME_VALUES, REQUIRED_COLUMNS, GRAPHICS_DIR, REPORTS_DIR, OUTPUTS_DIR
from utils import logger, ensure_columns, normalize_text, safe_dt, topn

@dataclass
class AuditResult:
    indicadores: Dict
    df: pd.DataFrame

class FoodAuditAnalyzer:
    def __init__(self, csv_path: str | Path):
        self.csv_path = Path(csv_path)
        self.df = pd.DataFrame()
        self.indicadores: Dict = {}

    def load(self) -> pd.DataFrame:
        self.df = pd.read_csv(self.csv_path, encoding="utf-8")
        ensure_columns(self.df, REQUIRED_COLUMNS)
        logger.info(f"CSV carregado: {len(self.df)} linhas")
        return self.df

    def clean(self) -> pd.DataFrame:
        df = self.df.copy()
        text_cols = ["Setor", "Auditor", "Item auditado", "Categoria", "Observação", "Ação corretiva", "Responsável"]
        for c in text_cols:
            df[c] = normalize_text(df[c])

        df["Conforme"] = df["Conforme"].astype(str).str.strip().str.lower()
        df["Conforme_Numerico"] = df["Conforme"].apply(lambda x: 1 if x in CONFORME_VALUES else 0)

        df["Data"] = safe_dt(df["Data"])
        df["Prazo"] = safe_dt(df["Prazo"])
        self.df = df
        logger.info("Dados limpos e normalizados")
        return df

    def indicators(self) -> Dict:
        df = self.df.copy()
        total = len(df) or 1
        nc_count = int((df["Conforme_Numerico"] == 0).sum())
        conformidade = round(((total - nc_count) / total) * 100, 2)

        nc = df[df["Conforme_Numerico"] == 0]
        setor_nc = topn(nc["Setor"])
        categoria_nc = topn(nc["Categoria"])
        itens = topn(nc["Item auditado"])
        recorrentes = {k: v for k, v in itens.items() if v > 1}

        temp = df.dropna(subset=["Data"]).copy()
        if not temp.empty:
            temp["Mes"] = temp["Data"].dt.to_period("M")
            evolucao = temp.groupby("Mes")["Conforme_Numerico"].agg(["count", "sum"])
            evolucao["nc_mensal"] = evolucao["count"] - evolucao["sum"]
        else:
            evolucao = pd.DataFrame(columns=["count", "sum", "nc_mensal"])

        self.indicadores = {
            "conformidade": conformidade,
            "nc_count": nc_count,
            "total": total,
            "top_sector": next(iter(setor_nc), "N/A"),
            "top_category": next(iter(categoria_nc), "N/A"),
            "recorrentes": recorrentes,
            "setor_nc": setor_nc,
            "categoria_nc": categoria_nc,
            "evolucao": evolucao,
        }
        logger.info("Indicadores calculados")
        return self.indicadores

    def save_cleaned_csv(self) -> Path:
        out = OUTPUTS_DIR / "auditoria_tratada.csv"
        self.df.to_csv(out, index=False, encoding="utf-8")
        return out

    def chart_dashboard(self):
        import matplotlib.pyplot as plt
        from matplotlib.gridspec import GridSpec
        import pandas as pd

        plt.style.use("seaborn-v0_8-whitegrid")

        fig = plt.figure(figsize=(10, 6), dpi=200)
        gs = GridSpec(
            3,
            4,
            figure=fig,
            height_ratios=[1.2, 1.5, 1.6],
            hspace=0.55,
            wspace=0.40
        )

        # ==========================================================
        # DONUT
        # ==========================================================

        ax_donut = fig.add_subplot(gs[0, 0])

        conformidade = self.indicadores["conformidade"]
        nao = 100 - conformidade

        ax_donut.pie(
            [conformidade, nao],
            startangle=90,
            wedgeprops=dict(width=0.38),
            autopct="%1.0f%%"
        )

        ax_donut.set_title("Conformidade", fontsize=11)

        # ==========================================================
        # KPI
        # ==========================================================

        ax_kpi = fig.add_subplot(gs[0, 1:4])
        ax_kpi.axis("off")

        texto = f"""
    CONFORMIDADE

    {self.indicadores['conformidade']} %

    Não Conformidades : {self.indicadores['nc_count']}

    Setor Crítico     : {self.indicadores['top_sector']}

    Categoria Crítica : {self.indicadores['top_category']}
    """

        ax_kpi.text(
            0,
            0.5,
            texto,
            fontsize=12,
            family="monospace",
            va="center"
        )

        # ==========================================================
        # SETORES
        # ==========================================================

        ax_setor = fig.add_subplot(gs[1, :2])

        setores = pd.Series(self.indicadores["setor_nc"]).head(5)

        if not setores.empty:

            ax_setor.barh(
                setores.index.astype(str),
                setores.values
            )

            ax_setor.invert_yaxis()

        ax_setor.set_title("Top Setores Críticos")

        # ==========================================================
        # CATEGORIAS
        # ==========================================================

        ax_cat = fig.add_subplot(gs[1, 2:4])

        categorias = pd.Series(self.indicadores["categoria_nc"]).head(5)

        if not categorias.empty:

            ax_cat.barh(
                categorias.index.astype(str),
                categorias.values
            )

            ax_cat.invert_yaxis()

        ax_cat.set_title("Categorias Críticas")

        # ==========================================================
        # EVOLUÇÃO
        # ==========================================================

        ax_line = fig.add_subplot(gs[2, :])

        evolucao = self.indicadores["evolucao"]

        if isinstance(evolucao, pd.DataFrame) and not evolucao.empty:

            ax_line.plot(
                evolucao.index.astype(str),
                evolucao["nc_mensal"],
                linewidth=2,
                marker="o"
            )

            ax_line.set_ylabel("NC")

        else:

            ax_line.text(
                0.5,
                0.5,
                "Sem dados suficientes",
                ha="center",
                va="center",
                fontsize=12
            )

        ax_line.set_title("Evolução das Não Conformidades")

        # ==========================================================

        fig.suptitle(
            "AI Food Audit Assistant",
            fontsize=16,
            fontweight="bold"
        )

        plt.tight_layout(rect=[0, 0, 1, 0.96])

        out = GRAPHICS_DIR / "dashboard_conformidade.png"

        plt.savefig(
            out,
            dpi=250,
            bbox_inches="tight"
        )

        plt.close(fig)

        return out

    def executive_report(self) -> Path:
        txt = f"""RELATÓRIO EXECUTIVO

Conformidade: {self.indicadores['conformidade']}%
Total de NC: {self.indicadores['nc_count']}
Setor crítico: {self.indicadores['top_sector']}
Categoria crítica: {self.indicadores['top_category']}
Itens recorrentes: {list(self.indicadores['recorrentes'].keys())[:5]}
"""
        out = REPORTS_DIR / "relatorio_executivo.txt"
        out.write_text(txt, encoding="utf-8")
        return out

    def run(self) -> AuditResult:
        self.load()
        self.clean()
        self.indicators()
        self.save_cleaned_csv()
        self.chart_dashboard()
        self.executive_report()
        return AuditResult(self.indicadores, self.df)
