"""Registro, inicio de sesión y control de acceso (HU-001 y HU-002)."""
import re
import time
from functools import wraps

import bcrypt
from flask import Blueprint, current_app, g, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from .db import fila, get_db

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

INTENTOS_MAXIMOS = 5
BLOQUEO_SEGUNDOS = 15 * 60
SESION_SEGUNDOS = 60 * 60
_intentos = {}  # correo -> (cantidad de intentos fallidos, bloqueado hasta)


def error(mensaje, status=400):
    return jsonify({"error": mensaje}), status


def validar_contrasena(contrasena):
    """Política de contraseñas definida en la sección Seguridad."""
    faltan = []
    if len(contrasena) < 8:
        faltan.append("al menos 8 caracteres")
    if not re.search(r"[A-Z]", contrasena):
        faltan.append("una letra mayúscula")
    if not re.search(r"[a-z]", contrasena):
        faltan.append("una letra minúscula")
    if not re.search(r"\d", contrasena):
        faltan.append("un número")
    return faltan


def _serializador():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="sesion")


def emitir_token(id_usuario):
    return _serializador().dumps({"id": id_usuario})


def requiere_sesion(rol=None):
    def decorador(funcion):
        @wraps(funcion)
        def envoltura(*args, **kwargs):
            encabezado = request.headers.get("Authorization", "")
            token = encabezado.removeprefix("Bearer ").strip()
            try:
                datos = _serializador().loads(token, max_age=SESION_SEGUNDOS)
            except SignatureExpired:
                return error("La sesión expiró. Volvé a iniciar sesión.", 401)
            except BadSignature:
                return error("Debés iniciar sesión.", 401)
            usuario = fila(get_db().execute(
                "SELECT id_usuario, nombre, apellido, correo, rol FROM usuario WHERE id_usuario = ?",
                (datos["id"],)).fetchone())
            if usuario is None:
                return error("Debés iniciar sesión.", 401)
            if rol and usuario["rol"] != rol:
                return error("No tenés permisos para realizar esta acción.", 403)
            g.usuario = usuario
            return funcion(*args, **kwargs)
        return envoltura
    return decorador


@bp.post("/registro")
def registro():
    datos = request.get_json(silent=True) or {}
    campos = ["nombre", "apellido", "correo", "contrasena"]
    if any(not str(datos.get(c, "")).strip() for c in campos):
        return error("Todos los campos son requeridos.")
    correo = datos["correo"].strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo):
        return error("El correo electrónico no es válido.")
    faltan = validar_contrasena(datos["contrasena"])
    if faltan:
        return error("La contraseña debe tener " + ", ".join(faltan) + ".")
    db = get_db()
    if db.execute("SELECT 1 FROM usuario WHERE correo = ?", (correo,)).fetchone():
        return error("El correo electrónico ya está en uso.", 409)
    contrasena_hash = bcrypt.hashpw(datos["contrasena"].encode(), bcrypt.gensalt()).decode()
    cursor = db.execute(
        "INSERT INTO usuario (nombre, apellido, correo, contrasena_hash) VALUES (?, ?, ?, ?)",
        (datos["nombre"].strip(), datos["apellido"].strip(), correo, contrasena_hash))
    return jsonify({"token": emitir_token(cursor.lastrowid),
                    "usuario": {"id_usuario": cursor.lastrowid, "nombre": datos["nombre"].strip(),
                                "rol": "usuario"},
                    "perfil_completo": False}), 201


@bp.post("/login")
def login():
    datos = request.get_json(silent=True) or {}
    correo = str(datos.get("correo", "")).strip().lower()
    contrasena = str(datos.get("contrasena", ""))
    if not correo or not contrasena:
        return error("Completá el correo y la contraseña.")
    fallidos, bloqueado_hasta = _intentos.get(correo, (0, 0))
    if bloqueado_hasta > time.time():
        minutos = int((bloqueado_hasta - time.time()) // 60) + 1
        return error(f"La cuenta está bloqueada por intentos fallidos. Intentá en {minutos} minutos.", 429)
    db = get_db()
    usuario = fila(db.execute("SELECT * FROM usuario WHERE correo = ?", (correo,)).fetchone())
    if usuario is None or not bcrypt.checkpw(contrasena.encode(), usuario["contrasena_hash"].encode()):
        fallidos += 1
        _intentos[correo] = (0, time.time() + BLOQUEO_SEGUNDOS) if fallidos >= INTENTOS_MAXIMOS \
            else (fallidos, 0)
        # El mensaje no indica cuál de los dos datos es incorrecto.
        return error("El correo o la contraseña son incorrectos.", 401)
    _intentos.pop(correo, None)
    perfil = db.execute("SELECT 1 FROM perfil WHERE id_usuario = ?", (usuario["id_usuario"],)).fetchone()
    return jsonify({"token": emitir_token(usuario["id_usuario"]),
                    "usuario": {"id_usuario": usuario["id_usuario"], "nombre": usuario["nombre"],
                                "rol": usuario["rol"]},
                    "perfil_completo": perfil is not None})
