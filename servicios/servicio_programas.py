"""Lógica de negocio de programas. No conoce Flask ni SQL."""
from dao.programa_dao import ProgramaDAO
from servicios.servicio_usuarios import ErrorNegocio
from utilidades.validadores_academicos import ESTADOS, validar_programa

def _limpiar(datos: dict) -> dict:
    limpio = {}
    for campo, valor in datos.items():
        if isinstance(valor, str):
            valor = valor.strip()
            if campo == "estado":
                valor = valor.upper()
            elif campo == "descripcion" and valor == "":
                valor = None
        limpio[campo] = valor
    return limpio

def _serializar(programa: dict) -> dict:
    return {campo: (valor.strftime("%Y-%m-%d %H:%M:%S")
                    if hasattr(valor, "strftime") else valor)
            for campo, valor in programa.items()}

class ServicioProgramas:
    def __init__(self, dao=None):
        self.dao = dao or ProgramaDAO()

    # ---------- C ----------
    def crear(self, datos) -> dict:
        datos = _limpiar(self._exigir_objeto(datos))
        self._exigir_validos(datos, completo=True)
        self._verificar_nombre_unico(datos["nombre"])
        id_programa = self.dao.insertar(datos)
        return _serializar(self.dao.buscar_por_id(id_programa))

    # ---------- R ----------
    def listar(self, estado: str | None = None) -> list:
        if estado is not None:
            estado = estado.strip().upper()
            if estado not in ESTADOS:
                raise ErrorNegocio("El filtro estado debe ser ACTIVO o INACTIVO.", 400)
        return [_serializar(p) for p in self.dao.listar(estado)]

    def obtener(self, id_programa: int) -> dict:
        return _serializar(self._obtener_o_404(id_programa))

    # ---------- U ----------
    def reemplazar(self, id_programa: int, datos) -> dict:
        actual = self._obtener_o_404(id_programa)
        datos = _limpiar(self._exigir_objeto(datos))
        self._exigir_validos(datos, completo=True)
        datos.setdefault("estado", actual["estado"])
        self._verificar_nombre_unico(datos["nombre"], id_actual=id_programa)
        self._verificar_desactivacion(actual, datos)
        self.dao.actualizar(id_programa, datos)
        return _serializar(self.dao.buscar_por_id(id_programa))

    def editar(self, id_programa: int, cambios) -> dict:
        actual = self._obtener_o_404(id_programa)
        cambios = _limpiar(self._exigir_objeto(cambios))
        if not cambios:
            raise ErrorNegocio("No se envió ningún campo para editar.", 400)
        self._exigir_validos(cambios, completo=False)
        final = {**actual, **cambios}
        self._verificar_nombre_unico(final["nombre"], id_actual=id_programa)
        self._verificar_desactivacion(actual, final)
        self.dao.actualizar(id_programa, final)
        return _serializar(self.dao.buscar_por_id(id_programa))

    # ---------- D ----------
    def eliminar(self, id_programa: int) -> dict:
        """Borrado lógico, pero solo si el programa ya no tiene fichas activas."""
        actual = self._obtener_o_404(id_programa)
        self._verificar_desactivacion(actual, {"estado": "INACTIVO"})
        self.dao.desactivar(id_programa)
        return {"id_programa": id_programa, "estado": "INACTIVO"}

    # ---------- Apoyo interno ----------
    def _obtener_o_404(self, id_programa: int) -> dict:
        programa = self.dao.buscar_por_id(id_programa)
        if programa is None:
            raise ErrorNegocio("Programa no encontrado.", 404)
        return programa

    @staticmethod
    def _exigir_objeto(datos) -> dict:
        if not isinstance(datos, dict):
            raise ErrorNegocio("El cuerpo debe ser un JSON válido (un objeto).", 400)
        return datos

    @staticmethod
    def _exigir_validos(datos: dict, completo: bool) -> None:
        errores = validar_programa(datos, completo)
        if errores:
            raise ErrorNegocio("Datos inválidos.", 400, errores)

    def _verificar_nombre_unico(self, nombre: str, id_actual: int | None = None) -> None:
        otro = self.dao.buscar_por_nombre(nombre)
        if otro and otro["id_programa"] != id_actual:
            raise ErrorNegocio("Ya existe un programa con ese nombre.", 409)

    def _verificar_desactivacion(self, actual: dict, final: dict) -> None:
        """Regla: no se puede pasar a INACTIVO un programa con fichas ACTIVAS."""
        if actual["estado"] == "ACTIVO" and final["estado"] == "INACTIVO":
            n = self.dao.contar_fichas_activas(actual["id_programa"])
            if n > 0:
                raise ErrorNegocio(
                    f"No se puede desactivar: el programa tiene {n} ficha(s) ACTIVA(S). "
                    "Desactiva o mueve esas fichas primero.", 409)