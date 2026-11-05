import { Navigate, NavLink, Route, Routes, useNavigate } from 'react-router-dom'
import { useSesion } from './sesion'
import Ingresar from './paginas/Ingresar'
import Registro from './paginas/Registro'
import Perfil from './paginas/Perfil'
import Rutas from './paginas/Rutas'
import FichaRuta from './paginas/FichaRuta'
import CrearSalida from './paginas/CrearSalida'
import MisSalidas from './paginas/MisSalidas'
import DetalleSalida from './paginas/DetalleSalida'
import AdminRutas from './paginas/AdminRutas'
import FormularioRuta from './paginas/FormularioRuta'

function Barra() {
  const { sesion, cerrar } = useSesion()
  const navegar = useNavigate()
  const salir = () => {
    cerrar()
    navegar('/ingresar')
  }
  const enlaces = sesion?.usuario.rol === 'administrador'
    ? [['/admin/rutas', 'Registro de rutas']]
    : [['/rutas', 'Rutas recomendadas'], ['/salidas', 'Mis salidas'], ['/perfil', 'Mi perfil']]
  return (
    <nav className="navbar navbar-expand barra navbar-dark px-3">
      <span className="navbar-brand fw-bold">Planificador Outdoor</span>
      {sesion && (
        <>
          <ul className="navbar-nav ms-auto me-3">
            {enlaces.map(([ruta, texto]) => (
              <li className="nav-item" key={ruta}>
                <NavLink className="nav-link" to={ruta}>{texto}</NavLink>
              </li>
            ))}
          </ul>
          <span className="text-white me-3">{sesion.usuario.nombre}</span>
          <button className="btn btn-sm btn-outline-light" onClick={salir}>Salir</button>
        </>
      )}
    </nav>
  )
}

function Protegida({ children, rol }) {
  const { sesion } = useSesion()
  if (!sesion) return <Navigate to="/ingresar" replace />
  if (rol && sesion.usuario.rol !== rol) return <Navigate to="/" replace />
  return children
}

function Inicio() {
  const { sesion } = useSesion()
  if (!sesion) return <Navigate to="/ingresar" replace />
  if (sesion.usuario.rol === 'administrador') return <Navigate to="/admin/rutas" replace />
  return <Navigate to={sesion.perfil_completo ? '/rutas' : '/perfil'} replace />
}

export default function App() {
  return (
    <>
      <Barra />
      <main className="container py-3">
        <Routes>
          <Route path="/" element={<Inicio />} />
          <Route path="/ingresar" element={<Ingresar />} />
          <Route path="/registro" element={<Registro />} />
          <Route path="/perfil" element={<Protegida><Perfil /></Protegida>} />
          <Route path="/rutas" element={<Protegida><Rutas /></Protegida>} />
          <Route path="/rutas/:id" element={<Protegida><FichaRuta /></Protegida>} />
          <Route path="/rutas/:id/nueva-salida" element={<Protegida><CrearSalida /></Protegida>} />
          <Route path="/salidas" element={<Protegida><MisSalidas /></Protegida>} />
          <Route path="/salidas/:id" element={<Protegida><DetalleSalida /></Protegida>} />
          <Route path="/admin/rutas" element={<Protegida rol="administrador"><AdminRutas /></Protegida>} />
          <Route path="/admin/rutas/nueva" element={<Protegida rol="administrador"><FormularioRuta /></Protegida>} />
          <Route path="/admin/rutas/:id" element={<Protegida rol="administrador"><FormularioRuta /></Protegida>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  )
}
