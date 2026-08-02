import type { WorldData, ContinentData, EconomicHub, FlowEdge } from './types'

// ── Global hubs ───────────────────────────────────────────────────────────────

const GLOBAL_HUBS: EconomicHub[] = [
  { id: 'gh-nyc',  name: 'New York',     position: { lon: -74.01, lat: 40.71 }, role: 'financial',   importance: 1.00 },
  { id: 'gh-lon',  name: 'London',       position: { lon: -0.13,  lat: 51.51 }, role: 'financial',   importance: 0.97 },
  { id: 'gh-tok',  name: 'Tokyo',        position: { lon: 139.69, lat: 35.69 }, role: 'financial',   importance: 0.94 },
  { id: 'gh-fra',  name: 'Frankfurt',    position: { lon: 8.68,   lat: 50.11 }, role: 'financial',   importance: 0.88 },
  { id: 'gh-sin',  name: 'Singapore',    position: { lon: 103.82, lat: 1.35  }, role: 'trade',       importance: 0.91 },
  { id: 'gh-dub',  name: 'Dubai',        position: { lon: 55.30,  lat: 25.20 }, role: 'trade',       importance: 0.86 },
  { id: 'gh-hkg',  name: 'Hong Kong',    position: { lon: 114.18, lat: 22.32 }, role: 'financial',   importance: 0.89 },
  { id: 'gh-sha',  name: 'Shanghai',     position: { lon: 121.47, lat: 31.23 }, role: 'trade',       importance: 0.92 },
  { id: 'gh-sao',  name: 'São Paulo',    position: { lon: -46.63, lat: -23.55 }, role: 'financial',  importance: 0.80 },
  { id: 'gh-mum',  name: 'Mumbai',       position: { lon: 72.88,  lat: 19.08 }, role: 'financial',   importance: 0.82 },
  { id: 'gh-syd',  name: 'Sydney',       position: { lon: 151.21, lat: -33.87 }, role: 'financial',  importance: 0.78 },
  { id: 'gh-tor',  name: 'Toronto',      position: { lon: -79.38, lat: 43.65 }, role: 'financial',   importance: 0.76 },
]

// ── Global flows ──────────────────────────────────────────────────────────────

const GLOBAL_FLOWS: FlowEdge[] = [
  { id: 'gf-01', fromId: 'gh-nyc', toId: 'gh-lon', type: 'capital',     value: 1850 },
  { id: 'gf-02', fromId: 'gh-nyc', toId: 'gh-tok', type: 'investment',  value: 1420 },
  { id: 'gf-03', fromId: 'gh-lon', toId: 'gh-fra', type: 'capital',     value: 1100 },
  { id: 'gf-04', fromId: 'gh-sha', toId: 'gh-nyc', type: 'trade',       value: 980  },
  { id: 'gf-05', fromId: 'gh-sin', toId: 'gh-sha', type: 'trade',       value: 760  },
  { id: 'gf-06', fromId: 'gh-tok', toId: 'gh-nyc', type: 'investment',  value: 890  },
  { id: 'gf-07', fromId: 'gh-lon', toId: 'gh-dub', type: 'capital',     value: 640  },
  { id: 'gf-08', fromId: 'gh-dub', toId: 'gh-mum', type: 'trade',       value: 520  },
  { id: 'gf-09', fromId: 'gh-nyc', toId: 'gh-sao', type: 'investment',  value: 430  },
  { id: 'gf-10', fromId: 'gh-syd', toId: 'gh-sin', type: 'trade',       value: 380  },
  { id: 'gf-11', fromId: 'gh-hkg', toId: 'gh-sha', type: 'capital',     value: 810  },
  { id: 'gf-12', fromId: 'gh-fra', toId: 'gh-nyc', type: 'investment',  value: 720  },
]

// ── Continent data ────────────────────────────────────────────────────────────

function makeHubs(continent: string, data: Array<[string, string, number, number, number]>): EconomicHub[] {
  return data.map(([suffix, name, lon, lat, importance]) => ({
    id: `${continent}-hub-${suffix}`,
    name,
    position: { lon, lat },
    role: 'regional' as const,
    importance,
  }))
}

function makeFlows(prefix: string, entries: Array<[string, string, number]>): FlowEdge[] {
  return entries.map(([from, to, value], i) => ({
    id: `${prefix}-flow-${i}`,
    fromId: from,
    toId: to,
    type: 'trade' as const,
    value,
  }))
}

const NORTH_AMERICA: ContinentData = {
  name: 'North America',
  center: [-100, 45],
  hubs: makeHubs('na', [
    ['nyc',    'New York',      -74.01,  40.71, 1.00],
    ['la',     'Los Angeles',  -118.24,  34.05, 0.84],
    ['chi',    'Chicago',       -87.63,  41.88, 0.78],
    ['tor',    'Toronto',       -79.38,  43.65, 0.72],
    ['mex',    'Mexico City',   -99.13,  19.43, 0.70],
  ]),
  flows: makeFlows('na', [
    ['na-hub-nyc', 'na-hub-la',  420],
    ['na-hub-nyc', 'na-hub-tor', 310],
    ['na-hub-la',  'na-hub-mex', 240],
    ['na-hub-chi', 'na-hub-nyc', 280],
  ]),
  gdpUsdT: 30.1,
  population: 595_000_000,
  growthPercent: 2.4,
  riskScore: 22,
  countryRankings: [
    { isoCode: 'US', name: 'United States',  gdpUsdT: 26.9, rank: 1 },
    { isoCode: 'CA', name: 'Canada',         gdpUsdT:  2.1, rank: 2 },
    { isoCode: 'MX', name: 'Mexico',         gdpUsdT:  1.3, rank: 3 },
  ],
}

const SOUTH_AMERICA: ContinentData = {
  name: 'South America',
  center: [-56, -15],
  hubs: makeHubs('sa', [
    ['sao', 'São Paulo',   -46.63, -23.55, 1.00],
    ['bue', 'Buenos Aires', -58.38, -34.61, 0.80],
    ['bog', 'Bogotá',       -74.08,   4.71, 0.68],
    ['lim', 'Lima',         -77.04, -12.05, 0.65],
    ['san', 'Santiago',     -70.67, -33.45, 0.72],
  ]),
  flows: makeFlows('sa', [
    ['sa-hub-sao', 'sa-hub-bue', 320],
    ['sa-hub-sao', 'sa-hub-bog', 190],
    ['sa-hub-san', 'sa-hub-sao', 150],
  ]),
  gdpUsdT: 3.8,
  population: 435_000_000,
  growthPercent: 2.1,
  riskScore: 45,
  countryRankings: [
    { isoCode: 'BR', name: 'Brazil',    gdpUsdT: 2.1, rank: 1 },
    { isoCode: 'AR', name: 'Argentina', gdpUsdT: 0.6, rank: 2 },
    { isoCode: 'CO', name: 'Colombia',  gdpUsdT: 0.4, rank: 3 },
    { isoCode: 'CL', name: 'Chile',     gdpUsdT: 0.3, rank: 4 },
  ],
}

const EUROPE: ContinentData = {
  name: 'Europe',
  center: [15, 52],
  hubs: makeHubs('eu', [
    ['lon', 'London',     -0.13,  51.51, 1.00],
    ['fra', 'Frankfurt',   8.68,  50.11, 0.90],
    ['par', 'Paris',       2.35,  48.85, 0.88],
    ['ams', 'Amsterdam',   4.90,  52.37, 0.82],
    ['zum', 'Zurich',      8.54,  47.38, 0.84],
    ['mad', 'Madrid',     -3.70,  40.42, 0.72],
  ]),
  flows: makeFlows('eu', [
    ['eu-hub-lon', 'eu-hub-fra', 650],
    ['eu-hub-fra', 'eu-hub-par', 480],
    ['eu-hub-ams', 'eu-hub-lon', 420],
    ['eu-hub-zum', 'eu-hub-fra', 380],
    ['eu-hub-mad', 'eu-hub-par', 200],
  ]),
  gdpUsdT: 23.0,
  population: 748_000_000,
  growthPercent: 1.4,
  riskScore: 28,
  countryRankings: [
    { isoCode: 'DE', name: 'Germany',       gdpUsdT: 4.3, rank: 1 },
    { isoCode: 'GB', name: 'United Kingdom', gdpUsdT: 3.1, rank: 2 },
    { isoCode: 'FR', name: 'France',        gdpUsdT: 2.9, rank: 3 },
    { isoCode: 'IT', name: 'Italy',         gdpUsdT: 2.1, rank: 4 },
    { isoCode: 'ES', name: 'Spain',         gdpUsdT: 1.5, rank: 5 },
  ],
}

const AFRICA: ContinentData = {
  name: 'Africa',
  center: [20, 5],
  hubs: makeHubs('af', [
    ['lag', 'Lagos',        3.38,   6.45, 1.00],
    ['joh', 'Johannesburg', 28.04, -26.20, 0.88],
    ['cai', 'Cairo',        31.23,  30.04, 0.84],
    ['nai', 'Nairobi',      36.82,  -1.29, 0.70],
    ['cas', 'Casablanca',   -7.59,  33.59, 0.65],
  ]),
  flows: makeFlows('af', [
    ['af-hub-lag', 'af-hub-joh', 180],
    ['af-hub-cai', 'af-hub-lag', 140],
    ['af-hub-nai', 'af-hub-joh', 110],
  ]),
  gdpUsdT: 3.1,
  population: 1_440_000_000,
  growthPercent: 3.8,
  riskScore: 55,
  countryRankings: [
    { isoCode: 'NG', name: 'Nigeria',      gdpUsdT: 0.5, rank: 1 },
    { isoCode: 'EG', name: 'Egypt',        gdpUsdT: 0.4, rank: 2 },
    { isoCode: 'ZA', name: 'South Africa', gdpUsdT: 0.4, rank: 3 },
    { isoCode: 'ET', name: 'Ethiopia',     gdpUsdT: 0.1, rank: 4 },
  ],
}

const ASIA: ContinentData = {
  name: 'Asia',
  center: [95, 35],
  hubs: makeHubs('as', [
    ['sha', 'Shanghai',   121.47,  31.23, 1.00],
    ['tok', 'Tokyo',      139.69,  35.69, 0.97],
    ['sin', 'Singapore',  103.82,   1.35, 0.93],
    ['hkg', 'Hong Kong',  114.18,  22.32, 0.90],
    ['mum', 'Mumbai',      72.88,  19.08, 0.84],
    ['seo', 'Seoul',      126.98,  37.57, 0.82],
    ['bej', 'Beijing',    116.41,  39.90, 0.94],
  ]),
  flows: makeFlows('as', [
    ['as-hub-sha', 'as-hub-tok', 780],
    ['as-hub-sha', 'as-hub-sin', 620],
    ['as-hub-hkg', 'as-hub-sha', 560],
    ['as-hub-sin', 'as-hub-mum', 340],
    ['as-hub-tok', 'as-hub-seo', 420],
    ['as-hub-bej', 'as-hub-sha', 850],
  ]),
  gdpUsdT: 35.0,
  population: 4_700_000_000,
  growthPercent: 4.2,
  riskScore: 36,
  countryRankings: [
    { isoCode: 'CN', name: 'China',       gdpUsdT: 17.7, rank: 1 },
    { isoCode: 'JP', name: 'Japan',       gdpUsdT:  4.2, rank: 2 },
    { isoCode: 'IN', name: 'India',       gdpUsdT:  3.7, rank: 3 },
    { isoCode: 'KR', name: 'South Korea', gdpUsdT:  1.7, rank: 4 },
    { isoCode: 'ID', name: 'Indonesia',   gdpUsdT:  1.4, rank: 5 },
  ],
}

const OCEANIA: ContinentData = {
  name: 'Oceania',
  center: [135, -25],
  hubs: makeHubs('oc', [
    ['syd', 'Sydney',    151.21, -33.87, 1.00],
    ['mel', 'Melbourne', 144.96, -37.81, 0.90],
    ['auc', 'Auckland',  174.77, -36.87, 0.72],
    ['per', 'Perth',     115.86, -31.95, 0.68],
  ]),
  flows: makeFlows('oc', [
    ['oc-hub-syd', 'oc-hub-mel', 280],
    ['oc-hub-syd', 'oc-hub-auc', 140],
    ['oc-hub-mel', 'oc-hub-per', 110],
  ]),
  gdpUsdT: 2.0,
  population: 45_000_000,
  growthPercent: 2.6,
  riskScore: 18,
  countryRankings: [
    { isoCode: 'AU', name: 'Australia',   gdpUsdT: 1.7, rank: 1 },
    { isoCode: 'NZ', name: 'New Zealand', gdpUsdT: 0.2, rank: 2 },
  ],
}

// ── World macro indicators ────────────────────────────────────────────────────

export const WORLD_MOCK_DATA: WorldData = {
  globalHubs: GLOBAL_HUBS,
  globalFlows: GLOBAL_FLOWS,
  macroMetrics: [
    { id: 'world-gdp',      label: 'World GDP',             value: 105.4, unit: 'T USD',  trend: 'up'   },
    { id: 'world-growth',   label: 'Global GDP Growth',     value: 3.1,   unit: '%',      trend: 'up'   },
    { id: 'world-trade',    label: 'Global Trade Volume',   value: 32.2,  unit: 'T USD',  trend: 'flat' },
    { id: 'world-fdi',      label: 'Global FDI',            value: 1.4,   unit: 'T USD',  trend: 'up'   },
    { id: 'world-debt',     label: 'World Debt / GDP',      value: 238,   unit: '%',      trend: 'up'   },
    { id: 'world-infl',     label: 'Global Avg Inflation',  value: 5.9,   unit: '%',      trend: 'down' },
    { id: 'world-pop',      label: 'World Population',      value: 8.1,   unit: 'B',      trend: 'up'   },
    { id: 'world-poverty',  label: 'Extreme Poverty Rate',  value: 9.1,   unit: '%',      trend: 'down' },
  ],
  continents: {
    'North America': NORTH_AMERICA,
    'South America': SOUTH_AMERICA,
    Europe:          EUROPE,
    Africa:          AFRICA,
    Asia:            ASIA,
    Oceania:         OCEANIA,
  },
}
