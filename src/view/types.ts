import type { Continent } from '../types/country'
import type { ZoomLevelId } from '../zoom/types'

// ── Geographic primitives ─────────────────────────────────────────────────────

export interface LngLatCoord {
  lon: number
  lat: number
}

// ── Economic Hub ──────────────────────────────────────────────────────────────

export type HubRole =
  | 'capital'
  | 'financial'
  | 'trade'
  | 'industrial'
  | 'logistics'
  | 'technology'
  | 'regional'

export interface EconomicHub {
  id: string
  name: string
  position: LngLatCoord
  role: HubRole
  /** Relative importance in [0, 1] — drives visibility thresholds */
  importance: number
  /** 24-hour volume in USD billions (optional) */
  volumeUsdB?: number
}

// ── Flow Edge ─────────────────────────────────────────────────────────────────

export type FlowEdgeType =
  | 'capital'
  | 'trade'
  | 'supply'
  | 'investment'
  | 'aid'
  | 'energy'

export interface FlowEdge {
  id: string
  fromId: string
  toId: string
  type: FlowEdgeType
  /** Economic magnitude in USD billions */
  value: number
  /** Optional explicit origin [lon, lat] — overrides hub lookup */
  fromPoint?: [number, number]
  /** Optional explicit destination [lon, lat] — overrides hub lookup */
  toPoint?: [number, number]
}

// ── Dashboard model ───────────────────────────────────────────────────────────

export type DashboardSectionType =
  | 'summary_badges'
  | 'macro_indicators'
  | 'capital_flow'
  | 'rankings'
  | 'sectors'
  | 'news'
  | 'risk'
  | 'sparklines'

export interface DashboardMetric {
  label: string
  value: string
  /** Optional CSS color for the value text */
  color?: string
}

export interface DashboardRankEntry {
  rank: number
  name: string
  value: string
  trend?: 'up' | 'flat' | 'down'
}

export interface DashboardNewsItem {
  category: string
  title: string
  source: string
  time: string
}

export interface DashboardSection {
  id: string
  type: DashboardSectionType
  title: string
  /** Generic key/value metrics */
  metrics?: DashboardMetric[]
  /** Ranking table rows */
  rankings?: DashboardRankEntry[]
  /** News items */
  news?: DashboardNewsItem[]
}

export interface DashboardModel {
  /** Which zoom level this dashboard belongs to */
  level: ZoomLevelId
  /** Scope identifier (country ISO, continent name, 'global') */
  scopeId: string
  /** Panel header title */
  title: string
  /** Optional subtitle */
  subtitle?: string
  sections: DashboardSection[]
}

// ── World Data ────────────────────────────────────────────────────────────────

export interface WorldMacroMetric {
  id: string
  label: string
  value: number
  unit: string
  trend?: 'up' | 'flat' | 'down'
}

export interface WorldData {
  /** Top-ranked global economic hubs */
  globalHubs: EconomicHub[]
  /** Major cross-border flows */
  globalFlows: FlowEdge[]
  /** World-scale macro indicators */
  macroMetrics: WorldMacroMetric[]
  /** Continent-level summaries, keyed by continent name */
  continents: Partial<Record<Continent, ContinentData>>
}

// ── Continent Data ────────────────────────────────────────────────────────────

export interface CountryRankEntry {
  isoCode: string
  name: string
  gdpUsdT: number
  rank: number
}

export interface ContinentData {
  name: Continent
  /** Camera-focus center [lon, lat] */
  center: [number, number]
  /** Major regional economic hubs */
  hubs: EconomicHub[]
  /** Regional flows between country hubs */
  flows: FlowEdge[]
  /** Aggregate continent GDP in USD trillions */
  gdpUsdT: number | null
  /** Total population */
  population: number | null
  /** Aggregate GDP growth rate % */
  growthPercent: number | null
  /** Risk score in [0, 100] */
  riskScore: number | null
  /** Country GDP rankings within this continent */
  countryRankings: CountryRankEntry[]
}

// ── Administrative Division ───────────────────────────────────────────────────

export type DivisionType =
  | 'state'
  | 'province'
  | 'prefecture'
  | 'region'
  | 'territory'
  | 'district'

export interface AdministrativeDivision {
  id: string
  /** ISO code of parent country */
  countryIsoCode: string
  name: string
  type: DivisionType
  /** Approximate geographic center [lon, lat] */
  center: [number, number]
  /** GDP in USD billions — null when unavailable */
  gdpUsdB: number | null
  /** GDP growth rate % */
  growthPercent: number | null
  /** Population — null when unavailable */
  population: number | null
  /** Population density (persons per km²) */
  densityPkm2: number | null
  /** Infrastructure quality index in [0, 100] */
  infrastructureIndex: number | null
  /** Name of the dominant economic sector */
  dominantSector: string | null
  /** Net capital flow (positive = inflow) in USD billions */
  netCapitalFlowUsdB: number | null
  /** Regional economic outlook */
  outlook: 'expanding' | 'stable' | 'contracting' | null
}

export interface CountryAdminData {
  countryIsoCode: string
  divisions: AdministrativeDivision[]
  /** Intra-country flows between division centers */
  intraFlows: FlowEdge[]
}

// ── View State ────────────────────────────────────────────────────────────────

/**
 * Snapshot of the viewer's current navigational context.
 * Fully describes what the renderer should show.
 */
export interface ViewState {
  /** Active zoom level (0 = Global, 1 = Continent, 2 = Country, 3 = Division) */
  level: ZoomLevelId
  /** Continent in focus — relevant at levels 1+ */
  activeContinent: Continent | null
  /** Country ISO-2 code in focus — relevant at levels 2+ */
  activeCountryIso: string | null
  /** Administrative division id in focus — relevant at level 3 */
  activeDivisionId: string | null
}

// ── Active Scope (resolved from ViewState) ────────────────────────────────────

export type ActiveScope =
  | { type: 'global' }
  | { type: 'continent'; continent: Continent }
  | { type: 'country'; isoCode: string }
  | { type: 'division'; countryIsoCode: string; divisionId: string }

// ── Visibility Scoring ────────────────────────────────────────────────────────

export interface VisibilityScore {
  /** Normalised score in [0, 1] — 0 = hidden, 1 = fully visible */
  score: number
  /** Optional diagnostic reason for suppression */
  reason?: string
}

// ── Resolved View Model ───────────────────────────────────────────────────────

export interface ResolvedHub extends EconomicHub {
  visibility: VisibilityScore
}

export interface ResolvedFlow extends FlowEdge {
  visibility: VisibilityScore
  /** Resolved origin [lon, lat] (from hub data or explicit fromPoint) */
  resolvedFromPoint: [number, number]
  /** Resolved destination [lon, lat] */
  resolvedToPoint: [number, number]
}

export interface ResolvedLabel {
  id: string
  text: string
  position: [number, number]
  visibility: VisibilityScore
  /** Text scale relative to base font size */
  scale: number
}

/**
 * Fully resolved, render-ready snapshot of the current view level and scope.
 * Consumed by the renderer pipeline — no raw/sparse data leaks through.
 */
export interface ResolvedViewModel {
  viewState: ViewState
  scope: ActiveScope
  dashboard: DashboardModel
  hubs: ResolvedHub[]
  flows: ResolvedFlow[]
  labels: ResolvedLabel[]
}
