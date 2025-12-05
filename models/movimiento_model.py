from database.connection import get_connection
from datetime import datetime


class MovimientoModel:

    @staticmethod
    def get_all():
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                SELECT 
                    m.*,
                    u.nombre as inventariador_nombre,
                    m.estado as estado_movimiento
                FROM movimientos m
                LEFT JOIN usuarios u ON m.inventariador_id = u.id
                ORDER BY m.fecha DESC, m.id DESC
                ''')
            result = cursor.fetchall()
        conn.close()
        return result

    @staticmethod
    def get_by_id(id):
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                SELECT 
                    m.*,
                    u.nombre as inventariador_nombre,
                    m.estado as estado_movimiento
                FROM movimientos m
                LEFT JOIN usuarios u ON m.inventariador_id = u.id
                WHERE m.bien_id = %s
                ORDER BY m.created_at ASC
                ''', (id,))
            result = cursor.fetchall()
        conn.close()

        return result

    @staticmethod
    def get_by_bien_id(bien_id):
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                SELECT 
                    m.*,
                    u.nombre as inventariador_nombre,
                    m.estado as estado_movimiento
                FROM movimientos m
                LEFT JOIN usuarios u ON m.inventariador_id = u.id
                WHERE m.bien_id = %s
                ORDER BY m.created_at ASC
                ''', (bien_id,))
            result = cursor.fetchall()
        conn.close()
        return result

    @staticmethod
    def get_recent_activity(limit=5):
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                SELECT 
                    b.descripcion as bien,
                    m.tipo as accion,
                    m.responsable as usuario,
                    m.fecha,
                    m.estado as estado_movimiento,
                    'Completado' as status
                FROM movimientos m
                JOIN bienes b ON m.bien_id = b.id
                ORDER BY m.fecha DESC, m.id DESC
                LIMIT %s
                ''', (limit,))
            result = cursor.fetchall()
        conn.close()
        return result

    @staticmethod
    def get_movements_by_month():
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                SELECT 
                    MONTH(fecha) as mes, 
                    COUNT(*) as total 
                FROM movimientos 
                WHERE YEAR(fecha) = YEAR(CURRENT_DATE())
                GROUP BY MONTH(fecha)
                ORDER BY MONTH(fecha) ASC
                ''')
            result = cursor.fetchall()
        conn.close()
        return result

    @staticmethod
    def create(data):
        conn = None
        try:
            conn = get_connection()
            with conn.cursor() as cursor:

                if not data.get("bien_id"):
                    return {"success": False, "error": "El bien_id es obligatorio"}

                query = """
                    INSERT INTO movimientos
                    (
                        bien_id, 
                        tipo, 
                        fecha, 
                        ubicacion_actual, 
                        responsable, 
                        modalidad_responsable,
                        inventariador_id,
                        documento_id,
                        observaciones,
                        estado
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    );
                """

                # Handle nullable fields
                documento_id = data.get("documento_id")
                if not documento_id:
                    documento_id = None
                
                inventariador_id = data.get("inventariador_id")
                if not inventariador_id:
                    inventariador_id = None

                values = (
                    data.get("bien_id"),
                    data.get("tipo", "Asignación"),
                    data.get("fecha") or datetime.now().strftime("%Y-%m-%d"),
                    data.get("ubicacion_actual") or data.get("ubicacion_destino"),
                    data.get("responsable") or data.get("responsable_nuevo"),
                    data.get("modalidad_responsable") or data.get("modalidad_responsable_nuevo") or data.get("modalidad"),
                    inventariador_id,
                    documento_id,
                    data.get("observaciones"),
                    data.get("estado")
                )

                cursor.execute(query, values)
                conn.commit()
                return {"success": True, "message": "Movimiento registrado exitosamente"}

        except Exception as e:
            print("❌ Error al registrar movimiento:", e)
            return {"success": False, "error": str(e)}

        finally:
            if conn:
                conn.close()

    @staticmethod
    def update(id, data):
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                # Actualizar el registro
                query = """
                    UPDATE movimientos SET
                        tipo = %s,
                        fecha = %s,
                        ubicacion_actual = %s,
                        responsable = %s,
                        modalidad_responsable = %s,
                        inventariador_id = %s,
                        documento_id = %s,
                        observaciones = %s,
                        estado = %s
                    WHERE id = %s
                """
                
                documento_id = data.get("documento_id")
                if not documento_id:
                    documento_id = None
                    
                inventariador_id = data.get("inventariador_id")
                if not inventariador_id:
                    inventariador_id = None

                values = (
                    data.get("tipo"),
                    data.get("fecha"),
                    data.get("ubicacion_actual"),
                    data.get("responsable"),
                    data.get("modalidad_responsable"),
                    inventariador_id,
                    documento_id,
                    data.get("observaciones"),
                    data.get("estado"),
                    id
                )

                cursor.execute(query, values)
                conn.commit()

            conn.close()
            return True

        except Exception as e:
            print(f"❌ Error al actualizar movimiento: {e}")
            return False

    @staticmethod
    def destroy(id):
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE movimientos
                SET deleted_at = %s
                WHERE id = %s
            """, (datetime.now(), id))
        conn.commit()
        conn.close()
