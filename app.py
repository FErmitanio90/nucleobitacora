from flask import Flask
from flask_cors import CORS
from extensions import db, jwt  # ✅ importar desde extensions
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# === Configuración de la base de datos ===
default_db_url = "postgresql://postgres:postgres@localhost:5432/postgres"

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", default_db_url)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "supersecretkey")

# Inicializar extensiones
db.init_app(app)
jwt.init_app(app)

# Importar blueprints DESPUÉS de inicializar db y jwt
from login import login_bp
from dashboard import dashboard_bp
from users import users_bp

# ✅ CORRECCIÓN IMPORTANTE:
# No duplicar rutas. El blueprint ya define "/dashboard" y "/users" internamente.
app.register_blueprint(login_bp, url_prefix="/")
app.register_blueprint(dashboard_bp, url_prefix="/")   # antes: /dashboard
app.register_blueprint(users_bp, url_prefix="/")       # antes: /users

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port)
