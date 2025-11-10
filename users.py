from flask import Blueprint, request, jsonify
from extensions import db
from models import User

users_bp = Blueprint("users_bp", __name__)

@users_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Debe enviar datos JSON"}), 400

    required = ["nombre", "apellido", "username", "password"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Falta el campo {field}"}), 400

    # Verificar username duplicado
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "El username ya está en uso"}), 409

    try:
        user = User(
            nombre=data["nombre"],
            apellido=data["apellido"],
            username=data["username"],
            password=data["password"]
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            "msg": "Usuario creado exitosamente",
            "usuario": {
                "iduser": user.iduser,
                "nombre": user.nombre,
                "apellido": user.apellido,
                "username": user.username
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al crear usuario: {str(e)}"}), 500

