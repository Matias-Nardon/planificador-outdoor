import { useEffect, useRef, useState } from 'react'

// HU-006: visualización del recorrido con Google Maps JavaScript API.
// Si no hay clave configurada o el servicio no responde, se muestra una vista
// esquemática del trazado, como prevé la política de disponibilidad del proyecto.
const CLAVE = import.meta.env.VITE_GOOGLE_MAPS_API_KEY
let cargaGoogle = null

function cargarGoogleMaps() {
  if (!CLAVE) return Promise.reject(new Error('sin clave'))
  if (window.google?.maps) return Promise.resolve(window.google.maps)
  if (!cargaGoogle) {
    cargaGoogle = new Promise((resolver, rechazar) => {
      const script = document.createElement('script')
      script.src = `https://maps.googleapis.com/maps/api/js?key=${CLAVE}`
      script.async = true
      script.onload = () => resolver(window.google.maps)
      script.onerror = rechazar
      document.head.appendChild(script)
    })
  }
  return cargaGoogle
}

export default function Mapa({ trazado, inicio, encuentro, onSeleccionar, altura = 320 }) {
  const contenedor = useRef(null)
  const [disponible, setDisponible] = useState(Boolean(CLAVE))

  useEffect(() => {
    let cancelado = false
    cargarGoogleMaps()
      .then((maps) => {
        if (cancelado || !contenedor.current) return
        const puntos = (trazado?.coordinates || []).map(([lng, lat]) => ({ lat, lng }))
        const centro = encuentro || puntos[0] || inicio || { lat: -31.2, lng: -64.3 }
        const mapa = new maps.Map(contenedor.current, { center: centro, zoom: 13, mapTypeId: 'terrain' })
        if (puntos.length > 1) {
          new maps.Polyline({ path: puntos, map: mapa, strokeColor: '#d9534f', strokeWeight: 4 })
          new maps.Marker({ position: puntos[0], map: mapa, label: 'I', title: 'Inicio' })
          new maps.Marker({ position: puntos[puntos.length - 1], map: mapa, label: 'F', title: 'Fin' })
          const limites = new maps.LatLngBounds()
          puntos.forEach((p) => limites.extend(p))
          mapa.fitBounds(limites)
        } else if (inicio) {
          new maps.Marker({ position: inicio, map: mapa, title: 'Inicio' })
        }
        let marcador = encuentro ? new maps.Marker({ position: encuentro, map: mapa, title: 'Punto de encuentro' }) : null
        if (onSeleccionar) {
          mapa.addListener('click', (e) => {
            const punto = { lat: e.latLng.lat(), lng: e.latLng.lng() }
            if (marcador) marcador.setPosition(punto)
            else marcador = new maps.Marker({ position: punto, map: mapa, title: 'Punto de encuentro' })
            onSeleccionar(punto)
          })
        }
      })
      .catch(() => !cancelado && setDisponible(false))
    return () => {
      cancelado = true
    }
  }, [trazado, inicio, encuentro, onSeleccionar])

  if (disponible) return <div ref={contenedor} className="mapa" style={{ height: altura }} />
  return <VistaEsquematica trazado={trazado} inicio={inicio} encuentro={encuentro} altura={altura} />
}

function VistaEsquematica({ trazado, inicio, encuentro, altura }) {
  const puntos = (trazado?.coordinates || []).map(([lng, lat]) => ({ lat, lng }))
  const todos = [...puntos, ...(encuentro ? [encuentro] : []), ...(!puntos.length && inicio ? [inicio] : [])]
  if (!todos.length) return <div className="mapa d-flex align-items-center justify-content-center text-muted">Sin información de ubicación</div>
  const lats = todos.map((p) => p.lat)
  const lngs = todos.map((p) => p.lng)
  const [minLat, maxLat, minLng, maxLng] = [Math.min(...lats), Math.max(...lats), Math.min(...lngs), Math.max(...lngs)]
  const rango = Math.max(maxLat - minLat, maxLng - minLng, 0.005)
  const xy = (p) => [20 + ((p.lng - minLng) / rango) * 360, 280 - ((p.lat - minLat) / rango) * 260]
  const linea = puntos.map((p) => xy(p).join(',')).join(' ')
  return (
    <div className="mapa position-relative" style={{ height: altura }}>
      <svg viewBox="0 0 400 300" width="100%" height="100%" preserveAspectRatio="xMidYMid meet">
        {puntos.length > 1 && <polyline points={linea} fill="none" stroke="#d9534f" strokeWidth="4" strokeLinejoin="round" />}
        {puntos.length > 0 && <circle cx={xy(puntos[0])[0]} cy={xy(puntos[0])[1]} r="7" fill="#2e7d32" />}
        {puntos.length > 1 && <circle cx={xy(puntos.at(-1))[0]} cy={xy(puntos.at(-1))[1]} r="7" fill="#c62828" />}
        {!puntos.length && inicio && <circle cx={xy(inicio)[0]} cy={xy(inicio)[1]} r="7" fill="#2e7d32" />}
        {encuentro && <circle cx={xy(encuentro)[0]} cy={xy(encuentro)[1]} r="8" fill="#2f6f4e" stroke="#fff" strokeWidth="2" />}
      </svg>
      <small className="position-absolute bottom-0 end-0 m-2 text-muted">Vista esquemática del recorrido</small>
    </div>
  )
}
