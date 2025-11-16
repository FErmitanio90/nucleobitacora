# dashboard.py Backend
from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Dashboard
from flask import send_file
from flask import make_response

from io import BytesIO

dashboard_bp = Blueprint("dashboard_bp", __name__)

# GET /dashboard
@dashboard_bp.route("/", methods=["GET"])
@jwt_required()
def get_dashboard():
    iduser = int(get_jwt_identity())  # ✅ PARCHE IMPORTANTÍSIMO

    try:
        sesiones = Dashboard.query.filter_by(iduser=iduser).order_by(Dashboard.fecha.desc()).all()

        resultado = [
            {
                "idsesion": s.idsesion,
                "cronica": s.cronica,
                "juego": s.juego,
                "numero_de_sesion": s.numero_de_sesion,
                "fecha": s.fecha.strftime("%Y-%m-%d"),
                "resumen": s.resumen
            }
            for s in sesiones
        ]

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"msg": "Error al obtener dashboard", "error": str(e)}), 500


# POST /dashboard
@dashboard_bp.route("/", methods=["POST"])
@jwt_required()
def create_dashboard():
    iduser = int(get_jwt_identity())  # ✅ convertir a int SIEMPRE
    data = request.get_json()

    if not data:
        return jsonify({"msg": "Debe enviar JSON"}), 400

    try:
        fecha_str = data.get("fecha")
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d") if fecha_str else datetime.utcnow()

        nueva = Dashboard(
            iduser=iduser,
            cronica=data.get("cronica"),
            juego=data.get("juego"),
            numero_de_sesion=data.get("numero_de_sesion"),
            fecha=fecha,
            resumen=data.get("resumen")
        )

        db.session.add(nueva)
        db.session.commit()

        return jsonify({"msg": "Sesión creada exitosamente"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al crear sesión", "error": str(e)}), 500


# PUT /dashboard/<idsesion>
@dashboard_bp.route("/<int:idsesion>", methods=["PUT"])
@jwt_required()
def update_dashboard(idsesion):
    iduser = int(get_jwt_identity())  # ✅ PARCHE
    data = request.get_json()

    if not data:
        return jsonify({"msg": "Debe enviar JSON"}), 400

    try:
        sesion = Dashboard.query.filter_by(idsesion=idsesion, iduser=iduser).first()

        if not sesion:
            return jsonify({"msg": "Sesión no encontrada o sin permiso"}), 404

        for field in ["cronica","juego", "numero_de_sesion", "resumen"]:
            if field in data:
                setattr(sesion, field, data[field])

        if "fecha" in data:
            sesion.fecha = datetime.strptime(data["fecha"], "%Y-%m-%d")

        db.session.commit()

        return jsonify({"msg": "Sesión actualizada exitosamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al actualizar sesión", "error": str(e)}), 500


# DELETE
@dashboard_bp.route("/<int:idsesion>", methods=["DELETE"])
@jwt_required()
def delete_dashboard(idsesion):
    iduser = int(get_jwt_identity())  # ✅ PARCHE

    try:
        sesion = Dashboard.query.filter_by(idsesion=idsesion, iduser=iduser).first()

        if not sesion:
            return jsonify({"msg": "Sesión no encontrada o sin permiso"}), 404

        db.session.delete(sesion)
        db.session.commit()

        return jsonify({"msg": "Sesión eliminada exitosamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al eliminar sesión", "error": str(e)}), 500
    
# GET /dashboard/<idsesion>/txt
@dashboard_bp.route("/<int:idsesion>/txt", methods=["GET"])
@jwt_required()
def get_dashboard_txt(idsesion):
    iduser = int(get_jwt_identity())

    try:
        # Buscar sesión
        sesion = Dashboard.query.filter_by(idsesion=idsesion, iduser=iduser).first()

        if not sesion:
            return jsonify({"msg": "Sesión no encontrada o sin permiso"}), 404

        # Generar contenido TXT
        contenido = []
        contenido.append(f"Cronica: {sesion.cronica}")
        contenido.append(f"Juego: {sesion.juego}")
        contenido.append(f"Número de Sesión: {sesion.numero_de_sesion}")
        contenido.append(f"Fecha: {sesion.fecha.strftime('%Y-%m-%d')}")
        contenido.append("")
        contenido.append("Resumen:")
        contenido.append("")
        contenido.append(sesion.resumen)

        txt_data = "\n".join(contenido)

        # Convertir a bytes
        buffer = BytesIO(txt_data.encode("utf-8"))
        buffer.seek(0)

        # Preparar respuesta (fix para Render)
        response = make_response(send_file(
            buffer,
            as_attachment=True,
            download_name=f"sesion_{idsesion}.txt",
            mimetype="text/plain"
        ))
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"

        return response

    except Exception as e:
        return jsonify({"msg": "Error al generar TXT", "error": str(e)}), 500

