import { createContext, useContext, useState } from 'react'
import { guardarSesion, leerSesion } from './api'

const ContextoSesion = createContext(null)

export function ProveedorSesion({ children }) {
  const [sesion, setSesion] = useState(leerSesion)

  const iniciar = (datos) => {
    guardarSesion(datos)
    setSesion(datos)
  }
  const actualizar = (cambios) => iniciar({ ...sesion, ...cambios })
  const cerrar = () => {
    guardarSesion(null)
    setSesion(null)
  }

  return (
    <ContextoSesion.Provider value={{ sesion, iniciar, actualizar, cerrar }}>
      {children}
    </ContextoSesion.Provider>
  )
}

export const useSesion = () => useContext(ContextoSesion)
