from database.connection import get_connection


class ResponsableModel:

    @staticmethod
    def get_all():
        """Obtiene todos los responsables activos"""
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    id,
                    nombre_original,
                    nombre_normalizado,
                    area,
                    tipo_contrato,
                    activo,
                    fecha_registro
                FROM responsables
                WHERE activo = TRUE
                ORDER BY nombre_normalizado ASC
            ''')
            result = cursor.fetchall()
        conn.close()
        return result

    @staticmethod
    def get_all_with_inactive():
        """Obtiene todos los responsables incluyendo inactivos"""
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    id,
                    nombre_original,
                    nombre_normalizado,
                    area,
                    tipo_contrato,
                    activo,
                    fecha_registro
                FROM responsables
                ORDER BY nombre_normalizado ASC
            ''')
            result = cursor.fetchall()
        conn.close()
        return result

    @staticmethod
    def get_by_id(id):
        """Obtiene un responsable por su ID"""
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    id,
                    nombre_original,
                    nombre_normalizado,
                    area,
                    tipo_contrato,
                    activo,
                    fecha_registro
                FROM responsables
                WHERE id = %s
            ''', (id,))
            result = cursor.fetchone()
        conn.close()
        return result

    @staticmethod
    def get_by_nombre_original(nombre_original):
        """Obtiene un responsable por su nombre original"""
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT id, nombre_original, nombre_normalizado, area, tipo_contrato, activo
                FROM responsables
                WHERE nombre_original = %s
            ''', (nombre_original,))
            result = cursor.fetchone()
        conn.close()
        return result

    @staticmethod
    def create(data):
        """Crea un nuevo responsable"""
        conn = None
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO responsables (
                        nombre_original,
                        nombre_normalizado,
                        area,
                        tipo_contrato,
                        activo
                    )
                    VALUES (%s, %s, %s, %s, %s)
                """
                values = (
                    data.get("nombre_original"),
                    data.get("nombre_normalizado", data.get("nombre_original")),
                    data.get("area"),
                    data.get("tipo_contrato"),
                    data.get("activo", True)
                )
                cursor.execute(query, values)
                responsable_id = cursor.lastrowid
                conn.commit()
                return {"success": True, "id": responsable_id, "message": "Responsable creado exitosamente"}
        except Exception as e:
            print(f"❌ Error al crear responsable: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                conn.close()

    @staticmethod
    def update(id, data):
        """Actualiza un responsable"""
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                query = """
                    UPDATE responsables SET
                        nombre_original = %s,
                        nombre_normalizado = %s,
                        area = %s,
                        tipo_contrato = %s,
                        activo = %s
                    WHERE id = %s
                """
                values = (
                    data.get("nombre_original"),
                    data.get("nombre_normalizado"),
                    data.get("area"),
                    data.get("tipo_contrato"),
                    data.get("activo", True),
                    id
                )
                cursor.execute(query, values)
                conn.commit()
            conn.close()
            return {"success": True, "message": "Responsable actualizado correctamente"}
        except Exception as e:
            print(f"❌ Error al actualizar responsable: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def toggle_active(id):
        """Activa/desactiva un responsable"""
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE responsables 
                    SET activo = NOT activo 
                    WHERE id = %s
                """, (id,))
                conn.commit()
            conn.close()
            return {"success": True, "message": "Estado de responsable actualizado"}
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def search(query):
        """Busca responsables por nombre"""
        conn = get_connection()
        with conn.cursor() as cursor:
            search_term = f"%{query}%"
            cursor.execute('''
                SELECT 
                    id,
                    nombre_original,
                    nombre_normalizado,
                    area,
                    tipo_contrato,
                    activo
                FROM responsables
                WHERE activo = TRUE
                AND (nombre_normalizado LIKE %s OR nombre_original LIKE %s)
                ORDER BY nombre_normalizado ASC
                LIMIT 20
            ''', (search_term, search_term))
            result = cursor.fetchall()
        conn.close()
        return result
