# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: universalCountryRenderer.test.ts >> Admin Division Boundaries >> every division has non-empty boundaryRings
- Location: tests/universalCountryRenderer.test.ts:377:3

# Error details

```
Error: BR/Goiás should have boundaryRings

expect(received).toBeDefined()

Received: undefined
```

# Test source

```ts
  284 |     expect(ids).toContain('growth_output')
  285 |     expect(ids).toContain('trade_external')
  286 |     expect(ids).toContain('government_finance')
  287 |   })
  288 | 
  289 |   test('resolved country flow model is capital-centered and directional', () => {
  290 |     const layer = generateEconomicLayer(JAPAN)
  291 |     const model = resolveCountryFlowModel({ country: JAPAN, economicLayer: layer })
  292 |     expect(model).not.toBeNull()
  293 |     const resolved = model!
  294 |     expect(resolved.capital.priority).toBe('capital')
  295 |     expect(resolved.priorityLabelIds[0]).toBe(resolved.capital.id)
  296 | 
  297 |     for (const edge of resolved.flowEdges) {
  298 |       expect(edge.fromId === resolved.capital.id || edge.toId === resolved.capital.id).toBe(true)
  299 |       if (edge.state === 'inflow') {
  300 |         expect(edge.toId).toBe(resolved.capital.id)
  301 |       }
  302 |       if (edge.state === 'outflow') {
  303 |         expect(edge.fromId).toBe(resolved.capital.id)
  304 |       }
  305 |       expect(edge.fromPoint).toHaveLength(2)
  306 |       expect(edge.toPoint).toHaveLength(2)
  307 |     }
  308 |   })
  309 | 
  310 |   test('resolver filters out invalid flow-location coordinates', () => {
  311 |     const invalidLayer: CountryEconomicLayer = {
  312 |       isoCode: 'JP',
  313 |       cities: [
  314 |         {
  315 |           id: 'jp-capital',
  316 |           name: 'Tokyo',
  317 |           position: { lon: 139.7319925, lat: 35.7090259 },
  318 |           type: 'capital',
  319 |           importance: 1,
  320 |         },
  321 |         {
  322 |           id: 'jp-invalid-city',
  323 |           name: 'Invalid',
  324 |           position: { lon: 999, lat: 999 },
  325 |           type: 'industrial',
  326 |           importance: 0.4,
  327 |         },
  328 |       ],
  329 |       nodes: [
  330 |         {
  331 |           id: 'jp-invalid-node',
  332 |           cityId: 'jp-invalid-city',
  333 |           type: 'industrial_hub',
  334 |           position: { lon: 999, lat: 999 },
  335 |         },
  336 |       ],
  337 |       flows: [
  338 |         {
  339 |           id: 'jp-flow-invalid',
  340 |           fromCityId: 'jp-capital',
  341 |           toCityId: 'jp-invalid-city',
  342 |           type: 'trade',
  343 |           value: 100,
  344 |           visualStyle: 'outflow',
  345 |         },
  346 |       ],
  347 |     }
  348 | 
  349 |     const model = resolveCountryFlowModel({ country: JAPAN, economicLayer: invalidLayer })
  350 |     expect(model).not.toBeNull()
  351 |     expect(model?.flowLocations).toHaveLength(0)
  352 |     expect(model?.flowEdges).toHaveLength(0)
  353 |   })
  354 | 
  355 |   test('multiple countries use the same renderer path and degrade safely', () => {
  356 |     const countries = [JAPAN, NIGERIA, VIETNAM, LUXEMBOURG, RUSSIA]
  357 |     for (const country of countries) {
  358 |       const layer = generateEconomicLayer(country)
  359 |       const model = resolveCountryFlowModel({ country, economicLayer: layer })
  360 |       expect(layer.cities.length).toBeGreaterThan(0)
  361 |       expect(model).not.toBeNull()
  362 |     }
  363 |   })
  364 | })
  365 | 
  366 | // ── Division boundary tests ───────────────────────────────────────────────────
  367 | 
  368 | test.describe('Admin Division Boundaries', () => {
  369 |   test('all admin-data countries have at least one division', () => {
  370 |     for (const iso of ADMIN_DATA_COUNTRIES) {
  371 |       const data = getAdminData(iso)
  372 |       expect(data, `${iso} should have admin data`).not.toBeNull()
  373 |       expect(data!.divisions.length, `${iso} should have divisions`).toBeGreaterThan(0)
  374 |     }
  375 |   })
  376 | 
  377 |   test('every division has non-empty boundaryRings', () => {
  378 |     for (const iso of ADMIN_DATA_COUNTRIES) {
  379 |       const data = getAdminData(iso)!
  380 |       for (const div of data.divisions) {
  381 |         expect(
  382 |           div.boundaryRings,
  383 |           `${iso}/${div.name} should have boundaryRings`,
> 384 |         ).toBeDefined()
      |           ^ Error: BR/Goiás should have boundaryRings
  385 |         expect(
  386 |           div.boundaryRings!.length,
  387 |           `${iso}/${div.name} boundaryRings must have at least one ring`,
  388 |         ).toBeGreaterThan(0)
  389 |         const ring = div.boundaryRings![0]!
  390 |         expect(
  391 |           ring.length,
  392 |           `${iso}/${div.name} outer ring must have at least 4 vertices`,
  393 |         ).toBeGreaterThanOrEqual(4)
  394 |         // First and last point must be identical (closed ring)
  395 |         expect(ring[0]).toEqual(ring[ring.length - 1])
  396 |       }
  397 |     }
  398 |   })
  399 | 
  400 |   test('boundary ring vertices are within valid coordinate bounds', () => {
  401 |     for (const iso of ADMIN_DATA_COUNTRIES) {
  402 |       const data = getAdminData(iso)!
  403 |       for (const div of data.divisions) {
  404 |         for (const ring of (div.boundaryRings ?? [])) {
  405 |           for (const [lon, lat] of ring) {
  406 |             expect(lon).toBeGreaterThanOrEqual(-180)
  407 |             expect(lon).toBeLessThanOrEqual(180)
  408 |             expect(lat).toBeGreaterThanOrEqual(-90)
  409 |             expect(lat).toBeLessThanOrEqual(90)
  410 |           }
  411 |         }
  412 |       }
  413 |     }
  414 |   })
  415 | 
  416 |   test('resolveCountryFlowModel returns non-empty divisionGeometry for admin-data countries', () => {
  417 |     const countriesWithAdminData: Country[] = [
  418 |       JAPAN,
  419 |       { numericCode: 840, isoCode: 'US', iso3Code: 'USA', name: 'United States', englishName: 'United States', capital: 'Washington D.C.', continent: 'North America', center: [-98.6, 39.5], area: 9833517 },
  420 |       RUSSIA,
  421 |       INDIA,
  422 |       AUSTRALIA,
  423 |       CANADA,
  424 |     ]
  425 |     for (const country of countriesWithAdminData) {
  426 |       const layer    = generateEconomicLayer(country)
  427 |       const model    = resolveCountryFlowModel({ country, economicLayer: layer })
  428 |       expect(model, `${country.isoCode} should resolve`).not.toBeNull()
  429 |       // divisionGeometry is populated when adminData is passed
  430 |       const adminData = getAdminData(country.isoCode)
  431 |       if (adminData) {
  432 |         const model2 = resolveCountryFlowModel({ country, economicLayer: layer, adminData })
  433 |         expect(
  434 |           model2?.divisionGeometry.length,
  435 |           `${country.isoCode} should have divisionGeometry when adminData is provided`,
  436 |         ).toBeGreaterThan(0)
  437 |       }
  438 |     }
  439 |   })
  440 | 
  441 |   test('admin-data divisions expose closed real boundary rings', () => {
  442 |     const sampleDivisions: Array<[iso: string, division: string]> = [
  443 |       ['AU', 'New South Wales'],
  444 |       ['BR', 'São Paulo'],
  445 |       ['CA', 'Ontario'],
  446 |       ['CN', 'Guangdong'],
  447 |       ['DE', 'Bavaria'],
  448 |       ['IN', 'Maharashtra'],
  449 |       ['JP', 'Tokyo'],
  450 |       ['US', 'California'],
  451 |     ]
  452 | 
  453 |     for (const [iso, division] of sampleDivisions) {
  454 |       const ring = getAdmin1BoundaryRing(iso, division)
  455 |       expect(ring, `${iso}:${division} should resolve to a real boundary ring`).not.toBeNull()
  456 |       expect(ring!.length, `${iso}:${division} ring should have multiple vertices`).toBeGreaterThan(4)
  457 |       expect(ring![0], `${iso}:${division} ring should be closed`).toEqual(ring![ring!.length - 1])
  458 |       for (const [lon, lat] of ring!) {
  459 |         expect(lon).toBeGreaterThanOrEqual(-180)
  460 |         expect(lon).toBeLessThanOrEqual(180)
  461 |         expect(lat).toBeGreaterThanOrEqual(-90)
  462 |         expect(lat).toBeLessThanOrEqual(90)
  463 |       }
  464 |     }
  465 |   })
  466 | 
  467 |   test('estimateDivisionRadius returns reasonable degree values', () => {
  468 |     // Japan: 377 972 km² / 10 prefectures → ~1.0°
  469 |     expect(estimateDivisionRadius(377972, 10)).toBeCloseTo(0.99, 1)
  470 |     // US: 9 833 517 km² / 10 states → ~5.0°
  471 |     expect(estimateDivisionRadius(9833517, 10)).toBeCloseTo(5.04, 0)
  472 |     // Germany: 357 114 km² / 8 states → ~1.07°
  473 |     expect(estimateDivisionRadius(357114, 8)).toBeCloseTo(1.07, 1)
  474 |   })
  475 | })
  476 | 
  477 | // ── Secondary node coverage tests ────────────────────────────────────────────
  478 | 
  479 | test.describe('Secondary Node Coverage', () => {
  480 |   /** Countries that should have secondary city mock data (multi-city datasets). */
  481 |   const MULTI_CITY_ISOS = [
  482 |     'US', 'CN', 'DE', 'GB', 'FR', 'JP', 'IN', 'BR', 'RU', 'KR',
  483 |     'AU', 'CA', 'IT', 'MX', 'NL', 'ES', 'ZA', 'TR', 'SG', 'SA',
  484 |     'NG', 'EG', 'AR', 'PL', 'SE', 'TH', 'VN', 'MY',
```