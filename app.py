"""Punto de entrada de la API de Matrixcol. Ejecutar con: python app.py"""
from flask import Flask, jsonify

from rutas.usuarios_rutas import crear_blueprint as bp_usuarios
from rutas.programas_rutas import crear_blueprint as bp_programas # NUEVO IMPORT

def crear_app(servicio_usu=None, servicio_prog=None) -> Flask:
    """Fábrica de la aplicación."""
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.json.sort_keys = False
    
    app.register_blueprint(bp_usuarios(servicio_usu))
    app.register_blueprint(bp_programas(servicio_prog)) # NUEVO REGISTRO

    @app.get("/")
    def salud():
        """Endpoint de comprobación: confirma que la API está arriba."""
        return jsonify(estado="API de Matrixcol en línea")

    @app.errorhandler(404)
    def no_encontrado(e):
        return jsonify(error="La dirección solicitada no existe."), 404

    @app.errorhandler(405)
    def metodo_no_permitido(e):
        return jsonify(error="Método HTTP no permitido para esta dirección."), 405

    @app.errorhandler(ConnectionError)
    def error_bd(e):
        """Si MySQL no responde, se devuelve 503 sin exponer detalles internos."""
        return jsonify(error="Servicio de base de datos no disponible."), 503

    return app

if __name__ == "__main__":
    crear_app().run(host="127.0.0.1", port=5000, debug=True)
