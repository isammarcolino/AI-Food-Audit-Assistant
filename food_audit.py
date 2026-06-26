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
        from matplotlib.patches import FancyBboxPatch
        import pandas as pd

        plt.style.use("seaborn-v0_8-whitegrid")

        fig = plt.figure(figsize=(13, 7), dpi=200)
        gs = GridSpec(
            3, 4,
            figure=fig,
            height_ratios=[1.0, 1.25, 1.35],
            width_ratios=[1.15, 1.15, 1.15, 1.15],
            hspace=0.55,
            wspace=0.35
        )

        def kpi_card(ax, x, y, w, h, title, value, color="#1f77b4"):
            ax.add_patch(
                FancyBboxPatch(
                    (x, y), w, h,
                    boxstyle="round,pad=0.02,rounding_size=0.03",
                    linewidth=1.0,
                    edgecolor="#d0d7de",
                    facecolor="white",
                    transform=ax.transAxes
                )
            )
            ax.text(x + 0.06, y + h - 0.20, title, transform=ax.transAxes,
                    fontsize=9, fontweight="bold", va="top", color="#444")
            ax.text(x + 0.06, y + 0.12, value, transform=ax.transAxes,
                    fontsize=16, fontweight="bold", va="bottom", color=color)

        # ----------------------------------------------------------
        # DONUT
        # ----------------------------------------------------------
        ax_donut = fig.add_subplot(gs[0, 0])
        conformidade = float(self.indicadores["conformidade"])
        nao = max(0.0, 100.0 - conformidade)

        ax_donut.pie(
            [conformidade, nao],
            startangle=90,
            counterclock=False,
            wedgeprops=dict(width=0.38, edgecolor="white"),
            autopct=lambda p: f"{p:.0f}%" if p >= 5 else ""
        )
        ax_donut.set_title("Conformidade", fontsize=11, pad=10)
        ax_donut.set_aspect("equal")

        # ----------------------------------------------------------
        # KPI CARDS
        # ----------------------------------------------------------
        ax_kpi = fig.add_subplot(gs[0, 1:4])
        ax_kpi.axis("off")

        card_w = 0.23
        gap = 0.02
        y = 0.12

        kpi_card(ax_kpi, 0.00, y, card_w, 0.68, "Conformidade", f"{conformidade:.1f}%")
        kpi_card(ax_kpi, card_w + gap, y, card_w, 0.68, "NC", str(self.indicadores["nc_count"]), "#d62728")
        kpi_card(ax_kpi, 2 * (card_w + gap), y, card_w, 0.68, "Setor Crítico", str(self.indicadores["top_sector"]), "#ff7f0e")
        kpi_card(ax_kpi, 3 * (card_w + gap), y, card_w, 0.68, "Categoria Crítica", str(self.indicadores["top_category"]), "#9467bd")

        # ----------------------------------------------------------
        # SETORES
        # ----------------------------------------------------------
        ax_setor = fig.add_subplot(gs[1, :2])
        setores = pd.Series(self.indicadores["setor_nc"]).head(5)

        if not setores.empty:
            ax_setor.barh(setores.index.astype(str), setores.values, height=0.55)
            ax_setor.invert_yaxis()
            ax_setor.tick_params(axis="y", labelsize=9)
            ax_setor.tick_params(axis="x", labelsize=8)
            ax_setor.grid(axis="x", linestyle="--", alpha=0.25)
        else:
            ax_setor.text(0.5, 0.5, "Sem dados suficientes", ha="center", va="center")

        ax_setor.set_title("Top Setores Críticos", fontsize=11, pad=8)
        ax_setor.set_xlabel("Quantidade")
        ax_setor.spines["top"].set_visible(False)
        ax_setor.spines["right"].set_visible(False)

        # ----------------------------------------------------------
        # CATEGORIAS
        # ----------------------------------------------------------
        ax_cat = fig.add_subplot(gs[1, 2:4])
        categorias = pd.Series(self.indicadores["categoria_nc"]).head(5)

        if not categorias.empty:
            ax_cat.barh(categorias.index.astype(str), categorias.values, height=0.55)
            ax_cat.invert_yaxis()
            ax_cat.tick_params(axis="y", labelsize=9)
            ax_cat.tick_params(axis="x", labelsize=8)
            ax_cat.grid(axis="x", linestyle="--", alpha=0.25)
        else:
            ax_cat.text(0.5, 0.5, "Sem dados suficientes", ha="center", va="center")

        ax_cat.set_title("Categorias Críticas", fontsize=11, pad=8)
        ax_cat.set_xlabel("Quantidade")
        ax_cat.spines["top"].set_visible(False)
        ax_cat.spines["right"].set_visible(False)

        # ----------------------------------------------------------
        # EVOLUÇÃO
        # ----------------------------------------------------------
        ax_line = fig.add_subplot(gs[2, :])
        evolucao = self.indicadores["evolucao"]

        if isinstance(evolucao, pd.DataFrame) and not evolucao.empty:
            ax_line.plot(
                evolucao.index.astype(str),
                evolucao["nc_mensal"],
                linewidth=2,
                marker="o",
                markersize=5
            )
            ax_line.set_ylabel("NC")
            ax_line.tick_params(axis="x", labelsize=8)
            ax_line.tick_params(axis="y", labelsize=8)
            ax_line.grid(True, axis="y", linestyle="--", alpha=0.25)
        else:
            ax_line.text(0.5, 0.5, "Sem dados suficientes", ha="center", va="center", fontsize=11)
            ax_line.set_axis_off()

        ax_line.set_title("Evolução das Não Conformidades", fontsize=11, pad=8)
        ax_line.spines["top"].set_visible(False)
        ax_line.spines["right"].set_visible(False)

        fig.suptitle("AI Food Audit Assistant", fontsize=15, fontweight="bold", y=0.98)
        plt.subplots_adjust(left=0.05, right=0.98, top=0.92, bottom=0.07)

        out = GRAPHICS_DIR / "dashboard_conformidade.png"
        plt.savefig(out, dpi=250, bbox_inches="tight")
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
