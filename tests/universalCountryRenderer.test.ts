/**
 * Universal Country Renderer Tests
 *
 * Validates that the country economic layer generator produces a valid
 * capital-centred flow network for multiple countries, including countries
 * with explicit mock data and countries that rely on the universal fallback.
 *
 * Run with:  npx playwright test tests/universalCountryRenderer.test.ts
 */

import { test, expect } from '@playwright/test'
import { generateEconomicLayer } from '../src/world/country/CountryEconomicGenerator'
import type { Country } from '../src/types/country'
import type { CountryEconomicData } from '../src/types/country'
import { buildCountryDashboardMock } from '../src/data/countryDashboardMock'

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

// ── Shared assertions ─────────────────────────────────────────────────────────

function assertValidLayer(layer: ReturnType<typeof generateEconomicLayer>, isoCode: string) {
  expect(layer.isoCode).toBe(isoCode)
  expect(layer.cities.length).toBeGreaterThan(0)
  expect(layer.nodes.length).toBeGreaterThan(0)
  expect(layer.flows.length).toBeGreaterThan(0)

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

  // All flows must have a positive value
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

  test('generates a universal layer for Nigeria (no mock data)', () => {
    const layer = generateEconomicLayer(NIGERIA, NIGERIA_ECONOMIC)
    assertValidLayer(layer, 'NG')

    // Capital must be Abuja
    const capital = layer.cities.find((c) => c.type === 'capital')
    expect(capital!.name).toBe('Abuja')

    // All capital→hub flows must be outflow; hub→capital flows must be inflow
    const capitalId = capital!.id
    const outflows = layer.flows.filter((f) => f.fromCityId === capitalId)
    const inflows  = layer.flows.filter((f) => f.toCityId   === capitalId)
    expect(outflows.length).toBeGreaterThan(0)
    expect(inflows.length).toBeGreaterThan(0)
    expect(outflows.every((f) => f.visualStyle === 'outflow')).toBe(true)
    expect(inflows.every((f)  => f.visualStyle === 'inflow')).toBe(true)

    // capitalFlow24H totals must be present and positive
    expect(layer.capitalFlow24H).toBeDefined()
    expect(layer.capitalFlow24H!.inflowUsdB).toBeGreaterThan(0)
    expect(layer.capitalFlow24H!.outflowUsdB).toBeGreaterThan(0)
  })

  test('generates a universal layer for Vietnam (no mock data)', () => {
    const layer = generateEconomicLayer(VIETNAM)
    assertValidLayer(layer, 'VN')

    const capital = layer.cities.find((c) => c.type === 'capital')
    expect(capital!.name).toBe('Hanoi')
  })

  test('generates a valid layer for Luxembourg (micro-state)', () => {
    const layer = generateEconomicLayer(LUXEMBOURG)
    assertValidLayer(layer, 'LU')

    // Micro-state — at least a capital + 2 hubs
    expect(layer.cities.length).toBeGreaterThanOrEqual(3)
  })

  test('generates a valid layer for Russia (very large country)', () => {
    const layer = generateEconomicLayer(RUSSIA)
    assertValidLayer(layer, 'RU')

    // Russia has explicit mock data — 4 cities
    expect(layer.cities.length).toBe(4)
  })

  test('hub positions for universal layer stay within valid coordinate bounds', () => {
    for (const country of [NIGERIA, VIETNAM, LUXEMBOURG]) {
      const layer = generateEconomicLayer(country)
      for (const city of layer.cities) {
        expect(city.position.lon).toBeGreaterThanOrEqual(-180)
        expect(city.position.lon).toBeLessThanOrEqual(180)
        expect(city.position.lat).toBeGreaterThanOrEqual(-85)
        expect(city.position.lat).toBeLessThanOrEqual(85)
      }
    }
  })

  test('universal layer includes a central_bank node at the capital', () => {
    const layer = generateEconomicLayer(NIGERIA)
    const capitalId = layer.cities.find((c) => c.type === 'capital')!.id
    const cbNode = layer.nodes.find((n) => n.type === 'central_bank' && n.cityId === capitalId)
    expect(cbNode).toBeDefined()
  })

  test('universal layer always includes an airport node', () => {
    const layer = generateEconomicLayer(NIGERIA)
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

  test('multiple countries use the same renderer path and produce consistent structure', () => {
    const countries = [JAPAN, NIGERIA, VIETNAM, LUXEMBOURG, RUSSIA]
    for (const country of countries) {
      const layer = generateEconomicLayer(country)
      // Every country produces a capital
      const capital = layer.cities.find((c) => c.type === 'capital')
      expect(capital).toBeDefined()
      // Every country produces flows
      expect(layer.flows.length).toBeGreaterThan(0)
    }
  })
})
