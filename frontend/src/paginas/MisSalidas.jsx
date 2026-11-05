import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { Cargando, Escala, etiquetaEstado, formatoFecha } from '../componentes'

const SECCIONES = [
  ['organizadas', 'Salidas que organizo'],
  ['invitaciones', 'Invitaciones recibidas'],
  ['confirmadas', 'Salidas confirmadas'],
  ['disponibles', 'Salidas abiertas compatibles con mi nivel'],
]

export default function MisSalidas() {
  const [datos, setDatos] = useState(null)
  useEffect(() => {
    api('/mis-salidas').then(setDatos)
  }, [])
  if (!datos) return <Cargando />

  return (
    <>
      <h3 className="mt-3">Mis salidas</h3>
      {SECCIONES.map(([clave, titulo]) => (
        <section key={clave} className="mt-4">
          <h6>{titulo}</h6>
          {datos[clave].length === 0 && <p className="text-muted small">No hay salidas en esta sección.</p>}
          {datos[clave].map((s) => (
            <div key={s.id_salida} className="tarjeta p-3 mb-2 d-flex flex-wrap align-items-center gap-3">
              <div className="flex-grow-1">
                <strong>{s.ruta.nombre}</strong>
                <div className="small text-muted">
                  {formatoFecha(s.fecha)} · {s.horario} · {s.punto_encuentro} · Dificultad <Escala valor={s.ruta.nivel_dificultad} />
                </div>
              </div>
              <span className="small">Cupo: {s.ocupados} de {s.cupo}</span>
              <span className="badge text-bg-light border">{etiquetaEstado[s.estado]}</span>
              <Link to={`/salidas/${s.id_salida}`} className="btn btn-outline-verde btn-sm">Ver salida</Link>
            </div>
          ))}
        </section>
      ))}
    </>
  )
}
