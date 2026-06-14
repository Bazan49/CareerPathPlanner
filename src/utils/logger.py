import logging
import sys
from pathlib import Path

def setup_logger(name: str = "CareerPathPlanner", log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Configura y devuelve un logger con formato estándar.
    Si se proporciona log_file, también escribe en archivo.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Evitar duplicar handlers si ya existen
    if logger.handlers:
        return logger

    # Formato: timestamp - nombre - nivel - nombre del archivo - mensaje
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler para archivo (opcional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# Logger por defecto con archivo en raíz del proyecto 
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_LOG_FILE = ROOT_DIR.joinpath("app.log")

default_logger = setup_logger(log_file=str(DEFAULT_LOG_FILE))
