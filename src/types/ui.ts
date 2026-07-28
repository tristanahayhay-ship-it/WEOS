/** Top-level navigation tabs in the WEOS dashboard */
export type TopbarTab =
  | 'global-view'
  | 'flows'
  | 'sectors'
  | 'nations'
  | 'analytics'
  | 'settings'

/** Visualization mode for the main canvas */
export type ViewMode = '2d' | '3d' | 'flow' | 'chart'
