import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { Alerta } from '../componentes'
import { useSesion } from '../sesion'

// HU-001: registro de usuario. Al registrarse, el usuario completa su perfil.
export default function Registro() {
  const { iniciar } = useSesion()
  const navegar = useNavigate()
  const [datos, setDatos] = useState({ nombre: '', apellido: '', correo: '', contrasena: '' })
  const [error, setError] = useState('')
  const campo = (nombre) => ({ value: datos[nombre], onChange: (e) => setDatos({ ...datos, [nombre]: e.target.value }) })

  const enviar = async (e) => {
    e.preventDefault()
    setError('')
    try {
      iniciar(await api('/auth/registro', { method: 'POST', body: datos }))
      navegar('/perfil')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="row justify-content-center mt-4">
      <div className="col-md-6">
        <form className="tarjeta p-4" onSubmit={enviar}>
          <h4 className="mb-3">Crear una cuenta</h4>
          <Alerta>{error}</Alerta>
          <div className="row">
            <div className="col"><label className="form-label small text-muted">Nombre</label><input className="form-control mb-3" {...campo('nombre')} /></div>
            <div className="col"><label className="form-label small text-muted">Apellido</label><input className="form-control mb-3" {...campo('apellido')} /></div>
          </div>
          <label className="form-label small text-muted">Correo electrónico</label>
          <input className="form-control mb-3" type="email" {...campo('correo')} />
          <label className="form-label small text-muted">Contraseña</label>
          <input className="form-control" type="password" {...campo('contrasena')} />
          <div className="form-text mb-3">Mínimo 8 caracteres, con al menos una mayúscula, una minúscula y un número.</div>
          <button className="btn btn-verde w-100">Registrarme</button>
          <Link to="/ingresar" className="d-block text-center mt-3">Ya tengo cuenta</Link>
        </form>
      </div>
    </div>
  )
}
