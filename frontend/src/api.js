// Cliente de la API REST. Envía el token de sesión en cada solicitud.
const CLAVE_SESION = 'planificador.sesion'

export function leerSesion() {
  try {
    return JSON.parse(localStorage.getItem(CLAVE_SESION)) || null
  } catch {
    return null
  }
}

export function guardarSesion(sesion) {
  if (sesion) localStorage.setItem(CLAVE_SESION, JSON.stringify(sesion))
  else localStorage.removeItem(CLAVE_SESION)
}

export async function api(ruta, { method = 'GET', body } = {}) {
  const sesion = leerSesion()
  const respuesta = await fetch(`/api${ruta}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(sesion?.token ? { Authorization: `Bearer ${sesion.token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  })
  const datos = await respuesta.json().catch(() => ({}))
  if (respuesta.status === 401 && sesion) {
    guardarSesion(null)
    window.location.assign('/ingresar')
  }
  if (!respuesta.ok) {
    const error = new Error(datos.error || 'Ocurrió un error inesperado.')
    error.status = respuesta.status
    throw error
  }
  return datos
}
