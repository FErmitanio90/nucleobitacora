# app.py backend
from flask import Flask
from flask_cors import CORS
from extensions import db, jwt
from dotenv import load_dotenv
import os

# 🔹 Importar Flask-Migrate
from flask_migrate import Migrate  

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

# 🔹 Inicializar Flask-Migrate (CORRECTO)
migrate = Migrate(app, db)

# Importar modelos ANTES de registrar blueprints
from models import User, Dashboard, Personaje

# Importar blueprints DESPUÉS de inicializar db y jwt
from login import login_bp
from dashboard import dashboard_bp
from users import users_bp
from personajes import personajes_bp

# Rutas
app.register_blueprint(login_bp, url_prefix="/login")
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
app.register_blueprint(users_bp, url_prefix="/users")
app.register_blueprint(personajes_bp, url_prefix="/personajes")

@app.route("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5050)))