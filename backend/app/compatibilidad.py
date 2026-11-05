"""Motor de compatibilidad (tarea técnica TT-04).

Implementa las reglas de negocio de las historias de usuario HU-007
(recomendación de rutas) y HU-009 (sugerencia de participantes). Ambas
utilizan el mismo cálculo: en HU-007 el usuario queda fijo y se evalúan
las rutas; en HU-009 la ruta queda fija y se evalúan los usuarios.
"""
from math import asin, cos, radians, sin, sqrt

# R4: pesos de cada componente del puntaje (suman 100).
PESOS = {"dificultad": 35, "distancia": 20, "desnivel": 20, "duracion": 15, "cercania": 10}

# R2: desnivel positivo máximo recomendado según la condición física (metros).
DESNIVEL_MAXIMO = {1: 300, 2: 500, 3: 800, 4: 1200, 5: 2000}

DISTANCIA_CERCANIA_KM = 60   # R7: a partir de esta distancia la cercanía vale 0.
EXCESO_TOLERADO = 0.5        # R6: el componente vale 0 cuando el exceso llega al 50 %.
PUNTAJE_MINIMO = 50          # R9: puntaje mínimo para mostrar un resultado.
MAXIMO_CANDIDATOS = 10       # HU-009 R4.


def nivel_usuario(nivel_experiencia, condicion_fisica):
    """R1: el nivel es el menor valor entre experiencia y condición física."""
    return min(nivel_experiencia, condicion_fisica)


def distancia_km(lat1, lon1, lat2, lon2):
    """Distancia entre dos coordenadas geográficas (fórmula de Haversine)."""
    if None in (lat1, lon1, lat2, lon2):
        return None
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))


def componente_limite(valor, maximo):
    """R6: vale 1 si no se supera el máximo y disminuye en forma proporcional al exceso."""
    if valor <= maximo:
        return 1.0
    return max(0.0, 1 - (valor - maximo) / (EXCESO_TOLERADO * maximo))


def componente_cercania(km):
    """R7: vale 1 en el mismo lugar y 0 a partir de 60 km."""
    if km is None:
        return 0.0
    return max(0.0, 1 - km / DISTANCIA_CERCANIA_KM)


def motivo_exclusion(perfil, ruta):
    """R3: restricciones obligatorias. Devuelve el motivo o None si la ruta es compatible."""
    nivel = nivel_usuario(perfil["nivel_experiencia"], perfil["condicion_fisica"])
    if ruta["nivel_dificultad"] > nivel:
        return "dificultad"
    if ruta["tipo_actividad"] != perfil["tipo_actividad"]:
        return "actividad"
    if ruta["ubicacion"] != perfil["zona_interes"]:
        return "zona"
    return None


def calcular_puntaje(perfil, ruta, km=None):
    """R4 a R7: puntaje de compatibilidad de 0 a 100 entre un perfil y una ruta.

    `perfil` debe incluir nivel_experiencia, condicion_fisica, distancia_maxima,
    duracion_maxima, latitud y longitud. Si se indica `km` se usa esa distancia
    en lugar de calcularla a partir de las coordenadas.
    """
    nivel = nivel_usuario(perfil["nivel_experiencia"], perfil["condicion_fisica"])
    if km is None:
        km = distancia_km(perfil.get("latitud"), perfil.get("longitud"),
                          ruta.get("latitud_inicio"), ruta.get("longitud_inicio"))
    componentes = {
        "dificultad": 1 - (nivel - ruta["nivel_dificultad"]) / 4,
        "distancia": componente_limite(ruta["distancia"], perfil["distancia_maxima"]),
        "desnivel": componente_limite(ruta["desnivel"], DESNIVEL_MAXIMO[perfil["condicion_fisica"]]),
        "duracion": componente_limite(ruta["duracion_estimada"], perfil["duracion_maxima"]),
        "cercania": componente_cercania(km),
    }
    puntaje = sum(PESOS[k] * v for k, v in componentes.items())
    return round(puntaje, 1), km


def recomendar_rutas(perfil, rutas):
    """HU-007: filtra, puntúa y ordena las rutas para un perfil.

    Devuelve (recomendadas, excluidas), donde excluidas cuenta las rutas
    descartadas por las restricciones obligatorias o por no alcanzar el puntaje mínimo.
    """
    recomendadas, excluidas = [], 0
    for ruta in rutas:
        if motivo_exclusion(perfil, ruta):
            excluidas += 1
            continue
        puntaje, km = calcular_puntaje(perfil, ruta)
        if puntaje < PUNTAJE_MINIMO:
            excluidas += 1
            continue
        recomendadas.append({**ruta, "puntaje": puntaje, "distancia_usuario_km": km})
    # R9: de mayor a menor puntaje; ante igual puntaje, primero la más cercana.
    recomendadas.sort(key=lambda r: (-r["puntaje"], r["distancia_usuario_km"] or 0))
    return recomendadas, excluidas


def sugerir_participantes(ruta, candidatos, excluir_ids=()):
    """HU-009: mismo mecanismo aplicado con la ruta fija y cada candidato evaluado."""
    sugeridos = []
    for perfil in candidatos:
        if perfil["id_usuario"] in excluir_ids:
            continue
        if motivo_exclusion(perfil, ruta):
            continue
        puntaje, km = calcular_puntaje(perfil, ruta)
        if puntaje < PUNTAJE_MINIMO:
            continue
        sugeridos.append({**perfil, "puntaje": puntaje, "distancia_ruta_km": km})
    sugeridos.sort(key=lambda p: (-p["puntaje"], p["distancia_ruta_km"] or 0))
    return sugeridos[:MAXIMO_CANDIDATOS]
