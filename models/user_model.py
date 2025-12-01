import bcrypt
from database.connection import get_connection

class UserModel:

    @staticmethod
    def get_all():
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.nombre, u.usuario, u.correo, u.dni, u.rol_id, u.activo, u.creado_en, r.nombre as rol_nombre
                FROM usuarios u
                JOIN roles r ON u.rol_id = r.id
                ORDER BY u.id DESC
            """)
            result = cursor.fetchall()
        conn.close()
        return result

    @staticmethod
    def find_by_id(user_id):
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.nombre, u.usuario, u.correo, u.dni, u.rol_id, u.activo, u.creado_en, r.nombre as rol_nombre
                FROM usuarios u
                JOIN roles r ON u.rol_id = r.id
                WHERE u.id = %s
            """, (user_id,))
            user = cursor.fetchone()
        conn.close()
        return user

    @staticmethod
    def find_by_email(correo):
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, contrasena, nombre, rol_id, correo, activo FROM usuarios WHERE correo = %s", (correo,))
            user = cursor.fetchone()
        conn.close()
        return user

    @staticmethod
    def find_by_dni(dni):
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, contrasena, nombre, rol_id, dni, activo 
                FROM usuarios 
                WHERE dni = %s
            """, (dni,))
            user = cursor.fetchone()
        conn.close()
        return user

    @staticmethod
    def create(data):
        conn = get_connection()
        try:
            contrasena = data.get("contrasena")
            hashed = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())

            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO usuarios (nombre, usuario, correo, contrasena, rol_id, dni, activo) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    data.get("nombre"),
                    data.get("usuario"),
                    data.get("correo"),
                    hashed,
                    data.get("rol_id"),
                    data.get("dni"),
                    data.get("activo", 1)
                ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def update(id, data):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # Build query dynamically based on provided fields
                fields = []
                values = []

                if "nombre" in data:
                    fields.append("nombre = %s")
                    values.append(data["nombre"])
                if "usuario" in data:
                    fields.append("usuario = %s")
                    values.append(data["usuario"])
                if "correo" in data:
                    fields.append("correo = %s")
                    values.append(data["correo"])
                if "dni" in data:
                    fields.append("dni = %s")
                    values.append(data["dni"])
                if "rol_id" in data:
                    fields.append("rol_id = %s")
                    values.append(data["rol_id"])
                if "activo" in data:
                    fields.append("activo = %s")
                    values.append(data["activo"])
                
                if "contrasena" in data and data["contrasena"]:
                    hashed = bcrypt.hashpw(data["contrasena"].encode('utf-8'), bcrypt.gensalt())
                    fields.append("contrasena = %s")
                    values.append(hashed)

                if not fields:
                    return False

                query = f"UPDATE usuarios SET {', '.join(fields)} WHERE id = %s"
                values.append(id)

                cursor.execute(query, tuple(values))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(id):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
        finally:
            conn.close()

    # Alias for backward compatibility if needed, or update AuthController
    @staticmethod
    def create_user(nombre, dni, contrasena, rol_id):
        return UserModel.create({
            "nombre": nombre,
            "dni": dni,
            "contrasena": contrasena,
            "rol_id": rol_id
        })
