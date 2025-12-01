from flask import jsonify, request
from models.bien_model import BienModel
from models.movimiento_model import MovimientoModel
from utils.auth_middleware import auth_required

class BienController:

    @staticmethod
    @auth_required(roles=[1, 2]) 
    def index():
        page = request.args.get('page', type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        
        filters = {
            'search': request.args.get('search'),
            'categoria': request.args.get('categoria'),
            'estado': request.args.get('estado'),
            'ubicacion': request.args.get('ubicacion')
        }

        if page:
            bienes = BienModel.get_paginated(page, per_page, filters)
        else:
            bienes = BienModel.get_all()
            
        return jsonify(bienes)

    @staticmethod
    @auth_required(roles=[1, 2])
    def verify_code():
        codigo = request.args.get('codigo')
        if not codigo:
            return jsonify({"message": "Código requerido"}), 400
            
        result = BienModel.check_existence(codigo)
        if result:
            return jsonify({
                "exists": True,
                "bien": result
            })
        return jsonify({"exists": False})

    @staticmethod
    @auth_required(roles=[1, 2]) 
    def stats():
        stats = BienModel.get_stats()
        return jsonify(stats)

    @staticmethod
    @auth_required(roles=[1, 2]) 
    def show(id):
        bien = BienModel.get_by_id(id)
        if bien:
            movimientos = MovimientoModel.get_by_bien_id(id)
            bien['movimientos'] = movimientos
            return jsonify(bien)
        return jsonify({"message": "Bien no encontrado"}), 404

    @staticmethod
    @auth_required(roles=[1, 2])
    def store():
        data = request.get_json()
        BienModel.create(data)
        return jsonify({"message": "Bien creado exitosamente"}), 201
    
    @staticmethod    
    @auth_required(roles=[1, 2])
    def update(id):
        data = request.get_json()
        result = BienModel.update(id, data)
        
        if result.get("success"):
            return jsonify({
                "message": result.get("message"),
                "data": result.get("data")
            }), 200
        else:
            return jsonify({
                "message": result.get("message", "Error al actualizar"),
                "error": result.get("error")
            }), 500

    @staticmethod
    @auth_required(roles=[1])
    def destroy(id):
        BienModel.destroy(id)
        return jsonify({"message": "Bien eliminado exitosamente"}), 200