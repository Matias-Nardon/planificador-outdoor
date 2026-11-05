import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { Alerta, Cargando, Pasos } from '../componentes'
import { useSesion } from '../sesion'

// HU-003: registro y actualización del perfil.
export default function Perfil() {
  const { actualizar } = useSesion()
  const navegar = useNavigate()
  const [catalogos, setCatalogos] = useState(null)
  const [datos, setDatos] = useState({
    nivel_experiencia: 3, condicion_fisica: 3, ubicacion: 'Córdoba Capital', tipo_actividad: 'Senderismo',
    distancia_maxima: 15, duracion_maxima: 6, zona_interes: 'Sierras Chicas',
  })
  const [mensaje, setMensaje] = useState({ tipo: 'danger', texto: '' })

  useEffect(() => {
    Promise.all([api('/catalogos'), api('/perfil')]).then(([c, p]) => {
      setCatalogos(c)
      if (p.perfil) setDatos((d) => ({ ...d, ...p.perfil }))
    })
  }, [])

  const campo = (nombre) => ({ value: datos[nombre], onChange: (e) => setDatos({ ...datos, [nombre]: e.target.value }) })

  const guardar = async (destino) => {
    setMensaje({ texto: '' })
    try {
      await api('/perfil', { method: 'PUT', body: datos })
      actualizar({ perfil_completo: true })
      if (destino) navegar(destino)
      else setMensaje({ tipo: 'success', texto: 'El perfil se guardó correctamente.' })
    } catch (err) {
      setMensaje({ tipo: 'danger', texto: err.message })
    }
  }

  if (!catalogos) return <Cargando />
  const nivel = Math.min(Number(datos.nivel_experiencia), Number(datos.condicion_fisica))

  return (
    <>
      <Pasos actual={0} />
      <h3>Mi perfil</h3>
      <Alerta tipo={mensaje.tipo}>{mensaje.texto}</Alerta>
      <div className="row g-3">
        <div className="col-md-6">
          <div className="tarjeta p-3 h-100">
            <h6>Características del usuario</h6>
            <label className="form-label small text-muted">Nivel de experiencia (1 a 5)</label>
            <select className="form-select mb-3" {...campo('nivel_experiencia')}>
              {Object.entries(catalogos.niveles).map(([n, t]) => <option key={n} value={n}>{n} - {t}</option>)}
            </select>
            <label className="form-label small text-muted">Condición física (1 a 5)</label>
            <select className="form-select mb-3" {...campo('condicion_fisica')}>
              {Object.entries(catalogos.condicion_fisica).map(([n, t]) => <option key={n} value={n}>{n} - {t}</option>)}
            </select>
            <label className="form-label small text-muted">Ubicación</label>
            <select className="form-select mb-3" {...campo('ubicacion')}>
              {catalogos.localidades.map((l) => <option key={l}>{l}</option>)}
            </select>
            <div className="alert alert-success py-2 small mb-0">
              Tu nivel para las recomendaciones es <strong>{nivel}</strong>: el menor valor entre tu experiencia y tu condición física.
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="tarjeta p-3 h-100">
            <h6>Preferencias</h6>
            <label className="form-label small text-muted">Tipo de actividad</label>
            <select className="form-select mb-3" {...campo('tipo_actividad')}>
              {catalogos.actividades.map((a) => <option key={a}>{a}</option>)}
            </select>
            <div className="row">
              <div className="col"><label className="form-label small text-muted">Distancia máxima (km)</label><input type="number" min="1" className="form-control mb-3" {...campo('distancia_maxima')} /></div>
              <div className="col"><label className="form-label small text-muted">Duración máxima (h)</label><input type="number" min="1" step="0.5" className="form-control mb-3" {...campo('duracion_maxima')} /></div>
            </div>
            <label className="form-label small text-muted">Zona de interés</label>
            <select className="form-select mb-3" {...campo('zona_interes')}>
              {catalogos.zonas.map((z) => <option key={z}>{z}</option>)}
            </select>
          </div>
        </div>
      </div>
      <div className="d-flex justify-content-between mt-3">
        <button className="btn btn-outline-verde" onClick={() => guardar()}>Guardar perfil</button>
        <button className="btn btn-verde" onClick={() => guardar('/rutas')}>Ver rutas recomendadas →</button>
      </div>
    </>
  )
}
