import { useEffect, useRef } from 'react'

import { capitalFlows, countries } from '../../data/mockData'
import { useStore } from '../../store/useStore'

const FLOW_BASE_TRAVEL_FRAMES = 80
const FLOW_SPEED_FACTOR = 10
const FLOW_MAX_ACCELERATION = 20
const FLOW_PHASE_OFFSET = 0.07

/** Neon colors by flow direction */
const FLOW_TRAIL_COLOR: Record<string, string> = {
  inbound: 'rgba(0, 255, 136, 0.42)',
  outbound: 'rgba(255, 80, 50, 0.38)',
  bidirectional: 'rgba(0, 180, 255, 0.36)',
}
const FLOW_DOT_COLOR: Record<string, string> = {
  inbound: '#00ff88',
  outbound: '#ff5533',
  bidirectional: '#00d4ff',
}

const toCanvasPoint = (lat: number, lon: number, width: number, height: number) => ({
  x: ((lon + 180) / 360) * width,
  y: ((90 - lat) / 180) * height,
})

export function FlowAnimation() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const flowSpeed = useStore((state) => state.flowSpeed)

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

      capitalFlows.slice(0, 20).forEach((flow, index) => {
        const fromCountry = countries.find((country) => country.id === flow.from)
        const toCountry = countries.find((country) => country.id === flow.to)
        if (!fromCountry || !toCountry) return

        const start = toCanvasPoint(fromCountry.coordinates.lat, fromCountry.coordinates.lon, canvas.width, canvas.height)
        const end = toCanvasPoint(toCountry.coordinates.lat, toCountry.coordinates.lon, canvas.width, canvas.height)
        const control = {
          x: (start.x + end.x) / 2,
          y: Math.min(start.y, end.y) - 44 - (index % 5) * 14,
        }

        const trailColor = FLOW_TRAIL_COLOR[flow.direction] ?? FLOW_TRAIL_COLOR.bidirectional
        const dotColor = FLOW_DOT_COLOR[flow.direction] ?? FLOW_DOT_COLOR.bidirectional
        const lineW = Math.max(0.8, flow.value / 180)

        // Draw trail arc
        context.lineWidth = lineW
        context.strokeStyle = trailColor
        context.shadowBlur = 0
        context.beginPath()
        context.moveTo(start.x, start.y)
        context.quadraticCurveTo(control.x, control.y, end.x, end.y)
        context.stroke()

        // Draw animated dot
        const progress =
          ((frame * flowSpeed) /
            (FLOW_BASE_TRAVEL_FRAMES - Math.min(flow.speed * FLOW_SPEED_FACTOR, FLOW_MAX_ACCELERATION)) +
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

        const dotRadius = 2.6 + flow.value / 140
        context.fillStyle = dotColor
        context.shadowBlur = 16
        context.shadowColor = dotColor
        context.beginPath()
        context.arc(pointX, pointY, dotRadius, 0, Math.PI * 2)
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
  }, [flowSpeed])

  return <canvas ref={canvasRef} className="flow-layer" />
}
