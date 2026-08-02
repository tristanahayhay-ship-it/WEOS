/** Top-level navigation tabs in the WEOS dashboard */
export type TopbarTab =
  | 'global-view'
  | 'flows'
  | 'sectors'
  | 'nations'
  | 'analytics'
  | 'settings'

/** Per-country navigation tabs shown when a country is selected */
export type CountryTab =
  | 'overview'
  | 'economy'
  | 'markets'
  | 'trade'
  | 'industry'
  | 'government'
  | 'infrastructure'
  | 'news'

/** Visualization mode for the main canvas */
export type ViewMode = '2d' | '3d' | 'flow' | 'chart'
