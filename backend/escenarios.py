"""Ejecución de los escenarios de prueba del prototipo (tarea técnica TT-07, objetivo específico 5).

Cada escenario parte de un usuario de prueba con un nivel distinto, planifica una
salida grupal completa en el sistema y registra:
  - la cantidad de pasos necesarios para planificar la salida;
  - la cantidad de herramientas o fuentes de información consultadas;
  - el grado de correspondencia entre el perfil y las rutas recomendadas.

Se ejecuta sobre una copia de los datos de prueba, por lo que no modifica la base de datos.
Uso:  python escenarios.py
"""
import shutil
import tempfile
from datetime import date, timedelta
from pathlib import Path

import seed
from app import create_app
from app.compatibilidad import DESNIVEL_MAXIMO, nivel_usuario

ESCENARIOS = [
    ("E1", "Principiante", "camila.diaz@prueba.local"),
    ("E2", "Intermedio", "martin.gomez@prueba.local"),
    ("E3", "Avanzado", "valentina.lopez@prueba.local"),
    ("E4", "Experiencia alta y condición física baja", "nicolas.ortiz@prueba.local"),
]
# Usuario de nivel insuficiente que intenta sumarse a cada salida, para verificar el control de nivel.
PRINCIPIANTE = "camila.diaz@prueba.local"

# Proceso actual relevado (Figura 2): pasos hasta la confirmación de los participantes
# y herramientas que intervienen.
PASOS_ACTUALES = [
    "Buscar rutas en plataformas de rutas",
    "Consultar la ficha de la ruta y los comentarios",
    "Evaluar si la ruta es adecuada según la propia experiencia",
    "Consultar el pronóstico y el equipamiento recomendado",
    "Publicar la convocatoria en redes sociales o grupos de mensajería",
    "Consultar por mensaje la dificultad, el ritmo y el equipamiento (participante)",
    "Responder las consultas según su criterio (organizador)",
    "Confirmar la asistencia en el chat (participante)",
    "Armar la lista de participantes y comunicar los cambios (organizador)",
]
HERRAMIENTAS_ACTUALES = ["Plataformas de rutas", "Servicios meteorológicos", "Redes sociales",
                         "Aplicaciones de mensajería"]

FECHA = (date.today() + timedelta(days=21)).isoformat()


def corresponde(perfil, ruta):
    """Verifica, característica por característica, si una ruta recomendada se corresponde con el perfil."""
    nivel = nivel_usuario(perfil["nivel_experiencia"], perfil["condicion_fisica"])
    controles = {
        "dificultad": ruta["nivel_dificultad"] <= nivel,
        "actividad": ruta["tipo_actividad"] == perfil["tipo_actividad"],
        "zona": ruta["ubicacion"] == perfil["zona_interes"],
        "distancia": ruta["distancia"] <= perfil["distancia_maxima"],
        "desnivel": ruta["desnivel"] <= DESNIVEL_MAXIMO[perfil["condicion_fisica"]],
        "duracion": ruta["duracion_estimada"] <= perfil["duracion_maxima"],
    }
    return all(controles.values()), [k for k, v in controles.items() if not v]


def main():
    tmp = Path(tempfile.mkdtemp())
    base = Path(__file__).resolve().parent / "planificador.db"
    respaldo = base.read_bytes() if base.exists() else None
    seed.main()                                   # datos de prueba iniciales
    shutil.copy(base, tmp / "escenarios.db")
    if respaldo is not None:
        base.write_bytes(respaldo)                # se restaura la base del usuario
    app = create_app({"DATABASE": str(tmp / "escenarios.db")})
    c = app.test_client()

    def sesion(correo):
        token = c.post("/api/auth/login", json={"correo": correo, "contrasena": seed.CONTRASENA_PRUEBA}).get_json()["token"]
        return {"Authorization": f"Bearer {token}"}

    print("\nProceso actual: %d pasos y %d herramientas" % (len(PASOS_ACTUALES), len(HERRAMIENTAS_ACTUALES)))
    resumen = []
    for codigo, descripcion, correo in ESCENARIOS:
        h = sesion(correo)
        pasos = []
        perfil = c.get("/api/perfil", headers=h).get_json()["perfil"]
        pasos.append("Revisar o completar el perfil")
        reco = c.get("/api/recomendaciones", headers=h).get_json()
        pasos.append("Consultar las rutas recomendadas")
        rutas = reco["rutas"]
        nivel = reco["nivel_usuario"]
        evaluacion = [corresponde(perfil, r) for r in rutas]
        correspondientes = sum(1 for ok, _ in evaluacion if ok)

        print(f"\n{codigo} - {descripcion} ({correo})")
        print(f"   Perfil: experiencia {perfil['nivel_experiencia']}, condición {perfil['condicion_fisica']} -> nivel {nivel}; "
              f"{perfil['tipo_actividad']}, hasta {perfil['distancia_maxima']} km y {perfil['duracion_maxima']} h, {perfil['zona_interes']}")
        for r, (ok, fallas) in zip(rutas, evaluacion):
            print(f"   {r['puntaje']:5.1f}  dif {r['nivel_dificultad']}  {r['nombre']}" + ("" if ok else f"  [no cumple: {', '.join(fallas)}]"))
        print(f"   Recomendadas: {len(rutas)} | Excluidas: {reco['excluidas']} | Correspondencia: {correspondientes}/{len(rutas)}")

        elegida = rutas[0]
        c.get(f"/api/rutas/{elegida['id_ruta']}", headers=h)
        pasos.append("Consultar la ficha y el mapa de la ruta")
        salida = c.post("/api/salidas", headers=h, json={"id_ruta": elegida["id_ruta"], "fecha": FECHA, "horario": "08:00",
                                                          "punto_encuentro": "Inicio del sendero", "cupo": 4}).get_json()
        id_salida = salida["id_salida"]
        pasos.append("Crear la salida grupal")
        sug = c.get(f"/api/salidas/{id_salida}/sugerencias", headers=h).get_json()["sugeridos"]
        sugeridos_compatibles = all(p["nivel"] >= elegida["nivel_dificultad"] for p in sug)
        invitado = sug[0] if sug else None
        if invitado:
            c.post(f"/api/salidas/{id_salida}/invitaciones", headers=h, json={"id_usuario": invitado["id_usuario"]})
        pasos.append("Invitar a los participantes sugeridos")
        confirmacion = None
        if invitado:
            correo_invitado = next(u[2] for u in seed.USUARIOS
                                   if f"{u[0]} {u[1][0]}." == invitado["nombre"])
            confirmacion = c.post(f"/api/salidas/{id_salida}/confirmar", headers=sesion(correo_invitado)).get_json()
        pasos.append("Confirmar la asistencia (participante)")
        rechazo = c.post(f"/api/salidas/{id_salida}/confirmar", headers=sesion(PRINCIPIANTE)).get_json() \
            if correo != PRINCIPIANTE and elegida["nivel_dificultad"] > 2 else None

        print(f"   Salida sobre '{elegida['nombre']}': {len(sug)} sugeridos, todos con nivel suficiente: {sugeridos_compatibles}")
        if invitado:
            print(f"   Invitado: {invitado['nombre']} ({invitado['puntaje']} %) -> {confirmacion.get('estado')}, "
                  f"cupo {confirmacion.get('ocupados')}/{confirmacion.get('cupo')}")
        if rechazo:
            print(f"   Intento de un usuario de nivel 2: {rechazo.get('error')}")
        print(f"   Pasos: {len(pasos)} | Herramientas: 1 (sistema) + 1 (servicio meteorológico, fuera del alcance)")
        resumen.append((codigo, descripcion, nivel, len(rutas), reco["excluidas"], correspondientes,
                        len(sug), sugeridos_compatibles, len(pasos)))

    print("\nRESUMEN")
    for fila in resumen:
        print(" | ".join(str(x) for x in fila))
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
