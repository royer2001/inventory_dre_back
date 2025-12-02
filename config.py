import os

MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT')),
    'cursorclass': 'DictCursor'
}

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

SECRET_KEY = os.getenv("SECRET_KEY")
JWT_EXPIRATION_MINUTES = 480

