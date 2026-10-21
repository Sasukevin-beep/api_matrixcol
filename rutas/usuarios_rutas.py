"""Capa de presentación de la API: define los endpoints HTTP de usuarios.
No contiene SQL ni reglas de negocio."""
from flask import Blueprint, jsonify, request

from servicios.servicio_usuarios import ErrorNegocio, ServicioUsuarios

def crear_blueprint(servicio: ServicioUsuarios | None = None) -> Blueprint:
    """Crea el Blueprint de usuarios."""
    bp = Blueprint("usuarios", __name__, url_prefix="/api/usuarios")
    servicio = servicio or ServicioUsuarios()

    @bp.errorhandler(ErrorNegocio)
    def manejar_error_negocio(e):
        """Un solo lugar que traduce cualquier ErrorNegocio a respuesta HTTP."""
        cuerpo = {"error": e.mensaje}
        if e.detalles:
            cuerpo["detalles"] = e.detalles
        return jsonify(cuerpo), e.codigo

    @bp.post("")
    def crear():
        usuario = servicio.crear(request.get_json(silent=True))
        return (jsonify(mensaje="Usuario creado.", usuario=usuario), 201,
                {"Location": f"/api/usuarios/{usuario['id_usuario']}"})

    @bp.get("")
    def listar():
        usuarios = servicio.listar(request.args.get("estado"))
        return jsonify(total=len(usuarios), usuarios=usuarios), 200

    @bp.get("/<int:id_usuario>")
    def obtener(id_usuario):
        return jsonify(usuario=servicio.obtener(id_usuario)), 200

    @bp.put("/<int:id_usuario>")
    def reemplazar(id_usuario):
        usuario = servicio.reemplazar(id_usuario, request.get_json(silent=True))
        return jsonify(mensaje="Usuario modificado.", usuario=usuario), 200

    @bp.patch("/<int:id_usuario>")
    def editar(id_usuario):
        usuario = servicio.editar(id_usuario, request.get_json(silent=True))
        return jsonify(mensaje="Usuario editado.", usuario=usuario), 200

    @bp.delete("/<int:id_usuario>")
    def eliminar(id_usuario):
        resultado = servicio.eliminar(id_usuario)
        return jsonify(mensaje="Usuario eliminado (queda INACTIVO).", **resultado), 200

    return bp