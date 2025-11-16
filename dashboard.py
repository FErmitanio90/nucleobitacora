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
    
# GET /dashboard/<idsesion>/pdf
@dashboard_bp.route("/<int:idsesion>/pdf", methods=["GET"])
@jwt_required()
def get_dashboard_pdf(idsesion):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm

    iduser = int(get_jwt_identity())

    try:
        # Buscar sesión
        sesion = Dashboard.query.filter_by(idsesion=idsesion, iduser=iduser).first()
        if not sesion:
            return jsonify({"msg": "Sesión no encontrada o sin permiso"}), 404

        # --- CONFIG PDF ---
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        width, height = A4
        margin = 20 * mm
        y = height - margin

        # --- Encabezado ---
        c.setFont("Helvetica-Bold", 16)
        c.drawString(margin, y, "Bitácora de Sesión")
        y -= 15

        c.setFont("Helvetica", 12)
        datos = [
            f"Crónica: {sesion.cronica}",
            f"Juego: {sesion.juego}",
            f"Número de Sesión: {sesion.numero_de_sesion}",
            f"Fecha: {sesion.fecha.strftime('%Y-%m-%d')}",
        ]

        for d in datos:
            y -= 15
            c.drawString(margin, y, d)

        y -= 25
        c.setFont("Helvetica-Bold", 13)
        c.drawString(margin, y, "Resumen:")
        y -= 20

        c.setFont("Helvetica", 11)

        # --- Word Wrapping automático ---
        def draw_wrapped(text, x, y, max_width):
            from reportlab.pdfbase.pdfmetrics import stringWidth

            lines = []
            for linea in text.split("\n"):
                palabras = linea.split()
                linea_actual = ""

                for palabra in palabras:
                    test = linea_actual + " " + palabra if linea_actual else palabra
                    if stringWidth(test, "Helvetica", 11) < max_width:
                        linea_actual = test
                    else:
                        lines.append(linea_actual)
                        linea_actual = palabra

                if linea_actual:
                    lines.append(linea_actual)

            return lines

        max_width = width - (2 * margin)
        lineas = draw_wrapped(sesion.resumen, margin, y, max_width)

        for linea in lineas:
            if y < margin:
                c.showPage()
                y = height - margin
                c.setFont("Helvetica", 11)

            c.drawString(margin, y, linea)
            y -= 14

        c.save()
        buffer.seek(0)

        response = make_response(send_file(
            buffer,
            as_attachment=True,
            download_name=f"sesion_{idsesion}.pdf",
            mimetype="application/pdf"
        ))
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return response

    except Exception as e:
        return jsonify({"msg": "Error al generar PDF", "error": str(e)}), 500



