# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: universalCountryRenderer.test.ts >> Admin Division Boundaries >> resolveCountryFlowModel returns non-empty divisionGeometry for admin-data countries
- Location: tests/universalCountryRenderer.test.ts:416:3

# Error details

```
Error: RU should have divisionGeometry when adminData is provided

expect(received).toBeGreaterThan(expected)

Expected: > 0
Received:   0
```

# Test source

```ts
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
  384 |         ).toBeDefined()
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
> 436 |         ).toBeGreaterThan(0)
      |           ^ Error: RU should have divisionGeometry when adminData is provided
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
  485 |   ]
  486 | 
  487 |   function makeCountry(isoCode: string): Country {
  488 |     return {
  489 |       numericCode: 0,
  490 |       isoCode,
  491 |       iso3Code: isoCode,
  492 |       name: isoCode,
  493 |       englishName: isoCode,
  494 |       capital: isoCode,
  495 |       continent: 'Asia',
  496 |       center: [0, 0],
  497 |       area: 500000,
  498 |     }
  499 |   }
  500 | 
  501 |   test('28 countries have multi-city economic data with at least 2 cities', () => {
  502 |     expect(MULTI_CITY_ISOS).toHaveLength(28)
  503 |     for (const iso of MULTI_CITY_ISOS) {
  504 |       const layer = generateEconomicLayer(makeCountry(iso))
  505 |       expect(
  506 |         layer.cities.length,
  507 |         `${iso} should have at least 2 cities (capital + secondary)`,
  508 |       ).toBeGreaterThanOrEqual(2)
  509 |     }
  510 |   })
  511 | 
  512 |   test('every multi-city country has at least one financial or trade node', () => {
  513 |     const financialTypes = new Set(['government', 'financial_hub', 'central_bank', 'financial_center'])
  514 |     for (const iso of MULTI_CITY_ISOS) {
  515 |       const layer = generateEconomicLayer(makeCountry(iso))
  516 |       const hasFinancialNode = layer.nodes.some((n) => financialTypes.has(n.type))
  517 |       expect(hasFinancialNode, `${iso} should have at least one financial-type node`).toBe(true)
  518 |     }
  519 |   })
  520 | 
  521 |   test('every multi-city country produces non-empty flow edges in the resolved model', () => {
  522 |     for (const iso of MULTI_CITY_ISOS) {
  523 |       const country = makeCountry(iso)
  524 |       const layer   = generateEconomicLayer(country)
  525 |       const model   = resolveCountryFlowModel({ country, economicLayer: layer })
  526 |       expect(model, `${iso} should resolve`).not.toBeNull()
  527 |       expect(
  528 |         model!.flowEdges.length,
  529 |         `${iso} should have at least one flow edge`,
  530 |       ).toBeGreaterThan(0)
  531 |     }
  532 |   })
  533 | 
  534 |   test('capital coordinates are factual for all multi-city countries', () => {
  535 |     for (const iso of MULTI_CITY_ISOS) {
  536 |       const expected = getCapitalCoordinate(iso)
```