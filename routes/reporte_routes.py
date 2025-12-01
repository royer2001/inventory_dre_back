from flask import Blueprint
from controllers.reporte_controller import ReporteController

reporte_bp = Blueprint('reporte_bp', __name__)

@reporte_bp.route('/bienes-responsable', methods=['POST'])
def generar_reporte_bienes_responsable():
    return ReporteController.generar_excel_bienes_responsable()

@reporte_bp.route('/options', methods=['GET'])
def get_report_options():
    return ReporteController.get_options()

@reporte_bp.route('/recent-activity', methods=['GET'])
def get_recent_activity():
    return ReporteController.get_recent_activity()

@reporte_bp.route('/movements-chart', methods=['GET'])
def get_movements_chart():
    return ReporteController.get_movements_chart()

@reporte_bp.route('/detalles-options', methods=['GET'])
def get_detalles_options():
    return ReporteController.get_detalles_options()

@reporte_bp.route('/pdf-bienes-estado', methods=['POST'])
def generar_pdf_bienes_estado():
    return ReporteController.generar_pdf_bienes_estado()
