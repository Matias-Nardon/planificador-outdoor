import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { Cargando, Escala, num } from '../componentes'

// HU-004: listado de rutas registradas por el administrador.
export default function AdminRutas() {
  const [rutas, setRutas] = useState(null)
  useEffect(() => {
    api('/rutas').then(setRutas)
  }, [])
  if (!rutas) return <Cargando />
  return (
    <>
      <div className="d-flex justify-content-between align-items-center mt-3">
        <h3>Rutas registradas</h3>
        <Link to="/admin/rutas/nueva" className="btn btn-verde">Registrar ruta</Link>
      </div>
      <table className="table bg-white align-middle mt-3">
        <thead><tr><th>Nombre</th><th>Actividad</th><th>Zona</th><th>Distancia</th><th>Desnivel</th><th>Dificultad</th><th /></tr></thead>
        <tbody>
          {rutas.map((r) => (
            <tr key={r.id_ruta}>
              <td>{r.nombre}</td><td>{r.tipo_actividad}</td><td>{r.ubicacion}</td>
              <td>{num(r.distancia)} km</td><td>{num(r.desnivel)} m</td><td><Escala valor={r.nivel_dificultad} /></td>
              <td><Link to={`/admin/rutas/${r.id_ruta}`} className="btn btn-sm btn-outline-verde">Modificar</Link></td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  )
}
