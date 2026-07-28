# WEOS Overlay Engine — Phase 4B

## Overview

The Economic Overlay Engine is an **independent visualization layer** built on top of the existing globe without modifying the Globe Engine, Country Layer, or Country Panel.

It allows users to toggle a country-level color overlay driven by economic data from `economicStore` (which is itself populated by the Data Provider Layer introduced in Phase 4A).

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Shell.tsx (layout wrapper)                                  │
│  ┌──────────────────┐  ┌──────────────────────────────────┐  │
│  │  GlobeEngine     │  │  Overlay Layer (Phase 4B)        │  │
│  │  (untouched)     │  │  ├── OverlayCanvas.tsx           │  │
│  └──────────────────┘  │  │    (dots on top of globe)     │  │
│                         │  ├── OverlayPanel.tsx            │  │
│  CountryPanel           │  │    (toggle + metric selector) │  │
│  (untouched)            │  └── OverlayLegend.tsx           │  │
│                         │       (color scale key)          │  │
│                         └──────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                           reads
                             │
              ┌──────────────┴───────────────┐
              │                              │
   ┌──────────▼────────┐         ┌───────────▼──────────┐
   │  overlayStore     │         │  economicStore        │
   │  (active metric,  │         │  (country data map    │
   │   visibility)     │         │   keyed by ISO α-2)   │
   └───────────────────┘         └──────────────────────-┘
              │
              ▼
   ┌────────────────────┐
   │  OVERLAYS registry │
   │  (src/overlays/)   │
   │  ├── gdpOverlay    │
   │  ├── population    │
   │  ├── inflation     │
   │  └── interestRate  │
   └────────────────────┘
              │
              ▼
   ┌────────────────────┐
   │  OverlayEngine     │
   │  (color mapping)   │
   └────────────────────┘
```

### Key design principles

| Principle | How it's applied |
|-----------|-----------------|
| **Independent** | All overlay files live under `src/overlays/` and `src/components/overlay/`. They never import from `GlobeEngine`, `CountryLayer`, or `CountryPanel`. |
| **Data from store only** | Overlays read `useEconomicStore` — they do not make API calls directly. |
| **Resilient** | `OverlayEngine.getColor()` returns a `noData` state instead of throwing when data is null. |
| **Extensible** | Adding a new overlay requires only two steps (see below). |
| **Backward-compatible** | The overlay is **off by default** (`isVisible: false` in `overlayStore`). Phase 4A behavior is fully preserved. |

---

## File Reference

| File | Role |
|------|------|
| `src/overlays/types.ts` | `EconomicOverlay` interface, `OverlayMetric`, `ColorStop`, `OverlayColorResult` |
| `src/overlays/overlayEngine.ts` | Stateless `OverlayEngine` class — maps data values → hex colors |
| `src/overlays/definitions/gdpOverlay.ts` | GDP overlay (domain: 0–20 000 B USD) |
| `src/overlays/definitions/populationOverlay.ts` | Population overlay (domain: 0–1.4 B) |
| `src/overlays/definitions/inflationOverlay.ts` | CPI Inflation overlay (domain: 0–100 %) |
| `src/overlays/definitions/interestRateOverlay.ts` | Policy rate overlay (domain: 0–30 %) |
| `src/overlays/index.ts` | Registry — `OVERLAYS` map + `OVERLAY_LIST` |
| `src/stores/overlayStore.ts` | Zustand store — `isVisible`, `activeMetric` |
| `src/components/overlay/OverlayCanvas.tsx` | HTML5 canvas — renders colored dots above the globe |
| `src/components/overlay/OverlayPanel.tsx` | Floating controls (toggle + metric selector) |
| `src/components/overlay/OverlayLegend.tsx` | Color-scale legend |

---

## How overlay data maps to `economicStore`

Each overlay's `getValue(data: CountryEconomicData)` method picks a single field from the store record:

| Overlay | `economicStore` field |
|---------|----------------------|
| GDP | `gdpUsd` (USD billions) |
| Population | `population` (persons) |
| Inflation | `inflationPercent` (annual %) |
| Interest Rate | `interestRatePercent` (policy %) |

If the field is `null` for a country, the overlay returns `hasData: false` and renders the `noDataColor` (`#1f2937`) instead of a colored dot.

---

## How to add a new overlay

### Step 1 — Create the definition file

```ts
// src/overlays/definitions/myMetricOverlay.ts
import type { EconomicOverlay, ColorStop } from '../types'
import type { CountryEconomicData } from '../../types/country'

const COLOR_SCALE: ColorStop[] = [
  { position: 0, color: '#0f172a', label: 'Low' },
  { position: 1, color: '#f59e0b', label: 'High' },
]

export const myMetricOverlay: EconomicOverlay = {
  id: 'myMetric',        // must be a new OverlayMetric literal
  name: 'My Metric',
  description: 'Description shown in the legend',
  unit: 'unit',
  domain: [0, 100],      // [min, max] for the color scale
  colorScale: COLOR_SCALE,
  noDataColor: '#1f2937',

  getValue(data: CountryEconomicData): number | null {
    return data.someField ?? null
  },

  formatValue(value: number | null): string {
    if (value === null) return 'No Data'
    return `${value.toFixed(2)} unit`
  },
}
```

### Step 2 — Register it

Open `src/overlays/index.ts` and:

1. Import the new overlay.
2. Add it to `OVERLAYS` and `OVERLAY_LIST`.
3. Add `'myMetric'` to the `OverlayMetric` union in `src/overlays/types.ts`.

```ts
// src/overlays/types.ts
export type OverlayMetric = 'gdp' | 'population' | 'inflation' | 'interestRate' | 'myMetric'
```

```ts
// src/overlays/index.ts
import { myMetricOverlay } from './definitions/myMetricOverlay'

export const OVERLAYS: Readonly<Record<OverlayMetric, EconomicOverlay>> = {
  // ... existing entries
  myMetric: myMetricOverlay,
}

export const OVERLAY_LIST: EconomicOverlay[] = [
  // ... existing entries
  myMetricOverlay,
]
```

No other file needs to change — the UI and engine discover overlays via `OVERLAYS` and `OVERLAY_LIST` automatically.

---

## Color scale design

Each overlay declares:

- **`domain: [min, max]`** — the expected value range. Values outside this range are clamped.
- **`colorScale: ColorStop[]`** — an ordered array of `{ position, color, label }` where `position` is a normalised 0–1 value within the domain.

The `OverlayEngine` normalises the raw value into 0–1 and linearly interpolates the hex color between the two nearest stops. This produces smooth gradients across the full range.

---

## Visual overlay (OverlayCanvas)

`OverlayCanvas` renders a transparent HTML5 canvas on top of the Three.js canvas.  For each country in `COUNTRIES` it:

1. Reads the country's geographic centre `[lon, lat]`.
2. Projects it to screen coordinates using an **orthographic approximation** (accurate at the default camera orientation, approximate after user rotation).
3. Draws a small colored dot using the color from `OverlayEngine.getColor()`.

Countries on the back hemisphere (not facing the camera) are skipped automatically.

> **Note:** A pixel-perfect per-country fill would require exposing the Globe Engine's camera and world transforms to the overlay layer — this is the natural next step for a future phase if desired.
