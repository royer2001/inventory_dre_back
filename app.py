from flask import Flask
from routes.bien_routes import bien_bp
from routes.auth_routes import auth_bp
from routes.movimiento_routes import movimiento_bp
from routes.usuario_routes import usuario_bp
from routes.reporte_routes import reporte_bp
from routes.barcode_routes import barcode_bp
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
app.url_map.strict_slashes = False


CORS(app, origins=["http://localhost:5173", "https://benevolent-pudding-a44fae.netlify.app"])

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(bien_bp, url_prefix="/bienes")
app.register_blueprint(movimiento_bp, url_prefix="/movimientos")
app.register_blueprint(usuario_bp, url_prefix="/usuarios")
app.register_blueprint(reporte_bp, url_prefix="/reportes")
app.register_blueprint(barcode_bp, url_prefix="/barcode")



if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
