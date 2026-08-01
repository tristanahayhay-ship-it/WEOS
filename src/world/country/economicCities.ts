import type { EconomicCity, EconomicNode, CityFlow } from './types'

/**
 * Structured mock data for Country View V3.
 *
 * Each entry is keyed by ISO 3166-1 alpha-2 code and contains cities, economic
 * nodes, and capital/goods flows.  Values are approximate and designed to be
 * structurally realistic so they can be replaced by a real data API later.
 *
 * City importance is in [0, 1]; the primate/capital city is always 1.0.
 */

export interface CountryMockData {
  cities: EconomicCity[]
  nodes: EconomicNode[]
  flows: CityFlow[]
}

const DATA: Record<string, CountryMockData> = {

  // ── United States ────────────────────────────────────────────────────────
  US: {
    cities: [
      { id: 'us-dc',  name: 'Washington D.C.', position: { lon: -77.04, lat: 38.91 }, type: 'capital',    importance: 1.0 },
      { id: 'us-nyc', name: 'New York',         position: { lon: -74.01, lat: 40.71 }, type: 'financial',  importance: 0.98 },
      { id: 'us-la',  name: 'Los Angeles',      position: { lon: -118.24, lat: 34.05 }, type: 'port',     importance: 0.82 },
      { id: 'us-chi', name: 'Chicago',          position: { lon: -87.63, lat: 41.88 }, type: 'logistics', importance: 0.78 },
      { id: 'us-sf',  name: 'San Francisco',    position: { lon: -122.42, lat: 37.77 }, type: 'technology', importance: 0.76 },
      { id: 'us-hou', name: 'Houston',          position: { lon: -95.37, lat: 29.76 }, type: 'industrial', importance: 0.70 },
    ],
    nodes: [
      { id: 'us-dc-gov',  cityId: 'us-dc',  type: 'government',   position: { lon: -77.04, lat: 38.91 } },
      { id: 'us-nyc-fin', cityId: 'us-nyc', type: 'financial_hub', position: { lon: -74.00, lat: 40.70 } },
      { id: 'us-nyc-cb',  cityId: 'us-nyc', type: 'central_bank',  position: { lon: -74.01, lat: 40.72 } },
      { id: 'us-la-port', cityId: 'us-la',  type: 'port',          position: { lon: -118.28, lat: 33.75 } },
      { id: 'us-chi-log', cityId: 'us-chi', type: 'logistics_hub', position: { lon: -87.67, lat: 41.87 } },
      { id: 'us-sf-tech', cityId: 'us-sf',  type: 'tech_hub',      position: { lon: -122.40, lat: 37.77 } },
      { id: 'us-hou-ind', cityId: 'us-hou', type: 'industrial_hub', position: { lon: -95.37, lat: 29.76 } },
    ],
    flows: [
      { id: 'us-f1', fromCityId: 'us-dc',  toCityId: 'us-nyc', type: 'capital',   value: 420 },
      { id: 'us-f2', fromCityId: 'us-nyc', toCityId: 'us-la',  type: 'trade',     value: 280 },
      { id: 'us-f3', fromCityId: 'us-nyc', toCityId: 'us-sf',  type: 'capital',   value: 195 },
      { id: 'us-f4', fromCityId: 'us-la',  toCityId: 'us-chi', type: 'logistics', value: 160 },
      { id: 'us-f5', fromCityId: 'us-hou', toCityId: 'us-nyc', type: 'supply',    value: 140 },
      { id: 'us-f6', fromCityId: 'us-sf',  toCityId: 'us-nyc', type: 'capital',   value: 210 },
    ],
  },

  // ── China ─────────────────────────────────────────────────────────────────
  CN: {
    cities: [
      { id: 'cn-bj',  name: 'Beijing',   position: { lon: 116.41, lat: 39.90 }, type: 'capital',    importance: 1.0 },
      { id: 'cn-sh',  name: 'Shanghai',  position: { lon: 121.47, lat: 31.23 }, type: 'financial',  importance: 0.97 },
      { id: 'cn-gz',  name: 'Guangzhou', position: { lon: 113.27, lat: 23.13 }, type: 'port',       importance: 0.80 },
      { id: 'cn-sz',  name: 'Shenzhen',  position: { lon: 114.05, lat: 22.55 }, type: 'technology', importance: 0.82 },
      { id: 'cn-cd',  name: 'Chengdu',   position: { lon: 104.06, lat: 30.65 }, type: 'logistics',  importance: 0.70 },
      { id: 'cn-wh',  name: 'Wuhan',     position: { lon: 114.30, lat: 30.59 }, type: 'industrial', importance: 0.72 },
    ],
    nodes: [
      { id: 'cn-bj-gov',  cityId: 'cn-bj', type: 'government',    position: { lon: 116.41, lat: 39.90 } },
      { id: 'cn-bj-cb',   cityId: 'cn-bj', type: 'central_bank',  position: { lon: 116.40, lat: 39.92 } },
      { id: 'cn-sh-fin',  cityId: 'cn-sh', type: 'financial_hub', position: { lon: 121.47, lat: 31.23 } },
      { id: 'cn-sh-port', cityId: 'cn-sh', type: 'port',          position: { lon: 121.88, lat: 31.03 } },
      { id: 'cn-gz-port', cityId: 'cn-gz', type: 'port',          position: { lon: 113.42, lat: 22.82 } },
      { id: 'cn-sz-tech', cityId: 'cn-sz', type: 'tech_hub',      position: { lon: 114.05, lat: 22.55 } },
      { id: 'cn-wh-ind',  cityId: 'cn-wh', type: 'industrial_hub', position: { lon: 114.30, lat: 30.59 } },
    ],
    flows: [
      { id: 'cn-f1', fromCityId: 'cn-bj', toCityId: 'cn-sh', type: 'capital',   value: 550 },
      { id: 'cn-f2', fromCityId: 'cn-sh', toCityId: 'cn-gz', type: 'trade',     value: 380 },
      { id: 'cn-f3', fromCityId: 'cn-sh', toCityId: 'cn-sz', type: 'capital',   value: 290 },
      { id: 'cn-f4', fromCityId: 'cn-bj', toCityId: 'cn-cd', type: 'logistics', value: 175 },
      { id: 'cn-f5', fromCityId: 'cn-wh', toCityId: 'cn-sh', type: 'supply',    value: 220 },
    ],
  },

  // ── Germany ───────────────────────────────────────────────────────────────
  DE: {
    cities: [
      { id: 'de-ber', name: 'Berlin',    position: { lon: 13.40, lat: 52.52 }, type: 'capital',    importance: 1.0 },
      { id: 'de-ffm', name: 'Frankfurt', position: { lon:  8.68, lat: 50.11 }, type: 'financial',  importance: 0.90 },
      { id: 'de-ham', name: 'Hamburg',   position: { lon:  9.99, lat: 53.55 }, type: 'port',       importance: 0.82 },
      { id: 'de-muc', name: 'Munich',    position: { lon: 11.58, lat: 48.14 }, type: 'industrial', importance: 0.85 },
      { id: 'de-col', name: 'Cologne',   position: { lon:  6.96, lat: 50.94 }, type: 'logistics',  importance: 0.72 },
    ],
    nodes: [
      { id: 'de-ber-gov',  cityId: 'de-ber', type: 'government',    position: { lon: 13.40, lat: 52.52 } },
      { id: 'de-ffm-fin',  cityId: 'de-ffm', type: 'financial_hub', position: { lon:  8.68, lat: 50.11 } },
      { id: 'de-ffm-cb',   cityId: 'de-ffm', type: 'central_bank',  position: { lon:  8.70, lat: 50.12 } },
      { id: 'de-ham-port', cityId: 'de-ham', type: 'port',          position: { lon:  9.97, lat: 53.53 } },
      { id: 'de-muc-ind',  cityId: 'de-muc', type: 'industrial_hub', position: { lon: 11.58, lat: 48.14 } },
    ],
    flows: [
      { id: 'de-f1', fromCityId: 'de-ber', toCityId: 'de-ffm', type: 'capital',   value: 210 },
      { id: 'de-f2', fromCityId: 'de-ffm', toCityId: 'de-ham', type: 'capital',   value: 175 },
      { id: 'de-f3', fromCityId: 'de-muc', toCityId: 'de-ffm', type: 'trade',     value: 160 },
      { id: 'de-f4', fromCityId: 'de-ham', toCityId: 'de-col', type: 'logistics', value: 120 },
    ],
  },

  // ── United Kingdom ────────────────────────────────────────────────────────
  GB: {
    cities: [
      { id: 'gb-lon', name: 'London',     position: { lon: -0.13, lat: 51.51 }, type: 'capital',    importance: 1.0 },
      { id: 'gb-man', name: 'Manchester', position: { lon: -2.24, lat: 53.48 }, type: 'industrial', importance: 0.72 },
      { id: 'gb-bir', name: 'Birmingham', position: { lon: -1.90, lat: 52.48 }, type: 'industrial', importance: 0.68 },
      { id: 'gb-edi', name: 'Edinburgh',  position: { lon: -3.19, lat: 55.95 }, type: 'financial',  importance: 0.65 },
      { id: 'gb-liv', name: 'Liverpool',  position: { lon: -2.98, lat: 53.41 }, type: 'port',       importance: 0.62 },
    ],
    nodes: [
      { id: 'gb-lon-gov',  cityId: 'gb-lon', type: 'government',    position: { lon: -0.13, lat: 51.51 } },
      { id: 'gb-lon-fin',  cityId: 'gb-lon', type: 'financial_hub', position: { lon: -0.09, lat: 51.51 } },
      { id: 'gb-lon-cb',   cityId: 'gb-lon', type: 'central_bank',  position: { lon: -0.09, lat: 51.52 } },
      { id: 'gb-liv-port', cityId: 'gb-liv', type: 'port',          position: { lon: -2.98, lat: 53.41 } },
    ],
    flows: [
      { id: 'gb-f1', fromCityId: 'gb-lon', toCityId: 'gb-man', type: 'trade',     value: 95  },
      { id: 'gb-f2', fromCityId: 'gb-lon', toCityId: 'gb-edi', type: 'capital',   value: 80  },
      { id: 'gb-f3', fromCityId: 'gb-man', toCityId: 'gb-liv', type: 'logistics', value: 70  },
    ],
  },

  // ── France ────────────────────────────────────────────────────────────────
  FR: {
    cities: [
      { id: 'fr-par', name: 'Paris',     position: { lon:  2.35, lat: 48.85 }, type: 'capital',    importance: 1.0 },
      { id: 'fr-lyo', name: 'Lyon',      position: { lon:  4.83, lat: 45.75 }, type: 'industrial', importance: 0.74 },
      { id: 'fr-mar', name: 'Marseille', position: { lon:  5.37, lat: 43.30 }, type: 'port',       importance: 0.72 },
      { id: 'fr-bor', name: 'Bordeaux',  position: { lon: -0.58, lat: 44.84 }, type: 'logistics',  importance: 0.65 },
    ],
    nodes: [
      { id: 'fr-par-gov',  cityId: 'fr-par', type: 'government',    position: { lon:  2.35, lat: 48.85 } },
      { id: 'fr-par-fin',  cityId: 'fr-par', type: 'financial_hub', position: { lon:  2.33, lat: 48.87 } },
      { id: 'fr-mar-port', cityId: 'fr-mar', type: 'port',          position: { lon:  5.37, lat: 43.30 } },
      { id: 'fr-lyo-ind',  cityId: 'fr-lyo', type: 'industrial_hub', position: { lon:  4.83, lat: 45.75 } },
    ],
    flows: [
      { id: 'fr-f1', fromCityId: 'fr-par', toCityId: 'fr-lyo', type: 'trade',     value: 130 },
      { id: 'fr-f2', fromCityId: 'fr-par', toCityId: 'fr-mar', type: 'trade',     value: 110 },
      { id: 'fr-f3', fromCityId: 'fr-lyo', toCityId: 'fr-mar', type: 'logistics', value:  85 },
    ],
  },

  // ── Japan ─────────────────────────────────────────────────────────────────
  JP: {
    cities: [
      { id: 'jp-tok', name: 'Tokyo',    position: { lon: 139.69, lat: 35.69 }, type: 'capital',    importance: 1.0 },
      { id: 'jp-osa', name: 'Osaka',    position: { lon: 135.50, lat: 34.69 }, type: 'industrial', importance: 0.85 },
      { id: 'jp-nag', name: 'Nagoya',   position: { lon: 136.91, lat: 35.18 }, type: 'industrial', importance: 0.78 },
      { id: 'jp-yok', name: 'Yokohama', position: { lon: 139.64, lat: 35.44 }, type: 'port',       importance: 0.72 },
      { id: 'jp-fuk', name: 'Fukuoka',  position: { lon: 130.40, lat: 33.59 }, type: 'logistics',  importance: 0.62 },
    ],
    nodes: [
      { id: 'jp-tok-gov',  cityId: 'jp-tok', type: 'government',    position: { lon: 139.69, lat: 35.69 } },
      { id: 'jp-tok-fin',  cityId: 'jp-tok', type: 'financial_hub', position: { lon: 139.70, lat: 35.68 } },
      { id: 'jp-yok-port', cityId: 'jp-yok', type: 'port',          position: { lon: 139.64, lat: 35.44 } },
      { id: 'jp-nag-ind',  cityId: 'jp-nag', type: 'industrial_hub', position: { lon: 136.91, lat: 35.18 } },
    ],
    flows: [
      { id: 'jp-f1', fromCityId: 'jp-tok', toCityId: 'jp-osa', type: 'trade',     value: 260 },
      { id: 'jp-f2', fromCityId: 'jp-tok', toCityId: 'jp-yok', type: 'logistics', value: 180 },
      { id: 'jp-f3', fromCityId: 'jp-nag', toCityId: 'jp-yok', type: 'supply',    value: 155 },
      { id: 'jp-f4', fromCityId: 'jp-osa', toCityId: 'jp-fuk', type: 'trade',     value:  90 },
    ],
  },

  // ── India ─────────────────────────────────────────────────────────────────
  IN: {
    cities: [
      { id: 'in-del', name: 'New Delhi', position: { lon:  77.21, lat: 28.61 }, type: 'capital',    importance: 1.0 },
      { id: 'in-mum', name: 'Mumbai',    position: { lon:  72.88, lat: 19.07 }, type: 'financial',  importance: 0.95 },
      { id: 'in-ban', name: 'Bangalore', position: { lon:  77.59, lat: 12.97 }, type: 'technology', importance: 0.85 },
      { id: 'in-che', name: 'Chennai',   position: { lon:  80.28, lat: 13.08 }, type: 'port',       importance: 0.74 },
      { id: 'in-kol', name: 'Kolkata',   position: { lon:  88.37, lat: 22.57 }, type: 'port',       importance: 0.70 },
      { id: 'in-hyd', name: 'Hyderabad', position: { lon:  78.47, lat: 17.38 }, type: 'technology', importance: 0.72 },
    ],
    nodes: [
      { id: 'in-del-gov',  cityId: 'in-del', type: 'government',    position: { lon:  77.21, lat: 28.61 } },
      { id: 'in-mum-fin',  cityId: 'in-mum', type: 'financial_hub', position: { lon:  72.88, lat: 19.07 } },
      { id: 'in-mum-port', cityId: 'in-mum', type: 'port',          position: { lon:  72.84, lat: 18.95 } },
      { id: 'in-ban-tech', cityId: 'in-ban', type: 'tech_hub',      position: { lon:  77.59, lat: 12.97 } },
      { id: 'in-kol-port', cityId: 'in-kol', type: 'port',          position: { lon:  88.37, lat: 22.57 } },
    ],
    flows: [
      { id: 'in-f1', fromCityId: 'in-del', toCityId: 'in-mum', type: 'capital',   value: 310 },
      { id: 'in-f2', fromCityId: 'in-mum', toCityId: 'in-ban', type: 'capital',   value: 220 },
      { id: 'in-f3', fromCityId: 'in-mum', toCityId: 'in-che', type: 'trade',     value: 170 },
      { id: 'in-f4', fromCityId: 'in-ban', toCityId: 'in-hyd', type: 'supply',    value: 130 },
    ],
  },

  // ── Brazil ────────────────────────────────────────────────────────────────
  BR: {
    cities: [
      { id: 'br-bsb', name: 'Brasília',         position: { lon: -47.93, lat: -15.78 }, type: 'capital',    importance: 1.0 },
      { id: 'br-sao', name: 'São Paulo',         position: { lon: -46.63, lat: -23.55 }, type: 'financial',  importance: 0.97 },
      { id: 'br-rio', name: 'Rio de Janeiro',    position: { lon: -43.17, lat: -22.91 }, type: 'port',       importance: 0.85 },
      { id: 'br-bho', name: 'Belo Horizonte',    position: { lon: -43.94, lat: -19.92 }, type: 'industrial', importance: 0.70 },
      { id: 'br-man', name: 'Manaus',            position: { lon: -60.02, lat:  -3.10 }, type: 'logistics',  importance: 0.60 },
    ],
    nodes: [
      { id: 'br-bsb-gov',  cityId: 'br-bsb', type: 'government',    position: { lon: -47.93, lat: -15.78 } },
      { id: 'br-sao-fin',  cityId: 'br-sao', type: 'financial_hub', position: { lon: -46.63, lat: -23.55 } },
      { id: 'br-rio-port', cityId: 'br-rio', type: 'port',          position: { lon: -43.17, lat: -22.91 } },
      { id: 'br-bho-ind',  cityId: 'br-bho', type: 'industrial_hub', position: { lon: -43.94, lat: -19.92 } },
    ],
    flows: [
      { id: 'br-f1', fromCityId: 'br-bsb', toCityId: 'br-sao', type: 'capital',   value: 290 },
      { id: 'br-f2', fromCityId: 'br-sao', toCityId: 'br-rio', type: 'trade',     value: 205 },
      { id: 'br-f3', fromCityId: 'br-bho', toCityId: 'br-sao', type: 'supply',    value: 140 },
      { id: 'br-f4', fromCityId: 'br-rio', toCityId: 'br-man', type: 'logistics', value:  90 },
    ],
  },

  // ── Russia ────────────────────────────────────────────────────────────────
  RU: {
    cities: [
      { id: 'ru-mow', name: 'Moscow',          position: { lon:  37.62, lat: 55.75 }, type: 'capital',    importance: 1.0 },
      { id: 'ru-spb', name: 'St. Petersburg',  position: { lon:  30.32, lat: 59.94 }, type: 'port',       importance: 0.82 },
      { id: 'ru-nov', name: 'Novosibirsk',     position: { lon:  82.92, lat: 54.99 }, type: 'industrial', importance: 0.65 },
      { id: 'ru-eka', name: 'Yekaterinburg',   position: { lon:  60.60, lat: 56.84 }, type: 'industrial', importance: 0.62 },
    ],
    nodes: [
      { id: 'ru-mow-gov', cityId: 'ru-mow', type: 'government',    position: { lon:  37.62, lat: 55.75 } },
      { id: 'ru-mow-fin', cityId: 'ru-mow', type: 'financial_hub', position: { lon:  37.63, lat: 55.76 } },
      { id: 'ru-spb-port',cityId: 'ru-spb', type: 'port',          position: { lon:  30.32, lat: 59.94 } },
      { id: 'ru-nov-ind', cityId: 'ru-nov', type: 'industrial_hub', position: { lon:  82.92, lat: 54.99 } },
    ],
    flows: [
      { id: 'ru-f1', fromCityId: 'ru-mow', toCityId: 'ru-spb', type: 'capital',   value: 190 },
      { id: 'ru-f2', fromCityId: 'ru-mow', toCityId: 'ru-eka', type: 'supply',    value: 145 },
      { id: 'ru-f3', fromCityId: 'ru-eka', toCityId: 'ru-nov', type: 'logistics', value: 100 },
    ],
  },

  // ── South Korea ───────────────────────────────────────────────────────────
  KR: {
    cities: [
      { id: 'kr-sel', name: 'Seoul',   position: { lon: 126.98, lat: 37.57 }, type: 'capital',    importance: 1.0 },
      { id: 'kr-bus', name: 'Busan',   position: { lon: 129.07, lat: 35.18 }, type: 'port',       importance: 0.78 },
      { id: 'kr-ich', name: 'Incheon', position: { lon: 126.71, lat: 37.46 }, type: 'logistics',  importance: 0.72 },
      { id: 'kr-uls', name: 'Ulsan',   position: { lon: 129.32, lat: 35.54 }, type: 'industrial', importance: 0.70 },
    ],
    nodes: [
      { id: 'kr-sel-gov',  cityId: 'kr-sel', type: 'government',    position: { lon: 126.98, lat: 37.57 } },
      { id: 'kr-sel-fin',  cityId: 'kr-sel', type: 'financial_hub', position: { lon: 126.97, lat: 37.56 } },
      { id: 'kr-bus-port', cityId: 'kr-bus', type: 'port',          position: { lon: 129.07, lat: 35.18 } },
      { id: 'kr-ich-log',  cityId: 'kr-ich', type: 'logistics_hub', position: { lon: 126.71, lat: 37.46 } },
      { id: 'kr-uls-ind',  cityId: 'kr-uls', type: 'industrial_hub', position: { lon: 129.32, lat: 35.54 } },
    ],
    flows: [
      { id: 'kr-f1', fromCityId: 'kr-sel', toCityId: 'kr-bus', type: 'trade',     value: 175 },
      { id: 'kr-f2', fromCityId: 'kr-sel', toCityId: 'kr-ich', type: 'logistics', value: 145 },
      { id: 'kr-f3', fromCityId: 'kr-uls', toCityId: 'kr-bus', type: 'supply',    value: 120 },
    ],
  },

  // ── Australia ─────────────────────────────────────────────────────────────
  AU: {
    cities: [
      { id: 'au-cbr', name: 'Canberra',  position: { lon: 149.13, lat: -35.28 }, type: 'capital',    importance: 1.0 },
      { id: 'au-syd', name: 'Sydney',    position: { lon: 151.21, lat: -33.87 }, type: 'financial',  importance: 0.95 },
      { id: 'au-mel', name: 'Melbourne', position: { lon: 144.97, lat: -37.81 }, type: 'financial',  importance: 0.90 },
      { id: 'au-bne', name: 'Brisbane',  position: { lon: 153.02, lat: -27.47 }, type: 'logistics',  importance: 0.72 },
      { id: 'au-per', name: 'Perth',     position: { lon: 115.86, lat: -31.95 }, type: 'industrial', importance: 0.68 },
    ],
    nodes: [
      { id: 'au-cbr-gov',  cityId: 'au-cbr', type: 'government',    position: { lon: 149.13, lat: -35.28 } },
      { id: 'au-syd-fin',  cityId: 'au-syd', type: 'financial_hub', position: { lon: 151.21, lat: -33.87 } },
      { id: 'au-syd-port', cityId: 'au-syd', type: 'port',          position: { lon: 151.21, lat: -33.87 } },
      { id: 'au-per-ind',  cityId: 'au-per', type: 'industrial_hub', position: { lon: 115.86, lat: -31.95 } },
    ],
    flows: [
      { id: 'au-f1', fromCityId: 'au-cbr', toCityId: 'au-syd', type: 'capital',   value: 160 },
      { id: 'au-f2', fromCityId: 'au-syd', toCityId: 'au-mel', type: 'trade',     value: 210 },
      { id: 'au-f3', fromCityId: 'au-mel', toCityId: 'au-bne', type: 'logistics', value: 120 },
      { id: 'au-f4', fromCityId: 'au-per', toCityId: 'au-mel', type: 'supply',    value:  90 },
    ],
  },

  // ── Canada ────────────────────────────────────────────────────────────────
  CA: {
    cities: [
      { id: 'ca-ott', name: 'Ottawa',    position: { lon: -75.70, lat: 45.42 }, type: 'capital',    importance: 1.0 },
      { id: 'ca-tor', name: 'Toronto',   position: { lon: -79.38, lat: 43.65 }, type: 'financial',  importance: 0.95 },
      { id: 'ca-van', name: 'Vancouver', position: { lon: -123.12, lat: 49.28 }, type: 'port',      importance: 0.82 },
      { id: 'ca-mtl', name: 'Montréal',  position: { lon: -73.57, lat: 45.50 }, type: 'industrial', importance: 0.80 },
      { id: 'ca-cal', name: 'Calgary',   position: { lon: -114.07, lat: 51.05 }, type: 'logistics', importance: 0.68 },
    ],
    nodes: [
      { id: 'ca-ott-gov',  cityId: 'ca-ott', type: 'government',    position: { lon: -75.70, lat: 45.42 } },
      { id: 'ca-tor-fin',  cityId: 'ca-tor', type: 'financial_hub', position: { lon: -79.38, lat: 43.65 } },
      { id: 'ca-van-port', cityId: 'ca-van', type: 'port',          position: { lon: -123.12, lat: 49.28 } },
      { id: 'ca-mtl-ind',  cityId: 'ca-mtl', type: 'industrial_hub', position: { lon: -73.57, lat: 45.50 } },
    ],
    flows: [
      { id: 'ca-f1', fromCityId: 'ca-ott', toCityId: 'ca-tor', type: 'capital',   value: 185 },
      { id: 'ca-f2', fromCityId: 'ca-tor', toCityId: 'ca-van', type: 'trade',     value: 150 },
      { id: 'ca-f3', fromCityId: 'ca-van', toCityId: 'ca-cal', type: 'logistics', value: 110 },
      { id: 'ca-f4', fromCityId: 'ca-tor', toCityId: 'ca-mtl', type: 'supply',    value: 125 },
    ],
  },

  // ── Italy ─────────────────────────────────────────────────────────────────
  IT: {
    cities: [
      { id: 'it-rom', name: 'Rome',   position: { lon: 12.49, lat: 41.90 }, type: 'capital',    importance: 1.0 },
      { id: 'it-mil', name: 'Milan',  position: { lon:  9.19, lat: 45.46 }, type: 'financial',  importance: 0.93 },
      { id: 'it-nap', name: 'Naples', position: { lon: 14.27, lat: 40.85 }, type: 'port',       importance: 0.70 },
      { id: 'it-tur', name: 'Turin',  position: { lon:  7.68, lat: 45.07 }, type: 'industrial', importance: 0.72 },
    ],
    nodes: [
      { id: 'it-rom-gov',  cityId: 'it-rom', type: 'government',    position: { lon: 12.49, lat: 41.90 } },
      { id: 'it-mil-fin',  cityId: 'it-mil', type: 'financial_hub', position: { lon:  9.19, lat: 45.46 } },
      { id: 'it-nap-port', cityId: 'it-nap', type: 'port',          position: { lon: 14.27, lat: 40.85 } },
      { id: 'it-tur-ind',  cityId: 'it-tur', type: 'industrial_hub', position: { lon:  7.68, lat: 45.07 } },
    ],
    flows: [
      { id: 'it-f1', fromCityId: 'it-rom', toCityId: 'it-mil', type: 'capital', value: 195 },
      { id: 'it-f2', fromCityId: 'it-mil', toCityId: 'it-tur', type: 'trade',   value: 140 },
      { id: 'it-f3', fromCityId: 'it-nap', toCityId: 'it-rom', type: 'supply',  value:  90 },
    ],
  },

  // ── Mexico ────────────────────────────────────────────────────────────────
  MX: {
    cities: [
      { id: 'mx-cdmx', name: 'Mexico City',  position: { lon: -99.13, lat: 19.43 }, type: 'capital',    importance: 1.0 },
      { id: 'mx-gdl',  name: 'Guadalajara',  position: { lon: -103.35, lat: 20.66 }, type: 'industrial', importance: 0.72 },
      { id: 'mx-mty',  name: 'Monterrey',    position: { lon: -100.32, lat: 25.67 }, type: 'industrial', importance: 0.78 },
      { id: 'mx-ver',  name: 'Veracruz',     position: { lon: -96.13, lat: 19.19 }, type: 'port',       importance: 0.65 },
    ],
    nodes: [
      { id: 'mx-cdmx-gov',  cityId: 'mx-cdmx', type: 'government',    position: { lon: -99.13, lat: 19.43 } },
      { id: 'mx-cdmx-fin',  cityId: 'mx-cdmx', type: 'financial_hub', position: { lon: -99.17, lat: 19.42 } },
      { id: 'mx-mty-ind',   cityId: 'mx-mty',  type: 'industrial_hub', position: { lon: -100.32, lat: 25.67 } },
      { id: 'mx-ver-port',  cityId: 'mx-ver',  type: 'port',           position: { lon: -96.13, lat: 19.19 } },
    ],
    flows: [
      { id: 'mx-f1', fromCityId: 'mx-cdmx', toCityId: 'mx-mty', type: 'capital',   value: 150 },
      { id: 'mx-f2', fromCityId: 'mx-mty',  toCityId: 'mx-gdl', type: 'supply',    value: 105 },
      { id: 'mx-f3', fromCityId: 'mx-ver',  toCityId: 'mx-cdmx', type: 'trade',    value:  90 },
    ],
  },

  // ── Netherlands ───────────────────────────────────────────────────────────
  NL: {
    cities: [
      { id: 'nl-ams', name: 'Amsterdam', position: { lon:  4.90, lat: 52.37 }, type: 'capital',    importance: 1.0 },
      { id: 'nl-rot', name: 'Rotterdam', position: { lon:  4.48, lat: 51.92 }, type: 'port',       importance: 0.90 },
      { id: 'nl-hag', name: 'The Hague', position: { lon:  4.30, lat: 52.08 }, type: 'logistics',  importance: 0.68 },
      { id: 'nl-ein', name: 'Eindhoven', position: { lon:  5.48, lat: 51.44 }, type: 'technology', importance: 0.72 },
    ],
    nodes: [
      { id: 'nl-ams-gov',  cityId: 'nl-ams', type: 'government',    position: { lon:  4.90, lat: 52.37 } },
      { id: 'nl-ams-fin',  cityId: 'nl-ams', type: 'financial_hub', position: { lon:  4.90, lat: 52.37 } },
      { id: 'nl-rot-port', cityId: 'nl-rot', type: 'port',          position: { lon:  4.48, lat: 51.92 } },
      { id: 'nl-ein-tech', cityId: 'nl-ein', type: 'tech_hub',      position: { lon:  5.48, lat: 51.44 } },
    ],
    flows: [
      { id: 'nl-f1', fromCityId: 'nl-ams', toCityId: 'nl-rot', type: 'capital',   value: 140 },
      { id: 'nl-f2', fromCityId: 'nl-rot', toCityId: 'nl-ein', type: 'logistics', value: 100 },
      { id: 'nl-f3', fromCityId: 'nl-ein', toCityId: 'nl-ams', type: 'trade',     value:  80 },
    ],
  },

  // ── Spain ─────────────────────────────────────────────────────────────────
  ES: {
    cities: [
      { id: 'es-mad', name: 'Madrid',    position: { lon: -3.70, lat: 40.42 }, type: 'capital',    importance: 1.0 },
      { id: 'es-bcn', name: 'Barcelona', position: { lon:  2.16, lat: 41.39 }, type: 'port',       importance: 0.88 },
      { id: 'es-val', name: 'Valencia',  position: { lon: -0.38, lat: 39.47 }, type: 'port',       importance: 0.70 },
      { id: 'es-sev', name: 'Seville',   position: { lon: -5.98, lat: 37.39 }, type: 'logistics',  importance: 0.65 },
    ],
    nodes: [
      { id: 'es-mad-gov',  cityId: 'es-mad', type: 'government',    position: { lon: -3.70, lat: 40.42 } },
      { id: 'es-mad-fin',  cityId: 'es-mad', type: 'financial_hub', position: { lon: -3.69, lat: 40.42 } },
      { id: 'es-bcn-port', cityId: 'es-bcn', type: 'port',          position: { lon:  2.16, lat: 41.39 } },
      { id: 'es-val-port', cityId: 'es-val', type: 'port',          position: { lon: -0.38, lat: 39.47 } },
    ],
    flows: [
      { id: 'es-f1', fromCityId: 'es-mad', toCityId: 'es-bcn', type: 'trade',     value: 165 },
      { id: 'es-f2', fromCityId: 'es-bcn', toCityId: 'es-val', type: 'logistics', value: 110 },
      { id: 'es-f3', fromCityId: 'es-mad', toCityId: 'es-sev', type: 'capital',   value:  85 },
    ],
  },

  // ── South Africa ──────────────────────────────────────────────────────────
  ZA: {
    cities: [
      { id: 'za-pre', name: 'Pretoria',      position: { lon: 28.19, lat: -25.75 }, type: 'capital',    importance: 1.0 },
      { id: 'za-jnb', name: 'Johannesburg',  position: { lon: 28.05, lat: -26.20 }, type: 'financial',  importance: 0.95 },
      { id: 'za-cpt', name: 'Cape Town',     position: { lon: 18.42, lat: -33.93 }, type: 'port',       importance: 0.80 },
      { id: 'za-dur', name: 'Durban',        position: { lon: 31.03, lat: -29.86 }, type: 'port',       importance: 0.72 },
    ],
    nodes: [
      { id: 'za-pre-gov',  cityId: 'za-pre', type: 'government',    position: { lon: 28.19, lat: -25.75 } },
      { id: 'za-jnb-fin',  cityId: 'za-jnb', type: 'financial_hub', position: { lon: 28.05, lat: -26.20 } },
      { id: 'za-cpt-port', cityId: 'za-cpt', type: 'port',          position: { lon: 18.42, lat: -33.93 } },
      { id: 'za-dur-port', cityId: 'za-dur', type: 'port',          position: { lon: 31.03, lat: -29.86 } },
    ],
    flows: [
      { id: 'za-f1', fromCityId: 'za-pre', toCityId: 'za-jnb', type: 'capital', value: 120 },
      { id: 'za-f2', fromCityId: 'za-jnb', toCityId: 'za-cpt', type: 'trade',   value:  95 },
      { id: 'za-f3', fromCityId: 'za-dur', toCityId: 'za-jnb', type: 'supply',  value:  80 },
    ],
  },

  // ── Turkey ────────────────────────────────────────────────────────────────
  TR: {
    cities: [
      { id: 'tr-ank', name: 'Ankara',   position: { lon: 32.87, lat: 39.93 }, type: 'capital',    importance: 1.0 },
      { id: 'tr-ist', name: 'Istanbul', position: { lon: 29.01, lat: 41.01 }, type: 'financial',  importance: 0.97 },
      { id: 'tr-izm', name: 'İzmir',    position: { lon: 27.14, lat: 38.42 }, type: 'port',       importance: 0.75 },
      { id: 'tr-bur', name: 'Bursa',    position: { lon: 29.06, lat: 40.20 }, type: 'industrial', importance: 0.68 },
    ],
    nodes: [
      { id: 'tr-ank-gov',  cityId: 'tr-ank', type: 'government',    position: { lon: 32.87, lat: 39.93 } },
      { id: 'tr-ist-fin',  cityId: 'tr-ist', type: 'financial_hub', position: { lon: 29.01, lat: 41.01 } },
      { id: 'tr-izm-port', cityId: 'tr-izm', type: 'port',          position: { lon: 27.14, lat: 38.42 } },
      { id: 'tr-bur-ind',  cityId: 'tr-bur', type: 'industrial_hub', position: { lon: 29.06, lat: 40.20 } },
    ],
    flows: [
      { id: 'tr-f1', fromCityId: 'tr-ank', toCityId: 'tr-ist', type: 'capital', value: 180 },
      { id: 'tr-f2', fromCityId: 'tr-ist', toCityId: 'tr-izm', type: 'trade',   value: 135 },
      { id: 'tr-f3', fromCityId: 'tr-bur', toCityId: 'tr-ist', type: 'supply',  value:  95 },
    ],
  },

  // ── Singapore ─────────────────────────────────────────────────────────────
  SG: {
    cities: [
      { id: 'sg-sin', name: 'Singapore', position: { lon: 103.82, lat: 1.35 }, type: 'capital',    importance: 1.0 },
      { id: 'sg-jur', name: 'Jurong',    position: { lon: 103.71, lat: 1.34 }, type: 'industrial', importance: 0.75 },
      { id: 'sg-cbd', name: 'CBD',       position: { lon: 103.85, lat: 1.28 }, type: 'financial',  importance: 0.90 },
      { id: 'sg-psi', name: 'Pasir Panjang', position: { lon: 103.79, lat: 1.28 }, type: 'port',  importance: 0.85 },
    ],
    nodes: [
      { id: 'sg-sin-gov',  cityId: 'sg-sin', type: 'government',    position: { lon: 103.82, lat: 1.35 } },
      { id: 'sg-cbd-fin',  cityId: 'sg-cbd', type: 'financial_hub', position: { lon: 103.85, lat: 1.28 } },
      { id: 'sg-psi-port', cityId: 'sg-psi', type: 'port',          position: { lon: 103.79, lat: 1.28 } },
      { id: 'sg-jur-ind',  cityId: 'sg-jur', type: 'industrial_hub', position: { lon: 103.71, lat: 1.34 } },
    ],
    flows: [
      { id: 'sg-f1', fromCityId: 'sg-sin', toCityId: 'sg-cbd', type: 'capital',   value: 240 },
      { id: 'sg-f2', fromCityId: 'sg-psi', toCityId: 'sg-jur', type: 'logistics', value: 190 },
      { id: 'sg-f3', fromCityId: 'sg-cbd', toCityId: 'sg-psi', type: 'trade',     value: 200 },
    ],
  },

  // ── Saudi Arabia ──────────────────────────────────────────────────────────
  SA: {
    cities: [
      { id: 'sa-riy', name: 'Riyadh',  position: { lon: 46.68, lat: 24.69 }, type: 'capital',    importance: 1.0 },
      { id: 'sa-jed', name: 'Jeddah',  position: { lon: 39.19, lat: 21.49 }, type: 'port',       importance: 0.85 },
      { id: 'sa-dam', name: 'Dammam',  position: { lon: 50.10, lat: 26.43 }, type: 'port',       importance: 0.74 },
      { id: 'sa-kho', name: 'Khobar',  position: { lon: 50.20, lat: 26.28 }, type: 'industrial', importance: 0.65 },
    ],
    nodes: [
      { id: 'sa-riy-gov',  cityId: 'sa-riy', type: 'government',    position: { lon: 46.68, lat: 24.69 } },
      { id: 'sa-riy-fin',  cityId: 'sa-riy', type: 'financial_hub', position: { lon: 46.72, lat: 24.68 } },
      { id: 'sa-jed-port', cityId: 'sa-jed', type: 'port',          position: { lon: 39.19, lat: 21.49 } },
      { id: 'sa-dam-port', cityId: 'sa-dam', type: 'port',          position: { lon: 50.10, lat: 26.43 } },
    ],
    flows: [
      { id: 'sa-f1', fromCityId: 'sa-riy', toCityId: 'sa-jed', type: 'capital', value: 200 },
      { id: 'sa-f2', fromCityId: 'sa-dam', toCityId: 'sa-riy', type: 'supply',  value: 155 },
      { id: 'sa-f3', fromCityId: 'sa-jed', toCityId: 'sa-dam', type: 'trade',   value: 110 },
    ],
  },
}

/**
 * Retrieve structured mock city/node/flow data for a given ISO 3166-1 alpha-2 code.
 * Returns `null` when no mock data is available (use the procedural fallback instead).
 */
export function getMockEconomicData(isoCode: string): CountryMockData | null {
  return DATA[isoCode] ?? null
}
