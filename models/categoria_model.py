from database.connection import get_connection


class CategoriaModel:
    @staticmethod
    def get_all():
        """Obtiene todas las categorías"""
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nombre FROM categorias ORDER BY nombre ASC")
            result = cursor.fetchall()
        conn.close()
        return result
    
    @staticmethod
    def get_by_id(id):
        """Obtiene una categoría por su ID"""
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nombre FROM categorias WHERE id = %s", (id,))
            result = cursor.fetchone()
        conn.close()
        return result
