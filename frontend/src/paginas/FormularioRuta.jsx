import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import { Alerta, Cargando } from '../componentes'
import Mapa from '../Mapa'

// HU-004: registro y modificación de rutas con su clasificación de dificultad.
const VACIA = {
  nombre: '', tipo_actividad: 'Senderismo', ubicacion: 'Sierras Chicas', distancia: '', desnivel: '',
  duracion_estimada: '', nivel_dificultad: 3, latitud_inicio: '', longitud_inicio: '',
  equipamiento: '', condiciones_terreno: '', trazado: '',
}

export default function FormularioRuta() {
  const { id } = useParams()
  const navegar = useNavigate()
  const [catalogos, setCatalogos] = useState(null)
  const [datos, setDatos] = useState(VACIA)
  const [error, setError] = useState('')

  useEffect(() => {
    api('/catalogos').then(setCatalogos)
    if (id) {
      api(`/rutas/${id}`).then((r) => setDatos({
        ...VACIA, ...Object.fromEntries(Object.entries(r).map(([k, v]) => [k, v ?? ''])),
        trazado: r.trazado ? JSON.stringify(r.trazado) : '',
      }))
    }
  }, [id])

  const campo = (nombre) => ({ value: datos[nombre], onChange: (e) => setDatos({ ...datos, [nombre]: e.target.value }) })

  const cargarArchivo = (e) => {
    const archivo = e.target.files?.[0]
    if (!archivo) return
    archivo.text().then((texto) => {
      try {
        const geo = JSON.parse(texto)
        const linea = geo.type === 'FeatureCollection' ? geo.features[0].geometry : geo.type === 'Feature' ? geo.geometry : geo
        const [lng, lat] = linea.coordinates[0]
        setDatos((d) => ({ ...d, trazado: JSON.stringify(linea), latitud_inicio: lat, longitud_inicio: lng }))
      } catch {
        setError('El archivo no contiene un trazado GeoJSON válido.')
      }
    })
  }

  const guardar = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await api(id ? `/rutas/${id}` : '/rutas', { method: id ? 'PUT' : 'POST', body: datos })
      navegar('/admin/rutas')
    } catch (err) {
      setError(err.message)
    }
  }

  if (!catalogos) return <Cargando />
  let trazado = null
  try {
    trazado = datos.trazado ? JSON.parse(datos.trazado) : null
  } catch { /* trazado inválido: se informa al guardar */ }

  return (
    <form onSubmit={guardar}>
      <h3 className="mt-3">{id ? 'Modificar ruta' : 'Registro de ruta'}</h3>
      <Alerta>{error}</Alerta>
      <div className="row g-3">
        <div className="col-md-6">
          <div className="tarjeta p-3">
            <label className="form-label small text-muted">Nombre</label>
            <input className="form-control mb-2" {...campo('nombre')} />
            <div className="row">
              <div className="col"><label className="form-label small text-muted">Tipo de actividad</label>
                <select className="form-select mb-2" {...campo('tipo_actividad')}>{catalogos.actividades.map((a) => <option key={a}>{a}</option>)}</select></div>
              <div className="col"><label className="form-label small text-muted">Nivel de dificultad (1 a 5)</label>
                <select className="form-select mb-2" {...campo('nivel_dificultad')}>
                  {Object.entries(catalogos.dificultad).map(([n, t]) => <option key={n} value={n}>{n} - {t}</option>)}
                </select></div>
            </div>
            <div className="row">
              <div className="col"><label className="form-label small text-muted">Distancia (km)</label><input type="number" step="0.1" className="form-control mb-2" {...campo('distancia')} /></div>
              <div className="col"><label className="form-label small text-muted">Desnivel (m)</label><input type="number" className="form-control mb-2" {...campo('desnivel')} /></div>
              <div className="col"><label className="form-label small text-muted">Duración (h)</label><input type="number" step="0.5" className="form-control mb-2" {...campo('duracion_estimada')} /></div>
            </div>
            <label className="form-label small text-muted">Zona</label>
            <select className="form-select mb-2" {...campo('ubicacion')}>{catalogos.zonas.map((z) => <option key={z}>{z}</option>)}</select>
            <div className="row">
              <div className="col"><label className="form-label small text-muted">Latitud de inicio</label><input type="number" step="any" className="form-control mb-2" {...campo('latitud_inicio')} /></div>
              <div className="col"><label className="form-label small text-muted">Longitud de inicio</label><input type="number" step="any" className="form-control mb-2" {...campo('longitud_inicio')} /></div>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="tarjeta p-3">
            <label className="form-label small text-muted">Equipamiento recomendado</label>
            <textarea className="form-control mb-2" rows="2" {...campo('equipamiento')} />
            <label className="form-label small text-muted">Condiciones del terreno</label>
            <textarea className="form-control mb-2" rows="2" {...campo('condiciones_terreno')} />
            <label className="form-label small text-muted">Trazado del recorrido (archivo GeoJSON)</label>
            <input type="file" accept=".json,.geojson" className="form-control mb-2" onChange={cargarArchivo} />
            <Mapa trazado={trazado} inicio={datos.latitud_inicio ? { lat: Number(datos.latitud_inicio), lng: Number(datos.longitud_inicio) } : null} altura={220} />
          </div>
        </div>
      </div>
      <div className="d-flex justify-content-between mt-3">
        <button type="button" className="btn btn-outline-verde" onClick={() => navegar('/admin/rutas')}>Cancelar</button>
        <button className="btn btn-verde">Guardar ruta</button>
      </div>
    </form>
  )
}
