"""
Configurações centrais do projeto AI Food Audit Assistant.
"""
import os
from pathlib import Path

# Caminhos principais
ROOT_DIR = Path(__file__).parent.resolve()
DATA_DIR = ROOT_DIR / "data"
OUTPUTS_DIR = ROOT_DIR / "outputs"
MODELS_DIR = ROOT_DIR / "models"
GRAPHICS_DIR = OUTPUTS_DIR / "graficos"
REPORTS_DIR = OUTPUTS_DIR / "relatorios"

# Criação de diretórios
for directory in [DATA_DIR, OUTPUTS_DIR, GRAPHICS_DIR, REPORTS_DIR, MODELS_DIR]:
    directory.mkdir(exist_ok=True)

# Configurações do modelo
MODEL_NAME = "qwen2.5-3b-instruct-q4_k_m.gguf"
MODEL_URL = f"https://huggingface.co/TheBloke/Qwen2.5-3B-Instruct-GGUF/resolve/main/{MODEL_NAME}"
MODEL_PATH = MODELS_DIR / MODEL_NAME

# Parâmetros de inferência
LLM_PARAMS = {
    "model_path": str(MODEL_PATH),
    "n_ctx": 4096,
    "n_threads": 4,
    "n_gpu_layers": 35,
    "verbose": False,
}

# Configurações de análise
CONFORME_VALUES = ["Sim", "sim", "SIM", "S", "s"]
Nao_CONFORME_VALUES = ["Não", "nao", "NÃO", "N", "n", "NO"]
