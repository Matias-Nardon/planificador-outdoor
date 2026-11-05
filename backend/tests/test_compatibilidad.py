"""Pruebas del motor de compatibilidad según los criterios de aceptación de HU-007 y HU-009."""
import unittest

from app.compatibilidad import (calcular_puntaje, motivo_exclusion, nivel_usuario, recomendar_rutas,
                                sugerir_participantes)

ARROYO_BLANCO = {"id_ruta": 1, "nombre": "Sendero Quebrada del Arroyo Blanco", "tipo_actividad": "Senderismo",
                 "ubicacion": "Sierras Chicas", "nivel_dificultad": 3, "distancia": 12.4, "desnivel": 650,
                 "duracion_estimada": 5, "latitud_inicio": None, "longitud_inicio": None}


def perfil(**cambios):
    base = {"id_usuario": 1, "nivel_experiencia": 3, "condicion_fisica": 3, "tipo_actividad": "Senderismo",
            "zona_interes": "Sierras Chicas", "distancia_maxima": 15, "duracion_maxima": 6,
            "latitud": None, "longitud": None}
    return {**base, **cambios}


class PruebasHU007(unittest.TestCase):
    def test_criterio_1_nivel_es_el_menor_valor(self):
        self.assertEqual(nivel_usuario(4, 3), 3)
        ruta_dificil = {**ARROYO_BLANCO, "nivel_dificultad": 4}
        self.assertEqual(motivo_exclusion(perfil(nivel_experiencia=4), ruta_dificil), "dificultad")

    def test_criterio_2_excluye_otra_actividad_y_otra_zona(self):
        self.assertEqual(motivo_exclusion(perfil(), {**ARROYO_BLANCO, "tipo_actividad": "Trekking"}), "actividad")
        self.assertEqual(motivo_exclusion(perfil(), {**ARROYO_BLANCO, "ubicacion": "Punilla"}), "zona")

    def test_criterio_3_puntaje_94(self):
        puntaje, _ = calcular_puntaje(perfil(), ARROYO_BLANCO, km=35)
        self.assertEqual(round(puntaje), 94)

    def test_criterio_4_exceso_de_distancia_resta_10_puntos(self):
        ruta = {**ARROYO_BLANCO, "distancia": 15 * 1.25}
        base, _ = calcular_puntaje(perfil(), {**ARROYO_BLANCO, "distancia": 15}, km=35)
        con_exceso, _ = calcular_puntaje(perfil(), ruta, km=35)
        self.assertAlmostEqual(base - con_exceso, 10, places=1)

    def test_criterio_5_orden_y_puntaje_minimo(self):
        rutas = [
            {**ARROYO_BLANCO, "id_ruta": 1, "nivel_dificultad": 2},
            {**ARROYO_BLANCO, "id_ruta": 2},
            {**ARROYO_BLANCO, "id_ruta": 3, "distancia": 40, "desnivel": 2000, "duracion_estimada": 20},
        ]
        recomendadas, excluidas = recomendar_rutas(perfil(), rutas)
        self.assertEqual([r["id_ruta"] for r in recomendadas], [2, 1])
        self.assertEqual(excluidas, 1)

    def test_criterio_6_sin_resultados(self):
        recomendadas, excluidas = recomendar_rutas(perfil(zona_interes="Punilla"), [ARROYO_BLANCO])
        self.assertEqual(recomendadas, [])
        self.assertEqual(excluidas, 1)


class PruebasHU009(unittest.TestCase):
    def test_criterio_1_y_2_excluye_candidatos_de_nivel_insuficiente(self):
        candidatos = [perfil(id_usuario=2, nivel_experiencia=2, condicion_fisica=2),
                      perfil(id_usuario=3, nivel_experiencia=4, condicion_fisica=2)]
        self.assertEqual(sugerir_participantes(ARROYO_BLANCO, candidatos), [])

    def test_criterio_4_puntaje_97(self):
        puntaje, _ = calcular_puntaje(perfil(), ARROYO_BLANCO, km=20)
        self.assertEqual(round(puntaje), 97)

    def test_criterio_5_nivel_superior_obtiene_17_5_puntos_menos(self):
        nivel_3, _ = calcular_puntaje(perfil(), ARROYO_BLANCO, km=20)
        nivel_5, _ = calcular_puntaje(perfil(nivel_experiencia=5, condicion_fisica=5), ARROYO_BLANCO, km=20)
        self.assertAlmostEqual(nivel_3 - nivel_5, 17.5, places=1)

    def test_criterio_6_excluye_organizador_e_invitados_y_limita_a_10(self):
        candidatos = [perfil(id_usuario=i) for i in range(1, 15)]
        sugeridos = sugerir_participantes(ARROYO_BLANCO, candidatos, excluir_ids={1, 2})
        self.assertEqual(len(sugeridos), 10)
        self.assertNotIn(1, [s["id_usuario"] for s in sugeridos])


if __name__ == "__main__":
    unittest.main()
