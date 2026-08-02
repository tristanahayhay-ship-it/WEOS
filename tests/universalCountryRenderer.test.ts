/**
 * Universal Country Renderer Tests
 *
 * Validates that country flow rendering uses a universal, capital-centered
 * normalization path for countries with available geo/economic data.
 *
 * Run with:  npx playwright test tests/universalCountryRenderer.test.ts
 */

import { test, expect } from '@playwright/test'
import { generateEconomicLayer } from '../src/world/country/CountryEconomicGenerator'
import type { Country } from '../src/types/country'
import type { CountryEconomicData } from '../src/types/country'
import { buildCountryDashboardMock } from '../src/data/countryDashboardMock'
import { getCapitalCoordinate } from '../src/data/capitalCoordinates'
import { resolveCountryFlowModel } from '../src/world/country/countryFlowModel'
import type { CountryEconomicLayer } from '../src/world/country/types'
import { getAdminData, ADMIN_DATA_COUNTRIES } from '../src/view/adminDivisionMockData'
import { buildApproximateBoundaryRings, estimateDivisionRadius } from '../src/utils/adminBoundaryApproximator'

// ── Test fixtures ─────────────────────────────────────────────────────────────

const JAPAN: Country = {
  numericCode: 392,
  isoCode: 'JP',
  iso3Code: 'JPN',
  name: 'Japan',
  englishName: 'Japan',
  capital: 'Tokyo',
  continent: 'Asia',
  center: [137.2, 36.2],
  area: 377972,
}

const NIGERIA_ECONOMIC: CountryEconomicData = {
  isoCode: 'NG',
  population: 218541212,
  gdpUsd: 477.38,
  gdpPerCapitaUsd: 2184,
  inflationPercent: 24.0,
  interestRatePercent: 18.75,
  currency: 'Nigerian Naira',
  currencyCode: 'NGN',
  timeZones: ['Africa/Lagos'],
}

const NIGERIA: Country = {
  numericCode: 566,
  isoCode: 'NG',
  iso3Code: 'NGA',
  name: 'Nigeria',
  englishName: 'Nigeria',
  capital: 'Abuja',
  continent: 'Africa',
  center: [8.7, 9.8],
  area: 923768,
}

const VIETNAM: Country = {
  numericCode: 704,
  isoCode: 'VN',
  iso3Code: 'VNM',
  name: 'Vietnam',
  englishName: 'Vietnam',
  capital: 'Hanoi',
  continent: 'Asia',
  center: [108.0, 16.2],
  area: 331212,
}

const LUXEMBOURG: Country = {
  numericCode: 442,
  isoCode: 'LU',
  iso3Code: 'LUX',
  name: 'Luxembourg',
  englishName: 'Luxembourg',
  capital: 'Luxembourg',
  continent: 'Europe',
  center: [6.1, 49.8],
  area: 2586,
}

const RUSSIA: Country = {
  numericCode: 643,
  isoCode: 'RU',
  iso3Code: 'RUS',
  name: 'Russia',
  englishName: 'Russia',
  capital: 'Moscow',
  continent: 'Europe',
  center: [105.3, 61.5],
  area: 17098246,
}

const INDIA: Country = {
  numericCode: 356,
  isoCode: 'IN',
  iso3Code: 'IND',
  name: 'India',
  englishName: 'India',
  capital: 'New Delhi',
  continent: 'Asia',
  center: [78.96, 20.59],
  area: 3287263,
}

const AUSTRALIA: Country = {
  numericCode: 36,
  isoCode: 'AU',
  iso3Code: 'AUS',
  name: 'Australia',
  englishName: 'Australia',
  capital: 'Canberra',
  continent: 'Oceania',
  center: [133.77, -25.27],
  area: 7692024,
}

const CANADA: Country = {
  numericCode: 124,
  isoCode: 'CA',
  iso3Code: 'CAN',
  name: 'Canada',
  englishName: 'Canada',
  capital: 'Ottawa',
  continent: 'North America',
  center: [-96.80, 56.13],
  area: 9984670,
}

// ── Shared assertions ─────────────────────────────────────────────────────────

function assertValidLayer(layer: ReturnType<typeof generateEconomicLayer>, isoCode: string) {
  expect(layer.isoCode).toBe(isoCode)
  expect(layer.cities.length).toBeGreaterThan(0)
  expect(layer.nodes.length).toBeGreaterThan(0)

  // Capital must be the first and most important city
  const capital = layer.cities.find((c) => c.type === 'capital')
  expect(capital).toBeDefined()
  expect(capital!.importance).toBe(1.0)

  // Every flow must reference valid city IDs
  const cityIds = new Set(layer.cities.map((c) => c.id))
  for (const flow of layer.flows) {
    expect(cityIds.has(flow.fromCityId), `fromCityId ${flow.fromCityId} should exist`).toBe(true)
    expect(cityIds.has(flow.toCityId),   `toCityId ${flow.toCityId} should exist`).toBe(true)
  }

  // Every node must reference a valid city
  for (const node of layer.nodes) {
    expect(cityIds.has(node.cityId), `node.cityId ${node.cityId} should exist`).toBe(true)
  }

  // All raw flows must have a positive value
  for (const flow of layer.flows) {
    expect(flow.value).toBeGreaterThan(0)
  }
}

// ── Tests ─────────────────────────────────────────────────────────────────────

test.describe('Universal Country Renderer', () => {
  test('returns explicit mock data for Japan (known country)', () => {
    const layer = generateEconomicLayer(JAPAN)
    assertValidLayer(layer, 'JP')

    // Japan mock has exactly 6 cities
    expect(layer.cities.length).toBe(6)

    // Tokyo (capital) must be present
    const tokyo = layer.cities.find((c) => c.name === 'TOKYO')
    expect(tokyo).toBeDefined()
    expect(tokyo!.type).toBe('capital')

    // Flows must have inflow/outflow visual styles
    const outflows = layer.flows.filter((f) => f.visualStyle === 'outflow')
    const inflows  = layer.flows.filter((f) => f.visualStyle === 'inflow')
    expect(outflows.length).toBeGreaterThan(0)
    expect(inflows.length).toBeGreaterThan(0)
  })

  test('builds a capital-rooted fallback layer for countries without flow-location data', () => {
    // Mozambique (MZ) has no entry in economicCities.ts — exercises the universal fallback
    const MOZAMBIQUE: Country = {
      numericCode: 508,
      isoCode: 'MZ',
      iso3Code: 'MOZ',
      name: 'Mozambique',
      englishName: 'Mozambique',
      capital: 'Maputo',
      continent: 'Africa',
      center: [35.0, -18.7],
      area: 801590,
    }
    const layer = generateEconomicLayer(MOZAMBIQUE)
    expect(layer.isoCode).toBe('MZ')
    expect(layer.cities).toHaveLength(1)
    expect(layer.nodes.length).toBeGreaterThanOrEqual(2)
    expect(layer.flows).toEqual([])
    expect(layer.cities[0]?.type).toBe('capital')
    expect(layer.cities[0]?.name).toBe('Maputo')
    expect(layer.nodes.some((node) => node.type === 'central_bank')).toBe(true)
    expect(layer.nodes.some((node) => node.type === 'airport')).toBe(false)
  })

  test('resolves a capital-only country flow model when only capital geo data exists', () => {
    const layer = generateEconomicLayer(LUXEMBOURG)
    const model = resolveCountryFlowModel({ country: LUXEMBOURG, economicLayer: layer })
    expect(model).not.toBeNull()
    expect(model?.capital.name).toBe('Luxembourg')
    expect(model?.flowEdges).toEqual([])
    expect(model?.flowLocations).toEqual([])
  })

  test('generates a valid layer for Russia (very large country)', () => {
    const layer = generateEconomicLayer(RUSSIA)
    assertValidLayer(layer, 'RU')

    // Russia has explicit mock data — 4 cities
    expect(layer.cities.length).toBe(4)
  })

  test('city positions stay within valid coordinate bounds for available datasets', () => {
    for (const country of [JAPAN, RUSSIA, NIGERIA, VIETNAM, LUXEMBOURG]) {
      const layer = generateEconomicLayer(country)
      for (const city of layer.cities) {
        expect(city.position.lon).toBeGreaterThanOrEqual(-180)
        expect(city.position.lon).toBeLessThanOrEqual(180)
        expect(city.position.lat).toBeGreaterThanOrEqual(-85)
        expect(city.position.lat).toBeLessThanOrEqual(85)
      }
    }
  })

  test('country datasets include a central_bank node at the capital', () => {
    const layer = generateEconomicLayer(JAPAN)
    const capitalId = layer.cities.find((c) => c.type === 'capital')?.id
    expect(capitalId).toBeDefined()
    const cbNode = layer.nodes.find((n) => n.type === 'central_bank' && n.cityId === capitalId)
    expect(cbNode).toBeDefined()
  })

  test('fallback countries use factual capital coordinates', () => {
    for (const country of [NIGERIA, VIETNAM, LUXEMBOURG]) {
      const layer = generateEconomicLayer(country)
      const capital = layer.cities.find((city) => city.type === 'capital')
      const expected = getCapitalCoordinate(country.isoCode)

      expect(capital).toBeDefined()
      expect(expected).not.toBeNull()
      expect(capital!.position.lat).toBeCloseTo(expected!.lat, 3)
      expect(capital!.position.lon).toBeCloseTo(expected!.lng, 3)
    }
  })

  test('country datasets include an airport node via normalization', () => {
    const layer = generateEconomicLayer(JAPAN)
    const airport = layer.nodes.find((n) => n.type === 'airport')
    expect(airport).toBeDefined()
  })

  test('dashboard indicator groups are populated for any country', () => {
    const dashboard = buildCountryDashboardMock(NIGERIA, NIGERIA_ECONOMIC)
    expect(dashboard.indicatorGroups.length).toBeGreaterThan(0)

    // Growth & Output group must be present with real GDP data
    const growthGroup = dashboard.indicatorGroups.find((g) => g.id === 'growth_output')
    expect(growthGroup).toBeDefined()
    expect(growthGroup!.metrics.length).toBeGreaterThan(0)

    // Inflation group must be present
    const inflGroup = dashboard.indicatorGroups.find((g) => g.id === 'inflation_prices')
    expect(inflGroup).toBeDefined()
  })

  test('dashboard indicator groups work without economic data (graceful degradation)', () => {
    const dashboard = buildCountryDashboardMock(VIETNAM, null)
    expect(dashboard.indicatorGroups.length).toBeGreaterThan(0)

    // Should still have at least growth, trade, government groups from seeded defaults
    const ids = dashboard.indicatorGroups.map((g) => g.id)
    expect(ids).toContain('growth_output')
    expect(ids).toContain('trade_external')
    expect(ids).toContain('government_finance')
  })

  test('resolved country flow model is capital-centered and directional', () => {
    const layer = generateEconomicLayer(JAPAN)
    const model = resolveCountryFlowModel({ country: JAPAN, economicLayer: layer })
    expect(model).not.toBeNull()
    const resolved = model!
    expect(resolved.capital.priority).toBe('capital')
    expect(resolved.priorityLabelIds[0]).toBe(resolved.capital.id)

    for (const edge of resolved.flowEdges) {
      expect(edge.fromId === resolved.capital.id || edge.toId === resolved.capital.id).toBe(true)
      if (edge.state === 'inflow') {
        expect(edge.toId).toBe(resolved.capital.id)
      }
      if (edge.state === 'outflow') {
        expect(edge.fromId).toBe(resolved.capital.id)
      }
      expect(edge.fromPoint).toHaveLength(2)
      expect(edge.toPoint).toHaveLength(2)
    }
  })

  test('resolver filters out invalid flow-location coordinates', () => {
    const invalidLayer: CountryEconomicLayer = {
      isoCode: 'JP',
      cities: [
        {
          id: 'jp-capital',
          name: 'Tokyo',
          position: { lon: 139.7319925, lat: 35.7090259 },
          type: 'capital',
          importance: 1,
        },
        {
          id: 'jp-invalid-city',
          name: 'Invalid',
          position: { lon: 999, lat: 999 },
          type: 'industrial',
          importance: 0.4,
        },
      ],
      nodes: [
        {
          id: 'jp-invalid-node',
          cityId: 'jp-invalid-city',
          type: 'industrial_hub',
          position: { lon: 999, lat: 999 },
        },
      ],
      flows: [
        {
          id: 'jp-flow-invalid',
          fromCityId: 'jp-capital',
          toCityId: 'jp-invalid-city',
          type: 'trade',
          value: 100,
          visualStyle: 'outflow',
        },
      ],
    }

    const model = resolveCountryFlowModel({ country: JAPAN, economicLayer: invalidLayer })
    expect(model).not.toBeNull()
    expect(model?.flowLocations).toHaveLength(0)
    expect(model?.flowEdges).toHaveLength(0)
  })

  test('multiple countries use the same renderer path and degrade safely', () => {
    const countries = [JAPAN, NIGERIA, VIETNAM, LUXEMBOURG, RUSSIA]
    for (const country of countries) {
      const layer = generateEconomicLayer(country)
      const model = resolveCountryFlowModel({ country, economicLayer: layer })
      expect(layer.cities.length).toBeGreaterThan(0)
      expect(model).not.toBeNull()
    }
  })
})

// ── Division boundary tests ───────────────────────────────────────────────────

test.describe('Admin Division Boundaries', () => {
  test('all admin-data countries have at least one division', () => {
    for (const iso of ADMIN_DATA_COUNTRIES) {
      const data = getAdminData(iso)
      expect(data, `${iso} should have admin data`).not.toBeNull()
      expect(data!.divisions.length, `${iso} should have divisions`).toBeGreaterThan(0)
    }
  })

  test('every division has non-empty boundaryRings', () => {
    for (const iso of ADMIN_DATA_COUNTRIES) {
      const data = getAdminData(iso)!
      for (const div of data.divisions) {
        expect(
          div.boundaryRings,
          `${iso}/${div.name} should have boundaryRings`,
        ).toBeDefined()
        expect(
          div.boundaryRings!.length,
          `${iso}/${div.name} boundaryRings must have at least one ring`,
        ).toBeGreaterThan(0)
        const ring = div.boundaryRings![0]!
        expect(
          ring.length,
          `${iso}/${div.name} outer ring must have at least 4 vertices`,
        ).toBeGreaterThanOrEqual(4)
        // First and last point must be identical (closed ring)
        expect(ring[0]).toEqual(ring[ring.length - 1])
      }
    }
  })

  test('boundary ring vertices are within valid coordinate bounds', () => {
    for (const iso of ADMIN_DATA_COUNTRIES) {
      const data = getAdminData(iso)!
      for (const div of data.divisions) {
        for (const ring of (div.boundaryRings ?? [])) {
          for (const [lon, lat] of ring) {
            expect(lon).toBeGreaterThanOrEqual(-180)
            expect(lon).toBeLessThanOrEqual(180)
            expect(lat).toBeGreaterThanOrEqual(-90)
            expect(lat).toBeLessThanOrEqual(90)
          }
        }
      }
    }
  })

  test('resolveCountryFlowModel returns non-empty divisionGeometry for admin-data countries', () => {
    const countriesWithAdminData: Country[] = [
      JAPAN,
      { numericCode: 840, isoCode: 'US', iso3Code: 'USA', name: 'United States', englishName: 'United States', capital: 'Washington D.C.', continent: 'North America', center: [-98.6, 39.5], area: 9833517 },
      RUSSIA,
      INDIA,
      AUSTRALIA,
      CANADA,
    ]
    for (const country of countriesWithAdminData) {
      const layer    = generateEconomicLayer(country)
      const model    = resolveCountryFlowModel({ country, economicLayer: layer })
      expect(model, `${country.isoCode} should resolve`).not.toBeNull()
      // divisionGeometry is populated when adminData is passed
      const adminData = getAdminData(country.isoCode)
      if (adminData) {
        const model2 = resolveCountryFlowModel({ country, economicLayer: layer, adminData })
        expect(
          model2?.divisionGeometry.length,
          `${country.isoCode} should have divisionGeometry when adminData is provided`,
        ).toBeGreaterThan(0)
      }
    }
  })

  test('approximate boundary ring approximator produces valid rings', () => {
    const testCases: Array<[lon: number, lat: number, radius: number]> = [
      [139.69,  35.69, 1.0],   // Tokyo
      [-77.04,  38.91, 5.0],   // Washington D.C.
      [ 55.75,  37.62, 9.4],   // Moscow region (high northern latitude)
      [-34.60, -58.38, 5.0],   // Buenos Aires (southern hemisphere)
      [  1.35,   3.14, 0.5],   // Near-equatorial (Singapore)
    ]
    for (const [lon, lat, radius] of testCases) {
      const rings = buildApproximateBoundaryRings([lon, lat], radius)
      expect(rings).toHaveLength(1)
      const ring = rings[0]!
      // Default 16 segments + closing vertex = 17 points
      expect(ring).toHaveLength(17)
      expect(ring[0]).toEqual(ring[ring.length - 1])
      for (const [rLon, rLat] of ring) {
        expect(rLon).toBeGreaterThanOrEqual(-180)
        expect(rLon).toBeLessThanOrEqual(180)
        expect(rLat).toBeGreaterThanOrEqual(-90)
        expect(rLat).toBeLessThanOrEqual(90)
      }
    }
  })

  test('estimateDivisionRadius returns reasonable degree values', () => {
    // Japan: 377 972 km² / 10 prefectures → ~1.0°
    expect(estimateDivisionRadius(377972, 10)).toBeCloseTo(0.99, 1)
    // US: 9 833 517 km² / 10 states → ~5.0°
    expect(estimateDivisionRadius(9833517, 10)).toBeCloseTo(5.04, 0)
    // Germany: 357 114 km² / 8 states → ~1.07°
    expect(estimateDivisionRadius(357114, 8)).toBeCloseTo(1.07, 1)
  })
})

// ── Secondary node coverage tests ────────────────────────────────────────────

test.describe('Secondary Node Coverage', () => {
  /** Countries that should have secondary city mock data (multi-city datasets). */
  const MULTI_CITY_ISOS = [
    'US', 'CN', 'DE', 'GB', 'FR', 'JP', 'IN', 'BR', 'RU', 'KR',
    'AU', 'CA', 'IT', 'MX', 'NL', 'ES', 'ZA', 'TR', 'SG', 'SA',
    'NG', 'EG', 'AR', 'PL', 'SE', 'TH', 'VN', 'MY',
  ]

  function makeCountry(isoCode: string): Country {
    return {
      numericCode: 0,
      isoCode,
      iso3Code: isoCode,
      name: isoCode,
      englishName: isoCode,
      capital: isoCode,
      continent: 'Asia',
      center: [0, 0],
      area: 500000,
    }
  }

  test('28 countries have multi-city economic data with at least 2 cities', () => {
    expect(MULTI_CITY_ISOS).toHaveLength(28)
    for (const iso of MULTI_CITY_ISOS) {
      const layer = generateEconomicLayer(makeCountry(iso))
      expect(
        layer.cities.length,
        `${iso} should have at least 2 cities (capital + secondary)`,
      ).toBeGreaterThanOrEqual(2)
    }
  })

  test('every multi-city country has at least one financial or trade node', () => {
    const financialTypes = new Set(['government', 'financial_hub', 'central_bank', 'financial_center'])
    for (const iso of MULTI_CITY_ISOS) {
      const layer = generateEconomicLayer(makeCountry(iso))
      const hasFinancialNode = layer.nodes.some((n) => financialTypes.has(n.type))
      expect(hasFinancialNode, `${iso} should have at least one financial-type node`).toBe(true)
    }
  })

  test('every multi-city country produces non-empty flow edges in the resolved model', () => {
    for (const iso of MULTI_CITY_ISOS) {
      const country = makeCountry(iso)
      const layer   = generateEconomicLayer(country)
      const model   = resolveCountryFlowModel({ country, economicLayer: layer })
      expect(model, `${iso} should resolve`).not.toBeNull()
      expect(
        model!.flowEdges.length,
        `${iso} should have at least one flow edge`,
      ).toBeGreaterThan(0)
    }
  })

  test('capital coordinates are factual for all multi-city countries', () => {
    for (const iso of MULTI_CITY_ISOS) {
      const expected = getCapitalCoordinate(iso)
      expect(expected, `${iso} should have a capital coordinate entry`).not.toBeNull()
      const layer = generateEconomicLayer(makeCountry(iso))
      const capital = layer.cities.find((c) => c.type === 'capital')
      expect(capital, `${iso} should have a capital city`).toBeDefined()
      expect(capital!.position.lat).toBeCloseTo(expected!.lat, 0)
      expect(capital!.position.lon).toBeCloseTo(expected!.lng, 0)
    }
  })
})
