import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import { Alerta, Cargando, Pasos } from '../componentes'
import Mapa from '../Mapa'

// HU-008: creación de la salida grupal a partir de una ruta.
export default function CrearSalida() {
  const { id } = useParams()
  const navegar = useNavigate()
  const [ruta, setRuta] = useState(null)
  const [datos, setDatos] = useState({ fecha: '', horario: '08:00', punto_encuentro: '', cupo: 10 })
  const [encuentro, setEncuentro] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api(`/rutas/${id}`).then((r) => {
      setRuta(r)
      if (r.latitud_inicio) setEncuentro({ lat: r.latitud_inicio, lng: r.longitud_inicio })
    }).catch((err) => setError(err.message))
  }, [id])

  const seleccionar = useCallback((punto) => setEncuentro(punto), [])
  const inicio = useMemo(() => (ruta?.latitud_inicio ? { lat: ruta.latitud_inicio, lng: ruta.longitud_inicio } : null), [ruta])
  const campo = (nombre) => ({ value: datos[nombre], onChange: (e) => setDatos({ ...datos, [nombre]: e.target.value }) })

  const crear = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const { id_salida } = await api('/salidas', {
        method: 'POST',
        body: { ...datos, id_ruta: Number(id), latitud_encuentro: encuentro?.lat, longitud_encuentro: encuentro?.lng },
      })
      navegar(`/salidas/${id_salida}`)
    } catch (err) {
      setError(err.message)
    }
  }

  if (!ruta) return error ? <Alerta>{error}</Alerta> : <Cargando />

  return (
    <>
      <Pasos actual={2} />
      <h3>Crear salida grupal</h3>
      <Alerta>{error}</Alerta>
      <div className="row g-3">
        <form className="col-md-5" onSubmit={crear}>
          <div className="tarjeta p-3">
            <label className="form-label small text-muted">Ruta seleccionada</label>
            <input className="form-control mb-3" disabled value={`${ruta.nombre} (dificultad ${ruta.nivel_dificultad}/5)`} />
            <div className="row">
              <div className="col"><label className="form-label small text-muted">Fecha</label><input type="date" className="form-control mb-3" {...campo('fecha')} /></div>
              <div className="col"><label className="form-label small text-muted">Horario</label><input type="time" className="form-control mb-3" {...campo('horario')} /></div>
            </div>
            <label className="form-label small text-muted">Punto de encuentro</label>
            <input className="form-control mb-3" placeholder="Por ejemplo: entrada al sendero" {...campo('punto_encuentro')} />
            <label className="form-label small text-muted">Cupo (incluye al organizador)</label>
            <input type="number" min="1" className="form-control mb-3" {...campo('cupo')} />
            <div className="d-flex justify-content-between">
              <button type="button" className="btn btn-outline-verde" onClick={() => navegar(-1)}>Cancelar</button>
              <button className="btn btn-verde">Crear salida →</button>
            </div>
          </div>
        </form>
        <div className="col-md-7">
          <h6>Punto de encuentro <small className="text-muted">(hacé clic en el mapa para ubicarlo)</small></h6>
          <Mapa trazado={ruta.trazado} inicio={inicio} encuentro={encuentro} onSeleccionar={seleccionar} altura={380} />
        </div>
      </div>
    </>
  )
}
