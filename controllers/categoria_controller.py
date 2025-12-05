from flask import jsonify
from models.categoria_model import CategoriaModel
from utils.auth_middleware import auth_required


class CategoriaController:

    @staticmethod
    @auth_required(roles=[1, 2])
    def index():
        """Lista todas las categorías"""
        categorias = CategoriaModel.get_all()
        return jsonify(categorias)

    @staticmethod
    @auth_required(roles=[1, 2])
    def show(id):
        """Muestra una categoría específica"""
        categoria = CategoriaModel.get_by_id(id)
        if categoria:
            return jsonify(categoria)
        return jsonify({"message": "Categoría no encontrada"}), 404
