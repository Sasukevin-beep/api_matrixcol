"""Acceso a datos de Fichas. Incluye JOIN con la tabla Programa."""
from database.conexion import Conexion

# Columnas para los SELECTs con JOIN
COLUMNAS_JOIN = (
    "f.id_ficha, f.id_programa, p.nombre AS nombre_programa, "
    "f.codigo_ficha, f.jornada, f.cupo_maximo, f.estado, "
    "f.fecha_creacion, f.fecha_actualizacion"
)
TABLAS_JOIN = "ficha f JOIN programa p ON f.id_programa = p.id_programa"

class FichaDAO:
    # ---------- C ----------
    def insertar(self, datos: dict) -> int:
        sql = ("INSERT INTO ficha (id_programa, codigo_ficha, jornada, cupo_maximo, estado) "
               "VALUES (%s, %s, %s, %s, %s)")
        valores = (datos["id_programa"], datos["codigo_ficha"], datos["jornada"],
                   datos.get("cupo_maximo", 30), datos.get("estado", "ACTIVO"))
        with Conexion() as cn:
            cursor = cn.cursor()
            cursor.execute(sql, valores)
            return cursor.lastrowid

    # ---------- R ----------
    def buscar_por_id(self, id_ficha: int):
        sql = f"SELECT {COLUMNAS_JOIN} FROM {TABLAS_JOIN} WHERE f.id_ficha = %s"
        with Conexion() as cn:
            cursor = cn.cursor(dictionary=True)
            cursor.execute(sql, (id_ficha,))
            return cursor.fetchone()

    def listar(self, estado: str | None = None) -> list:
        with Conexion() as cn:
            cursor = cn.cursor(dictionary=True)
            if estado:
                cursor.execute(f"SELECT {COLUMNAS_JOIN} FROM {TABLAS_JOIN} "
                               "WHERE f.estado = %s ORDER BY f.codigo_ficha", (estado,))
            else:
                cursor.execute(f"SELECT {COLUMNAS_JOIN} FROM {TABLAS_JOIN} ORDER BY f.codigo_ficha")
            return cursor.fetchall()

    def buscar_por_codigo(self, codigo_ficha: str):
        """Para evitar que dos fichas tengan el mismo código."""
        sql = f"SELECT {COLUMNAS_JOIN} FROM {TABLAS_JOIN} WHERE f.codigo_ficha = %s"
        with Conexion() as cn:
            cursor = cn.cursor(dictionary=True)
            cursor.execute(sql, (codigo_ficha,))
            return cursor.fetchone()

    # ---------- U ----------
    def actualizar(self, id_ficha: int, datos: dict) -> None:
        sql = ("UPDATE ficha SET id_programa = %s, codigo_ficha = %s, "
               "jornada = %s, cupo_maximo = %s, estado = %s WHERE id_ficha = %s")
        valores = (datos["id_programa"], datos["codigo_ficha"], datos["jornada"],
                   datos["cupo_maximo"], datos["estado"], id_ficha)
        with Conexion() as cn:
            cn.cursor().execute(sql, valores)

    # ---------- D (lógico) ----------
    def desactivar(self, id_ficha: int) -> None:
        sql = "UPDATE ficha SET estado = 'INACTIVO' WHERE id_ficha = %s"
        with Conexion() as cn:
            cn.cursor().execute(sql, (id_ficha,))