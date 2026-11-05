# Planificador Outdoor

Prototipo del **Sistema Web de Planificación Integrada de Actividades Outdoor Basado en la Compatibilidad Entre Usuarios y Rutas**, desarrollado como Trabajo Final de Grado de la carrera Ingeniería en Software (Universidad Siglo 21).

El sistema integra en un único proceso la planificación de una salida outdoor: recomienda rutas según la compatibilidad entre el perfil del usuario y las características de cada recorrido, y aplica ese mismo criterio para sugerir participantes compatibles con la ruta elegida.

## Funcionalidades implementadas

| Historia de usuario | Funcionalidad |
|---|---|
| HU-001 | Registro de usuario con validación de correo único y política de contraseñas |
| HU-002 | Inicio de sesión, acceso según el rol y bloqueo tras 5 intentos fallidos |
| HU-003 | Registro y actualización del perfil (experiencia, condición física, ubicación y preferencias) |
| HU-004 | Registro y modificación de rutas con su clasificación según la escala única de dificultad (administrador) |
| HU-005 | Ficha de la ruta con su puntaje de compatibilidad |
| HU-006 | Visualización del recorrido en el mapa (Google Maps o vista esquemática) |
| HU-007 | Recomendación de rutas según la compatibilidad con el perfil |
| HU-008 | Creación de la salida grupal |
| HU-009 | Sugerencia de participantes compatibles con la ruta e invitaciones |
| HU-010 | Confirmación de asistencia con control de nivel y de cupo |
| HU-011 | Actualización de los datos de la salida, con los cambios señalados a los participantes |

El motor de compatibilidad (tarea técnica TT-04) se encuentra en `backend/app/compatibilidad.py` e implementa las reglas de negocio definidas en las historias de usuario HU-007 y HU-009.

## Tecnologías

- **Backend:** Python 3.12 o superior, Flask, SQLite y bcrypt.
- **Frontend:** React, React Router y Bootstrap, con Vite como herramienta de desarrollo.
- **Mapas:** Google Maps JavaScript API (opcional).

## Requisitos previos

- [Python](https://www.python.org/downloads/) 3.12 o superior.
- [Node.js](https://nodejs.org/) 20 o superior (incluye npm).

## Instalación y ejecución

### 1. Backend (API)

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate
pip install -r requirements.txt
python seed.py      # crea la base de datos con datos de prueba
python run.py       # inicia la API en http://127.0.0.1:5000
```

### 2. Frontend

En otra terminal:

```bash
cd frontend
npm install
npm run dev         # inicia la aplicación en http://localhost:5173
```

Abrir **http://localhost:5173** en el navegador.

### 3. Google Maps (opcional)

Para ver los recorridos sobre Google Maps, copiar `frontend/.env.example` como `frontend/.env` y completar `VITE_GOOGLE_MAPS_API_KEY` con una clave de Google Maps JavaScript API. Sin clave, el sistema funciona igual y muestra una vista esquemática del recorrido.

## Usuarios de prueba

Los datos cargados por `seed.py` son ficticios.

| Rol | Correo | Contraseña | Perfil |
|---|---|---|---|
| Administrador | admin@prueba.local | Admin1234 | Registra y modifica rutas |
| Usuario | martin.gomez@prueba.local | Prueba123 | Experiencia 4, condición física 3 (nivel 3), Villa Allende |
| Usuario | sofia.ruiz@prueba.local | Prueba123 | Nivel 3, La Granja |
| Usuario | valentina.lopez@prueba.local | Prueba123 | Nivel 5, Córdoba Capital |
| Usuario | nicolas.ortiz@prueba.local | Prueba123 | Experiencia 4, condición física 2 (nivel 2) |
| Usuario | camila.diaz@prueba.local | Prueba123 | Nivel 2 |
| Usuario | ana.ramos@prueba.local | Prueba123 | Nivel 3, interés en Punilla |

También están disponibles lucia.fernandez, diego.perez, julian.molina y tomas.alvarez (`@prueba.local`, contraseña `Prueba123`).

## Recorrido sugerido

1. Ingresar como **martin.gomez@prueba.local** y revisar el perfil.
2. Ir a **Rutas recomendadas**: se muestran las rutas de Sierras Chicas compatibles con el nivel 3, ordenadas por puntaje, y la cantidad de rutas excluidas.
3. Abrir la ficha de una ruta y crear una **salida grupal**.
4. En el detalle de la salida, revisar los **participantes sugeridos** e invitar a uno.
5. Ingresar como **sofia.ruiz@prueba.local**, abrir **Mis salidas** y confirmar la asistencia.
6. Ingresar como **camila.diaz@prueba.local** e intentar confirmar la misma salida: el sistema lo impide porque la ruta supera su nivel.

Para volver a los datos iniciales, ejecutar nuevamente `python seed.py` con la API detenida.

## Pruebas automatizadas

Las pruebas verifican los criterios de aceptación de las historias de usuario, incluidos los puntajes de los ejemplos de HU-007 (94 puntos) y HU-009 (97 puntos):

```bash
cd backend
python -m unittest discover -s tests -t .
```

## Estructura del proyecto

```
backend/
  app/
    __init__.py         configuración de la aplicación Flask
    auth.py             registro, inicio de sesión y control de acceso
    perfiles.py         perfil y preferencias del usuario
    rutas.py            rutas, ficha y recomendaciones
    salidas.py          salidas grupales, sugerencias, invitaciones y cupo
    compatibilidad.py   motor de compatibilidad
    schema.sql          estructura de la base de datos
  seed.py               carga de datos de prueba
  tests/                pruebas automatizadas
frontend/
  src/
    paginas/            pantallas de la aplicación
    Mapa.jsx            integración con Google Maps
    api.js              cliente de la API
```
