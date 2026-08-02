import type { CountryAdminData, AdministrativeDivision, DivisionType } from './types'
import { getAdmin1BoundaryRing } from '../data/admin1BoundaryRings'

// ── Seeded deterministic helpers ──────────────────────────────────────────────

function hashStr(s: string) {
  return Array.from(s).reduce((acc, ch) => acc + ch.charCodeAt(0), 0)
}

function seeded(seed: number, offset: number, min: number, max: number, decimals = 2) {
  const h = seed + offset * 37
  const v = min + ((Math.sin(h) + 1) / 2) * (max - min)
  return Number(v.toFixed(decimals))
}

function divisionOutlook(growth: number): AdministrativeDivision['outlook'] {
  if (growth > 3.5) return 'expanding'
  if (growth < 0.5) return 'contracting'
  return 'stable'
}

// ── Builder ────────────────────────────────────────────────────────────────────

/**
 * Build an AdministrativeDivision entry with seeded economic metrics and a
 * real boundary ring from the Natural Earth admin-1 dataset.
 *
 * @param countryIso   ISO 3166-1 alpha-2 code of the parent country.
 * @param type         Division type (state, province, prefecture, …).
 * @param name         Human-readable division name.
 * @param center       Geographic centroid [longitude, latitude].
 * @param baseSeed     Integer offset for seeded random metrics.
 */
function buildDivision(
  countryIso: string,
  type: DivisionType,
  name: string,
  center: [number, number],
  baseSeed: number,
): AdministrativeDivision {
  const s = hashStr(countryIso + name) + baseSeed
  const growth = seeded(s, 1, -0.8, 7.2)
  const realRing = getAdmin1BoundaryRing(countryIso, name)
  return {
    id: `${countryIso.toLowerCase()}-${name.toLowerCase().replace(/\s+/g, '-')}`,
    countryIsoCode: countryIso,
    name,
    type,
    center,
    gdpUsdB: seeded(s, 2, 5, 1200),
    growthPercent: growth,
    population: Math.round(seeded(s, 3, 500_000, 40_000_000, 0)),
    densityPkm2: seeded(s, 4, 8, 420, 1),
    infrastructureIndex: seeded(s, 5, 30, 95, 1),
    dominantSector: (['Technology', 'Finance', 'Manufacturing', 'Energy', 'Agriculture'] as const)[
      Math.abs(s) % 5
    ] ?? 'Finance',
    netCapitalFlowUsdB: seeded(s, 6, -12, 22),
    outlook: divisionOutlook(growth),
    boundaryRings: realRing !== null ? [realRing] : undefined,
  }
}

// ── Japan — prefectures ────────────────────────────────────────────────────────

const JP_ADMIN: CountryAdminData = {
  countryIsoCode: 'JP',
  divisions: [
    buildDivision('JP', 'prefecture', 'Tokyo',  [139.69,  35.69], 0),
    buildDivision('JP', 'prefecture', 'Osaka',  [135.50,  34.69], 1),
    buildDivision('JP', 'prefecture', 'Kanagawa',  [139.64,  35.45], 2),
    buildDivision('JP', 'prefecture', 'Aichi',  [137.01,  35.18], 3),
    buildDivision('JP', 'prefecture', 'Saitama',  [139.65,  35.86], 4),
    buildDivision('JP', 'prefecture', 'Chiba',  [140.12,  35.61], 5),
    buildDivision('JP', 'prefecture', 'Hyogo',  [134.69,  34.69], 6),
    buildDivision('JP', 'prefecture', 'Hokkaido',  [142.81,  43.06], 7),
    buildDivision('JP', 'prefecture', 'Fukuoka',  [130.42,  33.60], 8),
    buildDivision('JP', 'prefecture', 'Shizuoka',  [138.39,  34.98], 9),
  ],
  intraFlows: [
    { id: 'jp-if-01', fromId: 'jp-tokyo',    toId: 'jp-osaka',    type: 'capital',  value: 320 },
    { id: 'jp-if-02', fromId: 'jp-tokyo',    toId: 'jp-kanagawa', type: 'trade',    value: 210 },
    { id: 'jp-if-03', fromId: 'jp-osaka',    toId: 'jp-aichi',    type: 'supply',   value: 160 },
    { id: 'jp-if-04', fromId: 'jp-aichi',    toId: 'jp-tokyo',    type: 'supply',   value: 190 },
    { id: 'jp-if-05', fromId: 'jp-fukuoka',  toId: 'jp-osaka',    type: 'trade',    value: 100 },
  ],
}

// ── United States — states ─────────────────────────────────────────────────────

const US_ADMIN: CountryAdminData = {
  countryIsoCode: 'US',
  divisions: [
    buildDivision('US', 'state', 'California',  [-119.42,  36.78], 0),
    buildDivision('US', 'state', 'Texas',  [-99.34,  31.47], 1),
    buildDivision('US', 'state', 'New York',  [-74.95,  43.30], 2),
    buildDivision('US', 'state', 'Florida',  [-81.52,  27.99], 3),
    buildDivision('US', 'state', 'Illinois',  [-89.20,  40.35], 4),
    buildDivision('US', 'state', 'Pennsylvania',  [-77.19,  41.20], 5),
    buildDivision('US', 'state', 'Ohio',  [-82.79,  40.42], 6),
    buildDivision('US', 'state', 'Georgia',  [-83.64,  32.16], 7),
    buildDivision('US', 'state', 'Washington',  [-120.74,  47.75], 8),
    buildDivision('US', 'state', 'Massachusetts',  [-71.53,  42.23], 9),
  ],
  intraFlows: [
    { id: 'us-if-01', fromId: 'us-new-york',    toId: 'us-california',  type: 'capital', value: 380 },
    { id: 'us-if-02', fromId: 'us-california',  toId: 'us-washington',  type: 'capital', value: 220 },
    { id: 'us-if-03', fromId: 'us-texas',       toId: 'us-new-york',    type: 'trade',   value: 180 },
    { id: 'us-if-04', fromId: 'us-illinois',    toId: 'us-new-york',    type: 'capital', value: 150 },
    { id: 'us-if-05', fromId: 'us-florida',     toId: 'us-new-york',    type: 'investment', value: 120 },
  ],
}

// ── China — provinces ─────────────────────────────────────────────────────────

const CN_ADMIN: CountryAdminData = {
  countryIsoCode: 'CN',
  divisions: [
    buildDivision('CN', 'province', 'Guangdong',  [113.27,  23.13], 0),
    buildDivision('CN', 'province', 'Jiangsu',  [119.46,  32.97], 1),
    buildDivision('CN', 'province', 'Shandong',  [117.00,  36.66], 2),
    buildDivision('CN', 'province', 'Zhejiang',  [120.15,  29.14], 3),
    buildDivision('CN', 'province', 'Henan',  [113.75,  34.77], 4),
    buildDivision('CN', 'province', 'Sichuan',  [103.00,  30.65], 5),
    buildDivision('CN', 'province', 'Hubei',  [112.30,  31.20], 6),
    buildDivision('CN', 'province', 'Fujian',  [117.98,  26.10], 7),
    buildDivision('CN', 'province', 'Hunan',  [112.98,  27.51], 8),
    buildDivision('CN', 'province', 'Shaanxi',  [108.95,  35.17], 9),
  ],
  intraFlows: [
    { id: 'cn-if-01', fromId: 'cn-guangdong', toId: 'cn-jiangsu',  type: 'trade',   value: 440 },
    { id: 'cn-if-02', fromId: 'cn-jiangsu',  toId: 'cn-zhejiang',  type: 'capital', value: 320 },
    { id: 'cn-if-03', fromId: 'cn-guangdong', toId: 'cn-hubei',    type: 'supply',  value: 210 },
    { id: 'cn-if-04', fromId: 'cn-sichuan',  toId: 'cn-guangdong', type: 'supply',  value: 160 },
    { id: 'cn-if-05', fromId: 'cn-shandong', toId: 'cn-jiangsu',   type: 'trade',   value: 180 },
  ],
}

// ── Germany — states ──────────────────────────────────────────────────────────

const DE_ADMIN: CountryAdminData = {
  countryIsoCode: 'DE',
  divisions: [
    buildDivision('DE', 'state', 'North Rhine-Westphalia',  [7.53, 51.53], 0),
    buildDivision('DE', 'state', 'Bavaria',  [12.00, 48.79], 1),
    buildDivision('DE', 'state', 'Baden-Württemberg',  [9.18, 48.78], 2),
    buildDivision('DE', 'state', 'Hesse',  [9.17, 50.65], 3),
    buildDivision('DE', 'state', 'Lower Saxony',  [9.75, 52.64], 4),
    buildDivision('DE', 'state', 'Berlin',  [13.40, 52.52], 5),
    buildDivision('DE', 'state', 'Saxony',  [13.40, 51.10], 6),
    buildDivision('DE', 'state', 'Hamburg',  [10.00, 53.55], 7),
  ],
  intraFlows: [
    { id: 'de-if-01', fromId: 'de-north-rhine-westphalia', toId: 'de-bavaria',          type: 'trade',   value: 280 },
    { id: 'de-if-02', fromId: 'de-bavaria',                toId: 'de-hesse',            type: 'capital', value: 210 },
    { id: 'de-if-03', fromId: 'de-berlin',                 toId: 'de-saxony',           type: 'investment', value: 140 },
    { id: 'de-if-04', fromId: 'de-hamburg',                toId: 'de-lower-saxony',     type: 'trade',   value: 160 },
    { id: 'de-if-05', fromId: 'de-hesse',                  toId: 'de-north-rhine-westphalia', type: 'capital', value: 180 },
  ],
}

// ── India — states ─────────────────────────────────────────────────────────────

const IN_ADMIN: CountryAdminData = {
  countryIsoCode: 'IN',
  divisions: [
    buildDivision('IN', 'state', 'Maharashtra',  [75.71,  19.75], 0),
    buildDivision('IN', 'state', 'Tamil Nadu',  [78.66,  11.13], 1),
    buildDivision('IN', 'state', 'Karnataka',  [75.72,  15.32], 2),
    buildDivision('IN', 'state', 'Gujarat',  [71.19,  22.26], 3),
    buildDivision('IN', 'state', 'Uttar Pradesh',  [80.91,  26.85], 4),
    buildDivision('IN', 'state', 'Rajasthan',  [74.22,  27.02], 5),
    buildDivision('IN', 'state', 'West Bengal',  [87.85,  22.99], 6),
    buildDivision('IN', 'state', 'Telangana',  [79.02,  17.91], 7),
    buildDivision('IN', 'state', 'Andhra Pradesh',  [79.74,  15.91], 8),
    buildDivision('IN', 'state', 'Madhya Pradesh',  [78.66,  23.47], 9),
  ],
  intraFlows: [
    { id: 'in-if-01', fromId: 'in-maharashtra', toId: 'in-gujarat',       type: 'trade',      value: 220 },
    { id: 'in-if-02', fromId: 'in-maharashtra', toId: 'in-karnataka',     type: 'capital',    value: 180 },
    { id: 'in-if-03', fromId: 'in-tamil-nadu',  toId: 'in-telangana',     type: 'trade',      value: 140 },
    { id: 'in-if-04', fromId: 'in-gujarat',     toId: 'in-uttar-pradesh', type: 'supply',     value: 110 },
    { id: 'in-if-05', fromId: 'in-west-bengal', toId: 'in-maharashtra',   type: 'investment', value: 95  },
  ],
}

// ── Brazil — states ────────────────────────────────────────────────────────────

const BR_ADMIN: CountryAdminData = {
  countryIsoCode: 'BR',
  divisions: [
    buildDivision('BR', 'state', 'São Paulo',  [-48.55, -22.19], 0),
    buildDivision('BR', 'state', 'Rio de Janeiro',  [-43.24, -22.91], 1),
    buildDivision('BR', 'state', 'Minas Gerais',  [-44.38, -18.51], 2),
    buildDivision('BR', 'state', 'Rio Grande do Sul',[-53.08, -30.03], 3),
    buildDivision('BR', 'state', 'Paraná',  [-51.61, -25.25], 4),
    buildDivision('BR', 'state', 'Bahia',  [-41.70, -12.97], 5),
    buildDivision('BR', 'state', 'Pernambuco',  [-37.82,  -8.81], 6),
    buildDivision('BR', 'state', 'Goiás',  [-49.32, -15.83], 7),
  ],
  intraFlows: [
    { id: 'br-if-01', fromId: 'br-são-paulo',      toId: 'br-rio-de-janeiro', type: 'capital', value: 320 },
    { id: 'br-if-02', fromId: 'br-são-paulo',      toId: 'br-minas-gerais',   type: 'trade',   value: 200 },
    { id: 'br-if-03', fromId: 'br-minas-gerais',   toId: 'br-bahia',          type: 'supply',  value: 100 },
    { id: 'br-if-04', fromId: 'br-paraná',         toId: 'br-são-paulo',      type: 'supply',  value: 140 },
    { id: 'br-if-05', fromId: 'br-rio-grande-do-sul', toId: 'br-são-paulo',   type: 'trade',   value: 120 },
  ],
}

// ── Russia — federal subjects ──────────────────────────────────────────────────

const RU_ADMIN: CountryAdminData = {
  countryIsoCode: 'RU',
  divisions: [
    buildDivision('RU', 'region', 'Moscow Oblast',  [37.62, 55.75], 0),
    buildDivision('RU', 'region', 'Saint Petersburg',  [30.32, 59.94], 1),
    buildDivision('RU', 'region', 'Sverdlovsk Oblast',  [60.60, 56.84], 2),
    buildDivision('RU', 'region', 'Novosibirsk Oblast',  [82.92, 54.99], 3),
    buildDivision('RU', 'region', 'Tatarstan',  [50.70, 55.40], 4),
  ],
  intraFlows: [
    { id: 'ru-if-01', fromId: 'ru-moscow-oblast',       toId: 'ru-saint-petersburg',    type: 'capital', value: 280 },
    { id: 'ru-if-02', fromId: 'ru-moscow-oblast',       toId: 'ru-sverdlovsk-oblast',   type: 'trade',   value: 200 },
    { id: 'ru-if-03', fromId: 'ru-sverdlovsk-oblast',   toId: 'ru-novosibirsk-oblast',  type: 'supply',  value: 150 },
    { id: 'ru-if-04', fromId: 'ru-tatarstan',           toId: 'ru-moscow-oblast',       type: 'trade',   value: 110 },
  ],
}

// ── Australia — states ─────────────────────────────────────────────────────────

const AU_ADMIN: CountryAdminData = {
  countryIsoCode: 'AU',
  divisions: [
    buildDivision('AU', 'state', 'New South Wales',  [146.92, -32.16], 0),
    buildDivision('AU', 'state', 'Victoria',  [144.78, -36.85], 1),
    buildDivision('AU', 'state', 'Queensland',  [144.08, -22.58], 2),
    buildDivision('AU', 'state', 'Western Australia',[121.63, -25.33], 3),
    buildDivision('AU', 'state', 'South Australia',  [135.76, -30.00], 4),
    buildDivision('AU', 'state', 'Tasmania',  [146.82, -42.00], 5),
  ],
  intraFlows: [
    { id: 'au-if-01', fromId: 'au-new-south-wales',  toId: 'au-victoria',          type: 'capital', value: 250 },
    { id: 'au-if-02', fromId: 'au-victoria',         toId: 'au-queensland',        type: 'trade',   value: 170 },
    { id: 'au-if-03', fromId: 'au-western-australia', toId: 'au-new-south-wales',  type: 'supply',  value: 140 },
    { id: 'au-if-04', fromId: 'au-queensland',       toId: 'au-new-south-wales',   type: 'trade',   value: 130 },
  ],
}

// ── Canada — provinces ─────────────────────────────────────────────────────────

const CA_ADMIN: CountryAdminData = {
  countryIsoCode: 'CA',
  divisions: [
    buildDivision('CA', 'province', 'Ontario',  [-85.32,  49.25], 0),
    buildDivision('CA', 'province', 'Quebec',  [-72.55,  52.94], 1),
    buildDivision('CA', 'province', 'British Columbia',  [-124.64,  53.73], 2),
    buildDivision('CA', 'province', 'Alberta',  [-113.49,  53.93], 3),
    buildDivision('CA', 'province', 'Manitoba',  [ -98.81,  56.41], 4),
  ],
  intraFlows: [
    { id: 'ca-if-01', fromId: 'ca-ontario',         toId: 'ca-quebec',           type: 'capital', value: 310 },
    { id: 'ca-if-02', fromId: 'ca-ontario',         toId: 'ca-alberta',          type: 'trade',   value: 195 },
    { id: 'ca-if-03', fromId: 'ca-british-columbia', toId: 'ca-alberta',         type: 'supply',  value: 160 },
    { id: 'ca-if-04', fromId: 'ca-alberta',         toId: 'ca-ontario',          type: 'trade',   value: 175 },
  ],
}

// ── Registry ──────────────────────────────────────────────────────────────────

const ADMIN_DATA: Record<string, CountryAdminData> = {
  JP: JP_ADMIN,
  US: US_ADMIN,
  CN: CN_ADMIN,
  DE: DE_ADMIN,
  IN: IN_ADMIN,
  BR: BR_ADMIN,
  RU: RU_ADMIN,
  AU: AU_ADMIN,
  CA: CA_ADMIN,
}

/**
 * Retrieve the admin-division dataset for a country by ISO-2 code.
 * Returns null when no data exists — callers should degrade gracefully.
 */
export function getAdminData(isoCode: string): CountryAdminData | null {
  return ADMIN_DATA[isoCode] ?? null
}

/** ISO codes of all countries that have admin-division data. */
export const ADMIN_DATA_COUNTRIES: readonly string[] = Object.keys(ADMIN_DATA)
