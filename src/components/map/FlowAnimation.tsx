import { useEffect, useRef } from 'react'

import { capitalFlows, countries } from '../../data/mockData'

const FLOW_BASE_TRAVEL_FRAMES = 80
const FLOW_SPEED_FACTOR = 10
const FLOW_MAX_ACCELERATION = 20
const FLOW_PHASE_OFFSET = 0.07

const toCanvasPoint = (lat: number, lon: number, width: number, height: number) => ({
  x: ((lon + 180) / 360) * width,
  y: ((90 - lat) / 180) * height,
})

export function FlowAnimation() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const context = canvas.getContext('2d')
    if (!context) return

    let frame = 0
    let animation = 0

    const resize = () => {
      const parent = canvas.parentElement
      if (!parent) return
      canvas.width = parent.clientWidth
      canvas.height = parent.clientHeight
    }

    const draw = () => {
      frame += 1
      context.clearRect(0, 0, canvas.width, canvas.height)
      context.lineWidth = 1

      capitalFlows.slice(0, 20).forEach((flow, index) => {
        const fromCountry = countries.find((country) => country.id === flow.from)
        const toCountry = countries.find((country) => country.id === flow.to)
        if (!fromCountry || !toCountry) return

        const start = toCanvasPoint(fromCountry.coordinates.lat, fromCountry.coordinates.lon, canvas.width, canvas.height)
        const end = toCanvasPoint(toCountry.coordinates.lat, toCountry.coordinates.lon, canvas.width, canvas.height)
        const control = {
          x: (start.x + end.x) / 2,
          y: Math.min(start.y, end.y) - 40 - (index % 5) * 12,
        }

        context.strokeStyle = index % 2 === 0 ? 'rgba(0, 212, 255, 0.22)' : 'rgba(0, 255, 136, 0.16)'
        context.beginPath()
        context.moveTo(start.x, start.y)
        context.quadraticCurveTo(control.x, control.y, end.x, end.y)
        context.stroke()

        const progress =
          ((frame / (FLOW_BASE_TRAVEL_FRAMES - Math.min(flow.speed * FLOW_SPEED_FACTOR, FLOW_MAX_ACCELERATION))) +
            index * FLOW_PHASE_OFFSET) %
          1
        const q0x = (1 - progress) * (1 - progress) * start.x
        const q1x = 2 * (1 - progress) * progress * control.x
        const q2x = progress * progress * end.x
        const q0y = (1 - progress) * (1 - progress) * start.y
        const q1y = 2 * (1 - progress) * progress * control.y
        const q2y = progress * progress * end.y
        const pointX = q0x + q1x + q2x
        const pointY = q0y + q1y + q2y

        context.fillStyle = index % 2 === 0 ? '#00d4ff' : '#00ff88'
        context.shadowBlur = 12
        context.shadowColor = context.fillStyle
        context.beginPath()
        context.arc(pointX, pointY, 2.4 + (flow.value / 160), 0, Math.PI * 2)
        context.fill()
        context.shadowBlur = 0
      })

      animation = window.requestAnimationFrame(draw)
    }

    resize()
    draw()
    window.addEventListener('resize', resize)

    return () => {
      window.removeEventListener('resize', resize)
      window.cancelAnimationFrame(animation)
    }
  }, [])

  return <canvas ref={canvasRef} className="flow-layer" />
}
