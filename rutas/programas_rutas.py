"""Capa de presentación: endpoints HTTP para Programas."""
from flask import Blueprint, jsonify, request

from servicios.servicio_programas import ErrorNegocio, ServicioProgramas

def crear_blueprint(servicio: ServicioProgramas | None = None) -> Blueprint:
    bp = Blueprint("programas", __name__, url_prefix="/api/programas")
    servicio = servicio or ServicioProgramas()

    @bp.errorhandler(ErrorNegocio)
    def manejar_error_negocio(e):
        cuerpo = {"error": e.mensaje}
        if e.detalles:
            cuerpo["detalles"] = e.detalles
        return jsonify(cuerpo), e.codigo

    @bp.post("")
    def crear():
        programa = servicio.crear(request.get_json(silent=True))
        return (jsonify(mensaje="Programa creado.", programa=programa), 201,
                {"Location": f"/api/programas/{programa['id_programa']}"})

    @bp.get("")
    def listar():
        programas = servicio.listar(request.args.get("estado"))
        return jsonify(total=len(programas), programas=programas), 200

    @bp.get("/<int:id_programa>")
    def obtener(id_programa):
        return jsonify(programa=servicio.obtener(id_programa)), 200

    @bp.put("/<int:id_programa>")
    def reemplazar(id_programa):
        programa = servicio.reemplazar(id_programa, request.get_json(silent=True))
        return jsonify(mensaje="Programa modificado.", programa=programa), 200

    @bp.patch("/<int:id_programa>")
    def editar(id_programa):
        programa = servicio.editar(id_programa, request.get_json(silent=True))
        return jsonify(mensaje="Programa editado.", programa=programa), 200

    @bp.delete("/<int:id_programa>")
    def eliminar(id_programa):
        resultado = servicio.eliminar(id_programa)
        return jsonify(mensaje="Programa eliminado (queda INACTIVO).", **resultado), 200

    return bp