import { useEffect, useMemo, useRef } from 'react'

import { capitalFlows, countries } from '../../data/mockData'
import { useStore } from '../../store/useStore'

const FLOW_BASE_TRAVEL_FRAMES = 80
const FLOW_SPEED_FACTOR = 10
const FLOW_MAX_ACCELERATION = 20
const FLOW_PHASE_OFFSET = 0.07
const CURVE_VERTICAL_BASE_OFFSET = 44
const CURVE_VERTICAL_INDEX_SPACING = 14
const FLOW_LINE_WIDTH_DIVISOR = 180
const FLOW_DOT_BASE_RADIUS = 2.6
const FLOW_DOT_SIZE_DIVISOR = 140

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
  const animatedFlows = useMemo(
    () =>
      capitalFlows.slice(0, 20).flatMap((flow) => {
        const fromCountry = countries.find((country) => country.id === flow.from)
        const toCountry = countries.find((country) => country.id === flow.to)
        if (!fromCountry || !toCountry) return []

        return [
          {
            ...flow,
            fromCoordinates: fromCountry.coordinates,
            toCoordinates: toCountry.coordinates,
            trailColor: FLOW_TRAIL_COLOR[flow.direction] ?? FLOW_TRAIL_COLOR.bidirectional,
            dotColor: FLOW_DOT_COLOR[flow.direction] ?? FLOW_DOT_COLOR.bidirectional,
            lineWidth: Math.max(0.8, flow.value / FLOW_LINE_WIDTH_DIVISOR),
            dotRadius: FLOW_DOT_BASE_RADIUS + flow.value / FLOW_DOT_SIZE_DIVISOR,
          },
        ]
      }),
    [],
  )

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

      animatedFlows.forEach((flow, index) => {
        const start = toCanvasPoint(flow.fromCoordinates.lat, flow.fromCoordinates.lon, canvas.width, canvas.height)
        const end = toCanvasPoint(flow.toCoordinates.lat, flow.toCoordinates.lon, canvas.width, canvas.height)
        const control = {
          x: (start.x + end.x) / 2,
          y: Math.min(start.y, end.y) - CURVE_VERTICAL_BASE_OFFSET - (index % 5) * CURVE_VERTICAL_INDEX_SPACING,
        }

        // Draw trail arc
        context.lineWidth = flow.lineWidth
        context.strokeStyle = flow.trailColor
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

        context.fillStyle = flow.dotColor
        context.shadowBlur = 16
        context.shadowColor = flow.dotColor
        context.beginPath()
        context.arc(pointX, pointY, flow.dotRadius, 0, Math.PI * 2)
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
  }, [animatedFlows, flowSpeed])

  return <canvas ref={canvasRef} className="flow-layer" />
}
