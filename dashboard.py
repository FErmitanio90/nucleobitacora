# dashboard.py Backend
from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Dashboard
from flask import send_file
from reportlab.pdfgen import canvas

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
    
# GET /dashboard/<idsesion>/pdf

@dashboard_bp.route("/<int:idsesion>/pdf", methods=["GET"])
@jwt_required()
def get_dashboard_pdf(idsesion):
    iduser = int(get_jwt_identity())

    try:
        sesion = Dashboard.query.filter_by(idsesion=idsesion, iduser=iduser).first()

        if not sesion:
            return jsonify({"msg": "Sesión no encontrada o sin permiso"}), 404

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)

        y = 800
        line_height = 16

        def write_line(text):
            nonlocal y
            if y < 50:
                pdf.showPage()
                y = 800
            pdf.drawString(40, y, text)
            y -= line_height

        write_line(f"Cronica: {sesion.cronica}")
        write_line(f"Juego: {sesion.juego}")
        write_line(f"Número de Sesión: {sesion.numero_de_sesion}")
        write_line(f"Fecha: {sesion.fecha.strftime('%Y-%m-%d')}")
        write_line("")
        write_line("Resumen:")
        write_line("")

        resumen = sesion.resumen.split("\n")
        for linea in resumen:
            while len(linea) > 90:
                write_line(linea[:90])
                linea = linea[90:]
            write_line(linea)

        pdf.save()
        buffer.seek(0)

        # FIX PARA RENDER
        from flask import make_response
        response = make_response(send_file(
            buffer,
            as_attachment=True,
            download_name=f"sesion_{idsesion}.pdf",
            mimetype='application/pdf'
        ))
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"

        return response

    except Exception as e:
        return jsonify({"msg": "Error al generar PDF", "error": str(e)}), 500

