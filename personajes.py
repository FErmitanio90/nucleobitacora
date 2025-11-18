#personajes.py backend
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Personaje
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import json

personajes_bp = Blueprint("personajes_bp", __name__)

# =============================
# GET /personajes
# =============================
@personajes_bp.route("/", methods=["GET"])
@jwt_required()
def get_personajes():
    iduser = int(get_jwt_identity())

    try:
        personajes = Personaje.query.filter_by(iduser=iduser).all()

        resultado = [
            {
                "idpersonaje": p.idpersonaje,
                "cronica": p.cronica,
                "juego": p.juego,
                "nombre": p.nombre,
                "apellido": p.apellido,
                "genero": p.genero,
                "edad": p.edad,
                "ocupacion": p.ocupacion,
                "etnia": p.etnia,
                "descripcion": p.descripcion,
                "historia": p.historia,
                "inventario": p.inventario,
                "notas": p.notas
            }
            for p in personajes
        ]

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"msg": "Error al obtener personajes", "error": str(e)}), 500


# =============================
# POST /personajes
# =============================
@personajes_bp.route("/", methods=["POST"])
@jwt_required()
def create_personaje():
    iduser = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({"msg": "Debe enviar JSON"}), 400

    try:
        nuevo = Personaje(
            iduser=iduser,
            cronica=data.get("cronica"),
            juego=data.get("juego"),
            nombre=data.get("nombre"),
            apellido=data.get("apellido"),
            genero=data.get("genero"),
            edad=data.get("edad"),
            ocupacion=data.get("ocupacion"),
            etnia=data.get("etnia"),
            descripcion=data.get("descripcion"),
            historia=data.get("historia"),
            inventario=data.get("inventario"),
            notas=data.get("notas")
        )

        db.session.add(nuevo)
        db.session.commit()

        return jsonify({"msg": "Personaje creado", "idpersonaje": nuevo.idpersonaje}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al crear personaje", "error": str(e)}), 500


# =============================
# PUT /personajes/<id>
# =============================
@personajes_bp.route("/<int:idpersonaje>", methods=["PUT"])
@jwt_required()
def update_personaje(idpersonaje):
    iduser = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({"msg": "Debe enviar JSON"}), 400

    try:
        personaje = Personaje.query.filter_by(idpersonaje=idpersonaje, iduser=iduser).first()

        if not personaje:
            return jsonify({"msg": "Personaje no encontrado"}), 404

        for campo in [
            "cronica", "juego",
            "nombre", "apellido", "genero", "edad", "ocupacion",
            "etnia", "descripcion", "historia", "inventario", "notas"
        ]:
            if campo in data:
                setattr(personaje, campo, data[campo])

        db.session.commit()

        return jsonify({"msg": "Personaje actualizado"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al actualizar personaje", "error": str(e)}), 500


# =============================
# DELETE /personajes/<id>
# =============================
@personajes_bp.route("/<int:idpersonaje>", methods=["DELETE"])
@jwt_required()
def delete_personaje(idpersonaje):
    iduser = int(get_jwt_identity())

    try:
        personaje = Personaje.query.filter_by(idpersonaje=idpersonaje, iduser=iduser).first()

        if not personaje:
            return jsonify({"msg": "Personaje no encontrado"}), 404

        db.session.delete(personaje)
        db.session.commit()

        return jsonify({"msg": "Personaje eliminado"}), 200

    except Exception as e:
        return jsonify({"msg": "Error al eliminar personaje", "error": str(e)}), 500


# =============================
# PDF
# =============================
@personajes_bp.route("/<int:idpersonaje>/pdf", methods=["GET"])
@jwt_required()
def get_personaje_pdf(idpersonaje):
    iduser = int(get_jwt_identity())

    try:
        personaje = Personaje.query.filter_by(idpersonaje=idpersonaje, iduser=iduser).first()

        if not personaje:
            return jsonify({"msg": "Personaje no encontrado"}), 404

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        y = 750

        def write(text, offset=20):
            nonlocal y
            pdf.drawString(100, y, str(text))
            y -= offset

        pdf.setFont("Helvetica-Bold", 14)
        write(f"{personaje.nombre} {personaje.apellido}", 30)

        pdf.setFont("Helvetica", 11)
        write(f"Cronica: {personaje.cronica or 'N/A'}")
        write(f"Juego: {personaje.juego or 'N/A'}")
        write(f"Género: {personaje.genero or 'N/A'}")
        write(f"Edad: {personaje.edad or 'N/A'}")
        write(f"Ocupación: {personaje.ocupacion or 'N/A'}")
        write(f"Etnia: {personaje.etnia or 'N/A'}")

        write("Descripción:", 25)
        for line in (personaje.descripcion or "N/A").split("\n"):
            write(line, 15)

        write("Historia:", 25)
        for line in (personaje.historia or "N/A").split("\n"):
            write(line, 15)

        write("Inventario:", 25)
        try:
            inventario = json.loads(personaje.inventario) if personaje.inventario else []
        except:
            inventario = [personaje.inventario]

        if inventario:
            for item in inventario:
                write(f"- {item}", 15)
        else:
            write("N/A", 15)

        write("Notas:", 25)
        for line in (personaje.notas or "N/A").split("\n"):
            write(line, 15)

        pdf.save()
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"{personaje.nombre}_{personaje.apellido}.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        print("❌ Error generando PDF:", e)
        return jsonify({"msg": "Error generando PDF", "error": str(e)}), 500
