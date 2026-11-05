import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { Alerta } from '../componentes'
import { useSesion } from '../sesion'

// HU-002: inicio de sesión.
export default function Ingresar() {
  const { iniciar } = useSesion()
  const navegar = useNavigate()
  const [datos, setDatos] = useState({ correo: '', contrasena: '' })
  const [error, setError] = useState('')

  const enviar = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const sesion = await api('/auth/login', { method: 'POST', body: datos })
      iniciar(sesion)
      navegar('/')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="row justify-content-center mt-4">
      <div className="col-md-5">
        <form className="tarjeta p-4" onSubmit={enviar}>
          <h4 className="text-center mb-3">Planificá tu próxima salida outdoor</h4>
          <Alerta>{error}</Alerta>
          <label className="form-label small text-muted">Correo electrónico</label>
          <input className="form-control mb-3" type="email" value={datos.correo}
                 onChange={(e) => setDatos({ ...datos, correo: e.target.value })} />
          <label className="form-label small text-muted">Contraseña</label>
          <input className="form-control mb-3" type="password" value={datos.contrasena}
                 onChange={(e) => setDatos({ ...datos, contrasena: e.target.value })} />
          <button className="btn btn-verde w-100">Ingresar</button>
          <p className="text-center text-muted mt-3 mb-1">¿No tenés cuenta?</p>
          <Link to="/registro" className="btn btn-outline-verde w-100">Registrarme</Link>
        </form>
      </div>
    </div>
  )
}
