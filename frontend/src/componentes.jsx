// Componentes visuales reutilizados en varias pantallas.
const PASOS = ['1 Perfil', '2 Ruta compatible', '3 Salida grupal', '4 Participantes']

/** Indicador de la etapa del proceso de planificación en la que se encuentra el usuario. */
export function Pasos({ actual }) {
  return (
    <div className="pasos my-3">
      {PASOS.map((paso, i) => (
        <span key={paso} className={`paso ${i === actual ? 'actual' : i < actual ? 'hecho' : ''}`}>
          {paso}
        </span>
      ))}
    </div>
  )
}

/** Escala de 1 a 5 representada con puntos. */
export function Escala({ valor }) {
  return (
    <span title={`${valor} de 5`}>
      {[1, 2, 3, 4, 5].map((n) => (
        <span key={n} className={`punto ${n <= valor ? 'lleno' : ''}`} />
      ))}
      <small className="text-muted ms-1">{valor}/5</small>
    </span>
  )
}

export function Compatibilidad({ puntaje }) {
  if (puntaje === null || puntaje === undefined) return null
  return <span className="insignia">{Math.round(puntaje)} %</span>
}

export function Alerta({ tipo = 'danger', children }) {
  if (!children) return null
  return <div className={`alert alert-${tipo} py-2`}>{children}</div>
}

export function Cargando() {
  return <div className="text-muted py-4">Cargando…</div>
}

export const sinInformacion = (valor) => (valor === null || valor === undefined || valor === '' ? 'Sin información' : valor)

export function formatoFecha(iso) {
  const [a, m, d] = iso.split('-')
  return `${d}/${m}/${a}`
}

export const etiquetaEstado = { abierta: 'Abierta', completa: 'Completa', finalizada: 'Finalizada' }

/** Números con formato argentino (coma decimal). */
export const num = (valor) => Number(valor).toLocaleString('es-AR', { maximumFractionDigits: 1 })
