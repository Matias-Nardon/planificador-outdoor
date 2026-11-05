import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { Alerta, Cargando, Compatibilidad, Escala, Pasos, num } from '../componentes'

// HU-007: recomendación de rutas según la compatibilidad con el perfil.
export default function Rutas() {
  const [datos, setDatos] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api('/recomendaciones').then(setDatos).catch((err) => setError(err.message))
  }, [])

  if (error) return (
    <>
      <Pasos actual={1} />
      <Alerta tipo="warning">{error}</Alerta>
      <Link to="/perfil" className="btn btn-verde">Completar mi perfil</Link>
    </>
  )
  if (!datos) return <Cargando />
  const p = datos.perfil

  return (
    <>
      <Pasos actual={1} />
      <h3>Rutas recomendadas</h3>
      <p className="text-muted">
        Según tu perfil: nivel {datos.nivel_usuario} · {p.tipo_actividad.toLowerCase()} · hasta {num(p.distancia_maxima)} km y {num(p.duracion_maxima)} h · {p.zona_interes}
      </p>
      {datos.rutas.length === 0 && (
        <Alerta tipo="warning">
          Ninguna ruta es compatible con tu perfil. Probá ajustar el tipo de actividad, la zona de interés o tus preferencias. <Link to="/perfil">Editar perfil</Link>
        </Alerta>
      )}
      {datos.rutas.map((r) => (
        <div key={r.id_ruta} className="tarjeta p-3 mb-2 d-flex flex-wrap align-items-center gap-3">
          <div className="flex-grow-1">
            <h6 className="mb-1">{r.nombre}</h6>
            <small className="text-muted">
              Distancia {num(r.distancia)} km · Desnivel {num(r.desnivel)} m · Duración {num(r.duracion_estimada)} h · A {Math.round(r.distancia_usuario_km)} km de tu ubicación · Dificultad{' '}
            </small>
            <Escala valor={r.nivel_dificultad} />
          </div>
          <div><small className="text-muted me-2">Compatibilidad</small><Compatibilidad puntaje={r.puntaje} /></div>
          <Link to={`/rutas/${r.id_ruta}`} className="btn btn-outline-verde">Ver ficha</Link>
        </div>
      ))}
      {datos.excluidas > 0 && (
        <div className="alert alert-warning py-2 mt-3">
          Se excluyeron {datos.excluidas} rutas porque su dificultad es superior a tu nivel, corresponden a otra actividad o zona, o su compatibilidad es menor al 50 %.
        </div>
      )}
    </>
  )
}
