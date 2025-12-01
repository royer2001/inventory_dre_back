from database.connection import get_connection

class PacienteModel:

    @staticmethod
    def get_all():
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM patients")
            result = cursor.fetchall()
        conn.close()
        return result

    @staticmethod
    def get_by_id(id):
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM patients WHERE id = %s", (id,))
            result = cursor.fetchone()
        conn.close()
        return result

    @staticmethod
    def create(data):
        conn = get_connection()
        with conn.cursor() as cursor:
            sql = "INSERT INTO patients (nombre, apellido, dni, telefono, correo) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (data["nombre"], data["apellido"], data["dni"], data["telefono"], data["correo"]))
        conn.commit()
        conn.close()
    
    @staticmethod
    def update(id, data):
        conn = get_connection()
        with conn.cursor() as cursor:
            sql = "UPDATE patients SET nombre = %s, apellido = %s, dni = %s, telefono = %s, correo = %s WHERE id = %s"
            cursor.execute(sql, (data["nombre"], data["apellido"], data["dni"], data["telefono"], data["correo"], id))
        conn.commit()
        conn.close()
