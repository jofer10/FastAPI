import logging

def setup_logging():
    # Configuración del logging
    logging.basicConfig(
        level=logging.INFO,  # Nivel de logs: DEBUG, INFO, WARNING, ERROR, CRITICAL
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("app.log"),  # Guarda los logs en un archivo
            # logging.StreamHandler()  # Muestra los logs en la consola
        ],
        force=True  # 🔄 Fuerza la reconfiguración si ya había logging activo
    )

def get_logger(name: str):
    return logging.getLogger(name)