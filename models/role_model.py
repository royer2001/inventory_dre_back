from database.connection import get_connection

class RoleModel:
    @staticmethod
    def get_all():
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM roles")
            result = cursor.fetchall()
        conn.close()
        return result
