import jwt
from datetime import datetime, timedelta
from config import SECRET_KEY, JWT_EXPIRATION_MINUTES

class JWTService:
    @staticmethod
    def create_token(data):
        payload = {
            "id": data["id"],
            "role_id": data["role_id"],
            "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token):
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return decoded
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
