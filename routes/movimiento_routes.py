from flask import Blueprint
from controllers.movimiento_controller import MovimientoController

movimiento_bp = Blueprint('movimiento_bp', __name__)

movimiento_bp.route('/', methods=['GET'])(MovimientoController.index)
movimiento_bp.route('/<int:id>', methods=['GET'])(MovimientoController.show)
movimiento_bp.route('/', methods=['POST'])(MovimientoController.store)
movimiento_bp.route('/<int:id>', methods=['PUT'])(MovimientoController.update)
movimiento_bp.route('/<int:id>', methods=['DELETE'])(MovimientoController.destroy)
