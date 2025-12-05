from flask import Blueprint
from controllers.categoria_controller import CategoriaController

categoria_bp = Blueprint('categoria_bp', __name__)

categoria_bp.route('/', methods=['GET'])(CategoriaController.index)
categoria_bp.route('/<int:id>', methods=['GET'])(CategoriaController.show)
