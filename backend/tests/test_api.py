"""Pruebas de la API según los criterios de aceptación de HU-001, HU-003, HU-008, HU-010 y HU-011."""
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from app import create_app

FUTURO = (date.today() + timedelta(days=10)).isoformat()


class PruebasAPI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app({"DATABASE": str(Path(self.tmp.name) / "test.db"), "TESTING": True})
        self.c = self.app.test_client()
        self.admin = self._crear_admin()
        self.id_ruta = self._post("/api/rutas", self.admin, {
            "nombre": "Ruta de prueba", "tipo_actividad": "Senderismo", "ubicacion": "Sierras Chicas",
            "distancia": 12, "desnivel": 600, "duracion_estimada": 5, "nivel_dificultad": 3,
            "latitud_inicio": -31.0, "longitud_inicio": -64.28}).get_json()["id_ruta"]

    def tearDown(self):
        self.tmp.cleanup()

    def _post(self, url, token, datos=None):
        return self.c.post(url, json=datos or {}, headers={"Authorization": f"Bearer {token}"})

    def _crear_admin(self):
        import bcrypt
        from app.db import get_db
        with self.app.app_context():
            get_db().execute("INSERT INTO usuario (nombre, apellido, correo, contrasena_hash, rol) VALUES (?,?,?,?,?)",
                             ("Admin", "Sistema", "admin@x.com",
                              bcrypt.hashpw(b"Admin1234", bcrypt.gensalt()).decode(), "administrador"))
        return self.c.post("/api/auth/login", json={"correo": "admin@x.com", "contrasena": "Admin1234"}).get_json()["token"]

    def _usuario(self, correo, experiencia=3, condicion=3):
        token = self.c.post("/api/auth/registro", json={"nombre": "Ana", "apellido": "Test", "correo": correo,
                                                        "contrasena": "Prueba123"}).get_json()["token"]
        self.c.put("/api/perfil", headers={"Authorization": f"Bearer {token}"}, json={
            "nivel_experiencia": experiencia, "condicion_fisica": condicion, "ubicacion": "Córdoba Capital",
            "tipo_actividad": "Senderismo", "distancia_maxima": 15, "duracion_maxima": 6,
            "zona_interes": "Sierras Chicas"})
        return token

    def _salida(self, token, cupo=10):
        return self._post("/api/salidas", token, {"id_ruta": self.id_ruta, "fecha": FUTURO, "horario": "08:00",
                                                  "punto_encuentro": "Plaza", "cupo": cupo})

    def test_hu001_correo_repetido_y_contrasena_debil(self):
        self._usuario("a@x.com")
        repetido = self.c.post("/api/auth/registro", json={"nombre": "A", "apellido": "B", "correo": "a@x.com",
                                                           "contrasena": "Prueba123"})
        self.assertEqual(repetido.status_code, 409)
        debil = self.c.post("/api/auth/registro", json={"nombre": "A", "apellido": "B", "correo": "b@x.com",
                                                        "contrasena": "prueba"})
        self.assertIn("mayúscula", debil.get_json()["error"])

    def test_hu002_bloqueo_tras_cinco_intentos(self):
        self._usuario("c@x.com")
        for _ in range(5):
            self.c.post("/api/auth/login", json={"correo": "c@x.com", "contrasena": "Incorrecta1"})
        bloqueado = self.c.post("/api/auth/login", json={"correo": "c@x.com", "contrasena": "Prueba123"})
        self.assertEqual(bloqueado.status_code, 429)

    def test_hu003_escala_fuera_de_rango(self):
        token = self._usuario("d@x.com")
        r = self.c.put("/api/perfil", headers={"Authorization": f"Bearer {token}"}, json={
            "nivel_experiencia": 7, "condicion_fisica": 3, "ubicacion": "Córdoba Capital",
            "tipo_actividad": "Senderismo", "distancia_maxima": 15, "duracion_maxima": 6, "zona_interes": "Sierras Chicas"})
        self.assertEqual(r.status_code, 400)

    def test_hu004_solo_el_administrador_registra_rutas(self):
        token = self._usuario("e@x.com")
        r = self._post("/api/rutas", token, {"nombre": "X"})
        self.assertEqual(r.status_code, 403)

    def test_hu008_fecha_pasada_y_cupo_invalido(self):
        token = self._usuario("f@x.com")
        pasada = self._post("/api/salidas", token, {"id_ruta": self.id_ruta, "fecha": "2020-01-01", "horario": "08:00",
                                                    "punto_encuentro": "Plaza", "cupo": 5})
        self.assertEqual(pasada.status_code, 400)
        self.assertEqual(self._salida(token, cupo=0).status_code, 400)

    def test_hu010_control_de_nivel_y_de_cupo(self):
        organizador = self._usuario("g@x.com")
        id_salida = self._salida(organizador, cupo=2).get_json()["id_salida"]
        detalle = self.c.get(f"/api/salidas/{id_salida}", headers={"Authorization": f"Bearer {organizador}"}).get_json()
        self.assertEqual((detalle["ocupados"], detalle["disponibles"]), (1, 1))

        principiante = self._usuario("h@x.com", experiencia=2, condicion=2)
        self.assertEqual(self._post(f"/api/salidas/{id_salida}/confirmar", principiante).status_code, 409)

        compatible = self._usuario("i@x.com")
        r = self._post(f"/api/salidas/{id_salida}/confirmar", compatible).get_json()
        self.assertEqual(r["estado_salida"], "completa")

        otro = self._usuario("j@x.com")
        lleno = self._post(f"/api/salidas/{id_salida}/confirmar", otro)
        self.assertIn("No hay lugares", lleno.get_json()["error"])

        cancelado = self._post(f"/api/salidas/{id_salida}/cancelar", compatible).get_json()
        self.assertEqual(cancelado["estado_salida"], "abierta")

    def test_hu011_cupo_menor_que_confirmados(self):
        organizador = self._usuario("k@x.com")
        id_salida = self._salida(organizador, cupo=3).get_json()["id_salida"]
        self._post(f"/api/salidas/{id_salida}/confirmar", self._usuario("l@x.com"))
        r = self.c.put(f"/api/salidas/{id_salida}", headers={"Authorization": f"Bearer {organizador}"},
                       json={"fecha": FUTURO, "horario": "07:30", "punto_encuentro": "Plaza", "cupo": 1})
        self.assertEqual(r.status_code, 400)
        ok = self.c.put(f"/api/salidas/{id_salida}", headers={"Authorization": f"Bearer {organizador}"},
                        json={"fecha": FUTURO, "horario": "07:30", "punto_encuentro": "Plaza", "cupo": 3}).get_json()
        self.assertIn("el horario cambió de 08:00 a 07:30", ok["ultimo_cambio"])


if __name__ == "__main__":
    unittest.main()
