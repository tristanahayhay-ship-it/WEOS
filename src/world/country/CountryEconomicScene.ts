import {
  AdditiveBlending,
  BufferGeometry,
  Float32BufferAttribute,
  Group,
  Line,
  LineBasicMaterial,
  Mesh,
  MeshBasicMaterial,
  SphereGeometry,
} from 'three'
import { EARTH_RADIUS, projectLngLatToCartesian } from '../../utils/globe'
import type { CityType, EconomicNodeType, EconomicCity, EconomicNode } from './types'
import type { NodeType, ResolvedCountryFlowModel, FlowLocation, FlowState } from './countryFlowModel'

// ── Altitude ──────────────────────────────────────────────────────────────────

const ALT_CITY_BASE = EARTH_RADIUS + 0.028
const ALT_NODE      = EARTH_RADIUS + 0.030

// ── Colour maps ───────────────────────────────────────────────────────────────

const CITY_COLORS: Record<CityType, string> = {
  capital:    '#facc15',  // pulsing yellow
  financial:  '#60a5fa',  // bright blue
  industrial: '#fb923c',  // orange
  port:       '#22d3ee',  // cyan
  logistics:  '#a78bfa',  // violet
  technology: '#4ade80',  // green
}

const NODE_COLORS: Record<EconomicNodeType, string> = {
  government:    '#fde68a',
  central_bank:  '#fbbf24',
  financial_hub: '#60a5fa',
  industrial_hub: '#fb923c',
  logistics_hub: '#a78bfa',
  port:          '#22d3ee',
  airport:       '#f97316',
  tech_hub:      '#4ade80',
  financial_center: '#60a5fa',
  industrial_center: '#fb923c',
  trade_hub: '#38bdf8',
  administrative_center: '#fde68a',
  production_zone: '#4ade80',
  consumption_zone: '#f59e0b',
  special_economic_zone: '#14b8a6',
}

const RESOLVED_NODE_COLORS: Record<NodeType, string> = {
  capital: '#facc15',
  financial_center: '#60a5fa',
  industrial_center: '#fb923c',
  port: '#22d3ee',
  airport: '#f97316',
  logistics_hub: '#a78bfa',
  trade_hub: '#38bdf8',
  administrative_center: '#fde68a',
  production_zone: '#4ade80',
  consumption_zone: '#f59e0b',
  special_economic_zone: '#14b8a6',
}

/** Inner sphere radius (world units) — scales with city importance */
function cityInnerRadius(importance: number): number {
  return 0.006 + importance * 0.009
}

/** Outer glow halo radius — 1.9× the inner sphere */
function cityGlowRadius(importance: number): number {
  return cityInnerRadius(importance) * 1.9
}

/** Small node marker radius */
const NODE_RADIUS = 0.003

// ── Helpers ───────────────────────────────────────────────────────────────────

function cityAltitude(importance: number): number {
  return ALT_CITY_BASE + importance * 0.002
}

/**
 * Place a glowing city sphere at a geographic position.
 *
 * Glow is approximated by a semi-transparent, additively-blended outer sphere
 * that is slightly larger than the solid inner sphere.  No post-processing is
 * required.
 */
function addCityMarker(group: Group, city: EconomicCity): void {
  const color = CITY_COLORS[city.type]
  const alt   = cityAltitude(city.importance)
  const [x, y, z] = projectLngLatToCartesian(city.position.lon, city.position.lat, alt)

  // ── Inner solid sphere ─────────────────────────────────────────────────────
  const innerR = cityInnerRadius(city.importance)
  const inner = new Mesh(
    new SphereGeometry(innerR, 8, 8),
    new MeshBasicMaterial({ color }),
  )
  inner.position.set(x, y, z)
  if (city.type === 'capital') {
    inner.userData.capitalPulseRole = 'core'
  }
  group.add(inner)

  // ── Glow halo (additively blended larger sphere) ───────────────────────────
  const glowR = cityGlowRadius(city.importance)
  const glow = new Mesh(
    new SphereGeometry(glowR, 10, 10),
    new MeshBasicMaterial({
      color,
      transparent: true,
      opacity:     0.18 + city.importance * 0.10,
      blending:    AdditiveBlending,
      depthWrite:  false,
    }),
  )
  glow.position.set(x, y, z)
  if (city.type === 'capital') {
    glow.userData.capitalPulseRole = 'glow'
    glow.userData.baseOpacity = 0.22 + city.importance * 0.14
    const glowMaterial = glow.material as MeshBasicMaterial
    glowMaterial.opacity = glow.userData.baseOpacity as number
  }
  group.add(glow)

  // ── Capital star ring – extra prominence for the primate city ─────────────
  if (city.importance >= 0.95) {
    const ringPts: number[] = []
    const segments = 36
    for (let i = 0; i <= segments; i += 1) {
      const a = (i / segments) * Math.PI * 2
      const ringR = glowR * 1.6
      const cosLat = Math.cos((city.position.lat * Math.PI) / 180) || 0.001
      const pt = projectLngLatToCartesian(
        city.position.lon + (ringR * 0.35 * Math.cos(a)) / cosLat,
        city.position.lat + ringR * 0.35 * Math.sin(a),
        alt + 0.001,
      )
      ringPts.push(...pt)
    }
    const geo = new BufferGeometry()
    geo.setAttribute('position', new Float32BufferAttribute(new Float32Array(ringPts), 3))
    group.add(new Line(geo, new LineBasicMaterial({ color, opacity: 0.55, transparent: true })))
  }
}

function addNodeMarker(group: Group, node: EconomicNode): void {
  const color = NODE_COLORS[node.type]
  const [x, y, z] = projectLngLatToCartesian(node.position.lon, node.position.lat, ALT_NODE)
  const marker = new Mesh(
    new SphereGeometry(NODE_RADIUS, 6, 6),
    new MeshBasicMaterial({ color }),
  )
  marker.position.set(x, y, z)
  group.add(marker)
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Append V3 economic city markers and economic nodes to `group`.
 *
 * Designed to be called after `addCountryInfrastructure` on the same group.
 * Only adds geometry; clearing is the caller's responsibility.
 */
export function addEconomicCities(group: Group, cities: EconomicCity[]): void {
  for (const city of cities) {
    addCityMarker(group, city)
  }
}

export function addEconomicNodes(group: Group, nodes: EconomicNode[]): void {
  for (const node of nodes) {
    addNodeMarker(group, node)
  }
}

function resolvedFlowTint(state: FlowState): string {
  if (state === 'inflow') return '#10b981'
  if (state === 'outflow') return '#ef4444'
  return '#94a3b8'
}

function locationRadius(location: FlowLocation): number {
  if (location.priority === 'primary') return 0.010
  if (location.priority === 'secondary') return 0.0075
  return 0.006
}

/**
 * Render normalized country capital + flow locations only from the resolved model.
 */
export function addResolvedCountryFlowNodes(group: Group, model: ResolvedCountryFlowModel): void {
  const [cx, cy, cz] = projectLngLatToCartesian(model.capital.lng, model.capital.lat, cityAltitude(1))
  const capitalCore = new Mesh(
    new SphereGeometry(cityInnerRadius(1), 10, 10),
    new MeshBasicMaterial({ color: '#facc15' }),
  )
  capitalCore.position.set(cx, cy, cz)
  capitalCore.userData.capitalPulseRole = 'core'
  group.add(capitalCore)

  const capitalGlow = new Mesh(
    new SphereGeometry(cityGlowRadius(1), 14, 14),
    new MeshBasicMaterial({
      color: '#facc15',
      transparent: true,
      opacity: 0.35,
      blending: AdditiveBlending,
      depthWrite: false,
    }),
  )
  capitalGlow.position.set(cx, cy, cz)
  capitalGlow.userData.capitalPulseRole = 'glow'
  capitalGlow.userData.baseOpacity = 0.35
  group.add(capitalGlow)

  for (const location of model.renderFlowLocations) {
    const [x, y, z] = projectLngLatToCartesian(location.lng, location.lat, ALT_NODE)
    const baseColor = RESOLVED_NODE_COLORS[location.nodeType] ?? '#cbd5e1'
    const tint = resolvedFlowTint(location.flowState)
    const material = new MeshBasicMaterial({
      color: location.flowState === 'neutral' ? baseColor : tint,
      transparent: true,
      opacity: 0.6 + location.intensity * 0.35,
    })
    const marker = new Mesh(
      new SphereGeometry(locationRadius(location), 8, 8),
      material,
    )
    marker.position.set(x, y, z)
    marker.userData.priority = location.priority
    group.add(marker)
  }
}
