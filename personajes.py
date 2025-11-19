# personajes.py (BACKEND)

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Personaje
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

personajes_bp = Blueprint("personajes_bp", __name__)


# ============================================================
# Utilidades
# ============================================================

def json_ok(msg=None, data=None, code=200):
    payload = {}
    if msg: payload["msg"] = msg
    if data is not None: payload["data"] = data
    return jsonify(payload), code


def json_error(msg="Error", error="", code=400):
    return jsonify({"msg": msg, "error": str(error)}), code


def safe_inventario(value):
    """Garantiza que inventario siempre sea lista (igual que dashboard)."""
    return value if isinstance(value, list) else []


# ============================================================
# GET /personajes
# ============================================================
@personajes_bp.route("/", methods=["GET"])
@jwt_required()
def get_personajes():
    iduser = int(get_jwt_identity())

    try:
        personajes = Personaje.query.filter_by(iduser=iduser).all()

        data = []
        for p in personajes:
            data.append({
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
                "inventario": safe_inventario(p.inventario),
                "notas": p.notas
            })

        return json_ok(data=data)

    except Exception as e:
        return json_error("Error al obtener personajes", e, 500)


# ============================================================
# POST /personajes
# ============================================================
@personajes_bp.route("/", methods=["POST"])
@jwt_required()
def create_personaje():
    iduser = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return json_error("Debe enviar JSON", code=400)

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
            inventario=safe_inventario(data.get("inventario")),
            notas=data.get("notas")
        )

        db.session.add(nuevo)
        db.session.commit()

        return json_ok("Personaje creado", {"idpersonaje": nuevo.idpersonaje}, 201)

    except Exception as e:
        db.session.rollback()
        return json_error("Error al crear personaje", e, 500)


# ============================================================
# PUT /personajes/<id>
# ============================================================
@personajes_bp.route("/<int:idpersonaje>", methods=["PUT"])
@jwt_required()
def update_personaje(idpersonaje):
    iduser = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return json_error("Debe enviar JSON", code=400)

    try:
        personaje = Personaje.query.filter_by(idpersonaje=idpersonaje, iduser=iduser).first()

        if not personaje:
            return json_error("Personaje no encontrado", code=404)

        # Actualizar campos
        for campo in [
            "cronica", "juego", "nombre", "apellido", "genero", "edad",
            "ocupacion", "etnia", "descripcion", "historia", "notas"
        ]:
            if campo in data:
                setattr(personaje, campo, data[campo])

        # Inventario
        if "inventario" in data:
            personaje.inventario = safe_inventario(data["inventario"])

        db.session.commit()

        return json_ok("Personaje actualizado")

    except Exception as e:
        db.session.rollback()
        return json_error("Error al actualizar personaje", e, 500)


# ============================================================
# GET /personajes/<id>
# ============================================================
@personajes_bp.route("/<int:idpersonaje>", methods=["GET"])
@jwt_required()
def get_personaje(idpersonaje):
    iduser = int(get_jwt_identity())

    try:
        p = Personaje.query.filter_by(idpersonaje=idpersonaje, iduser=iduser).first()

        if not p:
            return json_error("Personaje no encontrado", code=404)

        data = {
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
            "inventario": safe_inventario(p.inventario),
            "notas": p.notas
        }

        return json_ok(data=data)

    except Exception as e:
        return json_error("Error al obtener personaje", e, 500)


# ============================================================
# DELETE /personajes/<id>
# ============================================================
@personajes_bp.route("/<int:idpersonaje>", methods=["DELETE"])
@jwt_required()
def delete_personaje(idpersonaje):
    iduser = int(get_jwt_identity())

    try:
        personaje = Personaje.query.filter_by(idpersonaje=idpersonaje, iduser=iduser).first()

        if not personaje:
            return json_error("Personaje no encontrado", code=404)

        db.session.delete(personaje)
        db.session.commit()

        return json_ok("Personaje eliminado")

    except Exception as e:
        return json_error("Error al eliminar personaje", e, 500)


# ============================================================
# PDF
# ============================================================
@personajes_bp.route("/<int:idpersonaje>/pdf", methods=["GET"])
@jwt_required()
def get_personaje_pdf(idpersonaje):
    iduser = int(get_jwt_identity())

    try:
        personaje = Personaje.query.filter_by(idpersonaje=idpersonaje, iduser=iduser).first()

        if not personaje:
            return json_error("Personaje no encontrado", code=404)

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
        for item in safe_inventario(personaje.inventario):
            write(f"- {item}", 15)

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
        return json_error("Error generando PDF", e, 500)

