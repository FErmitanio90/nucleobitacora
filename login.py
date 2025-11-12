# login.py backend
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from datetime import timedelta
from extensions import db
from models import User

login_bp = Blueprint("login_bp", __name__)

@login_bp.route("/", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "Debe enviar JSON"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "error": "Faltan campos username y password"}), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"success": False, "error": "Usuario no encontrado"}), 404

    if user.password != password:  
        return jsonify({"success": False, "error": "Contraseña incorrecta"}), 401

    claims = {
        "username": user.username,
        "nombre": user.nombre,
        "apellido": user.apellido
    }

    # ✅ PARCHE IMPORTANTE: identity como STRING
    token = create_access_token(
        identity=str(user.iduser),
        additional_claims=claims,
        expires_delta=timedelta(hours=1)
    )

    return jsonify({
        "success": True,
        "msg": "Login exitoso",
        "access_token": token,
        "usuario": {
            "iduser": user.iduser,
            "nombre": user.nombre
        }
    }), 200