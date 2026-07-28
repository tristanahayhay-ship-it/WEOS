# WEOS Data Provider Layer — Phase 4A

## Overview

The Data Provider Layer is an independent module (`src/providers/`) that fetches
realtime economic data and merges it into the `economicStore`.  
It is designed so that:

- **The UI is never blocked.** Placeholder data (Phase 3B) is always shown while
  providers load in the background.
- **Providers are interchangeable.** Adding or removing a connector never requires
  changes to Globe Engine, Country Layer, or Country Panel.
- **Failures are silent.** If every provider fails, the app continues working with
  placeholder data.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  UI / React Components                                   │
│  (Globe Engine, Country Layer, Country Panel)            │
│  — never imports from src/providers/ directly —          │
└───────────────────────┬──────────────────────────────────┘
                        │ reads
                        ▼
┌──────────────────────────────────────────────────────────┐
│  economicStore  (src/stores/economicStore.ts)             │
│  • Starts with placeholder data (Phase 3B baseline)       │
│  • Calls initializeFromProviders() on load (async)        │
│  • Merges real data on top of placeholders in-place       │
└───────────────────────┬──────────────────────────────────┘
                        │ delegates
                        ▼
┌──────────────────────────────────────────────────────────┐
│  ProviderManager  (src/providers/providerManager.ts)      │
│  • Tries providers in registered order                    │
│  • Timeout / retry / cache per provider                   │
│  • Merges partial data from each successful provider      │
│  • Skips providers missing required API keys              │
└───────────────────────┬──────────────────────────────────┘
                        │ calls fetchAll()
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  Connectors  (src/providers/connectors/)                         │
│  ┌────────────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ WorldBankConnector │  │ ImfConnector │  │ FredConnector  │  │
│  │ (real: Pop + GDP)  │  │ (stub)       │  │ (stub, key req)│  │
│  └────────────────────┘  └──────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Provider contracts

Every connector must implement the `EconomicDataProvider` interface
(`src/providers/types.ts`):

```ts
interface EconomicDataProvider {
  /** Human-readable name for logs. */
  readonly name: string

  /** Set to true if an API key is required. */
  readonly requiresApiKey: boolean

  /**
   * Batch-fetch data for all supported countries.
   * Return an empty Map on failure — never throw.
   * Keys are ISO alpha-2 codes (e.g. "US", "DE").
   */
  fetchAll(): Promise<Map<string, PartialEconomicData>>
}
```

`PartialEconomicData` is `Partial<Omit<CountryEconomicData, 'isoCode'>>`.  
Providers only fill the fields they support; the manager merges all contributions.

---

## Adding a new provider

1. **Create a connector** in `src/providers/connectors/`:

   ```ts
   // src/providers/connectors/mySourceConnector.ts
   import type { EconomicDataProvider, PartialEconomicData } from '../types'

   export class MySourceConnector implements EconomicDataProvider {
     readonly name = 'MySource'
     readonly requiresApiKey = false // set true if an API key is needed

     async fetchAll(): Promise<Map<string, PartialEconomicData>> {
       // Call your API here.
       // Return a map from ISO alpha-2 country code → partial data.
       const result = new Map<string, PartialEconomicData>()
       // e.g. result.set('US', { population: 331_000_000 })
       return result
     }
   }
   ```

2. **Register it** in `src/providers/index.ts`:

   ```ts
   import { MySourceConnector } from './connectors/mySourceConnector'

   const defaultProviders = [
     new WorldBankConnector(),
     new ImfConnector(),
     new FredConnector(),
     new MySourceConnector(), // ← add here
   ]
   ```

3. **No other changes required.** The UI, Globe Engine, Country Layer, and Country
   Panel are unaffected.

---

## Configuring an API key

For connectors that require an API key (e.g. FRED), use Vite's environment
variable system:

1. Create a `.env.local` file in the project root (already in `.gitignore`):

   ```
   VITE_FRED_API_KEY=your_api_key_here
   ```

2. Read it in your connector:

   ```ts
   const apiKey = (import.meta.env as Record<string, string>)['VITE_FRED_API_KEY'] ?? ''
   ```

3. Set `requiresApiKey = true` in your connector class.  
   The `ProviderManager` will automatically skip the connector if no key is present,
   so the app stays functional without the key.

For production deployments (GitHub Actions / CI), set the key as a GitHub Actions
secret and expose it via the workflow's `env:` block:

```yaml
- name: Build
  run: npm run build
  env:
    VITE_FRED_API_KEY: ${{ secrets.FRED_API_KEY }}
```

---

## Implemented connectors

| Connector        | Status      | Fields                      | API key required |
|------------------|-------------|------------------------------|------------------|
| WorldBank        | ✅ Active   | `population`, `gdpUsd`, `gdpPerCapitaUsd` | No |
| IMF              | 🔲 Stub     | `inflationPercent`, `interestRatePercent` | No |
| FRED             | 🔲 Stub     | US-only fields               | Yes (`VITE_FRED_API_KEY`) |

### Activating the IMF connector

Edit `src/providers/connectors/imfConnector.ts` and implement `fetchAll()` using the
[IMF DataMapper REST API](https://www.imf.org/external/datamapper/api/v1/).

### Activating the FRED connector

Edit `src/providers/connectors/fredConnector.ts` and implement `fetchAll()` using the
[FRED REST API](https://fred.stlouisfed.org/docs/api/fred/).
Add your API key as described above.

---

## Cache and retry behaviour

| Setting          | Default  | Configure via `ProviderManagerConfig` |
|------------------|----------|---------------------------------------|
| Cache TTL        | 1 hour   | `cacheTtlMs`                          |
| Request timeout  | 10 s     | `timeoutMs`                           |
| Retry attempts   | 2        | `retryAttempts`                       |

Cached data is stored in memory and survives re-renders but not page reloads.

---

## Backward compatibility

- Phase 3A (Globe / Country Layer) — **unmodified**.
- Phase 3B (placeholder `economicData.ts`, `economicStore.ts` API) — **fully preserved**.
  The store still exposes `getEconomicData`, `setEconomicData`, and the same
  `ReadonlyMap<string, CountryEconomicData>` shape.
- Country Panel — **unmodified**.
- If all providers fail the store retains the Phase 3B placeholder values, so the
  UI is always functional.
