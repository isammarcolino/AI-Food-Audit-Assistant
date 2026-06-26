from pathlib import Path

ROOT_DIR = Path.cwd()
DATA_DIR = ROOT_DIR / "data"
OUTPUTS_DIR = ROOT_DIR / "outputs"
GRAPHICS_DIR = OUTPUTS_DIR / "graficos"
REPORTS_DIR = OUTPUTS_DIR / "relatorios"
MODELS_DIR = ROOT_DIR / "models"
LOGS_DIR = ROOT_DIR / "logs"

for d in [DATA_DIR, OUTPUTS_DIR, GRAPHICS_DIR, REPORTS_DIR, MODELS_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

MODEL_REPO = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
MODEL_FILE = "qwen2.5-0.5b-instruct-q5_k_m.gguf"

CONFORME_VALUES = {"sim", "s", "true", "1", "ok", "yes", "conforme"}
REQUIRED_COLUMNS = [
    "Data", "Setor", "Auditor", "Item auditado", "Categoria",
    "Conforme", "Observação", "Ação corretiva", "Responsável", "Prazo"
]
