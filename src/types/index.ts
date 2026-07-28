export type EntityType =
  | 'continent'
  | 'country'
  | 'province'
  | 'city'
  | 'district'
  | 'institution'
  | 'corporation'
  | 'facility'

export enum ZoomLevel {
  TongTheHeThong = 0,
  VungDiaKinhTe = 1,
  LucDia = 2,
  QuocGia = 3,
  VungLienKet = 4,
  TinhThanh = 5,
  DoThi = 6,
  DinhChe = 7,
  DoanhNghiep = 8,
  CoSo = 9,
  ThoiGianThuc = 10,
}

export type MapMode = '2D' | '3D'
export type TrendDirection = 'up' | 'down' | 'stable'
export type AlertSeverity = 'low' | 'medium' | 'high'
export type FlowDirection = 'inbound' | 'outbound' | 'bidirectional'

export type MetricGroupKey =
  | 'gdp'
  | 'growth'
  | 'inflation'
  | 'labour'
  | 'rates'
  | 'trade'
  | 'capital'
  | 'banking'
  | 'manufacturing'
  | 'services'
  | 'consumer'
  | 'energy'
  | 'logistics'
  | 'fiscal'
  | 'debt'
  | 'innovation'
  | 'digital'
  | 'climate'
  | 'stability'
  | 'sentiment'

export interface Coordinate {
  lat: number
  lon: number
}

export interface MetricPoint {
  label: string
  value: number | string
  unit?: string
  trend: TrendDirection
  change: number
}

export interface MetricGroup {
  key: MetricGroupKey
  title: string
  score: number
  trend: TrendDirection
  summary: string
  metrics: MetricPoint[]
}

export interface EconomicCoreMetrics {
  gdp: number
  gdpGrowth: number
  inflation: number
  unemployment: number
  interestRate: number
  riskIndex: number
  fxReserves: number
  tradeBalance: number
  marketCap: number
  compositeScore: number
}

export interface GeoEntity {
  id: string
  type: EntityType
  name: string
  code: string
  continent: string
  coordinates: Coordinate
  description: string
  economicHealth: number
  population: number
  color: string
  tags: string[]
  coreMetrics: EconomicCoreMetrics
  metricGroups: Record<MetricGroupKey, MetricGroup>
}

export interface CapitalFlow {
  id: string
  from: string
  to: string
  value: number
  direction: FlowDirection
  speed: number
  category: string
  timestamp: string
}

export interface NewsItem {
  id: string
  title: string
  summary: string
  region: string
  impact: AlertSeverity
  timestamp: string
  source: string
}

export interface AIInsight {
  id: string
  title: string
  summary: string
  confidence: number
  signal: TrendDirection
  scope: string
  timestamp: string
}

export interface AlertItem {
  id: string
  title: string
  description: string
  severity: AlertSeverity
  entityCode?: string
  timestamp: string
  acknowledged: boolean
}

export interface MarketIndex {
  id: string
  name: string
  value: number
  change: number
  region: string
}

export interface CalendarEvent {
  id: string
  title: string
  entity: string
  timestamp: string
  importance: AlertSeverity
}

export interface FinancialCenter {
  id: string
  name: string
  countryCode: string
  coordinates: Coordinate
  intensity: number
}

export interface TickerRow {
  symbol: string
  name: string
  last: number
  change: number
  volume: string
}

export interface ForexRow {
  pair: string
  rate: number
  change: number
}

export interface CommodityRow {
  symbol: string
  price: number
  change: number
}

export interface TradeFeedItem {
  id: string
  route: string
  sector: string
  notional: string
  tone: TrendDirection
  timestamp: string
}

export interface OrderBookLevel {
  price: number
  size: number
}
