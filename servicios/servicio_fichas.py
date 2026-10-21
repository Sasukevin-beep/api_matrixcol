"""Lógica de negocio de fichas. Valida relaciones con Programas."""
from dao.ficha_dao import FichaDAO
from dao.programa_dao import ProgramaDAO
from servicios.servicio_usuarios import ErrorNegocio
from utilidades.validadores_academicos import ESTADOS, validar_ficha

def _limpiar(datos: dict) -> dict:
    limpio = {}
    for campo, valor in datos.items():
        if isinstance(valor, str):
            valor = valor.strip()
            if campo in ("codigo_ficha", "estado"):
                valor = valor.upper()
        limpio[campo] = valor
    return limpio

def _serializar(ficha: dict) -> dict:
    return {campo: (valor.strftime("%Y-%m-%d %H:%M:%S")
                    if hasattr(valor, "strftime") else valor)
            for campo, valor in ficha.items()}

class ServicioFichas:
    def __init__(self, dao=None, programa_dao=None):
        self.dao = dao or FichaDAO()
        # Necesitamos el DAO de programas para verificar que el programa exista y esté activo
        self.programa_dao = programa_dao or ProgramaDAO()

    # ---------- C ----------
    def crear(self, datos) -> dict:
        datos = _limpiar(self._exigir_objeto(datos))
        self._exigir_validos(datos, completo=True)
        self._verificar_programa_valido(datos["id_programa"])
        self._verificar_codigo_unico(datos["codigo_ficha"])
        
        id_ficha = self.dao.insertar(datos)
        return _serializar(self.dao.buscar_por_id(id_ficha))

    # ---------- R ----------
    def listar(self, estado: str | None = None) -> list:
        if estado is not None:
            estado = estado.strip().upper()
            if estado not in ESTADOS:
                raise ErrorNegocio("El filtro estado debe ser ACTIVO o INACTIVO.", 400)
        return [_serializar(f) for f in self.dao.listar(estado)]

    def obtener(self, id_ficha: int) -> dict:
        return _serializar(self._obtener_o_404(id_ficha))

    # ---------- U ----------
    def reemplazar(self, id_ficha: int, datos) -> dict:
        actual = self._obtener_o_404(id_ficha)
        datos = _limpiar(self._exigir_objeto(datos))
        self._exigir_validos(datos, completo=True)
        datos.setdefault("estado", actual["estado"])
        
        # Si cambiaron el id_programa, verificamos que el nuevo sea válido
        if datos["id_programa"] != actual["id_programa"]:
            self._verificar_programa_valido(datos["id_programa"])
            
        self._verificar_codigo_unico(datos["codigo_ficha"], id_actual=id_ficha)
        self.dao.actualizar(id_ficha, datos)
        return _serializar(self.dao.buscar_por_id(id_ficha))

    def editar(self, id_ficha: int, cambios) -> dict:
        actual = self._obtener_o_404(id_ficha)
        cambios = _limpiar(self._exigir_objeto(cambios))
        if not cambios:
            raise ErrorNegocio("No se envió ningún campo para editar.", 400)
        self._exigir_validos(cambios, completo=False)
        
        final = {**actual, **cambios}
        if final["id_programa"] != actual["id_programa"]:
            self._verificar_programa_valido(final["id_programa"])
            
        self._verificar_codigo_unico(final["codigo_ficha"], id_actual=id_ficha)
        self.dao.actualizar(id_ficha, final)
        return _serializar(self.dao.buscar_por_id(id_ficha))

    # ---------- D ----------
    def eliminar(self, id_ficha: int) -> dict:
        self._obtener_o_404(id_ficha)
        self.dao.desactivar(id_ficha)
        return {"id_ficha": id_ficha, "estado": "INACTIVO"}

    # ---------- Apoyo interno ----------
    def _obtener_o_404(self, id_ficha: int) -> dict:
        ficha = self.dao.buscar_por_id(id_ficha)
        if ficha is None:
            raise ErrorNegocio("Ficha no encontrada.", 404)
        return ficha

    @staticmethod
    def _exigir_objeto(datos) -> dict:
        if not isinstance(datos, dict):
            raise ErrorNegocio("El cuerpo debe ser un JSON válido (un objeto).", 400)
        return datos

    @staticmethod
    def _exigir_validos(datos: dict, completo: bool) -> None:
        errores = validar_ficha(datos, completo)
        if errores:
            raise ErrorNegocio("Datos inválidos.", 400, errores)

    def _verificar_codigo_unico(self, codigo: str, id_actual: int | None = None) -> None:
        otra = self.dao.buscar_por_codigo(codigo)
        if otra and otra["id_ficha"] != id_actual:
            raise ErrorNegocio("Ya existe una ficha con ese código.", 409)

    def _verificar_programa_valido(self, id_programa: int) -> None:
        programa = self.programa_dao.buscar_por_id(id_programa)
        if not programa:
            raise ErrorNegocio(f"El programa con id {id_programa} no existe.", 404)
        if programa["estado"] == "INACTIVO":
            raise ErrorNegocio(f"El programa '{programa['nombre']}' está INACTIVO. No se le pueden asignar fichas.", 409)