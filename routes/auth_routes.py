from flask import Blueprint
from controllers.auth_controller import AuthController

auth_bp = Blueprint('auth_bp', __name__)

auth_bp.route('/login/', methods=['POST'])(AuthController.login)
auth_bp.route('/register/', methods=['POST'])(AuthController.register)
auth_bp.route('/me/', methods=['GET'])(AuthController.get_current_user)
auth_bp.route('/change-password/', methods=['POST'])(AuthController.change_password)

# auth_bp.route('/logout/', methods=['POST'])(AuthController.logout)
