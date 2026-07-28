# WEOS — World Economic Operating System

A production-grade geospatial analytics platform for visualizing global economic flows, trade networks, and macroeconomic data.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI Framework | React 19 + TypeScript |
| Build Tool | Vite 6 |
| Styling | Tailwind CSS v4 |
| 2D Maps | MapLibre GL |
| 3D Visualization | deck.gl |
| State Management | Zustand |
| Charts | ECharts |
| Linting | oxlint |
| Deployment | GitHub Pages |

## Getting Started

### Prerequisites

- Node.js 20+
- npm 10+

### Install dependencies

```bash
npm install
```

### Start development server

```bash
npm run dev
```

Open [http://localhost:5173/WEOS/](http://localhost:5173/WEOS/)

### Build for production

```bash
npm run build
```

Output is placed in the `dist/` directory.

### Preview production build

```bash
npm run preview
```

### Lint

```bash
npm run lint
```

## Project Structure

```
src/
├── components/
│   └── layout/
│       ├── Shell.tsx      # Root dashboard shell
│       ├── Topbar.tsx     # Tabbed navigation (GLOBAL VIEW … SETTINGS)
│       └── Footer.tsx     # Mode-navigation footer (2D / 3D / FLOW / CHART)
├── stores/
│   └── uiStore.ts         # Zustand UI state (active tab, view mode)
├── types/
│   ├── ui.ts              # UI type definitions
│   └── geo.ts             # Geographic type definitions
├── App.tsx
├── main.tsx
└── index.css
```

## Deployment

Merging to `main` triggers the GitHub Actions workflow (`.github/workflows/deploy.yml`) which builds and deploys to GitHub Pages at:

`https://tristanahayhay-ship-it.github.io/WEOS/`

## Roadmap

- **Phase 1** ✅ Project Foundation — monorepo setup, layout shell, type system, CI/CD
- **Phase 2** Map Integration — MapLibre GL base map with 2D/3D toggle
- **Phase 3** Data Layer — economic datasets, trade flow APIs, GeoJSON processing
- **Phase 4** Visualization — deck.gl overlays, flow arcs, ECharts panels
- **Phase 5** Analytics — cross-sector indicators, time-series playback
