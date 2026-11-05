"""Carga de datos de prueba (tareas técnicas TT-03 y TT-05).

Recrea la base de datos con un administrador, usuarios de distinto nivel,
un conjunto de rutas clasificadas con la escala única de dificultad y dos
salidas grupales de ejemplo. Los datos son ficticios.

Uso:  python seed.py
"""
import json
from datetime import date, datetime, timedelta
from pathlib import Path

import bcrypt

from app import create_app
from app.catalogos import LOCALIDADES
from app.db import get_db

CONTRASENA_PRUEBA = "Prueba123"
CONTRASENA_ADMIN = "Admin1234"


def trazado(lat, lon, pasos):
    """Genera un recorrido GeoJSON de ejemplo a partir del punto de inicio."""
    puntos, (la, lo) = [[lon, lat]], (lat, lon)
    for dlat, dlon in pasos:
        la, lo = la + dlat, lo + dlon
        puntos.append([round(lo, 5), round(la, 5)])
    return json.dumps({"type": "LineString", "coordinates": puntos})


IDA = [(0.004, 0.003), (0.003, 0.006), (0.006, 0.004), (0.004, 0.007), (0.007, 0.003), (0.003, 0.006)]
CIRCUITO = [(0.006, 0.002), (0.004, 0.007), (-0.003, 0.008), (-0.007, 0.002), (-0.004, -0.009), (0.004, -0.010)]

# nombre, actividad, zona, lat, lon, distancia, desnivel, duración, dificultad, equipamiento, terreno, forma
RUTAS = [
    ("Sendero Quebrada del Arroyo Blanco", "Senderismo", "Sierras Chicas", -31.0050, -64.2850, 12.4, 650, 5, 3,
     "Calzado de trekking, 2 litros de agua, protector solar y abrigo liviano.",
     "Sendero de tierra y piedra suelta. Tramo final empinado.", IDA),
    ("Mirador de los Cóndores", "Senderismo", "Sierras Chicas", -31.1450, -64.3450, 14.8, 720, 6, 3,
     "Calzado de trekking, bastones, 2 litros de agua y comida para el día.",
     "Sendero de montaña con pendientes sostenidas y sectores rocosos.", IDA),
    ("Circuito Cerro de las Piedras", "Senderismo", "Sierras Chicas", -31.2650, -64.3250, 8.2, 420, 3, 2,
     "Calzado deportivo con buena suela, agua y gorra.",
     "Sendero marcado de tierra con algunos escalones de piedra.", CIRCUITO),
    ("Sendero del Río Seco", "Senderismo", "Sierras Chicas", -31.1850, -64.3000, 10.1, 380, 4, 2,
     "Calzado deportivo, agua y repelente.", "Sendero amplio junto al cauce, con cruces de arroyo.", IDA),
    ("Paseo del Arroyo Saldán", "Senderismo", "Sierras Chicas", -31.3050, -64.3100, 5.0, 120, 1.5, 1,
     "Calzado cómodo y agua.", "Camino llano de tierra, apto para principiantes.", CIRCUITO),
    ("Travesía Cumbres de Ochoa", "Senderismo", "Sierras Chicas", -31.0800, -64.3700, 18.0, 1100, 8, 4,
     "Calzado de trekking, bastones, 3 litros de agua, abrigo e impermeable.",
     "Senda de montaña poco marcada, con pendientes fuertes.", IDA),
    ("Filo de las Sierras Chicas", "Senderismo", "Sierras Chicas", -31.1100, -64.3900, 24.0, 1500, 10, 5,
     "Equipo completo de montaña, GPS y 4 litros de agua.",
     "Travesía por filo expuesto, sin sendero en varios tramos.", IDA),
    ("Circuito del Dique La Quebrada", "Ciclismo de montaña", "Sierras Chicas", -31.1600, -64.3300, 22.0, 450, 3, 2,
     "Bicicleta de montaña, casco, kit de reparación y agua.", "Camino de ripio con subidas cortas.", CIRCUITO),
    ("Cerro Pan de Azúcar", "Senderismo", "Punilla", -31.2350, -64.4250, 9.0, 550, 4, 3,
     "Calzado de trekking y agua.", "Sendero de montaña con escalones naturales.", IDA),
    ("Cerro Uritorco", "Senderismo", "Punilla", -30.8500, -64.5000, 11.0, 1000, 6, 4,
     "Calzado de trekking, 3 litros de agua y abrigo.", "Sendero de montaña con fuerte pendiente.", IDA),
    ("Quebrada del Condorito", "Trekking", "Traslasierra", -31.6400, -64.7000, 9.0, 400, 4, 2,
     "Calzado de trekking, abrigo y agua.", "Sendero de altura expuesto al viento.", IDA),
    ("Cerro Champaquí", "Trekking", "Calamuchita", -31.9900, -64.9300, 26.0, 1600, 10, 5,
     "Equipo completo de montaña, carpa y 4 litros de agua.", "Travesía de alta montaña.", IDA),
]

# nombre, apellido, correo, experiencia, condición, localidad, actividad, distancia máx., duración máx., zona
USUARIOS = [
    ("Martín", "Gómez", "martin.gomez@prueba.local", 4, 3, "Villa Allende", "Senderismo", 15, 6, "Sierras Chicas"),
    ("Lucía", "Fernández", "lucia.fernandez@prueba.local", 3, 3, "Córdoba Capital", "Senderismo", 15, 6, "Sierras Chicas"),
    ("Sofía", "Ruiz", "sofia.ruiz@prueba.local", 3, 3, "La Granja", "Senderismo", 15, 6, "Sierras Chicas"),
    ("Diego", "Pérez", "diego.perez@prueba.local", 3, 3, "Córdoba Capital", "Senderismo", 12, 6, "Sierras Chicas"),
    ("Julián", "Molina", "julian.molina@prueba.local", 4, 4, "Río Ceballos", "Senderismo", 20, 8, "Sierras Chicas"),
    ("Tomás", "Álvarez", "tomas.alvarez@prueba.local", 3, 3, "Villa Allende", "Senderismo", 15, 4, "Sierras Chicas"),
    ("Valentina", "López", "valentina.lopez@prueba.local", 5, 5, "Córdoba Capital", "Senderismo", 25, 8, "Sierras Chicas"),
    ("Nicolás", "Ortiz", "nicolas.ortiz@prueba.local", 4, 2, "Río Ceballos", "Senderismo", 15, 6, "Sierras Chicas"),
    ("Camila", "Díaz", "camila.diaz@prueba.local", 2, 2, "Villa Allende", "Senderismo", 10, 4, "Sierras Chicas"),
    ("Ana", "Ramos", "ana.ramos@prueba.local", 3, 3, "Cosquín", "Senderismo", 15, 6, "Punilla"),
]


def hash_(contrasena):
    return bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt()).decode()


def sabado_proximo(semanas=1):
    hoy = date.today()
    return (hoy + timedelta(days=(5 - hoy.weekday()) % 7 + 7 * semanas)).isoformat()


def main():
    base = Path(__file__).resolve().parent / "planificador.db"
    base.unlink(missing_ok=True)
    app = create_app({"DATABASE": str(base)})
    with app.app_context():
        db = get_db()
        db.execute("BEGIN")
        db.execute("INSERT INTO usuario (nombre, apellido, correo, contrasena_hash, rol) VALUES (?, ?, ?, ?, ?)",
                   ("Admin", "Sistema", "admin@prueba.local", hash_(CONTRASENA_ADMIN), "administrador"))
        hash_prueba = hash_(CONTRASENA_PRUEBA)
        ids = {}
        for nombre, apellido, correo, exp, cond, loc, act, dmax, tmax, zona in USUARIOS:
            id_usuario = db.execute("INSERT INTO usuario (nombre, apellido, correo, contrasena_hash) VALUES (?, ?, ?, ?)",
                                    (nombre, apellido, correo, hash_prueba)).lastrowid
            lat, lon = LOCALIDADES[loc]
            id_perfil = db.execute("""INSERT INTO perfil (id_usuario, nivel_experiencia, condicion_fisica, ubicacion,
                                      latitud, longitud) VALUES (?, ?, ?, ?, ?, ?)""",
                                   (id_usuario, exp, cond, loc, lat, lon)).lastrowid
            db.execute("""INSERT INTO preferencia (id_perfil, tipo_actividad, distancia_maxima, duracion_maxima,
                          zona_interes) VALUES (?, ?, ?, ?, ?)""", (id_perfil, act, dmax, tmax, zona))
            ids[nombre] = id_usuario
        rutas = {}
        for (nombre, act, zona, lat, lon, dist, desn, dur, dif, equipo, terreno, forma) in RUTAS:
            rutas[nombre] = db.execute(
                """INSERT INTO ruta (nombre, tipo_actividad, ubicacion, latitud_inicio, longitud_inicio, trazado,
                   distancia, desnivel, duracion_estimada, nivel_dificultad, equipamiento, condiciones_terreno)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (nombre, act, zona, lat, lon, trazado(lat, lon, forma), dist, desn, dur, dif, equipo, terreno)).lastrowid

        marca = datetime.now().isoformat(timespec="seconds")
        # Salida de ejemplo organizada por Julián, con lugares disponibles.
        s1 = db.execute("""INSERT INTO salida (id_ruta, id_organizador, fecha, horario, punto_encuentro,
                           latitud_encuentro, longitud_encuentro, cupo, estado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'abierta')""",
                        (rutas["Mirador de los Cóndores"], ids["Julián"], sabado_proximo(2), "07:30",
                         "Plaza central de Río Ceballos", -31.1667, -64.3167, 8)).lastrowid
        for nombre in ("Julián", "Valentina", "Tomás"):
            db.execute("INSERT INTO participacion (id_salida, id_usuario, estado, fecha_estado) VALUES (?, ?, 'confirmado', ?)",
                       (s1, ids[nombre], marca))
        # Salida con un solo lugar disponible, para mostrar el control del cupo.
        s2 = db.execute("""INSERT INTO salida (id_ruta, id_organizador, fecha, horario, punto_encuentro,
                           latitud_encuentro, longitud_encuentro, cupo, estado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'abierta')""",
                        (rutas["Circuito Cerro de las Piedras"], ids["Sofía"], sabado_proximo(1), "09:00",
                         "Estacionamiento del ingreso al circuito", -31.2650, -64.3250, 3)).lastrowid
        for nombre in ("Sofía", "Diego"):
            db.execute("INSERT INTO participacion (id_salida, id_usuario, estado, fecha_estado) VALUES (?, ?, 'confirmado', ?)",
                       (s2, ids[nombre], marca))
        db.execute("COMMIT")
    print(f"Base de datos creada en {base}")
    print(f"Administrador: admin@prueba.local / {CONTRASENA_ADMIN}")
    print(f"Usuarios de prueba (contraseña {CONTRASENA_PRUEBA}): " + ", ".join(u[2] for u in USUARIOS))


if __name__ == "__main__":
    main()
