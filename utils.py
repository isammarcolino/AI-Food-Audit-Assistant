"""
Utilitários reutilizáveis: logging, download, formatação, etc.
"""
import logging
import requests
import os
from pathlib import Path
from tqdm import tqdm
from typing import Union

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_directories():
    """Cria diretórios necessários se não existirem."""
    for path in ["logs", "outputs/graficos", "outputs/relatorios", "models"]:
        Path(path).mkdir(exist_ok=True)

def download_file(url: str, dest: Union[Path, str]) -> bool:
    """
    Baixa arquivo com barra de progresso.
    Útil para modelos GGUF grandes.
    """
    dest = Path(dest)
    if dest.exists():
        logger.info(f"{dest.name} já existe. Pulando download.")
        return True

    try:
        logger.info(f"Baixando {url} -> {dest}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))

        with open(dest, 'wb') as f, tqdm(
            desc=dest.name,
            total=total_size,
            unit='B',
            unit_scale=True
        ) as pbar:
            for chunk in response.iterable:
                f.write(chunk)
                pbar.update(len(chunk))
        logger.info("Download concluído.")
        return True
    except Exception as e:
        logger.error(f"Erro no download: {e}")
        return False
