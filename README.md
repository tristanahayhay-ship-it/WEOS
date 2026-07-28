# WEOS — World Economic Operating System

A production-grade geospatial analytics platform for visualizing global economic flows, trade networks, and macroeconomic data.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI Framework | React 19 + TypeScript |
| Build Tool | Vite 6 |
| Styling | Tailwind CSS v4 |
| 2D Maps | MapLibre GL |
| 3D Visualization | Three.js |
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
│   ├── globe/
│   │   └── GlobeEngine.tsx # Interactive 3D globe engine
│   └── layout/
│       ├── Shell.tsx      # Root dashboard shell
│       ├── Topbar.tsx     # Tabbed navigation (GLOBAL VIEW … SETTINGS)
│       └── Footer.tsx     # Mode-navigation footer (2D / 3D / FLOW / CHART)
├── hooks/
│   └── useElementSize.ts  # Responsive measurement hook for canvas containers
├── stores/
│   └── uiStore.ts         # Zustand UI state (active tab, view mode)
├── types/
│   ├── ui.ts              # UI type definitions
│   └── geo.ts             # Geographic type definitions
├── utils/
│   └── globe.ts           # Globe geometry and boundary conversion helpers
├── App.tsx
├── main.tsx
└── index.css
```

## Deployment

Merging to `main` triggers the GitHub Actions workflow (`.github/workflows/deploy.yml`) which builds and deploys to GitHub Pages at:

`https://tristanahayhay-ship-it.github.io/WEOS/`

## Current Status

- **Phase 1** ✅ Project Foundation — layout shell, type system, CI/CD
- **Phase 2** ✅ Globe Engine — responsive interactive 3D Earth with coastlines and country boundaries
- **Phase 3** ⏭️ Data Layer — economic datasets, trade flow APIs, GeoJSON processing
- **Phase 4** ⏭️ Visualization — overlays, flow arcs, charts, and analytics surfaces
