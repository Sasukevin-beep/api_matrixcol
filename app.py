"""Punto de entrada de la API de Matrixcol. Ejecutar con: python app.py"""
from flask import Flask, jsonify

from rutas.usuarios_rutas import crear_blueprint

def crear_app(servicio=None) -> Flask:
    """Fábrica de la aplicación."""
    app = Flask(__name__)
    app.json.ensure_ascii = False   # Que las tildes y la ñ se vean tal cual en el JSON.
    app.json.sort_keys = False      # Respeta el orden en que escribimos las claves.
    app.register_blueprint(crear_blueprint(servicio))

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