from flask import Blueprint
from controllers.barcode_controller import BarcodeController

barcode_bp = Blueprint('barcode_bp', __name__)

# Obtener lista de oficinas
@barcode_bp.route('/offices', methods=['GET'])
def get_offices():
    """GET /api/barcode/offices - Obtiene lista de oficinas disponibles"""
    return BarcodeController.get_offices()


# Obtener bienes para códigos de barras
@barcode_bp.route('/bienes', methods=['GET'])
def get_bienes_for_barcode():
    """
    GET /api/barcode/bienes?office=X&search=Y&page=1&per_page=50
    Obtiene bienes filtrados para generación de códigos de barras
    """
    return BarcodeController.get_bienes_for_barcode()


# Generar PDF por selección personalizada
@barcode_bp.route('/generate/selection', methods=['POST'])
def generate_pdf_by_selection():
    """
    POST /api/barcode/generate/selection
    Body: {
        "bienes": [
            {
                "codigo": "...",
                "detalle_bien": "...",
                "tipo_registro": "...",
                "oficina": "..."
            }
        ]
    }
    """
    return BarcodeController.generate_pdf_by_selection()


# Generar PDF por múltiples oficinas
@barcode_bp.route('/generate/offices', methods=['POST'])
def generate_pdf_by_offices():
    """
    POST /api/barcode/generate/offices
    Body: {
        "offices": ["Oficina 1", "Oficina 2", ...]
    }
    """
    return BarcodeController.generate_pdf_by_offices()


# Generar PDF por filtro actual
@barcode_bp.route('/generate/filter', methods=['POST'])
def generate_pdf_by_filter():
    """
    POST /api/barcode/generate/filter
    Body: {
        "office": "...",  // opcional
        "search": "..."   // opcional
    }
    """
    return BarcodeController.generate_pdf_by_filter()
