"""Validadores de entrada para la tabla Usuario. 
Cada función devuelve un mensaje de error o None si todo está bien."""
import re

TIPOS_DOCUMENTO = ("CC", "CE", "NIT", "PP", "TI")
ESTADOS = ("ACTIVO", "INACTIVO")

def validar_tipo_documento(valor) -> str | None:
    if valor not in TIPOS_DOCUMENTO:
        return "Debe ser uno de: CC, CE, NIT, PP, TI."
    return None

def validar_numero_documento(valor) -> str | None:
    if not isinstance(valor, str) or not re.fullmatch(r"[0-9A-Za-z-]{5,20}", valor):
        return "Debe tener entre 5 y 20 caracteres (letras, números o guion)."
    return None

def validar_nombre(valor) -> str | None:
    if not isinstance(valor, str) or not 3 <= len(valor) <= 100:
        return "Debe tener entre 3 y 100 caracteres."
    return None

def validar_correo(valor) -> str | None:
    if not isinstance(valor, str) or len(valor) > 100 \
            or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", valor):
        return "No es un correo válido (ejemplo: usuario@correo.com)."
    return None

def validar_telefono(valor) -> str | None:
    if not isinstance(valor, str) or not re.fullmatch(r"\+?\d{7,15}", valor):
        return "Debe tener entre 7 y 15 dígitos (puede iniciar con +)."
    return None

def validar_direccion(valor) -> str | None:
    if not isinstance(valor, str) or len(valor) > 150:
        return "Máximo 150 caracteres."
    return None

def validar_ciudad(valor) -> str | None:
    if not isinstance(valor, str) or len(valor) > 60:
        return "Máximo 60 caracteres."
    return None

def validar_estado(valor) -> str | None:
    if valor not in ESTADOS:
        return "Debe ser ACTIVO o INACTIVO."
    return None

# campo: (¿obligatorio?, función que lo valida)
REGLAS = {
    "tipo_documento": (True, validar_tipo_documento),
    "numero_documento": (True, validar_numero_documento),
    "nombre": (True, validar_nombre),
    "correo": (True, validar_correo),
    "telefono": (True, validar_telefono),
    "direccion": (False, validar_direccion),
    "ciudad": (False, validar_ciudad),
    "estado": (False, validar_estado),
}

def validar_usuario(datos: dict, completo: bool) -> dict:
    """Valida los campos recibidos y devuelve {campo: mensaje} con los errores.
    completo=True  -> se exigen todos los campos obligatorios (POST y PUT).
    completo=False -> solo se validan los campos enviados (PATCH).
    """
    errores = {}

    for campo in datos:
        if campo not in REGLAS:
            errores[campo] = "Campo no permitido."

    for campo, (obligatorio, validar) in REGLAS.items():
        valor = datos.get(campo)
        if valor is None:
            # Falta el campo, o llegó como null.
            if obligatorio and (completo or campo in datos):
                errores[campo] = "Es obligatorio."
            continue
        error = validar(valor)
        if error:
            errores[campo] = error

    return errores