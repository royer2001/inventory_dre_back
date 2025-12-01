from flask import send_file, request, jsonify
from models.bien_model import BienModel
from utils.barcode_generator import generate_barcodes_pdf
from database.connection import get_connection
from datetime import datetime
import os


class BarcodeController:
    
    @staticmethod
    def get_offices():
        """Obtiene lista única de oficinas desde movimientos.ubicacion_actual."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Obtener ubicaciones únicas de los últimos movimientos
            cursor.execute("""
                SELECT DISTINCT ubicacion_actual
                FROM movimientos
                WHERE ubicacion_actual IS NOT NULL 
                  AND ubicacion_actual != ''
                ORDER BY ubicacion_actual ASC
            """)
            
            offices = [row['ubicacion_actual'] for row in cursor.fetchall()]
            conn.close()
            
            return jsonify({
                'success': True,
                'offices': offices
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def get_bienes_for_barcode():
        """
        Obtiene bienes con su ubicación actual desde el último movimiento.
        
        Query params:
        - office: Filtrar por oficina
        - search: Búsqueda global
        - page: Página actual (opcional)
        - per_page: Items por página (opcional)
        """
        try:
            office = request.args.get('office', '')
            search = request.args.get('search', '')
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 50))
            
            conn = get_connection()
            cursor = conn.cursor()
            
            # Query simplificada: obtener último movimiento por bien_id
            base_query = """
                SELECT 
                    b.codigo_completo,
                    b.codigo_patrimonio,
                    b.codigo_interno,
                    b.detalle_bien,
                    b.descripcion,
                    COALESCE(
                        (SELECT ubicacion_actual 
                         FROM movimientos m 
                         WHERE m.bien_id = b.id 
                           AND m.ubicacion_actual IS NOT NULL
                         ORDER BY m.id DESC 
                         LIMIT 1),
                        'SIN UBICACIÓN'
                    ) as ubicacion_nombre,
                    COALESCE(b.tipo_origen, 'SIGA') as fuente,
                    COALESCE(b.tipo_origen, 'SIGA') as tipo_registro
                FROM bienes b
                WHERE b.deleted_at IS NULL
            """
            
            params = []
            
            # Filtro por oficina
            if office:
                base_query += """ AND (
                    SELECT ubicacion_actual 
                    FROM movimientos m 
                    WHERE m.bien_id = b.id 
                      AND m.ubicacion_actual IS NOT NULL
                    ORDER BY m.id DESC 
                    LIMIT 1
                ) = %s"""
                params.append(office)
            
            # Búsqueda global
            if search:
                base_query += """ AND (
                    b.codigo_completo LIKE %s OR
                    b.codigo_patrimonio LIKE %s OR
                    b.codigo_interno LIKE %s OR
                    b.detalle_bien LIKE %s OR
                    b.descripcion LIKE %s OR
                    (SELECT ubicacion_actual 
                     FROM movimientos m 
                     WHERE m.bien_id = b.id 
                       AND m.ubicacion_actual IS NOT NULL
                     ORDER BY m.id DESC 
                     LIMIT 1) LIKE %s
                )"""
                search_param = f"%{search}%"
                params.extend([search_param] * 6)
            
            # Ordenar por ubicación y código
            base_query += """ ORDER BY 
                (SELECT ubicacion_actual 
                 FROM movimientos m 
                 WHERE m.bien_id = b.id 
                   AND m.ubicacion_actual IS NOT NULL
                 ORDER BY m.id DESC 
                 LIMIT 1),
                b.codigo_completo
            """
            
            # Ejecutar query completa para contar total
            cursor.execute(base_query, params)
            all_results = cursor.fetchall()
            total = len(all_results)
            
            # Paginación
            offset = (page - 1) * per_page
            paginated_query = base_query + f" LIMIT %s OFFSET %s"
            params.extend([per_page, offset])
            
            cursor.execute(paginated_query, params)
            rows = cursor.fetchall()
            conn.close()
            
            bienes = []
            for row in rows:
                bienes.append({
                    'codigo_completo': row['codigo_completo'] or '',
                    'codigo_patrimonio': row['codigo_patrimonio'] or '',
                    'codigo_interno': row['codigo_interno'] or '',
                    'detalle_bien': row['detalle_bien'] or '',
                    'descripcion': row['descripcion'] or '',
                    'oficina': row['ubicacion_nombre'] or 'SIN UBICACIÓN',
                    'fuente': row['fuente'] or 'SIGA',
                    'tipo_registro': row['tipo_registro'] or 'SIGA'
                })
            
            return jsonify({
                'success': True,
                'data': bienes,
                'pagination': {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (total + per_page - 1) // per_page
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def generate_pdf_by_selection():
        """
        Genera PDF de códigos de barras para una selección personalizada de bienes.
        
        POST body:
        {
            "bienes": [
                {
                    "codigo": "...",
                    "detalle_bien": "...",
                    "tipo_registro": "...",
                    "oficina": "..."
                },
                ...
            ]
        }
        """
        try:
            data = request.json
            bienes = data.get('bienes', [])
            
            if not bienes:
                return jsonify({
                    'success': False,
                    'error': 'No se proporcionaron bienes para generar'
                }), 400
            
            # Preparar registros para el generador
            records = []
            for bien in bienes:
                records.append((
                    bien.get('codigo', ''),
                    bien.get('detalle_bien', ''),
                    bien.get('tipo_registro', 'SIGA'),
                    bien.get('oficina', 'SIN UBICACIÓN')
                ))
            
            # Generar PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"seleccion_personalizada_{timestamp}.pdf"
            
            pdf_path = generate_barcodes_pdf(
                records=records,
                output_filename=output_filename,
                selected_office="SELECCION_PERSONALIZADA"
            )
            
            return send_file(
                pdf_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=output_filename
            )
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def generate_pdf_by_offices():
        """
        Genera PDF de códigos de barras para múltiples oficinas seleccionadas.
        
        POST body:
        {
            "offices": ["Oficina 1", "Oficina 2", ...]
        }
        """
        try:
            data = request.json
            offices = data.get('offices', [])
            
            if not offices:
                return jsonify({
                    'success': False,
                    'error': 'No se proporcionaron oficinas para generar'
                }), 400
            
            conn = get_connection()
            cursor = conn.cursor()
            
            # Query con subconsulta para último movimiento
            placeholders = ','.join(['%s'] * len(offices))
            query = f"""
                SELECT 
                    b.codigo_completo,
                    b.detalle_bien,
                    COALESCE(b.tipo_origen, 'SIGA') as tipo_registro,
                    COALESCE(
                        (SELECT ubicacion_actual 
                         FROM movimientos m 
                         WHERE m.bien_id = b.id 
                           AND m.ubicacion_actual IS NOT NULL
                         ORDER BY m.id DESC 
                         LIMIT 1),
                        'SIN UBICACIÓN'
                    ) as ubicacion_nombre
                FROM bienes b
                WHERE b.deleted_at IS NULL
                  AND (SELECT ubicacion_actual 
                       FROM movimientos m 
                       WHERE m.bien_id = b.id 
                         AND m.ubicacion_actual IS NOT NULL
                       ORDER BY m.id DESC 
                       LIMIT 1) IN ({placeholders})
                ORDER BY ubicacion_nombre, b.codigo_completo
            """
            
            cursor.execute(query, offices)
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return jsonify({
                    'success': False,
                    'error': 'No se encontraron bienes para las oficinas seleccionadas'
                }), 404
            
            # Preparar registros
            records = [(row['codigo_completo'], row['detalle_bien'], 
                       row['tipo_registro'] or 'SIGA', row['ubicacion_nombre']) 
                      for row in rows]
            
            # Generar PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            office_label = "_".join(offices[:3]) if len(offices) <= 3 else "SELECCION_MULTIPLE"
            output_filename = f"oficinas_{office_label}_{timestamp}.pdf"
            
            pdf_path = generate_barcodes_pdf(
                records=records,
                output_filename=output_filename,
                selected_office=office_label
            )
            
            return send_file(
                pdf_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=output_filename
            )
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def generate_pdf_by_filter():
        """
        Genera PDF de códigos de barras basado en filtro actual.
        
        POST body:
        {
            "office": "...",  // opcional
            "search": "..."   // opcional
        }
        """
        try:
            data = request.json
            office = data.get('office', '')
            search = data.get('search', '')
            
            conn = get_connection()
            cursor = conn.cursor()
            
            # Base query con subconsulta para último movimiento
            query = """
                SELECT 
                    b.codigo_completo,
                    b.detalle_bien,
                    COALESCE(b.tipo_origen, 'SIGA') as tipo_registro,
                    COALESCE(
                        (SELECT ubicacion_actual 
                         FROM movimientos m 
                         WHERE m.bien_id = b.id 
                           AND m.ubicacion_actual IS NOT NULL
                         ORDER BY m.id DESC 
                         LIMIT 1),
                        'SIN UBICACIÓN'
                    ) as ubicacion_nombre
                FROM bienes b
                WHERE b.deleted_at IS NULL
            """
            
            params = []
            
            # Filtro por oficina
            if office:
                query += """ AND (
                    SELECT ubicacion_actual 
                    FROM movimientos m 
                    WHERE m.bien_id = b.id 
                      AND m.ubicacion_actual IS NOT NULL
                    ORDER BY m.id DESC 
                    LIMIT 1
                ) = %s"""
                params.append(office)
            
            # Búsqueda global
            if search:
                query += """ AND (
                    b.codigo_completo LIKE %s OR
                    b.detalle_bien LIKE %s OR
                    b.descripcion LIKE %s OR
                    (SELECT ubicacion_actual 
                     FROM movimientos m 
                     WHERE m.bien_id = b.id 
                       AND m.ubicacion_actual IS NOT NULL
                     ORDER BY m.id DESC 
                     LIMIT 1) LIKE %s
                )"""
                search_param = f"%{search}%"
                params.extend([search_param] * 4)
            
            query += """ ORDER BY 
                (SELECT ubicacion_actual 
                 FROM movimientos m 
                 WHERE m.bien_id = b.id 
                   AND m.ubicacion_actual IS NOT NULL
                 ORDER BY m.id DESC 
                 LIMIT 1),
                b.codigo_completo
            """
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return jsonify({
                    'success': False,
                    'error': 'No se encontraron bienes con los filtros aplicados'
                }), 404
            
            # Preparar registros
            records = [(row['codigo_completo'], row['detalle_bien'], 
                       row['tipo_registro'] or 'SIGA', row['ubicacion_nombre']) 
                      for row in rows]
            
            # Generar PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            office_label = office if office else "TODOS"
            output_filename = f"filtro_{office_label}_{timestamp}.pdf"
            
            pdf_path = generate_barcodes_pdf(
                records=records,
                output_filename=output_filename,
                selected_office=office_label
            )
            
            return send_file(
                pdf_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=output_filename
            )
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
