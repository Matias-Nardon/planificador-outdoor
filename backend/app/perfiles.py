"""Perfil del usuario y sus preferencias (HU-003)."""
from flask import Blueprint, g, jsonify, request

from . import catalogos
from .auth import error, requiere_sesion
from .db import fila, get_db

bp = Blueprint("perfiles", __name__, url_prefix="/api")

CONSULTA_PERFIL = """
    SELECT u.id_usuario, u.nombre, u.apellido, p.id_perfil, p.nivel_experiencia,
           p.condicion_fisica, p.ubicacion, p.latitud, p.longitud,
           pr.tipo_actividad, pr.distancia_maxima, pr.duracion_maxima, pr.zona_interes
    FROM usuario u
    JOIN perfil p ON p.id_usuario = u.id_usuario
    JOIN preferencia pr ON pr.id_perfil = p.id_perfil
"""


def obtener_perfil(id_usuario):
    return fila(get_db().execute(CONSULTA_PERFIL + " WHERE u.id_usuario = ?", (id_usuario,)).fetchone())


def entero_en_escala(valor):
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return None
    return numero if 1 <= numero <= 5 else None


@bp.get("/catalogos")
def obtener_catalogos():
    return jsonify({
        "actividades": catalogos.ACTIVIDADES,
        "zonas": catalogos.ZONAS,
        "localidades": list(catalogos.LOCALIDADES),
        "niveles": catalogos.NIVELES,
        "condicion_fisica": catalogos.CONDICION_FISICA,
        "dificultad": catalogos.DIFICULTAD,
    })


@bp.get("/perfil")
@requiere_sesion()
def ver_perfil():
    perfil = obtener_perfil(g.usuario["id_usuario"])
    return jsonify({"perfil": perfil, "usuario": g.usuario})


@bp.put("/perfil")
@requiere_sesion()
def guardar_perfil():
    datos = request.get_json(silent=True) or {}
    experiencia = entero_en_escala(datos.get("nivel_experiencia"))
    condicion = entero_en_escala(datos.get("condicion_fisica"))
    if experiencia is None or condicion is None:
        return error("El nivel de experiencia y la condición física deben estar entre 1 y 5.")
    ubicacion = datos.get("ubicacion")
    if ubicacion not in catalogos.LOCALIDADES:
        return error("Seleccioná una ubicación válida.")
    if datos.get("tipo_actividad") not in catalogos.ACTIVIDADES:
        return error("Seleccioná un tipo de actividad válido.")
    if datos.get("zona_interes") not in catalogos.ZONAS:
        return error("Seleccioná una zona de interés válida.")
    try:
        distancia = float(datos.get("distancia_maxima"))
        duracion = float(datos.get("duracion_maxima"))
    except (TypeError, ValueError):
        return error("La distancia y la duración máximas deben ser numéricas.")
    if distancia <= 0 or duracion <= 0:
        return error("La distancia y la duración máximas deben ser mayores que cero.")

    latitud, longitud = catalogos.LOCALIDADES[ubicacion]
    db = get_db()
    id_usuario = g.usuario["id_usuario"]
    db.execute("BEGIN")
    existente = db.execute("SELECT id_perfil FROM perfil WHERE id_usuario = ?", (id_usuario,)).fetchone()
    if existente:
        id_perfil = existente["id_perfil"]
        db.execute("""UPDATE perfil SET nivel_experiencia = ?, condicion_fisica = ?, ubicacion = ?,
                      latitud = ?, longitud = ? WHERE id_perfil = ?""",
                   (experiencia, condicion, ubicacion, latitud, longitud, id_perfil))
        db.execute("""UPDATE preferencia SET tipo_actividad = ?, distancia_maxima = ?,
                      duracion_maxima = ?, zona_interes = ? WHERE id_perfil = ?""",
                   (datos["tipo_actividad"], distancia, duracion, datos["zona_interes"], id_perfil))
    else:
        id_perfil = db.execute("""INSERT INTO perfil (id_usuario, nivel_experiencia, condicion_fisica,
                                  ubicacion, latitud, longitud) VALUES (?, ?, ?, ?, ?, ?)""",
                               (id_usuario, experiencia, condicion, ubicacion, latitud, longitud)).lastrowid
        db.execute("""INSERT INTO preferencia (id_perfil, tipo_actividad, distancia_maxima,
                      duracion_maxima, zona_interes) VALUES (?, ?, ?, ?, ?)""",
                   (id_perfil, datos["tipo_actividad"], distancia, duracion, datos["zona_interes"]))
    db.execute("COMMIT")
    return jsonify({"perfil": obtener_perfil(id_usuario)})
