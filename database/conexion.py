import mysql.connector
from mysql.connector import Error
from config.configuracion import Config

class Conexion:
    """Context manager: abre la conexión, hace COMMIT si todo salió bien
    y ROLLBACK si ocurrió una excepción. Siempre cierra la conexión.
    """
    def __init__(self):
        self.conexion = None

    def __enter__(self):
        try:
            self.conexion = mysql.connector.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                charset="utf8mb4",
            )
            return self.conexion
        except Error as e:
            raise ConnectionError(f"No fue posible conectar a MySQL: {e}")

    def __exit__(self, tipo_exc, valor_exc, traza):
        if self.conexion and self.conexion.is_connected():
            if tipo_exc is None:
                self.conexion.commit()    # Todo bien: se confirma.
            else:
                self.conexion.rollback()  # Hubo error: se deshace.
            self.conexion.close()
        return False