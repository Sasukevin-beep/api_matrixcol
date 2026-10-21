"""Validadores de Programas y Fichas. Cada función devuelve un error o None."""
import re

ESTADOS = ("ACTIVO", "INACTIVO")

# ---------- Campos de Programa ----------
def validar_nombre_programa(valor) -> str | None:
    if not isinstance(valor, str) or not 3 <= len(valor) <= 100:
        return "Debe tener entre 3 y 100 caracteres."
    return None

def validar_descripcion(valor) -> str | None:
    if not isinstance(valor, str) or len(valor) > 200:
        return "Máximo 200 caracteres."
    return None

# ---------- Campos de Ficha ----------
def validar_id_programa(valor) -> str | None:
    if not isinstance(valor, int) or isinstance(valor, bool) or valor < 1:
        return "Debe ser un número entero mayor que 0."
    return None

def validar_codigo_ficha(valor) -> str | None:
    if not isinstance(valor, str) or not re.fullmatch(r"[A-Z0-9-]{3,20}", valor):
        return "Debe tener entre 3 y 20 caracteres: letras, números o guion."
    return None

def validar_jornada(valor) -> str | None:
    if not isinstance(valor, str) or not 3 <= len(valor) <= 100:
        return "Debe tener entre 3 y 100 caracteres."
    return None

def validar_cupo_maximo(valor) -> str | None:
    if not isinstance(valor, int) or isinstance(valor, bool) or valor < 0:
        return "Debe ser un número entero mayor o igual a 0."
    return None

def validar_estado(valor) -> str | None:
    if valor not in ESTADOS:
        return "Debe ser ACTIVO o INACTIVO."
    return None

# Diccionarios de reglas (campo: ¿obligatorio?, función)
REGLAS_PROGRAMA = {
    "nombre": (True, validar_nombre_programa),
    "descripcion": (False, validar_descripcion),
    "estado": (False, validar_estado),
}

REGLAS_FICHA = {
    "id_programa": (True, validar_id_programa),
    "codigo_ficha": (True, validar_codigo_ficha),
    "jornada": (True, validar_jornada),
    "cupo_maximo": (True, validar_cupo_maximo),
    "estado": (False, validar_estado),
}

def _validar(datos: dict, reglas: dict, completo: bool) -> dict:
    """Validador general que aplica las reglas recibidas por parámetro."""
    errores = {}
    for campo in datos:
        if campo not in reglas:
            errores[campo] = "Campo no permitido."
            
    for campo, (obligatorio, validar) in reglas.items():
        valor = datos.get(campo)
        if valor is None:
            if obligatorio and (completo or campo in datos):
                errores[campo] = "Es obligatorio."
            continue
        error = validar(valor)
        if error:
            errores[campo] = error
    return errores

def validar_programa(datos: dict, completo: bool) -> dict:
    return _validar(datos, REGLAS_PROGRAMA, completo)

def validar_ficha(datos: dict, completo: bool) -> dict:
    return _validar(datos, REGLAS_FICHA, completo)