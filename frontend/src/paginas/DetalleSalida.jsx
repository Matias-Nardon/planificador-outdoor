import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api'
import { Alerta, Cargando, Compatibilidad, Escala, Pasos, etiquetaEstado, formatoFecha } from '../componentes'
import Mapa from '../Mapa'

// HU-009, HU-010 y HU-011: participantes sugeridos, confirmación con control del cupo
// y actualización de los datos de la salida.
export default function DetalleSalida() {
  const { id } = useParams()
  const [salida, setSalida] = useState(null)
  const [sugerencias, setSugerencias] = useState(null)
  const [mensaje, setMensaje] = useState({ tipo: 'danger', texto: '' })
  const [edicion, setEdicion] = useState(null)

  const cargar = useCallback(async () => {
    const s = await api(`/salidas/${id}`)
    setSalida(s)
    if (s.es_organizador && s.estado !== 'finalizada') setSugerencias(await api(`/salidas/${id}/sugerencias`))
  }, [id])

  useEffect(() => {
    cargar().catch((err) => setMensaje({ tipo: 'danger', texto: err.message }))
  }, [cargar])

  const accion = async (ruta, body, exito) => {
    setMensaje({ texto: '' })
    try {
      await api(ruta, { method: 'POST', body })
      await cargar()
      if (exito) setMensaje({ tipo: 'success', texto: exito })
    } catch (err) {
      setMensaje({ tipo: 'danger', texto: err.message })
    }
  }

  const guardarCambios = async (e) => {
    e.preventDefault()
    try {
      await api(`/salidas/${id}`, { method: 'PUT', body: edicion })
      setEdicion(null)
      await cargar()
      setMensaje({ tipo: 'success', texto: 'Los cambios se guardaron y se muestran a los participantes confirmados.' })
    } catch (err) {
      setMensaje({ tipo: 'danger', texto: err.message })
    }
  }

  const encuentro = useMemo(() => (salida?.latitud_encuentro ? { lat: salida.latitud_encuentro, lng: salida.longitud_encuentro } : null), [salida])

  if (!salida) return mensaje.texto ? <Alerta>{mensaje.texto}</Alerta> : <Cargando />
  const { ruta } = salida
  const campo = (nombre) => ({ value: edicion[nombre], onChange: (e) => setEdicion({ ...edicion, [nombre]: e.target.value }) })

  return (
    <>
      <Pasos actual={3} />
      <h3>Salida: {ruta.nombre}</h3>
      {salida.ultimo_cambio && <div className="alert alert-warning py-2">{salida.ultimo_cambio}</div>}
      <Alerta tipo={mensaje.tipo}>{mensaje.texto}</Alerta>

      <div className="row g-3">
        <div className="col-md-5">
          <div className="tarjeta p-3">
            {!edicion ? (
              <table className="table table-sm">
                <tbody>
                  <tr><td className="text-muted">Fecha</td><td className="fw-semibold">{formatoFecha(salida.fecha)}</td></tr>
                  <tr><td className="text-muted">Horario</td><td className="fw-semibold">{salida.horario}</td></tr>
                  <tr><td className="text-muted">Punto de encuentro</td><td className="fw-semibold">{salida.punto_encuentro}</td></tr>
                  <tr><td className="text-muted">Organizador</td><td className="fw-semibold">{salida.organizador}</td></tr>
                  <tr><td className="text-muted">Dificultad</td><td><Escala valor={ruta.nivel_dificultad} /></td></tr>
                  <tr><td className="text-muted">Tu compatibilidad</td><td><Compatibilidad puntaje={salida.mi_puntaje} /></td></tr>
                  <tr><td className="text-muted">Estado</td><td>{etiquetaEstado[salida.estado]}</td></tr>
                </tbody>
              </table>
            ) : (
              <form onSubmit={guardarCambios}>
                <label className="form-label small text-muted">Fecha</label>
                <input type="date" className="form-control mb-2" {...campo('fecha')} />
                <label className="form-label small text-muted">Horario</label>
                <input type="time" className="form-control mb-2" {...campo('horario')} />
                <label className="form-label small text-muted">Punto de encuentro</label>
                <input className="form-control mb-2" {...campo('punto_encuentro')} />
                <label className="form-label small text-muted">Cupo</label>
                <input type="number" min="1" className="form-control mb-3" {...campo('cupo')} />
                <div className="d-flex gap-2">
                  <button type="button" className="btn btn-outline-verde" onClick={() => setEdicion(null)}>Cancelar</button>
                  <button className="btn btn-verde">Guardar cambios</button>
                </div>
              </form>
            )}

            <h6 className="mt-3">Participantes confirmados ({salida.ocupados} de {salida.cupo})</h6>
            <ul className="small">
              {salida.participantes.map((p) => <li key={p.id_usuario}>{p.nombre}{p.organizador ? ' (organizador)' : ''}</li>)}
            </ul>

            {salida.estado !== 'finalizada' && !edicion && (
              <div className="d-flex gap-2 flex-wrap">
                {salida.es_organizador && (
                  <button className="btn btn-outline-verde"
                          onClick={() => setEdicion({ fecha: salida.fecha, horario: salida.horario, punto_encuentro: salida.punto_encuentro, cupo: salida.cupo, latitud_encuentro: salida.latitud_encuentro, longitud_encuentro: salida.longitud_encuentro })}>
                    Modificar salida
                  </button>
                )}
                {!salida.es_organizador && salida.mi_estado === 'confirmado' && (
                  <button className="btn btn-outline-verde" onClick={() => accion(`/salidas/${id}/cancelar`, null, 'Cancelaste tu asistencia y se liberó tu lugar.')}>
                    Cancelar asistencia
                  </button>
                )}
                {!salida.es_organizador && salida.mi_estado !== 'confirmado' && (
                  <button className="btn btn-verde" onClick={() => accion(`/salidas/${id}/confirmar`, null, 'Confirmaste tu asistencia.')}>
                    Confirmar asistencia
                  </button>
                )}
              </div>
            )}
            {!salida.es_organizador && !salida.puedo_participar && (
              <p className="small text-danger mt-2">La dificultad de esta ruta supera tu nivel ({salida.mi_nivel}).</p>
            )}
          </div>
        </div>
        <div className="col-md-7">
          <Mapa trazado={ruta.trazado} encuentro={encuentro} altura={380} />
        </div>
      </div>

      {sugerencias && (
        <section className="mt-4">
          <h4>Participantes sugeridos</h4>
          <div className="alert alert-success py-2 small">
            Usuarios con nivel igual o superior a la dificultad de la ruta ({ruta.nivel_dificultad}/5) e interés en {ruta.ubicacion}, ordenados por compatibilidad.
          </div>
          {sugerencias.sugeridos.length === 0 ? (
            <p className="text-muted">No hay usuarios compatibles con la ruta para invitar.</p>
          ) : (
            <table className="table bg-white align-middle">
              <thead><tr><th>Usuario</th><th>Nivel</th><th>Ubicación</th><th>Compatibilidad</th><th>Acción</th></tr></thead>
              <tbody>
                {sugerencias.sugeridos.map((p) => (
                  <tr key={p.id_usuario}>
                    <td>{p.nombre}</td>
                    <td><Escala valor={p.nivel} /></td>
                    <td>{p.ubicacion}</td>
                    <td><Compatibilidad puntaje={p.puntaje} /></td>
                    <td><button className="btn btn-sm btn-verde" onClick={() => accion(`/salidas/${id}/invitaciones`, { id_usuario: p.id_usuario }, `Se invitó a ${p.nombre}.`)}>Invitar</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {sugerencias.invitados.length > 0 && (
            <p className="small text-muted">Invitados pendientes de confirmar: {sugerencias.invitados.map((i) => i.nombre).join(', ')}.</p>
          )}
        </section>
      )}
      <Link to="/salidas" className="btn btn-outline-verde mt-3">← Mis salidas</Link>
    </>
  )
}
