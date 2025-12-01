from flask import jsonify, request
from models.movimiento_model import MovimientoModel
from utils.auth_middleware import auth_required

class MovimientoController:

    @staticmethod
    @auth_required(roles=[1, 2]) 
    def index():
        movimientos = MovimientoModel.get_all()
        return jsonify(movimientos)

    @staticmethod
    @auth_required(roles=[1, 2]) 
    def show(id):
        movimiento = MovimientoModel.get_by_id(id)
        if movimiento:
            return jsonify(movimiento)
        return jsonify({"message": "Movimiento no encontrado"}), 404

    @staticmethod
    @auth_required(roles=[1, 2])
    def store():
        data = request.get_json()
        result = MovimientoModel.create(data)
        if result.get("success"):
            return jsonify({"message": result.get("message")}), 201
        return jsonify({"message": result.get("error")}), 500
    
    @staticmethod    
    @auth_required(roles=[1, 2])
    def update(id):
        data = request.get_json()
        MovimientoModel.update(id, data)
        return jsonify({"message": "Movimiento actualizado exitosamente"}), 200

    @staticmethod
    @auth_required(roles=[1])
    def destroy(id):
        MovimientoModel.destroy(id)
        return jsonify({"message": "Movimiento eliminado exitosamente"}), 200