"""Lógica de negocio de usuarios. No conoce Flask ni SQL."""
from dao.usuario_dao import UsuarioDAO
from utilidades.validadores import ESTADOS, validar_usuario

class ErrorNegocio(Exception):
    """Error controlado. Lleva el código HTTP que la ruta debe devolver."""
    def __init__(self, mensaje: str, codigo: int = 400, detalles: dict | None = None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo
        self.detalles = detalles

def _limpiar(datos: dict) -> dict:
    """Normaliza lo que escribió el usuario: quita espacios y unifica mayúsculas."""
    limpio = {}
    for campo, valor in datos.items():
        if isinstance(valor, str):
            valor = valor.strip()
            if campo in ("tipo_documento", "estado"):
                valor = valor.upper()
            elif campo == "correo":
                valor = valor.lower()
            elif campo in ("direccion", "ciudad") and valor == "":
                valor = None          # Texto vacío = sin dato.
        limpio[campo] = valor
    return limpio

def _serializar(usuario: dict) -> dict:
    """Convierte las fechas a texto 'AAAA-MM-DD HH:MM:SS' para devolverlas en JSON."""
    return {campo: (valor.strftime("%Y-%m-%d %H:%M:%S")
                    if hasattr(valor, "strftime") else valor)
            for campo, valor in usuario.items()}

class ServicioUsuarios:
    def __init__(self, dao=None):
        self.dao = dao or UsuarioDAO()

    # ---------- C ----------
    def crear(self, datos) -> dict:
        datos = self._exigir_objeto(datos)
        datos = _limpiar(datos)
        self._exigir_validos(datos, completo=True)
        self._verificar_unicos(datos)

        id_usuario = self.dao.insertar(datos)
        return _serializar(self.dao.buscar_por_id(id_usuario))

    # ---------- R ----------
    def listar(self, estado: str | None = None) -> list:
        if estado is not None:
            estado = estado.strip().upper()
            if estado not in ESTADOS:
                raise ErrorNegocio("El filtro estado debe ser ACTIVO o INACTIVO.", 400)
        return [_serializar(u) for u in self.dao.listar(estado)]

    def obtener(self, id_usuario: int) -> dict:
        return _serializar(self._obtener_o_404(id_usuario))

    # ---------- U ----------
    def reemplazar(self, id_usuario: int, datos) -> dict:
        """PUT: el usuario queda EXACTAMENTE con los datos enviados."""
        actual = self._obtener_o_404(id_usuario)
        datos = self._exigir_objeto(datos)
        datos = _limpiar(datos)
        self._exigir_validos(datos, completo=True)
        self._verificar_unicos(datos, id_actual=id_usuario)

        datos.setdefault("estado", actual["estado"])
        self.dao.actualizar(id_usuario, datos)
        return _serializar(self.dao.buscar_por_id(id_usuario))

    def editar(self, id_usuario: int, cambios) -> dict:
        """PATCH: solo cambian los campos enviados; los demás se conservan."""
        actual = self._obtener_o_404(id_usuario)
        cambios = self._exigir_objeto(cambios)
        if not cambios:
            raise ErrorNegocio("No se envió ningún campo para editar.", 400)
        cambios = _limpiar(cambios)
        self._exigir_validos(cambios, completo=False)

        final = {**actual, **cambios}                  # Lo actual + lo que cambió.
        self._verificar_unicos(final, id_actual=id_usuario)
        self.dao.actualizar(id_usuario, final)
        return _serializar(self.dao.buscar_por_id(id_usuario))

    # ---------- D ----------
    def eliminar(self, id_usuario: int) -> dict:
        """Borrado lógico: el usuario queda INACTIVO."""
        self._obtener_o_404(id_usuario)
        self.dao.desactivar(id_usuario)
        return {"id_usuario": id_usuario, "estado": "INACTIVO"}

    # ---------- Apoyo interno ----------
    def _obtener_o_404(self, id_usuario: int) -> dict:
        usuario = self.dao.buscar_por_id(id_usuario)
        if usuario is None:
            raise ErrorNegocio("Usuario no encontrado.", 404)
        return usuario

    @staticmethod
    def _exigir_objeto(datos) -> dict:
        if not isinstance(datos, dict):
            raise ErrorNegocio("El cuerpo debe ser un JSON válido (un objeto).", 400)
        return datos

    @staticmethod
    def _exigir_validos(datos: dict, completo: bool) -> None:
        errores = validar_usuario(datos, completo)
        if errores:
            raise ErrorNegocio("Datos inválidos.", 400, errores)

    def _verificar_unicos(self, datos: dict, id_actual: int | None = None) -> None:
        """Documento y correo no pueden repetirse (se ignora el propio usuario)."""
        otro = self.dao.buscar_por_documento(datos["tipo_documento"], datos["numero_documento"])
        if otro and otro["id_usuario"] != id_actual:
            raise ErrorNegocio("Ya existe un usuario con ese tipo y número de documento.", 409)

        otro = self.dao.buscar_por_correo(datos["correo"])
        if otro and otro["id_usuario"] != id_actual:
            raise ErrorNegocio("Ya existe un usuario con ese correo.", 409)