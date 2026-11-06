# Planificador Outdoor

Prototipo del **Sistema Web de Planificación Integrada de Actividades Outdoor Basado en la Compatibilidad Entre Usuarios y Rutas**, desarrollado como Trabajo Final de Grado de la carrera Ingeniería en Software (Universidad Siglo 21).

El sistema integra en un único proceso la planificación de una salida outdoor: recomienda rutas según la compatibilidad entre el perfil del usuario y las características de cada recorrido, y aplica ese mismo criterio para sugerir participantes compatibles con la ruta elegida.

## Video de demostración

Recorrido completo del prototipo: [ver el video en Google Drive](https://drive.google.com/file/d/1FEM3NgnDSuk1xB9hztTMyQE0vFvaEDhQ/view?usp=sharing)

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

Antes de comenzar, instalar en la computadora:

| Programa | Versión | Descarga | Observaciones |
|---|---|---|---|
| Python | 3.12 o superior | https://www.python.org/downloads/ | En Windows, durante la instalación marcar la opción **"Add python.exe to PATH"**. |
| Node.js | 20 o superior | https://nodejs.org/ (versión LTS) | Incluye npm. |
| Git (opcional) | Cualquiera | https://git-scm.com/downloads | Solo es necesario para descargar el proyecto con `git clone`. |

Para verificar la instalación, abrir una terminal y ejecutar `python --version` y `node --version`. Ambos comandos deben mostrar un número de versión.

> **¿Cómo abrir una terminal?** En Windows: menú Inicio → escribir **cmd** → Enter (se abre el Símbolo del sistema). En Visual Studio Code: menú **Terminal → Nueva terminal**. En macOS: aplicación **Terminal**. En Linux: la terminal del sistema.

## Instalación y ejecución

El sistema tiene dos partes que se ejecutan al mismo tiempo, cada una en su propia terminal:

- el **backend** (API en Python y Flask), en la carpeta `backend`;
- el **frontend** (interfaz en React), en la carpeta `frontend`.

Los comandos se indican para **Windows**. Las diferencias para **Linux y macOS** se aclaran en cada paso.

### Paso 1. Descargar el proyecto

**Opción A, con Git.** En una terminal, ubicarse en la carpeta donde se desea guardar el proyecto (por ejemplo, el Escritorio) y ejecutar:

```bash
cd Desktop
git clone https://github.com/Matias-Nardon/planificador-outdoor.git
```

**Opción B, sin Git.** En la página del repositorio, hacer clic en el botón verde **Code → Download ZIP**, descomprimir el archivo y renombrar la carpeta resultante (`planificador-outdoor-main`) como `planificador-outdoor`.

En ambos casos se obtiene una carpeta `planificador-outdoor` que contiene las carpetas `backend` y `frontend`.

### Paso 2. Instalar y ejecutar el backend (terminal 1)

1. Abrir una terminal y ubicarse **dentro de la carpeta `backend` del proyecto**. Por ejemplo, si el proyecto se descargó en el Escritorio:

   ```bash
   cd Desktop\planificador-outdoor\backend
   ```

   En Linux y macOS: `cd ~/Desktop/planificador-outdoor/backend`.

2. Crear el entorno virtual de Python (se hace una sola vez):

   ```bash
   python -m venv .venv
   ```

   Si Windows indica que no encuentra `python`, usar `py -m venv .venv`. En Linux y macOS puede ser necesario usar `python3`.

3. Instalar las dependencias (se hace una sola vez):

   ```bash
   .venv\Scripts\python -m pip install -r requirements.txt
   ```

   En Linux y macOS: `.venv/bin/python -m pip install -r requirements.txt`.

4. Crear la base de datos con los datos de prueba:

   ```bash
   .venv\Scripts\python seed.py
   ```

   En Linux y macOS: `.venv/bin/python seed.py`. Debe mostrar el mensaje *"Base de datos creada en…"* y la lista de usuarios de prueba.

5. Iniciar la API:

   ```bash
   .venv\Scripts\python run.py
   ```

   En Linux y macOS: `.venv/bin/python run.py`. Debe mostrar el mensaje *"Running on http://127.0.0.1:5000"*.

   **Esta terminal debe quedar abierta** mientras se utiliza el sistema. Para detener la API, presionar **Ctrl + C**.

### Paso 3. Instalar y ejecutar el frontend (terminal 2)

1. Abrir **una segunda terminal**, sin cerrar la del backend, y ubicarse **dentro de la carpeta `frontend` del proyecto**:

   ```bash
   cd Desktop\planificador-outdoor\frontend
   ```

   En Linux y macOS: `cd ~/Desktop/planificador-outdoor/frontend`.

2. Instalar las dependencias (se hace una sola vez; puede demorar uno o dos minutos):

   ```bash
   npm install
   ```

3. Iniciar la aplicación:

   ```bash
   npm run dev
   ```

   Debe mostrar el mensaje *"Local: http://localhost:5173/"*. Si el puerto 5173 está ocupado, se utiliza el siguiente disponible (por ejemplo, 5174); en ese caso, usar la dirección que indique la terminal.

   **Esta terminal también debe quedar abierta.** Para detener la aplicación, presionar **Ctrl + C**.

### Paso 4. Abrir el sistema

Abrir en el navegador la dirección **http://localhost:5173** e ingresar con alguno de los usuarios de prueba que se indican más abajo.

### Paso 5 (opcional). Configurar Google Maps

Para ver los recorridos sobre Google Maps:

1. En la carpeta `frontend`, copiar el archivo `.env.example` con el nombre `.env`.
2. Abrir `.env` con un editor de texto y completar `VITE_GOOGLE_MAPS_API_KEY=` con una clave de Google Maps JavaScript API.
3. Detener el frontend (Ctrl + C) y volver a iniciarlo con `npm run dev`.

Sin clave, el sistema funciona igual y muestra una vista esquemática del recorrido.

### Uso posterior

Una vez realizada la instalación, para volver a usar el sistema solo es necesario repetir los comandos de inicio: `.venv\Scripts\python run.py` en la carpeta `backend` y `npm run dev` en la carpeta `frontend`, cada uno en su terminal.

## Usuarios de prueba

Los datos cargados por `seed.py` son ficticios. Todos los usuarios tienen la contraseña **Prueba123**, excepto el administrador.

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

1. Ingresar como **martin.gomez@prueba.local**. Hacer clic en **Mi perfil** para revisar sus datos: su nivel es 3, el menor valor entre su experiencia (4) y su condición física (3).
2. Hacer clic en **Ver rutas recomendadas**. Se muestran las rutas de senderismo de Sierras Chicas compatibles con el nivel 3, ordenadas por puntaje de compatibilidad, y al final la cantidad de rutas excluidas.
3. En una ruta, hacer clic en **Ver ficha** y luego en **Crear salida grupal**. Completar una fecha futura, el horario, el punto de encuentro y el cupo, y hacer clic en **Crear salida**.
4. En el detalle de la salida, revisar la sección **Participantes sugeridos** y hacer clic en **Invitar** en el usuario Sofía R. Opcionalmente, hacer clic en **Modificar salida** y cambiar el horario para ver el aviso del cambio.
5. Hacer clic en **Salir**, ingresar como **sofia.ruiz@prueba.local**, abrir **Mis salidas**, hacer clic en **Ver salida** en la invitación recibida y luego en **Confirmar asistencia**. El cupo se actualiza.
6. Hacer clic en **Salir** e ingresar como **camila.diaz@prueba.local** (nivel 2). La salida no aparece entre sus salidas disponibles. Si se abre directamente su dirección (por ejemplo, `http://localhost:5173/salidas/3`) y se hace clic en **Confirmar asistencia**, el sistema lo impide porque la ruta supera su nivel.
7. Opcionalmente, ingresar como **admin@prueba.local** para ver el **Registro de rutas**.

Para volver a los datos iniciales: detener la API con **Ctrl + C**, ejecutar `.venv\Scripts\python seed.py` en la carpeta `backend` y volver a iniciarla con `.venv\Scripts\python run.py`. En el navegador, hacer clic en **Salir** para cerrar la sesión anterior.

## Pruebas automatizadas

Las pruebas verifican los criterios de aceptación de las historias de usuario, incluidos los puntajes de los ejemplos de HU-007 (94 puntos) y HU-009 (97 puntos). En una terminal, dentro de la carpeta `backend`:

```bash
.venv\Scripts\python -m unittest discover -s tests -t .
```

En Linux y macOS: `.venv/bin/python -m unittest discover -s tests -t .`. El resultado esperado es *"Ran 17 tests … OK"*.

## Escenarios de prueba

El script `escenarios.py` ejecuta los escenarios de prueba del objetivo específico 5 sobre una copia de los datos de prueba, por lo que no modifica la base de datos. Para cada perfil registra los pasos y las herramientas necesarias para planificar una salida grupal y la correspondencia entre el perfil y las rutas recomendadas. En una terminal, dentro de la carpeta `backend`:

```bash
.venv\Scripts\python escenarios.py
```

En Linux y macOS: `.venv/bin/python escenarios.py`. Al final se muestra un resumen con los resultados de los cuatro escenarios.

## Solución de problemas

| Problema | Solución |
|---|---|
| PowerShell indica que *"la ejecución de scripts está deshabilitada"* al ejecutar `npm` | Usar `npm.cmd install` y `npm.cmd run dev`, o abrir la terminal **Símbolo del sistema (cmd)** en lugar de PowerShell. Los comandos de Python de este instructivo no requieren activar el entorno virtual, por lo que no se ven afectados. |
| `python` no se reconoce como comando | Reinstalar Python marcando **"Add python.exe to PATH"**, o usar `py` en lugar de `python` al crear el entorno virtual. |
| La pantalla muestra errores al ingresar o no carga datos | Verificar que la terminal del backend siga abierta y muestre *"Running on http://127.0.0.1:5000"*. |
| `Port 5173 is in use` | No es un error: la aplicación se inicia en otro puerto (por ejemplo, 5174). Usar la dirección que indica la terminal. |
| Se quieren restablecer los datos de prueba | Ver el último párrafo de la sección **Recorrido sugerido**. |

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
  escenarios.py         escenarios de prueba del prototipo
  tests/                pruebas automatizadas
frontend/
  src/
    paginas/            pantallas de la aplicación
    Mapa.jsx            integración con Google Maps
    api.js              cliente de la API
```
