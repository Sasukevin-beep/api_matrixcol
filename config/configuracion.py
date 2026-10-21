import os
from dotenv import load_dotenv

# Carga el archivo .env (si existe) en las variables de entorno
load_dotenv()

class Config:
    """Parámetros de conexión a MySQL."""
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "matrixcol_db")