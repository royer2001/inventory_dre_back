from flask import request, jsonify
from services.jwt_service import JWTService

def auth_required(roles=None):
    def wrapper(func):
        def decorated(*args, **kwargs):
            token = None
            if 'Authorization' in request.headers:
                token = request.headers['Authorization'].split(" ")[1]
            if not token:
                return jsonify({"message": "Token no proporcionado"}), 401

            data = JWTService.verify_token(token)
            if not data:
                return jsonify({"message": "Token inválido o expirado"}), 401

            if roles and data["role_id"] not in roles:
                return jsonify({"message": "Acceso denegado"}), 403

            return func(*args, **kwargs)
        decorated.__name__ = func.__name__
        return decorated
    return wrapper
