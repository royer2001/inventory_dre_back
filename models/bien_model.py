from database.connection import get_connection
from datetime import datetime


class BienModel:

    @staticmethod
    def get_all():
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                SELECT 
                    b.*,
                    c.nombre AS categoria_nombre,
                    u.nombre AS inventariador_nombre,
                    (SELECT m.responsable FROM movimientos m WHERE m.bien_id = b.id ORDER BY m.fecha DESC, m.id DESC LIMIT 1) AS responsable_nombre,
                    b.estado AS estado_nombre,
                    (SELECT m.ubicacion_actual FROM movimientos m WHERE m.bien_id = b.id ORDER BY m.fecha DESC, m.id DESC LIMIT 1) AS ubicacion_nombre
                FROM bienes b
                LEFT JOIN categorias c 
                    ON b.categoria_id = c.id
                LEFT JOIN usuarios u
                    ON b.inventariador_id = u.id
                WHERE b.deleted_at IS NULL;
                ''')
            result = cursor.fetchall()
        conn.close()
        return result

    @staticmethod
    def get_stats():
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN estado = 'BUENO' THEN 1 ELSE 0 END) as buenos,
                    SUM(CASE WHEN estado = 'REGULAR' THEN 1 ELSE 0 END) as regulares,
                    SUM(CASE WHEN estado = 'MALO' THEN 1 ELSE 0 END) as malos
                FROM bienes
                WHERE deleted_at IS NULL
            """)
            result = cursor.fetchone()
        conn.close()
        
        # Ensure values are integers (handle None if no records)
        return {
            "total": int(result['total']) if result['total'] else 0,
            "buenos": int(result['buenos']) if result['buenos'] else 0,
            "regulares": int(result['regulares']) if result['regulares'] else 0,
            "malos": int(result['malos']) if result['malos'] else 0
        }

    @staticmethod
    def get_paginated(page, per_page, filters=None):
        offset = (page - 1) * per_page
        conn = get_connection()
        
        where_clauses = ["b.deleted_at IS NULL"]
        params = []

        if filters:
            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                where_clauses.append("(b.descripcion LIKE %s OR b.marca LIKE %s OR b.modelo LIKE %s OR b.codigo_patrimonio LIKE %s OR b.codigo_interno LIKE %s)")
                params.extend([search_term] * 5)
            
            if filters.get('estado'):
                where_clauses.append("b.estado = %s")
                params.append(filters['estado'])

            if filters.get('ubicacion'):
                 where_clauses.append("(SELECT m.ubicacion_actual FROM movimientos m WHERE m.bien_id = b.id ORDER BY m.fecha DESC, m.id DESC LIMIT 1) = %s")
                 params.append(filters['ubicacion'])

        where_str = " AND ".join(where_clauses)

        with conn.cursor() as cursor:
            # Get total count
            count_query = f"""
                SELECT COUNT(*) as total
                FROM bienes b
                LEFT JOIN categorias c ON b.categoria_id = c.id
                WHERE {where_str}
            """
            cursor.execute(count_query, tuple(params))
            total = cursor.fetchone()['total']

            # Get paginated items
            data_query = f"""
                SELECT 
                    b.*,
                    c.nombre AS categoria_nombre,
                    u.nombre AS inventariador_nombre,
                    (SELECT m.responsable FROM movimientos m WHERE m.bien_id = b.id ORDER BY m.fecha DESC, m.id DESC LIMIT 1) AS responsable_nombre,
                    b.estado AS estado_nombre,
                    (SELECT m.ubicacion_actual FROM movimientos m WHERE m.bien_id = b.id ORDER BY m.fecha DESC, m.id DESC LIMIT 1) AS ubicacion_nombre
                FROM bienes b
                LEFT JOIN categorias c 
                    ON b.categoria_id = c.id
                LEFT JOIN usuarios u
                    ON b.inventariador_id = u.id
                WHERE {where_str}
                LIMIT %s OFFSET %s;
            """
            cursor.execute(data_query, tuple(params + [per_page, offset]))
            result = cursor.fetchall()
        conn.close()
        
        return {
            "data": result,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 0
            }
        }

    @staticmethod
    def get_by_id(id):
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM bienes WHERE id = %s", (id,))
            result = cursor.fetchone()
        conn.close()
        return result

    @staticmethod
    def check_existence(codigo_completo):
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    b.id,
                    b.descripcion,
                    b.detalle_bien,
                    b.codigo_patrimonio,
                    b.codigo_interno,
                    b.codigo_completo,
                    b.tipo_origen,
                    (SELECT m.responsable FROM movimientos m WHERE m.bien_id = b.id ORDER BY m.fecha DESC, m.id DESC LIMIT 1) AS responsable,
                    (SELECT m.ubicacion_actual FROM movimientos m WHERE m.bien_id = b.id ORDER BY m.fecha DESC, m.id DESC LIMIT 1) AS ubicacion
                FROM bienes b
                WHERE b.codigo_completo = %s
                AND b.deleted_at IS NULL
            """, (codigo_completo,))
            result = cursor.fetchone()
        conn.close()
        return result

    @staticmethod
    def create(data):
        conn = None
        try:
            conn = get_connection()
            with conn.cursor() as cursor:

                # Generar codigo_completo
                codigo_patrimonio = data.get("codigo_patrimonio", "")
                codigo_interno = data.get("codigo_interno", "")
                tipo_origen = data.get("tipo_origen", "SIGA")
                
                codigo_completo = f"{codigo_patrimonio}{codigo_interno}"
                if tipo_origen == 'SOBRANTE':
                    codigo_completo += "S"

                query = """
                    INSERT INTO bienes (
                        codigo_patrimonio, 
                        codigo_interno,
                        codigo_completo,
                        detalle_bien, 
                        descripcion, 
                        categoria_id, 
                        marca, 
                        modelo, 
                        numero_serie,
                        dimension, 
                        color, 
                        fecha_adquisicion, 
                        fecha_asignacion, 
                        fecha_retiro, 
                        tipo_origen, 
                        ubicacion_id, 
                        estado, 
                        responsable_id, 
                        tipo_modalidad,
                        inventariador_id, 
                        observacion, 
                        codigo_barras,
                        codigo_patrimonial,
                        oficina,
                        fuente,
                        tipo_registro
                    ) 
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, %s
                    );
                """

                values = (
                    codigo_patrimonio,
                    codigo_interno,
                    codigo_completo,
                    data.get("detalle_bien", ""),
                    data.get("descripcion", ""),
                    data.get("categoria_id") or None,
                    data.get("marca", ""),
                    data.get("modelo", ""),
                    data.get("numero_serie", ""),
                    data.get("dimension", ""),
                    data.get("color", ""),
                    data.get("fecha_adquisicion") or None,
                    data.get("fecha_asignacion") or None,
                    data.get("fecha_retiro") or None,
                    tipo_origen,
                    None, # ubicacion_id
                    data.get("estado", "BUENO"),
                    None, # responsable_id
                    data.get("tipo_modalidad"),
                    data.get("inventariador_id") or None,
                    data.get("observacion"),
                    data.get("codigo_barras", ""),
                    data.get("codigo_patrimonial", ""),
                    data.get("oficina", ""),
                    data.get("fuente", ""),
                    data.get("tipo_registro", "")
                )

                cursor.execute(query, values)
                bien_id = cursor.lastrowid

                # Registrar movimiento inicial
                responsable_nombre = data.get("responsable")
                ubicacion_nombre = data.get("ubicacion")
                estado_bien = data.get("estado", "BUENO")

                query_mov = """
                    INSERT INTO movimientos (
                        bien_id, tipo, fecha, ubicacion_actual, responsable, 
                        modalidad_responsable, inventariador_id, observaciones, estado
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                fecha_mov = data.get("fecha_asignacion")
                if not fecha_mov:
                    fecha_mov = datetime.now().strftime("%Y-%m-%d")

                values_mov = (
                    bien_id,
                    'Asignación',
                    fecha_mov,
                    ubicacion_nombre,
                    responsable_nombre,
                    data.get("modalidad"),
                    data.get("inventariador_id"),
                    data.get("observacion"),
                    estado_bien
                )
                cursor.execute(query_mov, values_mov)

                conn.commit()
                return {"success": True, "message": "Bien registrado exitosamente"}

        except Exception as e:
            print("❌ Error al registrar bien:", e)
            return {"success": False, "error": str(e)}

        finally:
            if conn:
                conn.close()

    @staticmethod
    def update(id, data):
        try:
            conn = get_connection()
            
            # 1. Obtener datos actuales para auditoría y validación
            current_bien = BienModel.get_by_id(id)
            if not current_bien:
                return {"success": False, "message": "Bien no encontrado"}
            
            # 2. Validar que categoria_id existe si se proporciona
            categoria_id = data.get("categoria_id")
            if categoria_id:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id FROM categorias WHERE id = %s", (categoria_id,))
                    if not cursor.fetchone():
                        # Si la categoría no existe, establecer como None
                        data["categoria_id"] = None
                        print(f"⚠️ categoria_id {categoria_id} no existe, se establecerá como NULL")

            # 3. Definir campos inmutables que NO se deben actualizar vía este endpoint
            # Si se intenta cambiarlos, se ignoran silenciosamente o se podría lanzar error
            immutable_fields = ['codigo_patrimonio', 'codigo_interno', 'tipo_origen', 'codigo_completo']
            
            # Auditoría básica: Detectar cambios
            changes = []
            for key, value in data.items():
                if key not in immutable_fields and key in current_bien:
                    # Comparación simple (se puede mejorar para tipos específicos)
                    if str(value) != str(current_bien[key]):
                        changes.append(f"{key}: '{current_bien[key]}' -> '{value}'")

            if changes:
                print(f"📝 AUDITORÍA - Modificación de Bien ID {id}: {', '.join(changes)}")
            else:
                print(f"ℹ️ AUDITORÍA - Intento de actualización sin cambios efectivos para Bien ID {id}")

            with conn.cursor() as cursor:
                # 4. Query de actualización EXCLUYENDO campos inmutables
                # Nota: codigo_completo, codigo_patrimonio, etc. NO están en el SET
                query = """
                    UPDATE bienes SET
                        detalle_bien = %s,
                        descripcion = %s,
                        categoria_id = %s,
                        marca = %s,
                        modelo = %s,
                        numero_serie = %s,
                        dimension = %s,
                        color = %s,
                        fecha_adquisicion = %s,
                        fecha_asignacion = %s,
                        fecha_retiro = %s,
                        estado = %s,
                        tipo_modalidad = %s,
                        inventariador_id = %s,
                        observacion = %s,
                        codigo_barras = %s,
                        codigo_patrimonial = %s,
                        oficina = %s,
                        fuente = %s,
                        tipo_registro = %s,
                        updated_at = NOW()
                    WHERE id = %s
                """
                
                values = (
                    data.get("detalle_bien"),
                    data.get("descripcion"),
                    data.get("categoria_id") or None,
                    data.get("marca"),
                    data.get("modelo"),
                    data.get("numero_serie"),
                    data.get("dimension"),
                    data.get("color"),
                    data.get("fecha_adquisicion") or None,
                    data.get("fecha_asignacion") or None,
                    data.get("fecha_retiro") or None,
                    data.get("estado"),
                    data.get("tipo_modalidad"),
                    data.get("inventariador_id"),
                    data.get("observacion"),
                    data.get("codigo_barras"),
                    data.get("codigo_patrimonial"),
                    data.get("oficina"),
                    data.get("fuente"),
                    data.get("tipo_registro"),
                    id
                )

                cursor.execute(query, values)
                conn.commit()

            conn.close()
            
            # 5. Retornar el objeto actualizado
            updated_bien = BienModel.get_by_id(id)
            return {"success": True, "message": "Bien actualizado correctamente", "data": updated_bien}

        except Exception as e:
            print(f"❌ Error al actualizar bien: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def destroy(id):
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE bienes
                SET deleted_at = %s
                WHERE id = %s
            """, (datetime.now(), id))
        conn.commit()
        conn.close()

    @staticmethod
    def get_for_report(filters):
        conn = get_connection()
        
        where_clauses = ["b.deleted_at IS NULL"]
        params = []

        if filters.get('responsable'):
            where_clauses.append("(SELECT m.responsable FROM movimientos m WHERE m.bien_id = b.id ORDER BY m.fecha DESC, m.id DESC LIMIT 1) = %s")
            params.append(filters['responsable'])
            
        if filters.get('area'):
             where_clauses.append("(SELECT m.ubicacion_actual FROM movimientos m WHERE m.bien_id = b.id ORDER BY m.fecha DESC, m.id DESC LIMIT 1) = %s")
             params.append(filters['area'])

        where_str = " AND ".join(where_clauses)
        
        query = f"""
            SELECT 
                b.codigo_patrimonio,
                b.codigo_interno,
                b.descripcion,
                b.detalle_bien,
                b.marca,
                b.modelo,
                b.dimension,
                b.color,
                b.estado,
                (SELECT m.ubicacion_actual FROM movimientos m WHERE m.bien_id = b.id ORDER BY m.fecha DESC, m.id DESC LIMIT 1) AS ubicacion_nombre
            FROM bienes b
            WHERE {where_str}
            ORDER BY b.codigo_patrimonio ASC
        """
        
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(params))
            result = cursor.fetchall()
        conn.close()
        return result

    @staticmethod
    def get_report_options():
        conn = get_connection()
        with conn.cursor() as cursor:
            # Get distinct pairs of area (ubicacion_actual) and responsable
            cursor.execute("""
                SELECT DISTINCT m.ubicacion_actual as area, m.responsable 
                FROM movimientos m 
                JOIN bienes b ON m.bien_id = b.id 
                WHERE b.deleted_at IS NULL 
                AND m.ubicacion_actual IS NOT NULL AND m.ubicacion_actual != ''
                AND m.responsable IS NOT NULL AND m.responsable != ''
                ORDER BY m.ubicacion_actual, m.responsable
            """)
            rows = cursor.fetchall()
            
        conn.close()
        
        areas = sorted(list(set(row['area'] for row in rows)))
        responsables_by_area = {}
        
        for row in rows:
            area = row['area']
            responsable = row['responsable']
            if area not in responsables_by_area:
                responsables_by_area[area] = []
            responsables_by_area[area].append(responsable)
            
        return {
            "areas": areas,
            "responsables_by_area": responsables_by_area
        }

    @staticmethod
    def get_unique_detalles():
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT detalle_bien 
                FROM bienes 
                WHERE deleted_at IS NULL 
                AND detalle_bien IS NOT NULL 
                AND detalle_bien != ''
                ORDER BY detalle_bien ASC
            """)
            result = [row['detalle_bien'] for row in cursor.fetchall()]
        conn.close()
        return result

    @staticmethod
    def get_for_pdf_report(detalle=None, estado=None):
        conn = get_connection()
        
        where_clauses = ["b.deleted_at IS NULL"]
        params = []

        if detalle:
            where_clauses.append("b.detalle_bien = %s")
            params.append(detalle)
            
        if estado:
            where_clauses.append("b.estado = %s")
            params.append(estado)

        where_str = " AND ".join(where_clauses)
        
        query = f"""
            SELECT 
                b.codigo_patrimonio,
                b.descripcion,
                b.detalle_bien,
                b.marca,
                b.modelo,
                b.estado,
                (SELECT m.ubicacion_actual FROM movimientos m WHERE m.bien_id = b.id ORDER BY m.fecha DESC, m.id DESC LIMIT 1) AS ubicacion_actual
            FROM bienes b
            WHERE {where_str}
            ORDER BY b.detalle_bien ASC, b.codigo_patrimonio ASC
        """
        
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(params))
            result = cursor.fetchall()
        conn.close()
        return result
