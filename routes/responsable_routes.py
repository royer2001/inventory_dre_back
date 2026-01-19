from flask import Blueprint, jsonify, request
from models.responsable_model import ResponsableModel

responsable_bp = Blueprint('responsables', __name__)


@responsable_bp.route('/responsables', methods=['GET'])
def get_all():
    """Obtiene todos los responsables activos"""
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        
        if include_inactive:
            responsables = ResponsableModel.get_all_with_inactive()
        else:
            responsables = ResponsableModel.get_all()
        
        # Formatear respuesta para el frontend (nombre_normalizado como "nombre")
        formatted = []
        for r in responsables:
            formatted.append({
                'id': r['id'],
                'nombre': r['nombre_normalizado'],  # Usar nombre normalizado
                'nombre_original': r['nombre_original'],
                'area': r['area'],
                'tipo_contrato': r['tipo_contrato'],
                'activo': r['activo']
            })
        
        return jsonify(formatted), 200
    except Exception as e:
        print(f"❌ Error al obtener responsables: {e}")
        return jsonify({"error": str(e)}), 500


@responsable_bp.route('/responsables/<int:id>', methods=['GET'])
def get_by_id(id):
    """Obtiene un responsable por ID"""
    try:
        responsable = ResponsableModel.get_by_id(id)
        if responsable:
            return jsonify({
                'id': responsable['id'],
                'nombre': responsable['nombre_normalizado'],
                'nombre_original': responsable['nombre_original'],
                'area': responsable['area'],
                'tipo_contrato': responsable['tipo_contrato'],
                'activo': responsable['activo']
            }), 200
        return jsonify({"error": "Responsable no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@responsable_bp.route('/responsables', methods=['POST'])
def create():
    """Crea un nuevo responsable"""
    try:
        data = request.get_json()
        
        if not data.get('nombre_original'):
            return jsonify({"success": False, "error": "El nombre es requerido"}), 400
        
        result = ResponsableModel.create(data)
        
        if result['success']:
            return jsonify(result), 201
        return jsonify(result), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@responsable_bp.route('/responsables/<int:id>', methods=['PUT'])
def update(id):
    """Actualiza un responsable"""
    try:
        data = request.get_json()
        result = ResponsableModel.update(id, data)
        
        if result['success']:
            return jsonify(result), 200
        return jsonify(result), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@responsable_bp.route('/responsables/<int:id>/toggle', methods=['PATCH'])
def toggle_active(id):
    """Activa/desactiva un responsable"""
    try:
        result = ResponsableModel.toggle_active(id)
        
        if result['success']:
            return jsonify(result), 200
        return jsonify(result), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@responsable_bp.route('/responsables/search', methods=['GET'])
def search():
    """Busca responsables por nombre"""
    try:
        query = request.args.get('q', '')
        
        if len(query) < 2:
            return jsonify([]), 200
        
        responsables = ResponsableModel.search(query)
        
        formatted = []
        for r in responsables:
            formatted.append({
                'id': r['id'],
                'nombre': r['nombre_normalizado'],
                'nombre_original': r['nombre_original'],
                'area': r['area']
            })
        
        return jsonify(formatted), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
