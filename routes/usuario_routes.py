from flask import Blueprint
from controllers.usuario_controller import UsuarioController

usuario_bp = Blueprint('usuario_bp', __name__)

usuario_bp.route('/', methods=['GET'])(UsuarioController.index)
usuario_bp.route('/<int:id>', methods=['GET'])(UsuarioController.show)
usuario_bp.route('/', methods=['POST'])(UsuarioController.store)
usuario_bp.route('/<int:id>', methods=['PUT'])(UsuarioController.update)
usuario_bp.route('/<int:id>', methods=['DELETE'])(UsuarioController.destroy)
usuario_bp.route('/roles', methods=['GET'])(UsuarioController.get_roles)
