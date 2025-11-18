# models.py
from flask_migrate import Migrate
from datetime import datetime
from extensions import db
from sqlalchemy.dialects.postgresql import JSON   # 👈 IMPORTANTE

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
    juego = db.Column(db.Text, nullable=True)
    director = db.Column(db.String(100), nullable=True)
    jugadores = db.Column(db.Text, nullable=True)
    numero_de_sesion = db.Column(db.Integer, nullable=True)
    fecha = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    resumen = db.Column(db.Text, nullable=True)


class Personaje(db.Model):
    __tablename__ = "personajes"

    idpersonaje = db.Column(db.Integer, primary_key=True)
    iduser = db.Column(db.Integer, db.ForeignKey("users.iduser"), nullable=False)
    cronica = db.Column(db.String(100), nullable=True)
    juego = db.Column(db.String(100), nullable=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    genero = db.Column(db.String(50), nullable=True)
    edad = db.Column(db.Integer, nullable=True)
    ocupacion = db.Column(db.String(100), nullable=True)
    etnia = db.Column(db.String(100), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    historia = db.Column(db.Text, nullable=True)

    # ⬇⬇⬇ NUEVA COLUMNA JSON PARA LISTA DE ITEMS
    inventario = db.Column(JSON, nullable=True)

    notas = db.Column(db.Text, nullable=True)
