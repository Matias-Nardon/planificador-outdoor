"""Rutas: registro, ficha y recomendación (HU-004, HU-005, HU-006 y HU-007)."""
import json
from datetime import datetime

from flask import Blueprint, g, jsonify, request

from . import catalogos
from .auth import error, requiere_sesion
from .compatibilidad import calcular_puntaje, motivo_exclusion, nivel_usuario, recomendar_rutas
from .db import fila, filas, get_db
from .perfiles import obtener_perfil

bp = Blueprint("rutas", __name__, url_prefix="/api")

CAMPOS_OBLIGATORIOS = ["nombre", "tipo_actividad", "ubicacion", "distancia", "desnivel",
                       "duracion_estimada", "nivel_dificultad"]


def preparar_ruta(ruta):
    if ruta and ruta.get("trazado"):
        try:
            ruta["trazado"] = json.loads(ruta["trazado"])
        except ValueError:
            ruta["trazado"] = None
    return ruta


def validar_ruta(datos):
    """Criterios de aceptación de HU-004."""
    if any(datos.get(c) in (None, "") for c in CAMPOS_OBLIGATORIOS):
        return None, "Completá nombre, actividad, ubicación, distancia, desnivel, duración y dificultad."
    if datos["tipo_actividad"] not in catalogos.ACTIVIDADES:
        return None, "El tipo de actividad no es válido."
    if datos["ubicacion"] not in catalogos.ZONAS:
        return None, "La zona de la ruta no es válida."
    try:
        valores = {
            "distancia": float(datos["distancia"]),
            "desnivel": int(float(datos["desnivel"])),
            "duracion_estimada": float(datos["duracion_estimada"]),
            "nivel_dificultad": int(datos["nivel_dificultad"]),
            "latitud_inicio": float(datos["latitud_inicio"]) if datos.get("latitud_inicio") not in (None, "") else None,
            "longitud_inicio": float(datos["longitud_inicio"]) if datos.get("longitud_inicio") not in (None, "") else None,
        }
    except (TypeError, ValueError):
        return None, "Los valores numéricos no son válidos."
    if valores["distancia"] <= 0 or valores["duracion_estimada"] <= 0 or valores["desnivel"] < 0:
        return None, "La distancia y la duración deben ser mayores que cero y el desnivel no puede ser negativo."
    if not 1 <= valores["nivel_dificultad"] <= 5:
        return None, "El nivel de dificultad debe estar entre 1 y 5."
    trazado = datos.get("trazado")
    if trazado:
        try:
            geo = trazado if isinstance(trazado, dict) else json.loads(trazado)
            if geo.get("type") != "LineString" or len(geo.get("coordinates", [])) < 2:
                raise ValueError
            trazado = json.dumps(geo)
        except (ValueError, AttributeError):
            return None, "El trazado debe ser un GeoJSON de tipo LineString."
    valores.update({
        "nombre": datos["nombre"].strip(),
        "tipo_actividad": datos["tipo_actividad"],
        "ubicacion": datos["ubicacion"],
        "trazado": trazado or None,
        "equipamiento": (datos.get("equipamiento") or "").strip() or None,
        "condiciones_terreno": (datos.get("condiciones_terreno") or "").strip() or None,
    })
    return valores, None


@bp.get("/rutas")
@requiere_sesion(rol="administrador")
def listar_rutas():
    rutas = filas(get_db().execute("SELECT * FROM ruta ORDER BY ubicacion, nombre").fetchall())
    return jsonify([preparar_ruta(r) for r in rutas])


@bp.post("/rutas")
@requiere_sesion(rol="administrador")
def crear_ruta():
    valores, mensaje = validar_ruta(request.get_json(silent=True) or {})
    if mensaje:
        return error(mensaje)
    columnas = ", ".join(valores)
    marcas = ", ".join("?" for _ in valores)
    cursor = get_db().execute(f"INSERT INTO ruta ({columnas}) VALUES ({marcas})", tuple(valores.values()))
    return jsonify({"id_ruta": cursor.lastrowid}), 201


@bp.put("/rutas/<int:id_ruta>")
@requiere_sesion(rol="administrador")
def modificar_ruta(id_ruta):
    valores, mensaje = validar_ruta(request.get_json(silent=True) or {})
    if mensaje:
        return error(mensaje)
    asignaciones = ", ".join(f"{c} = ?" for c in valores)
    cursor = get_db().execute(f"UPDATE ruta SET {asignaciones} WHERE id_ruta = ?",
                              (*valores.values(), id_ruta))
    if cursor.rowcount == 0:
        return error("La ruta no existe.", 404)
    return jsonify({"id_ruta": id_ruta})


@bp.get("/rutas/<int:id_ruta>")
@requiere_sesion()
def ficha_ruta(id_ruta):
    """HU-005: ficha de la ruta, con el puntaje de compatibilidad del usuario."""
    ruta = preparar_ruta(fila(get_db().execute("SELECT * FROM ruta WHERE id_ruta = ?", (id_ruta,)).fetchone()))
    if ruta is None:
        return error("La ruta no existe.", 404)
    perfil = obtener_perfil(g.usuario["id_usuario"])
    if perfil:
        ruta["compatible"] = motivo_exclusion(perfil, ruta) is None
        ruta["puntaje"], ruta["distancia_usuario_km"] = calcular_puntaje(perfil, ruta)
        ruta["nivel_usuario"] = nivel_usuario(perfil["nivel_experiencia"], perfil["condicion_fisica"])
    return jsonify(ruta)


@bp.get("/recomendaciones")
@requiere_sesion()
def recomendaciones():
    """HU-007: rutas compatibles con el perfil, ordenadas por puntaje."""
    perfil = obtener_perfil(g.usuario["id_usuario"])
    if perfil is None:
        return error("Completá tu perfil para recibir recomendaciones de rutas.", 409)
    db = get_db()
    rutas = filas(db.execute("SELECT * FROM ruta").fetchall())
    recomendadas, excluidas = recomendar_rutas(perfil, rutas)
    ahora = datetime.now().isoformat(timespec="seconds")
    db.execute("BEGIN")
    db.execute("DELETE FROM recomendacion WHERE id_usuario = ?", (perfil["id_usuario"],))
    db.executemany("INSERT INTO recomendacion (id_usuario, id_ruta, puntaje, fecha) VALUES (?, ?, ?, ?)",
                   [(perfil["id_usuario"], r["id_ruta"], r["puntaje"], ahora) for r in recomendadas])
    db.execute("COMMIT")
    return jsonify({
        "perfil": perfil,
        "nivel_usuario": nivel_usuario(perfil["nivel_experiencia"], perfil["condicion_fisica"]),
        "rutas": [preparar_ruta(r) for r in recomendadas],
        "excluidas": excluidas,
    })
