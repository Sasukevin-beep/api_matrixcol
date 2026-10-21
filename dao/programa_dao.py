"""Acceso a datos de la entidad Programa. Solo SQL, sin reglas de negocio."""
from database.conexion import Conexion

COLUMNAS = "id_programa, nombre, descripcion, estado, fecha_creacion, fecha_actualizacion"

class ProgramaDAO:
    # ---------- C ----------
    def insertar(self, datos: dict) -> int:
        sql = "INSERT INTO programa (nombre, descripcion, estado) VALUES (%s, %s, %s)"
        valores = (datos["nombre"], datos.get("descripcion"), datos.get("estado", "ACTIVO"))
        with Conexion() as cn:
            cursor = cn.cursor()
            cursor.execute(sql, valores)
            return cursor.lastrowid

    # ---------- R ----------
    def buscar_por_id(self, id_programa: int):
        sql = f"SELECT {COLUMNAS} FROM programa WHERE id_programa = %s"
        with Conexion() as cn:
            cursor = cn.cursor(dictionary=True)
            cursor.execute(sql, (id_programa,))
            return cursor.fetchone()

    def listar(self, estado: str | None = None) -> list:
        with Conexion() as cn:
            cursor = cn.cursor(dictionary=True)
            if estado:
                cursor.execute(f"SELECT {COLUMNAS} FROM programa "
                               "WHERE estado = %s ORDER BY nombre", (estado,))
            else:
                cursor.execute(f"SELECT {COLUMNAS} FROM programa ORDER BY nombre")
            return cursor.fetchall()

    def buscar_por_nombre(self, nombre: str):
        """Para detectar nombres de programas repetidos."""
        sql = f"SELECT {COLUMNAS} FROM programa WHERE nombre = %s"
        with Conexion() as cn:
            cursor = cn.cursor(dictionary=True)
            cursor.execute(sql, (nombre,))
            return cursor.fetchone()

    def contar_fichas_activas(self, id_programa: int) -> int:
        """Cuántas fichas ACTIVAS tiene el programa (regla de seguridad para el borrado)."""
        sql = ("SELECT COUNT(*) FROM ficha "
               "WHERE id_programa = %s AND estado = 'ACTIVO'")
        with Conexion() as cn:
            cursor = cn.cursor()
            cursor.execute(sql, (id_programa,))
            return cursor.fetchone()[0]

    # ---------- U ----------
    def actualizar(self, id_programa: int, datos: dict) -> None:
        sql = ("UPDATE programa SET nombre = %s, descripcion = %s, estado = %s "
               "WHERE id_programa = %s")
        valores = (datos["nombre"], datos.get("descripcion"), datos["estado"], id_programa)
        with Conexion() as cn:
            cn.cursor().execute(sql, valores)

    # ---------- D (lógico) ----------
    def desactivar(self, id_programa: int) -> None:
        sql = "UPDATE programa SET estado = 'INACTIVO' WHERE id_programa = %s"
        with Conexion() as cn:
            cn.cursor().execute(sql, (id_programa,))