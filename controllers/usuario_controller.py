from flask import jsonify, request
from models.user_model import UserModel
from models.role_model import RoleModel
from utils.auth_middleware import auth_required

class UsuarioController:

    @staticmethod
    @auth_required(roles=[1])
    def index():
        users = UserModel.get_all()
        return jsonify(users)

    @staticmethod
    @auth_required(roles=[1])
    def show(id):
        user = UserModel.find_by_id(id)
        if user:
            return jsonify(user)
        return jsonify({"message": "Usuario no encontrado"}), 404

    @staticmethod
    @auth_required(roles=[1])
    def store():
        data = request.get_json()
        
        # Basic validation
        required_fields = ["nombre", "dni", "contrasena", "rol_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"message": f"El campo {field} es requerido"}), 400

        # Check if DNI or Email or Usuario already exists
        if UserModel.find_by_dni(data.get("dni")):
            return jsonify({"message": "El DNI ya está registrado"}), 400
        
        if data.get("correo") and UserModel.find_by_email(data.get("correo")):
             return jsonify({"message": "El correo ya está registrado"}), 400

        if UserModel.create(data):
            return jsonify({"message": "Usuario creado exitosamente"}), 201
        return jsonify({"message": "Error al crear usuario"}), 500

    @staticmethod
    @auth_required(roles=[1])
    def update(id):
        data = request.get_json()
        
        # Check existence
        user = UserModel.find_by_id(id)
        if not user:
             return jsonify({"message": "Usuario no encontrado"}), 404

        if UserModel.update(id, data):
            return jsonify({"message": "Usuario actualizado exitosamente"}), 200
        return jsonify({"message": "Error al actualizar usuario"}), 500

    @staticmethod
    @auth_required(roles=[1])
    def destroy(id):
        if UserModel.delete(id):
            return jsonify({"message": "Usuario eliminado exitosamente"}), 200
        return jsonify({"message": "Error al eliminar usuario"}), 500

    @staticmethod
    @auth_required(roles=[1])
    def get_roles():
        roles = RoleModel.get_all()
        return jsonify(roles)
