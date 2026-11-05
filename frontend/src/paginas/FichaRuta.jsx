import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api'
import { Alerta, Cargando, Compatibilidad, Escala, Pasos, num, sinInformacion } from '../componentes'
import Mapa from '../Mapa'

// HU-005 y HU-006: ficha de la ruta y recorrido en el mapa.
export default function FichaRuta() {
  const { id } = useParams()
  const [ruta, setRuta] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api(`/rutas/${id}`).then(setRuta).catch((err) => setError(err.message))
  }, [id])

  if (error) return <Alerta>{error}</Alerta>
  if (!ruta) return <Cargando />
  const filas = [
    ['Actividad', ruta.tipo_actividad], ['Zona', ruta.ubicacion], ['Distancia', `${num(ruta.distancia)} km`],
    ['Desnivel positivo', `${num(ruta.desnivel)} m`], ['Duración estimada', `${num(ruta.duracion_estimada)} h`],
  ]
  const inicio = ruta.latitud_inicio ? { lat: ruta.latitud_inicio, lng: ruta.longitud_inicio } : null

  return (
    <>
      <Pasos actual={1} />
      <h3>{ruta.nombre}</h3>
      <div className="row g-3">
        <div className="col-md-5">
          <div className="tarjeta p-3 h-100">
            <p><span className="text-muted me-2">Compatibilidad con tu perfil</span><Compatibilidad puntaje={ruta.puntaje} /></p>
            <table className="table table-sm">
              <tbody>
                {filas.map(([k, v]) => <tr key={k}><td className="text-muted">{k}</td><td className="fw-semibold">{v}</td></tr>)}
                <tr><td className="text-muted">Dificultad</td><td><Escala valor={ruta.nivel_dificultad} /></td></tr>
              </tbody>
            </table>
            <h6>Equipamiento recomendado</h6>
            <p className="small">{sinInformacion(ruta.equipamiento)}</p>
            <h6>Condiciones del terreno</h6>
            <p className="small">{sinInformacion(ruta.condiciones_terreno)}</p>
            {ruta.compatible === false && (
              <Alerta tipo="warning">Esta ruta no es compatible con tu perfil: su dificultad supera tu nivel o corresponde a otra actividad o zona.</Alerta>
            )}
          </div>
        </div>
        <div className="col-md-7">
          <Mapa trazado={ruta.trazado} inicio={inicio} altura={420} />
        </div>
      </div>
      <div className="d-flex justify-content-between mt-3">
        <Link to="/rutas" className="btn btn-outline-verde">← Volver</Link>
        {ruta.nivel_usuario >= ruta.nivel_dificultad && (
          <Link to={`/rutas/${ruta.id_ruta}/nueva-salida`} className="btn btn-verde">Crear salida grupal →</Link>
        )}
      </div>
    </>
  )
}
