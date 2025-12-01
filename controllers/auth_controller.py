from flask import jsonify, request
from models.user_model import UserModel
from services.jwt_service import JWTService
import bcrypt
import json


class AuthController:

    @staticmethod
    def login():
        try:
            data = request.get_json(silent=True)

            if isinstance(data, str):
                data = json.loads(data)

            if not data:
                return jsonify({"message": "No se recibieron datos"}), 400

            dni = data.get("dni")
            password = data.get("contrasena")

            if not dni or not password:
                return jsonify({"message": "DNI y contraseña son requeridos"}), 400

            user = UserModel.find_by_dni(dni)
            if not user or not bcrypt.checkpw(password.encode('utf-8'), user["contrasena"].encode('utf-8')):
                return jsonify({"message": "Credenciales inválidas"}), 401

            token = JWTService.create_token(
                {"id": user["id"], "role_id": user["rol_id"]})
            return jsonify({"access_token": token, "user": user}), 200

        except Exception as e:
            print("Error en login:", e)
            return jsonify({"message": "Error interno en el servidor"}), 500

    @staticmethod
    def get_current_user():
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"message": "Token es requerido"}), 400

            token = auth_header.split(" ")[1]
            payload = JWTService.verify_token(token)
            if not payload:
                return jsonify({"message": "Token inválido"}), 401

            user = UserModel.find_by_id(payload["id"])
            if not user:
                return jsonify({"message": "Usuario no encontrado"}), 404

            return jsonify({"user": user}), 200

        except Exception as e:
            print("Error al obtener el usuario actual:", e)
            return jsonify({"message": "Error interno en el servidor"}), 500

    @staticmethod
    def register():
        data = request.get_json()
        UserModel.create_user(
            data["nombre"], data["dni"], data["contrasena"], data["rol_id"]
        )
        return jsonify({"message": "Usuario registrado exitosamente"}), 201
