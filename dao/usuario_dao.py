"""Acceso a datos de la entidad Usuario. Solo SQL, sin reglas de negocio."""
from database.conexion import Conexion

COLUMNAS = ("id_usuario, tipo_documento, numero_documento, nombre, correo, telefono, "
            "direccion, ciudad, estado, fecha_creacion, fecha_actualizacion")

class UsuarioDAO:
    """Todas las consultas son parametrizadas (%s) para evitar inyección SQL."""

    # ---------- C: Create ----------
    def insertar(self, datos: dict) -> int:
        """Inserta un usuario nuevo y devuelve su id."""
        sql = ("INSERT INTO usuario (tipo_documento, numero_documento, nombre, correo, "
               "telefono, direccion, ciudad, estado) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
        valores = (datos["tipo_documento"], datos["numero_documento"], datos["nombre"],
                   datos["correo"], datos["telefono"], datos.get("direccion"),
                   datos.get("ciudad"), datos.get("estado", "ACTIVO"))
        with Conexion() as cn:
            cursor = cn.cursor()
            cursor.execute(sql, valores)
            return cursor.lastrowid

    # ---------- R: Read ----------
    def buscar_por_id(self, id_usuario: int):
        """Devuelve el usuario como diccionario, o None si no existe."""
        sql = f"SELECT {COLUMNAS} FROM usuario WHERE id_usuario = %s"
        with Conexion() as cn:
            cursor = cn.cursor(dictionary=True)
            cursor.execute(sql, (id_usuario,))
            return cursor.fetchone()

    def listar(self, estado: str | None = None) -> list:
        """Devuelve todos los usuarios, o solo los de un estado si se indica."""
        with Conexion() as cn:
            cursor = cn.cursor(dictionary=True)
            if estado:
                cursor.execute(f"SELECT {COLUMNAS} FROM usuario "
                               "WHERE estado = %s ORDER BY nombre", (estado,))
            else:
                cursor.execute(f"SELECT {COLUMNAS} FROM usuario ORDER BY nombre")
            return cursor.fetchall()

    def buscar_por_documento(self, tipo_documento: str, numero_documento: str):
        """Para detectar documentos repetidos. Devuelve el usuario o None."""
        sql = (f"SELECT {COLUMNAS} FROM usuario "
               "WHERE tipo_documento = %s AND numero_documento = %s")
        with Conexion() as cn:
            cursor = cn.cursor(dictionary=True)
            cursor.execute(sql, (tipo_documento, numero_documento))
            return cursor.fetchone()

    def buscar_por_correo(self, correo: str):
        """Para detectar correos repetidos. Devuelve el usuario o None."""
        sql = f"SELECT {COLUMNAS} FROM usuario WHERE correo = %s"
        with Conexion() as cn:
            cursor = cn.cursor(dictionary=True)
            cursor.execute(sql, (correo,))
            return cursor.fetchone()

    # ---------- U: Update ----------
    def actualizar(self, id_usuario: int, datos: dict) -> None:
        """Actualiza todos los campos editables de un usuario."""
        sql = ("UPDATE usuario SET tipo_documento = %s, numero_documento = %s, "
               "nombre = %s, correo = %s, telefono = %s, direccion = %s, "
               "ciudad = %s, estado = %s WHERE id_usuario = %s")
        valores = (datos["tipo_documento"], datos["numero_documento"], datos["nombre"],
                   datos["correo"], datos["telefono"], datos.get("direccion"),
                   datos.get("ciudad"), datos["estado"], id_usuario)
        with Conexion() as cn:
            cn.cursor().execute(sql, valores)

    # ---------- D: Delete (lógico) ----------
    def desactivar(self, id_usuario: int) -> None:
        """Borrado lógico: la fila se conserva, solo cambia su estado a INACTIVO."""
        sql = "UPDATE usuario SET estado = 'INACTIVO' WHERE id_usuario = %s"
        with Conexion() as cn:
            cn.cursor().execute(sql, (id_usuario,))