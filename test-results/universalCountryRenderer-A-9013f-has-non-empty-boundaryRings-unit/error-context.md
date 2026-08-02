# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: universalCountryRenderer.test.ts >> Admin Division Boundaries >> every division has non-empty boundaryRings
- Location: tests/universalCountryRenderer.test.ts:376:3

# Error details

```
Error: BR/Goiás should have boundaryRings

expect(received).toBeDefined()

Received: undefined
```

# Test source

```ts
  283 |     expect(ids).toContain('growth_output')
  284 |     expect(ids).toContain('trade_external')
  285 |     expect(ids).toContain('government_finance')
  286 |   })
  287 | 
  288 |   test('resolved country flow model is capital-centered and directional', () => {
  289 |     const layer = generateEconomicLayer(JAPAN)
  290 |     const model = resolveCountryFlowModel({ country: JAPAN, economicLayer: layer })
  291 |     expect(model).not.toBeNull()
  292 |     const resolved = model!
  293 |     expect(resolved.capital.priority).toBe('capital')
  294 |     expect(resolved.priorityLabelIds[0]).toBe(resolved.capital.id)
  295 | 
  296 |     for (const edge of resolved.flowEdges) {
  297 |       expect(edge.fromId === resolved.capital.id || edge.toId === resolved.capital.id).toBe(true)
  298 |       if (edge.state === 'inflow') {
  299 |         expect(edge.toId).toBe(resolved.capital.id)
  300 |       }
  301 |       if (edge.state === 'outflow') {
  302 |         expect(edge.fromId).toBe(resolved.capital.id)
  303 |       }
  304 |       expect(edge.fromPoint).toHaveLength(2)
  305 |       expect(edge.toPoint).toHaveLength(2)
  306 |     }
  307 |   })
  308 | 
  309 |   test('resolver filters out invalid flow-location coordinates', () => {
  310 |     const invalidLayer: CountryEconomicLayer = {
  311 |       isoCode: 'JP',
  312 |       cities: [
  313 |         {
  314 |           id: 'jp-capital',
  315 |           name: 'Tokyo',
  316 |           position: { lon: 139.7319925, lat: 35.7090259 },
  317 |           type: 'capital',
  318 |           importance: 1,
  319 |         },
  320 |         {
  321 |           id: 'jp-invalid-city',
  322 |           name: 'Invalid',
  323 |           position: { lon: 999, lat: 999 },
  324 |           type: 'industrial',
  325 |           importance: 0.4,
  326 |         },
  327 |       ],
  328 |       nodes: [
  329 |         {
  330 |           id: 'jp-invalid-node',
  331 |           cityId: 'jp-invalid-city',
  332 |           type: 'industrial_hub',
  333 |           position: { lon: 999, lat: 999 },
  334 |         },
  335 |       ],
  336 |       flows: [
  337 |         {
  338 |           id: 'jp-flow-invalid',
  339 |           fromCityId: 'jp-capital',
  340 |           toCityId: 'jp-invalid-city',
  341 |           type: 'trade',
  342 |           value: 100,
  343 |           visualStyle: 'outflow',
  344 |         },
  345 |       ],
  346 |     }
  347 | 
  348 |     const model = resolveCountryFlowModel({ country: JAPAN, economicLayer: invalidLayer })
  349 |     expect(model).not.toBeNull()
  350 |     expect(model?.flowLocations).toHaveLength(0)
  351 |     expect(model?.flowEdges).toHaveLength(0)
  352 |   })
  353 | 
  354 |   test('multiple countries use the same renderer path and degrade safely', () => {
  355 |     const countries = [JAPAN, NIGERIA, VIETNAM, LUXEMBOURG, RUSSIA]
  356 |     for (const country of countries) {
  357 |       const layer = generateEconomicLayer(country)
  358 |       const model = resolveCountryFlowModel({ country, economicLayer: layer })
  359 |       expect(layer.cities.length).toBeGreaterThan(0)
  360 |       expect(model).not.toBeNull()
  361 |     }
  362 |   })
  363 | })
  364 | 
  365 | // ── Division boundary tests ───────────────────────────────────────────────────
  366 | 
  367 | test.describe('Admin Division Boundaries', () => {
  368 |   test('all admin-data countries have at least one division', () => {
  369 |     for (const iso of ADMIN_DATA_COUNTRIES) {
  370 |       const data = getAdminData(iso)
  371 |       expect(data, `${iso} should have admin data`).not.toBeNull()
  372 |       expect(data!.divisions.length, `${iso} should have divisions`).toBeGreaterThan(0)
  373 |     }
  374 |   })
  375 | 
  376 |   test('every division has non-empty boundaryRings', () => {
  377 |     for (const iso of ADMIN_DATA_COUNTRIES) {
  378 |       const data = getAdminData(iso)!
  379 |       for (const div of data.divisions) {
  380 |         expect(
  381 |           div.boundaryRings,
  382 |           `${iso}/${div.name} should have boundaryRings`,
> 383 |         ).toBeDefined()
      |           ^ Error: BR/Goiás should have boundaryRings
  384 |         expect(
  385 |           div.boundaryRings!.length,
  386 |           `${iso}/${div.name} boundaryRings must have at least one ring`,
  387 |         ).toBeGreaterThan(0)
  388 |         const ring = div.boundaryRings![0]!
  389 |         expect(
  390 |           ring.length,
  391 |           `${iso}/${div.name} outer ring must have at least 4 vertices`,
  392 |         ).toBeGreaterThanOrEqual(4)
  393 |         // First and last point must be identical (closed ring)
  394 |         expect(ring[0]).toEqual(ring[ring.length - 1])
  395 |       }
  396 |     }
  397 |   })
  398 | 
  399 |   test('boundary ring vertices are within valid coordinate bounds', () => {
  400 |     for (const iso of ADMIN_DATA_COUNTRIES) {
  401 |       const data = getAdminData(iso)!
  402 |       for (const div of data.divisions) {
  403 |         for (const ring of (div.boundaryRings ?? [])) {
  404 |           for (const [lon, lat] of ring) {
  405 |             expect(lon).toBeGreaterThanOrEqual(-180)
  406 |             expect(lon).toBeLessThanOrEqual(180)
  407 |             expect(lat).toBeGreaterThanOrEqual(-90)
  408 |             expect(lat).toBeLessThanOrEqual(90)
  409 |           }
  410 |         }
  411 |       }
  412 |     }
  413 |   })
  414 | 
  415 |   test('resolveCountryFlowModel returns non-empty divisionGeometry for admin-data countries', () => {
  416 |     const countriesWithAdminData: Country[] = [
  417 |       JAPAN,
  418 |       { numericCode: 840, isoCode: 'US', iso3Code: 'USA', name: 'United States', englishName: 'United States', capital: 'Washington D.C.', continent: 'North America', center: [-98.6, 39.5], area: 9833517 },
  419 |       RUSSIA,
  420 |       INDIA,
  421 |       AUSTRALIA,
  422 |       CANADA,
  423 |     ]
  424 |     for (const country of countriesWithAdminData) {
  425 |       const layer    = generateEconomicLayer(country)
  426 |       const model    = resolveCountryFlowModel({ country, economicLayer: layer })
  427 |       expect(model, `${country.isoCode} should resolve`).not.toBeNull()
  428 |       // divisionGeometry is populated when adminData is passed
  429 |       const adminData = getAdminData(country.isoCode)
  430 |       if (adminData) {
  431 |         const model2 = resolveCountryFlowModel({ country, economicLayer: layer, adminData })
  432 |         expect(
  433 |           model2?.divisionGeometry.length,
  434 |           `${country.isoCode} should have divisionGeometry when adminData is provided`,
  435 |         ).toBeGreaterThan(0)
  436 |       }
  437 |     }
  438 |   })
  439 | 
  440 |   test('admin-data divisions expose closed real boundary rings', () => {
  441 |     for (const iso of ADMIN_DATA_COUNTRIES) {
  442 |       const data = getAdminData(iso)
  443 |       expect(data, `${iso} should have admin data`).not.toBeNull()
  444 |       for (const division of data!.divisions) {
  445 |         expect(
  446 |           division.boundaryRings?.length ?? 0,
  447 |           `${iso}:${division.name} should have at least one real boundary ring`,
  448 |         ).toBeGreaterThan(0)
  449 |         for (const ring of division.boundaryRings ?? []) {
  450 |           expect(ring.length, `${iso}:${division.name} ring should have multiple vertices`).toBeGreaterThan(4)
  451 |           expect(ring[0], `${iso}:${division.name} ring should be closed`).toEqual(ring[ring.length - 1])
  452 |         }
  453 |       }
  454 |     }
  455 |   })
  456 | 
  457 |   test('estimateDivisionRadius returns reasonable degree values', () => {
  458 |     // Japan: 377 972 km² / 10 prefectures → ~1.0°
  459 |     expect(estimateDivisionRadius(377972, 10)).toBeCloseTo(0.99, 1)
  460 |     // US: 9 833 517 km² / 10 states → ~5.0°
  461 |     expect(estimateDivisionRadius(9833517, 10)).toBeCloseTo(5.04, 0)
  462 |     // Germany: 357 114 km² / 8 states → ~1.07°
  463 |     expect(estimateDivisionRadius(357114, 8)).toBeCloseTo(1.07, 1)
  464 |   })
  465 | })
  466 | 
  467 | // ── Secondary node coverage tests ────────────────────────────────────────────
  468 | 
  469 | test.describe('Secondary Node Coverage', () => {
  470 |   /** Countries that should have secondary city mock data (multi-city datasets). */
  471 |   const MULTI_CITY_ISOS = [
  472 |     'US', 'CN', 'DE', 'GB', 'FR', 'JP', 'IN', 'BR', 'RU', 'KR',
  473 |     'AU', 'CA', 'IT', 'MX', 'NL', 'ES', 'ZA', 'TR', 'SG', 'SA',
  474 |     'NG', 'EG', 'AR', 'PL', 'SE', 'TH', 'VN', 'MY',
  475 |   ]
  476 | 
  477 |   function makeCountry(isoCode: string): Country {
  478 |     return {
  479 |       numericCode: 0,
  480 |       isoCode,
  481 |       iso3Code: isoCode,
  482 |       name: isoCode,
  483 |       englishName: isoCode,
```