import type {
  ViewState,
  ActiveScope,
  WorldData,
  ResolvedViewModel,
  ResolvedHub,
  ResolvedFlow,
  ResolvedLabel,
  EconomicHub,
  FlowEdge,
  VisibilityScore,
  DashboardModel,
} from './types'
import type { ZoomLevelId } from '../zoom/types'
import { levelFromCameraDistance } from '../zoom/levels'
import { buildDashboard } from './dashboardComposers'

// ── Level resolution ──────────────────────────────────────────────────────────

/**
 * Derive the active zoom level from a raw camera distance.
 */
export function resolveViewLevel(cameraDistance: number): ZoomLevelId {
  return levelFromCameraDistance(cameraDistance)
}

// ── Scope resolution ──────────────────────────────────────────────────────────

/**
 * Resolve the active geographic scope from a ViewState snapshot.
 *
 * Scope precedence:
 *  level 0 → global
 *  level 1 → continent (or global if none selected)
 *  level 2 → country (or global if none selected)
 *  level 3 → division (or country if no division; or global if no country)
 */
export function resolveActiveScope(viewState: ViewState): ActiveScope {
  const { level, activeContinent, activeCountryIso, activeDivisionId } = viewState

  if (level === 0) return { type: 'global' }

  if (level === 1) {
    return activeContinent
      ? { type: 'continent', continent: activeContinent }
      : { type: 'global' }
  }

  if (level === 2) {
    return activeCountryIso
      ? { type: 'country', isoCode: activeCountryIso }
      : { type: 'global' }
  }

  // level 3
  if (activeCountryIso) {
    return activeDivisionId
      ? { type: 'division', countryIsoCode: activeCountryIso, divisionId: activeDivisionId }
      : { type: 'country', isoCode: activeCountryIso }
  }
  return { type: 'global' }
}

// ── Visibility scoring ────────────────────────────────────────────────────────

/**
 * Importance thresholds per zoom level.
 * Entities with importance below the threshold at the current level
 * receive a visibility score of 0.
 */
const VISIBILITY_THRESHOLDS: Record<ZoomLevelId, number> = {
  0: 0.80, // Global: only major hubs
  1: 0.50, // Continent: regional hubs
  2: 0.20, // Country: most city hubs
  3: 0.00, // Division: all hubs
  4: 0.00,
  5: 0.00,
  6: 0.00,
  7: 0.00,
  8: 0.00,
  9: 0.00,
  10: 0.00,
}

/**
 * Compute a normalised visibility score for an entity at the current zoom level.
 *
 * @param entity  Any object with an optional `importance` in [0, 1].
 * @param viewState  Current view state (level drives the threshold).
 * @returns  VisibilityScore with `score` in [0, 1].
 */
export function scoreVisibility(
  entity: { importance?: number },
  viewState: ViewState,
): VisibilityScore {
  const importance = entity.importance ?? 0.5
  const threshold = VISIBILITY_THRESHOLDS[viewState.level] ?? 0.5

  if (importance < threshold) {
    return {
      score: 0,
      reason: `importance ${importance.toFixed(2)} below threshold ${threshold} at level ${viewState.level}`,
    }
  }

  return { score: Math.max(0, Math.min(1, importance)) }
}

// ── Hub / flow / label resolution ────────────────────────────────────────────

function resolveHubs(hubs: EconomicHub[], viewState: ViewState): ResolvedHub[] {
  return hubs.map((hub) => ({
    ...hub,
    visibility: scoreVisibility(hub, viewState),
  }))
}

function resolveFlows(
  flows: FlowEdge[],
  hubMap: Map<string, EconomicHub>,
  viewState: ViewState,
): ResolvedFlow[] {
  // Normalise value to [0, 1] against a cap of 2 000 USD B for scoring.
  const VALUE_CAP = 2000

  return flows.map((flow) => {
    const from = hubMap.get(flow.fromId)
    const to   = hubMap.get(flow.toId)

    const resolvedFromPoint: [number, number] = flow.fromPoint
      ?? (from ? [from.position.lon, from.position.lat] : [0, 0])
    const resolvedToPoint: [number, number] = flow.toPoint
      ?? (to ? [to.position.lon, to.position.lat] : [0, 0])

    const normImportance = Math.min(flow.value / VALUE_CAP, 1)
    const visibility = scoreVisibility({ importance: normImportance }, viewState)

    return { ...flow, resolvedFromPoint, resolvedToPoint, visibility }
  })
}

function resolveLabels(hubs: ResolvedHub[]): ResolvedLabel[] {
  return hubs
    .filter((hub) => hub.visibility.score > 0)
    .map((hub) => ({
      id: `label-${hub.id}`,
      text: hub.name,
      position: [hub.position.lon, hub.position.lat] as [number, number],
      visibility: hub.visibility,
      scale: 0.65 + 0.35 * hub.importance,
    }))
}

// ── Resolved view model builder ───────────────────────────────────────────────

/**
 * Build the complete render-ready ResolvedViewModel for the current ViewState.
 *
 * The model is data-driven:
 *   level 0 → global hubs & flows from WorldData
 *   level 1 → continent hubs & flows from the active continent
 *   level 2 → no hubs/flows here (handled by countryEconomicStore in the renderer)
 *   level 3 → no hubs/flows here (handled by adminDivisionMockData in the panel)
 *
 * Missing data degrades gracefully: empty arrays, not fabricated geometry.
 */
export function resolveResolvedViewModel(
  viewState: ViewState,
  worldData: WorldData,
): ResolvedViewModel {
  const scope = resolveActiveScope(viewState)

  let hubs: EconomicHub[] = []
  let flows: FlowEdge[] = []

  switch (scope.type) {
    case 'global':
      hubs  = worldData.globalHubs
      flows = worldData.globalFlows
      break

    case 'continent': {
      const continentData = worldData.continents[scope.continent]
      if (continentData) {
        hubs  = continentData.hubs
        flows = continentData.flows
      }
      break
    }

    // country & division: hubs/flows managed by dedicated stores and panels
    case 'country':
    case 'division':
      break
  }

  const hubMap = new Map(hubs.map((h) => [h.id, h]))
  const resolvedHubs   = resolveHubs(hubs, viewState)
  const resolvedFlows  = resolveFlows(flows, hubMap, viewState)
  const resolvedLabels = resolveLabels(resolvedHubs)
  const dashboard: DashboardModel = buildDashboard(viewState, worldData, scope)

  return {
    viewState,
    scope,
    dashboard,
    hubs:   resolvedHubs,
    flows:  resolvedFlows,
    labels: resolvedLabels,
  }
}
