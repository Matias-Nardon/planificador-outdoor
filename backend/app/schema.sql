-- Estructura de la base de datos según el diagrama de entidad-relación (TT-02).
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuario (
    id_usuario       INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre           TEXT NOT NULL,
    apellido         TEXT NOT NULL,
    correo           TEXT NOT NULL UNIQUE,
    contrasena_hash  TEXT NOT NULL,
    rol              TEXT NOT NULL DEFAULT 'usuario' CHECK (rol IN ('usuario', 'administrador'))
);

CREATE TABLE IF NOT EXISTS perfil (
    id_perfil          INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario         INTEGER NOT NULL UNIQUE REFERENCES usuario (id_usuario),
    nivel_experiencia  INTEGER NOT NULL CHECK (nivel_experiencia BETWEEN 1 AND 5),
    condicion_fisica   INTEGER NOT NULL CHECK (condicion_fisica BETWEEN 1 AND 5),
    ubicacion          TEXT NOT NULL,
    latitud            REAL,
    longitud           REAL
);

CREATE TABLE IF NOT EXISTS preferencia (
    id_preferencia    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_perfil         INTEGER NOT NULL REFERENCES perfil (id_perfil),
    tipo_actividad    TEXT NOT NULL,
    distancia_maxima  REAL NOT NULL CHECK (distancia_maxima > 0),
    duracion_maxima   REAL NOT NULL CHECK (duracion_maxima > 0),
    zona_interes      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ruta (
    id_ruta              INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre               TEXT NOT NULL,
    tipo_actividad       TEXT NOT NULL,
    ubicacion            TEXT NOT NULL,
    latitud_inicio       REAL,
    longitud_inicio      REAL,
    trazado              TEXT,
    distancia            REAL NOT NULL CHECK (distancia > 0),
    desnivel             INTEGER NOT NULL CHECK (desnivel >= 0),
    duracion_estimada    REAL NOT NULL CHECK (duracion_estimada > 0),
    nivel_dificultad     INTEGER NOT NULL CHECK (nivel_dificultad BETWEEN 1 AND 5),
    equipamiento         TEXT,
    condiciones_terreno  TEXT
);

CREATE TABLE IF NOT EXISTS recomendacion (
    id_recomendacion  INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario        INTEGER NOT NULL REFERENCES usuario (id_usuario),
    id_ruta           INTEGER NOT NULL REFERENCES ruta (id_ruta),
    puntaje           REAL NOT NULL,
    fecha             TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS salida (
    id_salida           INTEGER PRIMARY KEY AUTOINCREMENT,
    id_ruta             INTEGER NOT NULL REFERENCES ruta (id_ruta),
    id_organizador      INTEGER NOT NULL REFERENCES usuario (id_usuario),
    fecha               TEXT NOT NULL,
    horario             TEXT NOT NULL,
    punto_encuentro     TEXT NOT NULL,
    latitud_encuentro   REAL,
    longitud_encuentro  REAL,
    cupo                INTEGER NOT NULL CHECK (cupo > 0),
    estado              TEXT NOT NULL DEFAULT 'abierta' CHECK (estado IN ('abierta', 'completa', 'finalizada')),
    ultimo_cambio       TEXT
);

CREATE TABLE IF NOT EXISTS participacion (
    id_participacion  INTEGER PRIMARY KEY AUTOINCREMENT,
    id_salida         INTEGER NOT NULL REFERENCES salida (id_salida),
    id_usuario        INTEGER NOT NULL REFERENCES usuario (id_usuario),
    estado            TEXT NOT NULL CHECK (estado IN ('invitado', 'confirmado', 'cancelado')),
    fecha_estado      TEXT NOT NULL,
    UNIQUE (id_salida, id_usuario)
);
