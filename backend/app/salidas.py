"""Salidas grupales y participantes (HU-008, HU-009, HU-010 y HU-011)."""
from datetime import datetime

from flask import Blueprint, g, jsonify, request

from .auth import error, requiere_sesion
from .compatibilidad import calcular_puntaje, nivel_usuario, sugerir_participantes
from .db import fila, filas, get_db
from .perfiles import CONSULTA_PERFIL, obtener_perfil
from .rutas import preparar_ruta

bp = Blueprint("salidas", __name__, url_prefix="/api")


def ahora():
    return datetime.now()


def momento_salida(salida):
    return datetime.fromisoformat(f"{salida['fecha']}T{salida['horario']}")


def nombre_publico(persona):
    """Por privacidad, solo se muestra el nombre y la inicial del apellido."""
    return f"{persona['nombre']} {persona['apellido'][:1]}."


def lugares_ocupados(db, id_salida):
    return db.execute("SELECT COUNT(*) FROM participacion WHERE id_salida = ? AND estado = 'confirmado'",
                      (id_salida,)).fetchone()[0]


def actualizar_estado(db, salida):
    """HU-010 R3: abierta, completa o finalizada según el cupo y la fecha."""
    if momento_salida(salida) <= ahora():
        estado = "finalizada"
    elif lugares_ocupados(db, salida["id_salida"]) >= salida["cupo"]:
        estado = "completa"
    else:
        estado = "abierta"
    if estado != salida["estado"]:
        db.execute("UPDATE salida SET estado = ? WHERE id_salida = ?", (estado, salida["id_salida"]))
        salida["estado"] = estado
    return estado


def obtener_salida(db, id_salida):
    salida = fila(db.execute("SELECT * FROM salida WHERE id_salida = ?", (id_salida,)).fetchone())
    if salida:
        actualizar_estado(db, salida)
    return salida


def validar_datos_salida(datos, parcial=False):
    """Criterios de aceptación de HU-008 y HU-011."""
    campos = ["fecha", "horario", "punto_encuentro", "cupo"]
    if any(str(datos.get(c, "")).strip() == "" for c in campos):
        return None, "Completá la fecha, el horario, el punto de encuentro y el cupo."
    try:
        momento = datetime.fromisoformat(f"{datos['fecha']}T{datos['horario']}")
        cupo = int(datos["cupo"])
    except (TypeError, ValueError):
        return None, "La fecha, el horario o el cupo no son válidos."
    if momento <= ahora():
        return None, "La fecha y el horario de la salida deben ser posteriores al momento actual."
    if cupo <= 0:
        return None, "El cupo debe ser mayor que cero."
    valores = {
        "fecha": momento.date().isoformat(),
        "horario": momento.strftime("%H:%M"),
        "punto_encuentro": str(datos["punto_encuentro"]).strip(),
        "cupo": cupo,
    }
    for campo in ("latitud_encuentro", "longitud_encuentro"):
        valor = datos.get(campo)
        valores[campo] = float(valor) if valor not in (None, "") else None
    return valores, None


def resumen_salida(db, salida):
    ruta = fila(db.execute("SELECT id_ruta, nombre, ubicacion, nivel_dificultad, tipo_actividad FROM ruta WHERE id_ruta = ?",
                           (salida["id_ruta"],)).fetchone())
    return {**salida, "ruta": ruta, "ocupados": lugares_ocupados(db, salida["id_salida"])}


@bp.post("/salidas")
@requiere_sesion()
def crear_salida():
    """HU-008: el organizador crea la salida y ocupa el primer lugar del cupo."""
    datos = request.get_json(silent=True) or {}
    db = get_db()
    ruta = fila(db.execute("SELECT * FROM ruta WHERE id_ruta = ?", (datos.get("id_ruta"),)).fetchone())
    if ruta is None:
        return error("Seleccioná una ruta válida.")
    perfil = obtener_perfil(g.usuario["id_usuario"])
    if perfil is None:
        return error("Completá tu perfil antes de organizar una salida.", 409)
    if nivel_usuario(perfil["nivel_experiencia"], perfil["condicion_fisica"]) < ruta["nivel_dificultad"]:
        return error("La dificultad de la ruta supera tu nivel.", 409)
    valores, mensaje = validar_datos_salida(datos)
    if mensaje:
        return error(mensaje)
    marca = ahora().isoformat(timespec="seconds")
    db.execute("BEGIN")
    id_salida = db.execute(
        """INSERT INTO salida (id_ruta, id_organizador, fecha, horario, punto_encuentro,
           latitud_encuentro, longitud_encuentro, cupo, estado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'abierta')""",
        (ruta["id_ruta"], g.usuario["id_usuario"], valores["fecha"], valores["horario"],
         valores["punto_encuentro"], valores["latitud_encuentro"], valores["longitud_encuentro"],
         valores["cupo"])).lastrowid
    db.execute("INSERT INTO participacion (id_salida, id_usuario, estado, fecha_estado) VALUES (?, ?, 'confirmado', ?)",
               (id_salida, g.usuario["id_usuario"], marca))
    actualizar_estado(db, fila(db.execute("SELECT * FROM salida WHERE id_salida = ?", (id_salida,)).fetchone()))
    db.execute("COMMIT")
    return jsonify({"id_salida": id_salida}), 201


@bp.get("/salidas/<int:id_salida>")
@requiere_sesion()
def detalle_salida(id_salida):
    db = get_db()
    salida = obtener_salida(db, id_salida)
    if salida is None:
        return error("La salida no existe.", 404)
    ruta = preparar_ruta(fila(db.execute("SELECT * FROM ruta WHERE id_ruta = ?", (salida["id_ruta"],)).fetchone()))
    organizador = fila(db.execute("SELECT nombre, apellido FROM usuario WHERE id_usuario = ?",
                                  (salida["id_organizador"],)).fetchone())
    confirmados = filas(db.execute(
        """SELECT u.id_usuario, u.nombre, u.apellido FROM participacion pa
           JOIN usuario u ON u.id_usuario = pa.id_usuario
           WHERE pa.id_salida = ? AND pa.estado = 'confirmado' ORDER BY pa.fecha_estado""",
        (id_salida,)).fetchall())
    propia = fila(db.execute("SELECT estado FROM participacion WHERE id_salida = ? AND id_usuario = ?",
                             (id_salida, g.usuario["id_usuario"])).fetchone())
    perfil = obtener_perfil(g.usuario["id_usuario"])
    puntaje = calcular_puntaje(perfil, ruta)[0] if perfil else None
    nivel = nivel_usuario(perfil["nivel_experiencia"], perfil["condicion_fisica"]) if perfil else None
    return jsonify({
        **salida,
        "ruta": ruta,
        "organizador": nombre_publico(organizador),
        "es_organizador": salida["id_organizador"] == g.usuario["id_usuario"],
        "participantes": [{"id_usuario": p["id_usuario"], "nombre": nombre_publico(p),
                           "organizador": p["id_usuario"] == salida["id_organizador"]} for p in confirmados],
        "ocupados": len(confirmados),
        "disponibles": max(0, salida["cupo"] - len(confirmados)),
        "mi_estado": propia["estado"] if propia else None,
        "mi_puntaje": puntaje,
        "mi_nivel": nivel,
        "puedo_participar": nivel is not None and nivel >= ruta["nivel_dificultad"],
    })


@bp.put("/salidas/<int:id_salida>")
@requiere_sesion()
def modificar_salida(id_salida):
    """HU-011: solo el organizador modifica la salida, y los cambios quedan señalados."""
    db = get_db()
    salida = obtener_salida(db, id_salida)
    if salida is None:
        return error("La salida no existe.", 404)
    if salida["id_organizador"] != g.usuario["id_usuario"]:
        return error("Solo el organizador puede modificar la salida.", 403)
    if salida["estado"] == "finalizada":
        return error("La salida ya se realizó y no puede modificarse.", 409)
    valores, mensaje = validar_datos_salida(request.get_json(silent=True) or {})
    if mensaje:
        return error(mensaje)
    ocupados = lugares_ocupados(db, id_salida)
    if valores["cupo"] < ocupados:
        return error(f"El cupo no puede ser menor que los {ocupados} participantes confirmados.")
    etiquetas = {"fecha": "la fecha", "horario": "el horario", "punto_encuentro": "el punto de encuentro",
                 "cupo": "el cupo"}
    cambios = [f"{etiquetas[c]} cambió de {salida[c]} a {valores[c]}"
               for c in etiquetas if str(salida[c]) != str(valores[c])]
    texto = ("Modificado por el organizador: " + "; ".join(cambios) + ".") if cambios else salida["ultimo_cambio"]
    db.execute("""UPDATE salida SET fecha = ?, horario = ?, punto_encuentro = ?, latitud_encuentro = ?,
                  longitud_encuentro = ?, cupo = ?, ultimo_cambio = ? WHERE id_salida = ?""",
               (valores["fecha"], valores["horario"], valores["punto_encuentro"], valores["latitud_encuentro"],
                valores["longitud_encuentro"], valores["cupo"], texto, id_salida))
    actualizar_estado(db, obtener_salida(db, id_salida))
    return jsonify({"id_salida": id_salida, "ultimo_cambio": texto})


@bp.get("/salidas/<int:id_salida>/sugerencias")
@requiere_sesion()
def sugerencias(id_salida):
    """HU-009: candidatos compatibles con la ruta de la salida."""
    db = get_db()
    salida = obtener_salida(db, id_salida)
    if salida is None:
        return error("La salida no existe.", 404)
    if salida["id_organizador"] != g.usuario["id_usuario"]:
        return error("Solo el organizador puede ver las sugerencias.", 403)
    ruta = fila(db.execute("SELECT * FROM ruta WHERE id_ruta = ?", (salida["id_ruta"],)).fetchone())
    excluir = {r[0] for r in db.execute(
        "SELECT id_usuario FROM participacion WHERE id_salida = ? AND estado IN ('invitado', 'confirmado')",
        (id_salida,)).fetchall()}
    excluir.add(salida["id_organizador"])
    candidatos = filas(db.execute(CONSULTA_PERFIL + " WHERE u.rol = 'usuario'").fetchall())
    sugeridos = sugerir_participantes(ruta, candidatos, excluir)
    invitados = filas(db.execute(
        """SELECT u.id_usuario, u.nombre, u.apellido FROM participacion pa JOIN usuario u
           ON u.id_usuario = pa.id_usuario WHERE pa.id_salida = ? AND pa.estado = 'invitado'""",
        (id_salida,)).fetchall())
    return jsonify({
        "salida": resumen_salida(db, salida),
        "sugeridos": [{"id_usuario": p["id_usuario"], "nombre": nombre_publico(p),
                       "nivel": nivel_usuario(p["nivel_experiencia"], p["condicion_fisica"]),
                       "ubicacion": p["ubicacion"], "puntaje": p["puntaje"]} for p in sugeridos],
        "invitados": [{"id_usuario": p["id_usuario"], "nombre": nombre_publico(p)} for p in invitados],
    })


@bp.post("/salidas/<int:id_salida>/invitaciones")
@requiere_sesion()
def invitar(id_salida):
    """HU-009 criterio 7: la invitación no reserva un lugar del cupo."""
    db = get_db()
    salida = obtener_salida(db, id_salida)
    if salida is None:
        return error("La salida no existe.", 404)
    if salida["id_organizador"] != g.usuario["id_usuario"]:
        return error("Solo el organizador puede invitar participantes.", 403)
    if salida["estado"] == "finalizada":
        return error("La salida ya se realizó.", 409)
    id_usuario = (request.get_json(silent=True) or {}).get("id_usuario")
    ruta = fila(db.execute("SELECT * FROM ruta WHERE id_ruta = ?", (salida["id_ruta"],)).fetchone())
    candidato = fila(db.execute(CONSULTA_PERFIL + " WHERE u.id_usuario = ?", (id_usuario,)).fetchone())
    if candidato is None or not sugerir_participantes(ruta, [candidato]):
        return error("El usuario no es compatible con la ruta de la salida.")
    existente = fila(db.execute("SELECT estado FROM participacion WHERE id_salida = ? AND id_usuario = ?",
                                (id_salida, id_usuario)).fetchone())
    if existente and existente["estado"] == "confirmado":
        return error("El usuario ya confirmó su asistencia.", 409)
    marca = ahora().isoformat(timespec="seconds")
    db.execute("""INSERT INTO participacion (id_salida, id_usuario, estado, fecha_estado) VALUES (?, ?, 'invitado', ?)
                  ON CONFLICT (id_salida, id_usuario) DO UPDATE SET estado = 'invitado', fecha_estado = excluded.fecha_estado""",
               (id_salida, id_usuario, marca))
    return jsonify({"estado": "invitado"}), 201


@bp.post("/salidas/<int:id_salida>/confirmar")
@requiere_sesion()
def confirmar(id_salida):
    """HU-010: confirmación con control de nivel y de cupo."""
    db = get_db()
    perfil = obtener_perfil(g.usuario["id_usuario"])
    if perfil is None:
        return error("Completá tu perfil antes de sumarte a una salida.", 409)
    # BEGIN IMMEDIATE bloquea la escritura: si dos usuarios confirman a la vez el último
    # lugar, la segunda confirmación espera y encuentra el cupo completo (criterio 5).
    db.execute("BEGIN IMMEDIATE")
    try:
        salida = obtener_salida(db, id_salida)
        if salida is None:
            db.execute("ROLLBACK")
            return error("La salida no existe.", 404)
        ruta = fila(db.execute("SELECT nivel_dificultad FROM ruta WHERE id_ruta = ?", (salida["id_ruta"],)).fetchone())
        nivel = nivel_usuario(perfil["nivel_experiencia"], perfil["condicion_fisica"])
        if salida["estado"] == "finalizada":
            db.execute("ROLLBACK")
            return error("La salida ya se realizó.", 409)
        if nivel < ruta["nivel_dificultad"]:
            db.execute("ROLLBACK")
            return error(f"La ruta requiere un nivel {ruta['nivel_dificultad']} y tu nivel es {nivel}.", 409)
        propia = fila(db.execute("SELECT estado FROM participacion WHERE id_salida = ? AND id_usuario = ?",
                                 (id_salida, g.usuario["id_usuario"])).fetchone())
        if propia and propia["estado"] == "confirmado":
            db.execute("ROLLBACK")
            return error("Ya confirmaste tu asistencia.", 409)
        if lugares_ocupados(db, id_salida) >= salida["cupo"]:
            db.execute("ROLLBACK")
            return error("No hay lugares disponibles en esta salida.", 409)
        marca = ahora().isoformat(timespec="seconds")
        db.execute("""INSERT INTO participacion (id_salida, id_usuario, estado, fecha_estado) VALUES (?, ?, 'confirmado', ?)
                      ON CONFLICT (id_salida, id_usuario) DO UPDATE SET estado = 'confirmado', fecha_estado = excluded.fecha_estado""",
                   (id_salida, g.usuario["id_usuario"], marca))
        estado = actualizar_estado(db, salida)
        db.execute("COMMIT")
    except Exception:
        db.execute("ROLLBACK")
        raise
    return jsonify({"estado": "confirmado", "estado_salida": estado,
                    "ocupados": lugares_ocupados(db, id_salida), "cupo": salida["cupo"]})


@bp.post("/salidas/<int:id_salida>/cancelar")
@requiere_sesion()
def cancelar(id_salida):
    """HU-010 criterio 6: la cancelación libera el lugar."""
    db = get_db()
    salida = obtener_salida(db, id_salida)
    if salida is None:
        return error("La salida no existe.", 404)
    if salida["estado"] == "finalizada":
        return error("La salida ya se realizó.", 409)
    if salida["id_organizador"] == g.usuario["id_usuario"]:
        return error("El organizador no puede cancelar su asistencia.", 409)
    cursor = db.execute("""UPDATE participacion SET estado = 'cancelado', fecha_estado = ?
                           WHERE id_salida = ? AND id_usuario = ? AND estado = 'confirmado'""",
                        (ahora().isoformat(timespec="seconds"), id_salida, g.usuario["id_usuario"]))
    if cursor.rowcount == 0:
        return error("No tenés una asistencia confirmada en esta salida.", 409)
    estado = actualizar_estado(db, salida)
    return jsonify({"estado": "cancelado", "estado_salida": estado})


@bp.get("/mis-salidas")
@requiere_sesion()
def mis_salidas():
    db = get_db()
    yo = g.usuario["id_usuario"]
    perfil = obtener_perfil(yo)
    resultado = {"organizadas": [], "invitaciones": [], "confirmadas": [], "disponibles": []}
    for salida in filas(db.execute("SELECT * FROM salida ORDER BY fecha, horario").fetchall()):
        actualizar_estado(db, salida)
        propia = fila(db.execute("SELECT estado FROM participacion WHERE id_salida = ? AND id_usuario = ?",
                                 (salida["id_salida"], yo)).fetchone())
        item = resumen_salida(db, salida)
        if salida["id_organizador"] == yo:
            resultado["organizadas"].append(item)
        elif propia and propia["estado"] == "invitado":
            resultado["invitaciones"].append(item)
        elif propia and propia["estado"] == "confirmado":
            resultado["confirmadas"].append(item)
        elif perfil and salida["estado"] == "abierta":
            nivel = nivel_usuario(perfil["nivel_experiencia"], perfil["condicion_fisica"])
            ruta = item["ruta"]
            if nivel >= ruta["nivel_dificultad"] and ruta["ubicacion"] == perfil["zona_interes"]:
                resultado["disponibles"].append(item)
    return jsonify(resultado)
