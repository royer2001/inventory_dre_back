from flask import Blueprint
from controllers.bien_controller import BienController

bien_bp = Blueprint('bien_bp', __name__)

bien_bp.route('/', methods=['GET'])(BienController.index)
bien_bp.route('/verify-code', methods=['GET'])(BienController.verify_code)
bien_bp.route('/stats', methods=['GET'])(BienController.stats)
bien_bp.route('/<int:id>', methods=['GET'])(BienController.show)
bien_bp.route('/', methods=['POST'])(BienController.store)
bien_bp.route('/<int:id>', methods=['PUT'])(BienController.update)
bien_bp.route('/<int:id>', methods=['DELETE'])(BienController.destroy)
