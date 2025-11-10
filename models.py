# models.py
from datetime import datetime
from extensions import db  # ⚠️ Importa la instancia creada en app.py

class User(db.Model):
    __tablename__ = "users"

    iduser = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    dashboards = db.relationship("Dashboard", backref="usuario", lazy=True)


class Dashboard(db.Model):
    __tablename__ = "dashboard"

    idsesion = db.Column(db.Integer, primary_key=True)
    iduser = db.Column(db.Integer, db.ForeignKey("users.iduser"), nullable=False)
    cronica = db.Column(db.Text, nullable=True)
    numero_de_sesion = db.Column(db.Integer, nullable=True)
    fecha = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    resumen = db.Column(db.Text, nullable=True)
