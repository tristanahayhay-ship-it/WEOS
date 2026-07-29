import type { FlowObject } from './types'
import type { ZoomLevelId } from '../zoom/types'

/**
 * LOD-indexed collection of FlowObjects.
 *
 * Each key is a ZoomLevelId (0–6).  The FlowEngine activates the array for the
 * current level and fades it out when transitioning to an adjacent level.
 *
 * Level hierarchy:
 *  0 – Global      : intercontinental mega-routes (thick, slow, few)
 *  1 – Continent   : inter-city routes within a continent (medium)
 *  2 – Country     : flows between major cities, national scale (thinner)
 *  3 – City        : secondary-city flows, regional scale (thin, faster)
 *  4 – District    : same-country city pairs (thin, fast)
 *  5 – Institution : financial-hub connections (thin, medium-fast)
 *  6 – Corporation : company supply chain / partnership flows (thinnest, fastest)
 */
export const LOD_FLOWS: Record<ZoomLevelId, FlowObject[]> = {
  // ── Level 0: Global ──────────────────────────────────────────────────────
  // Intercontinental mega-routes — few in number, thick & strongly glowing.
  0: [
    {
      id: 'g0-nyc-lon',
      startPoint: [-74.006, 40.713],   // New York
      endPoint:   [-0.127, 51.507],    // London
      dataType:   'trade',
      value:      920,
      color:      '#3b82f6',
      colorHex:   0x3b82f6,
      thickness:  0.95,
      animationSpeed: 0.45,
      displayPriority: 10,
      lodRules: {
        visibleAtLevels: [0],
        splitIntoIds: ['c1-fra-lon', 'c1-nyc-tor', 'c1-nyc-chi'],
      },
      visibilityState: 0,
    },
    {
      id: 'g0-nyc-sha',
      startPoint: [-74.006, 40.713],   // New York
      endPoint:   [121.473, 31.230],   // Shanghai
      dataType:   'trade',
      value:      820,
      color:      '#3b82f6',
      colorHex:   0x3b82f6,
      thickness:  0.92,
      animationSpeed: 0.42,
      displayPriority: 10,
      lodRules: {
        visibleAtLevels: [0],
        splitIntoIds: ['c1-sha-tok', 'c1-sha-sel', 'c1-nyc-chi'],
      },
      visibilityState: 0,
    },
    {
      id: 'g0-lon-sha',
      startPoint: [-0.127, 51.507],    // London
      endPoint:   [121.473, 31.230],   // Shanghai
      dataType:   'trade',
      value:      680,
      color:      '#3b82f6',
      colorHex:   0x3b82f6,
      thickness:  0.88,
      animationSpeed: 0.40,
      displayPriority: 9,
      lodRules: {
        visibleAtLevels: [0],
        splitIntoIds: ['c1-fra-lon', 'c1-sha-tok'],
      },
      visibilityState: 0,
    },
    {
      id: 'g0-lax-tok',
      startPoint: [-118.243, 34.052],  // Los Angeles
      endPoint:   [139.691, 35.690],   // Tokyo
      dataType:   'investment',
      value:      540,
      color:      '#10b981',
      colorHex:   0x10b981,
      thickness:  0.85,
      animationSpeed: 0.48,
      displayPriority: 9,
      lodRules: {
        visibleAtLevels: [0],
        splitIntoIds: ['c1-tok-sin', 'c1-sha-tok'],
      },
      visibilityState: 0,
    },
    {
      id: 'g0-dxb-sin',
      startPoint: [55.297, 25.207],    // Dubai
      endPoint:   [103.820, 1.352],    // Singapore
      dataType:   'energy',
      value:      490,
      color:      '#eab308',
      colorHex:   0xeab308,
      thickness:  0.88,
      animationSpeed: 0.50,
      displayPriority: 8,
      lodRules: {
        visibleAtLevels: [0],
        splitIntoIds: ['c1-sin-hkg', 'c1-mum-sin'],
      },
      visibilityState: 0,
    },
    {
      id: 'g0-sao-lon',
      startPoint: [-46.633, -23.533],  // São Paulo
      endPoint:   [-0.127, 51.507],    // London
      dataType:   'investment',
      value:      310,
      color:      '#10b981',
      colorHex:   0x10b981,
      thickness:  0.80,
      animationSpeed: 0.52,
      displayPriority: 7,
      lodRules: {
        visibleAtLevels: [0],
      },
      visibilityState: 0,
    },
  ],

  // ── Level 1: Continent ───────────────────────────────────────────────────
  // Inter-city routes within a continent — more numerous, thinner.
  1: [
    // Europe cluster
    {
      id: 'c1-fra-lon',
      startPoint: [8.682, 50.111],     // Frankfurt
      endPoint:   [-0.127, 51.507],    // London
      dataType:   'trade',
      value:      320,
      color:      '#3b82f6',
      colorHex:   0x3b82f6,
      thickness:  0.68,
      animationSpeed: 0.65,
      displayPriority: 8,
      lodRules: { visibleAtLevels: [1], mergesIntoId: 'g0-lon-sha' },
      visibilityState: 0,
    },
    {
      id: 'c1-fra-par',
      startPoint: [8.682, 50.111],     // Frankfurt
      endPoint:   [2.352, 48.857],     // Paris
      dataType:   'trade',
      value:      285,
      color:      '#3b82f6',
      colorHex:   0x3b82f6,
      thickness:  0.65,
      animationSpeed: 0.68,
      displayPriority: 7,
      lodRules: { visibleAtLevels: [1] },
      visibilityState: 0,
    },
    {
      id: 'c1-par-lon',
      startPoint: [2.352, 48.857],     // Paris
      endPoint:   [-0.127, 51.507],    // London
      dataType:   'investment',
      value:      260,
      color:      '#10b981',
      colorHex:   0x10b981,
      thickness:  0.62,
      animationSpeed: 0.70,
      displayPriority: 7,
      lodRules: { visibleAtLevels: [1] },
      visibilityState: 0,
    },
    {
      id: 'c1-fra-mil',
      startPoint: [8.682, 50.111],     // Frankfurt
      endPoint:   [9.190, 45.465],     // Milan
      dataType:   'trade',
      value:      195,
      color:      '#3b82f6',
      colorHex:   0x3b82f6,
      thickness:  0.58,
      animationSpeed: 0.72,
      displayPriority: 6,
      lodRules: { visibleAtLevels: [1] },
      visibilityState: 0,
    },
    {
      id: 'c1-lon-ams',
      startPoint: [-0.127, 51.507],    // London
      endPoint:   [4.897, 52.377],     // Amsterdam
      dataType:   'capital',
      value:      220,
      color:      '#14b8a6',
      colorHex:   0x14b8a6,
      thickness:  0.60,
      animationSpeed: 0.70,
      displayPriority: 7,
      lodRules: { visibleAtLevels: [1] },
      visibilityState: 0,
    },
    // Americas cluster
    {
      id: 'c1-nyc-tor',
      startPoint: [-74.006, 40.713],   // New York
      endPoint:   [-79.383, 43.653],   // Toronto
      dataType:   'trade',
      value:      280,
      color:      '#3b82f6',
      colorHex:   0x3b82f6,
      thickness:  0.65,
      animationSpeed: 0.65,
      displayPriority: 7,
      lodRules: { visibleAtLevels: [1], mergesIntoId: 'g0-nyc-lon' },
      visibilityState: 0,
    },
    {
      id: 'c1-nyc-chi',
      startPoint: [-74.006, 40.713],   // New York
      endPoint:   [-87.629, 41.878],   // Chicago
      dataType:   'capital',
      value:      240,
      color:      '#14b8a6',
      colorHex:   0x14b8a6,
      thickness:  0.62,
      animationSpeed: 0.67,
      displayPriority: 7,
      lodRules: { visibleAtLevels: [1], mergesIntoId: 'g0-nyc-sha' },
      visibilityState: 0,
    },
    {
      id: 'c1-hou-mex',
      startPoint: [-95.370, 29.760],   // Houston
      endPoint:   [-99.133, 19.433],   // Mexico City
      dataType:   'trade',
      value:      165,
      color:      '#3b82f6',
      colorHex:   0x3b82f6,
      thickness:  0.55,
      animationSpeed: 0.72,
      displayPriority: 5,
      lodRules: { visibleAtLevels: [1] },
      visibilityState: 0,
    },
    // Asia cluster
    {
      id: 'c1-sha-tok',
      startPoint: [121.473, 31.230],   // Shanghai
      endPoint:   [139.691, 35.690],   // Tokyo
      dataType:   'trade',
      value:      310,
      color:      '#3b82f6',
      colorHex:   0x3b82f6,
      thickness:  0.68,
      animationSpeed: 0.63,
      displayPriority: 8,
      lodRules: { visibleAtLevels: [1], mergesIntoId: 'g0-lax-tok' },
      visibilityState: 0,
    },
    {
      id: 'c1-sha-sel',
      startPoint: [121.473, 31.230],   // Shanghai
      endPoint:   [126.978, 37.566],   // Seoul
      dataType:   'trade',
      value:      260,
      color:      '#3b82f6',
      colorHex:   0x3b82f6,
      thickness:  0.63,
      animationSpeed: 0.67,
      displayPriority: 7,
      lodRules: { visibleAtLevels: [1], mergesIntoId: 'g0-nyc-sha' },
      visibilityState: 0,
    },
    {
      id: 'c1-sin-hkg',
      startPoint: [103.820, 1.352],    // Singapore
      endPoint:   [114.177, 22.302],   // Hong Kong
      dataType:   'capital',
      value:      185,
      color:      '#14b8a6',
      colorHex:   0x14b8a6,
      thickness:  0.60,
      animationSpeed: 0.70,
      displayPriority: 7,
      lodRules: { visibleAtLevels: [1], mergesIntoId: 'g0-dxb-sin' },
      visibilityState: 0,
    },
    {
      id: 'c1-tok-sin',
      startPoint: [139.691, 35.690],   // Tokyo
      endPoint:   [103.820, 1.352],    // Singapore
      dataType:   'investment',
      value:      210,
      color:      '#10b981',
      colorHex:   0x10b981,
      thickness:  0.62,
      animationSpeed: 0.68,
      displayPriority: 7,
      lodRules: { visibleAtLevels: [1], mergesIntoId: 'g0-lax-tok' },
      visibilityState: 0,
    },
    {
      id: 'c1-mum-sin',
      startPoint: [72.878, 19.076],    // Mumbai
      endPoint:   [103.820, 1.352],    // Singapore
      dataType:   'trade',
      value:      175,
      color:      '#3b82f6',
      colorHex:   0x3b82f6,
      thickness:  0.57,
      animationSpeed: 0.72,
      displayPriority: 6,
      lodRules: { visibleAtLevels: [1], mergesIntoId: 'g0-dxb-sin' },
      visibilityState: 0,
    },
  ],

  // ── Level 2: Country ─────────────────────────────────────────────────────
  // Flows between major cities, national scale — thinner, hide global routes.
  2: [
    // US city pairs
    {
      id: 'cn2-nyc-chi',
      startPoint: [-74.006, 40.713],   // New York
      endPoint:   [-87.629, 41.878],   // Chicago
      dataType:   'capital',
      value:      180,
      color:      '#14b8a6',
      colorHex:   0x14b8a6,
      thickness:  0.50,
      animationSpeed: 0.85,
      displayPriority: 8,
      lodRules: { visibleAtLevels: [2] },
      visibilityState: 0,
    },
    {
      id: 'cn2-nyc-lax',
      startPoint: [-74.006, 40.713],   // New York
      endPoint:   [-118.243, 34.052],  // Los Angeles
      dataType:   'trade',
      value:      155,
      color:      '#3b82f6',
      colorHex:   0x3b82f6,
      thickness:  0.48,
      animationSpeed: 0.88,
      displayPriority: 7,
      lodRules: { visibleAtLevels: [2] },
      visibilityState: 0,
    },
    {
      id: 'cn2-chi-hou',
      startPoint: [-87.629, 41.878],   // Chicago
      endPoint:   [-95.370, 29.760],   // Houston
      dataType:   'energy',
      value:      130,
      color:      '#eab308',
      colorHex:   0xeab308,
      thickness:  0.45,
      animationSpeed: 0.90,
      displayPriority: 6,
      lodRules: { visibleAtLevels: [2] },
      visibilityState: 0,
    },
    // European city pairs
    {
      id: 'cn2-fra-ber',
      startPoint: [8.682, 50.111],     // Frankfurt
      endPoint:   [13.405, 52.520],    // Berlin
      dataType:   'capital',
      value:      140,
      color:      '#14b8a6',
      colorHex:   0x14b8a6,
      thickness:  0.50,
      animationSpeed: 0.85,
      displayPriority: 7,
      lodRules: { visibleAtLevels: [2] },
      visibilityState: 0,
    },
    {
      id: 'cn2-fra-zur',
      startPoint: [8.682, 50.111],     // Frankfurt
      endPoint:   [8.542, 47.376],     // Zurich
      dataType:   'capital',
      value:      165,
      color:      '#14b8a6',
      colorHex:   0x14b8a6,
      thickness:  0.52,
      animationSpeed: 0.83,
      displayPriority: 8,
      lodRules: { visibleAtLevels: [2] },
      visibilityState: 0,
    },
    {
      id: 'cn2-muc-ham',
      startPoint: [11.582, 48.135],    // Munich
      endPoint:   [9.993, 53.550],     // Hamburg
      dataType:   'trade',
      value:      120,
      color:      '#3b82f6',
      colorHex:   0x3b82f6,
      thickness:  0.45,
      animationSpeed: 0.90,
      displayPriority: 6,
      lodRules: { visibleAtLevels: [2] },
      visibilityState: 0,
    },
    // Asian city pairs
    {
      id: 'cn2-sha-bei',
      startPoint: [121.473, 31.230],   // Shanghai
      endPoint:   [116.407, 39.904],   // Beijing
      dataType:   'capital',
      value:      195,
      color:      '#14b8a6',
      colorHex:   0x14b8a6,
      thickness:  0.52,
      animationSpeed: 0.85,
      displayPriority: 8,
      lodRules: { visibleAtLevels: [2] },
      visibilityState: 0,
    },
    {
      id: 'cn2-sha-gua',
      startPoint: [121.473, 31.230],   // Shanghai
      endPoint:   [113.264, 23.129],   // Guangzhou
      dataType:   'trade',
      value:      160,
      color:      '#3b82f6',
      colorHex:   0x3b82f6,
      thickness:  0.48,
      animationSpeed: 0.88,
      displayPriority: 7,
      lodRules: { visibleAtLevels: [2] },
      visibilityState: 0,
    },
    {
      id: 'cn2-tok-osa',
      startPoint: [139.691, 35.690],   // Tokyo
      endPoint:   [135.502, 34.694],   // Osaka
      dataType:   'supply-chain',
      value:      145,
      color:      '#f97316',
      colorHex:   0xf97316,
      thickness:  0.47,
      animationSpeed: 0.90,
      displayPriority: 7,
      lodRules: { visibleAtLevels: [2] },
      visibilityState: 0,
    },
    {
      id: 'cn2-bei-che',
      startPoint: [116.407, 39.904],   // Beijing
      endPoint:   [104.065, 30.660],   // Chengdu
      dataType:   'trade',
      value:      118,
      color:      '#3b82f6',
      colorHex:   0x3b82f6,
      thickness:  0.44,
      animationSpeed: 0.92,
      displayPriority: 6,
      lodRules: { visibleAtLevels: [2] },
      visibilityState: 0,
    },
    {
      id: 'cn2-sel-bus',
      startPoint: [126.978, 37.566],   // Seoul
      endPoint:   [129.075, 35.179],   // Busan
      dataType:   'supply-chain',
      value:      105,
      color:      '#f97316',
      colorHex:   0xf97316,
      thickness:  0.42,
      animationSpeed: 0.93,
      displayPriority: 6,
      lodRules: { visibleAtLevels: [2] },
      visibilityState: 0,
    },
    {
      id: 'cn2-mad-bar',
      startPoint: [-3.703, 40.417],    // Madrid
      endPoint:   [2.154, 41.389],     // Barcelona
      dataType:   'trade',
      value:      108,
      color:      '#3b82f6',
      colorHex:   0x3b82f6,
      thickness:  0.43,
      animationSpeed: 0.93,
      displayPriority: 5,
      lodRules: { visibleAtLevels: [2] },
      visibilityState: 0,
    },
  ],

  // ── Level 3: City ────────────────────────────────────────────────────────
  // Secondary-city flows at regional scale — thinner, faster animation.
  3: [
    {
      id: 'ct3-nyc-phi',
      startPoint: [-74.006, 40.713],   // New York
      endPoint:   [-75.165, 39.952],   // Philadelphia
      dataType:   'capital',
      value:      95,
      color:      '#14b8a6',
      colorHex:   0x14b8a6,
      thickness:  0.38,
      animationSpeed: 1.10,
      displayPriority: 7,
      lodRules: { visibleAtLevels: [3] },
      visibilityState: 0,
    },
    {
      id: 'ct3-nyc-bos',
      startPoint: [-74.006, 40.713],   // New York
      endPoint:   [-71.057, 42.361],   // Boston
      dataType:   'data',
      value:      88,
      color:      '#06b6d4',
      colorHex:   0x06b6d4,
      thickness:  0.36,
      animationSpeed: 1.15,
      displayPriority: 7,
      lodRules: { visibleAtLevels: [3] },
      visibilityState: 0,
    },
    {
      id: 'ct3-nyc-wdc',
      startPoint: [-74.006, 40.713],   // New York
      endPoint:   [-77.036, 38.907],   // Washington DC
      dataType:   'capital',
      value:      110,
      color:      '#14b8a6',
      colorHex:   0x14b8a6,
      thickness:  0.40,
      animationSpeed: 1.08,
      displayPriority: 8,
      lodRules: { visibleAtLevels: [3] },
      visibilityState: 0,
    },
    {
      id: 'ct3-par-lyo',
      startPoint: [2.352, 48.857],     // Paris
      endPoint:   [4.835, 45.764],     // Lyon
      dataType:   'trade',
      value:      80,
      color:      '#3b82f6',
      colorHex:   0x3b82f6,
      thickness:  0.35,
      animationSpeed: 1.15,
      displayPriority: 6,
      lodRules: { visibleAtLevels: [3] },
      visibilityState: 0,
    },
    {
      id: 'ct3-sha-nan',
      startPoint: [121.473, 31.230],   // Shanghai
      endPoint:   [118.796, 32.061],   // Nanjing
      dataType:   'supply-chain',
      value:      78,
      color:      '#f97316',
      colorHex:   0xf97316,
      thickness:  0.34,
      animationSpeed: 1.18,
      displayPriority: 6,
      lodRules: { visibleAtLevels: [3] },
      visibilityState: 0,
    },
    {
      id: 'ct3-tok-yok',
      startPoint: [139.691, 35.690],   // Tokyo
      endPoint:   [139.638, 35.444],   // Yokohama
      dataType:   'supply-chain',
      value:      85,
      color:      '#f97316',
      colorHex:   0xf97316,
      thickness:  0.36,
      animationSpeed: 1.12,
      displayPriority: 7,
      lodRules: { visibleAtLevels: [3] },
      visibilityState: 0,
    },
    {
      id: 'ct3-lon-bri',
      startPoint: [-0.127, 51.507],    // London
      endPoint:   [-1.898, 52.480],    // Birmingham
      dataType:   'trade',
      value:      72,
      color:      '#3b82f6',
      colorHex:   0x3b82f6,
      thickness:  0.34,
      animationSpeed: 1.20,
      displayPriority: 6,
      lodRules: { visibleAtLevels: [3] },
      visibilityState: 0,
    },
    {
      id: 'ct3-ber-dre',
      startPoint: [13.405, 52.520],    // Berlin
      endPoint:   [13.738, 51.050],    // Dresden
      dataType:   'data',
      value:      65,
      color:      '#06b6d4',
      colorHex:   0x06b6d4,
      thickness:  0.32,
      animationSpeed: 1.22,
      displayPriority: 5,
      lodRules: { visibleAtLevels: [3] },
      visibilityState: 0,
    },
    {
      id: 'ct3-bos-phi',
      startPoint: [-71.057, 42.361],   // Boston
      endPoint:   [-75.165, 39.952],   // Philadelphia
      dataType:   'data',
      value:      70,
      color:      '#06b6d4',
      colorHex:   0x06b6d4,
      thickness:  0.33,
      animationSpeed: 1.18,
      displayPriority: 6,
      lodRules: { visibleAtLevels: [3] },
      visibilityState: 0,
    },
    {
      id: 'ct3-sin-kul',
      startPoint: [103.820, 1.352],    // Singapore
      endPoint:   [101.686, 3.140],    // Kuala Lumpur
      dataType:   'trade',
      value:      76,
      color:      '#3b82f6',
      colorHex:   0x3b82f6,
      thickness:  0.34,
      animationSpeed: 1.17,
      displayPriority: 6,
      lodRules: { visibleAtLevels: [3] },
      visibilityState: 0,
    },
  ],

  // ── Level 4: District ────────────────────────────────────────────────────
  // Within-country city-pair flows, shorter arcs — faster animation.
  4: [
    {
      id: 'd4-nyc-newk',
      startPoint: [-74.006, 40.713],   // New York (Manhattan)
      endPoint:   [-74.172, 40.736],   // Newark
      dataType:   'capital',
      value:      55,
      color:      '#14b8a6',
      colorHex:   0x14b8a6,
      thickness:  0.30,
      animationSpeed: 1.40,
      displayPriority: 7,
      lodRules: { visibleAtLevels: [4] },
      visibilityState: 0,
    },
    {
      id: 'd4-nyc-stam',
      startPoint: [-74.006, 40.713],   // New York
      endPoint:   [-73.539, 41.053],   // Stamford
      dataType:   'capital',
      value:      48,
      color:      '#14b8a6',
      colorHex:   0x14b8a6,
      thickness:  0.28,
      animationSpeed: 1.45,
      displayPriority: 6,
      lodRules: { visibleAtLevels: [4] },
      visibilityState: 0,
    },
    {
      id: 'd4-lon-rea',
      startPoint: [-0.127, 51.507],    // London
      endPoint:   [-0.978, 51.455],    // Reading
      dataType:   'data',
      value:      42,
      color:      '#06b6d4',
      colorHex:   0x06b6d4,
      thickness:  0.27,
      animationSpeed: 1.50,
      displayPriority: 6,
      lodRules: { visibleAtLevels: [4] },
      visibilityState: 0,
    },
    {
      id: 'd4-lon-sou',
      startPoint: [-0.127, 51.507],    // London
      endPoint:   [-1.404, 50.905],    // Southampton
      dataType:   'trade',
      value:      50,
      color:      '#3b82f6',
      colorHex:   0x3b82f6,
      thickness:  0.28,
      animationSpeed: 1.48,
      displayPriority: 6,
      lodRules: { visibleAtLevels: [4] },
      visibilityState: 0,
    },
    {
      id: 'd4-fra-man',
      startPoint: [8.682, 50.111],     // Frankfurt
      endPoint:   [8.465, 49.488],     // Mannheim
      dataType:   'supply-chain',
      value:      38,
      color:      '#f97316',
      colorHex:   0xf97316,
      thickness:  0.26,
      animationSpeed: 1.52,
      displayPriority: 5,
      lodRules: { visibleAtLevels: [4] },
      visibilityState: 0,
    },
    {
      id: 'd4-sha-sus',
      startPoint: [121.473, 31.230],   // Shanghai
      endPoint:   [120.655, 31.315],   // Suzhou
      dataType:   'supply-chain',
      value:      52,
      color:      '#f97316',
      colorHex:   0xf97316,
      thickness:  0.29,
      animationSpeed: 1.42,
      displayPriority: 7,
      lodRules: { visibleAtLevels: [4] },
      visibilityState: 0,
    },
    {
      id: 'd4-tok-kaw',
      startPoint: [139.691, 35.690],   // Tokyo
      endPoint:   [139.702, 35.530],   // Kawasaki
      dataType:   'supply-chain',
      value:      44,
      color:      '#f97316',
      colorHex:   0xf97316,
      thickness:  0.27,
      animationSpeed: 1.48,
      displayPriority: 6,
      lodRules: { visibleAtLevels: [4] },
      visibilityState: 0,
    },
    {
      id: 'd4-chi-oke',
      startPoint: [-87.629, 41.878],   // Chicago
      endPoint:   [-87.847, 41.622],   // Oak Park / Berwyn area
      dataType:   'capital',
      value:      36,
      color:      '#14b8a6',
      colorHex:   0x14b8a6,
      thickness:  0.26,
      animationSpeed: 1.55,
      displayPriority: 5,
      lodRules: { visibleAtLevels: [4] },
      visibilityState: 0,
    },
  ],

  // ── Level 5: Institution ─────────────────────────────────────────────────
  // Connections between banks, ports, factories, exchanges.
  5: [
    {
      id: 'i5-nyse-fed',
      startPoint: [-74.011, 40.707],   // NYSE (Wall Street)
      endPoint:   [-74.013, 40.714],   // Federal Reserve NY
      dataType:   'capital',
      value:      820,
      color:      '#14b8a6',
      colorHex:   0x14b8a6,
      thickness:  0.25,
      animationSpeed: 1.70,
      displayPriority: 10,
      lodRules: { visibleAtLevels: [5] },
      visibilityState: 0,
    },
    {
      id: 'i5-jpm-citi',
      startPoint: [-73.978, 40.754],   // JPMorgan HQ (Midtown)
      endPoint:   [-73.976, 40.754],   // Citibank HQ
      dataType:   'capital',
      value:      640,
      color:      '#14b8a6',
      colorHex:   0x14b8a6,
      thickness:  0.23,
      animationSpeed: 1.75,
      displayPriority: 9,
      lodRules: { visibleAtLevels: [5] },
      visibilityState: 0,
    },
    {
      id: 'i5-ldn-lse',
      startPoint: [-0.088, 51.514],    // Bank of England
      endPoint:   [-0.099, 51.514],    // London Stock Exchange
      dataType:   'capital',
      value:      580,
      color:      '#14b8a6',
      colorHex:   0x14b8a6,
      thickness:  0.22,
      animationSpeed: 1.80,
      displayPriority: 9,
      lodRules: { visibleAtLevels: [5] },
      visibilityState: 0,
    },
    {
      id: 'i5-fra-ecb',
      startPoint: [8.697, 50.112],     // Deutsche Bank HQ
      endPoint:   [8.682, 50.111],     // ECB / Frankfurt banking district
      dataType:   'capital',
      value:      490,
      color:      '#14b8a6',
      colorHex:   0x14b8a6,
      thickness:  0.21,
      animationSpeed: 1.82,
      displayPriority: 8,
      lodRules: { visibleAtLevels: [5] },
      visibilityState: 0,
    },
    {
      id: 'i5-sha-pboc',
      startPoint: [121.496, 31.240],   // PBOC Shanghai branch
      endPoint:   [121.473, 31.230],   // Shanghai Stock Exchange
      dataType:   'capital',
      value:      710,
      color:      '#14b8a6',
      colorHex:   0x14b8a6,
      thickness:  0.24,
      animationSpeed: 1.72,
      displayPriority: 9,
      lodRules: { visibleAtLevels: [5] },
      visibilityState: 0,
    },
    {
      id: 'i5-tok-boj',
      startPoint: [139.769, 35.686],   // Bank of Japan
      endPoint:   [139.691, 35.690],   // Tokyo Stock Exchange
      dataType:   'capital',
      value:      550,
      color:      '#14b8a6',
      colorHex:   0x14b8a6,
      thickness:  0.22,
      animationSpeed: 1.78,
      displayPriority: 8,
      lodRules: { visibleAtLevels: [5] },
      visibilityState: 0,
    },
  ],

  // ── Level 6: Corporation ─────────────────────────────────────────────────
  // Company-level: supply chain, capital, ownership, data, partnerships.
  6: [
    {
      id: 'co6-aapl-tsm',
      startPoint: [-122.030, 37.332],  // Apple HQ (Cupertino)
      endPoint:   [120.987, 24.779],   // TSMC (Hsinchu, Taiwan)
      dataType:   'supply-chain',
      value:      300,
      color:      '#f97316',
      colorHex:   0xf97316,
      thickness:  0.22,
      animationSpeed: 2.00,
      displayPriority: 10,
      lodRules: { visibleAtLevels: [6] },
      visibilityState: 0,
    },
    {
      id: 'co6-msft-amz',
      startPoint: [-122.129, 47.640],  // Microsoft HQ (Redmond)
      endPoint:   [-122.336, 47.622],  // Amazon HQ (Seattle)
      dataType:   'data',
      value:      220,
      color:      '#06b6d4',
      colorHex:   0x06b6d4,
      thickness:  0.20,
      animationSpeed: 2.10,
      displayPriority: 9,
      lodRules: { visibleAtLevels: [6] },
      visibilityState: 0,
    },
    {
      id: 'co6-toy-den',
      startPoint: [137.150, 35.083],   // Toyota HQ (Toyota City)
      endPoint:   [136.888, 35.170],   // Denso (Kariya)
      dataType:   'supply-chain',
      value:      195,
      color:      '#f97316',
      colorHex:   0xf97316,
      thickness:  0.19,
      animationSpeed: 2.15,
      displayPriority: 9,
      lodRules: { visibleAtLevels: [6] },
      visibilityState: 0,
    },
    {
      id: 'co6-goog-meta',
      startPoint: [-122.085, 37.422],  // Google HQ (Mountain View)
      endPoint:   [-122.149, 37.484],  // Meta HQ (Menlo Park)
      dataType:   'partnership',
      value:      160,
      color:      '#ec4899',
      colorHex:   0xec4899,
      thickness:  0.18,
      animationSpeed: 2.20,
      displayPriority: 8,
      lodRules: { visibleAtLevels: [6] },
      visibilityState: 0,
    },
    {
      id: 'co6-vw-bmw',
      startPoint: [10.806, 52.422],    // VW HQ (Wolfsburg)
      endPoint:   [11.582, 48.135],    // BMW HQ (Munich)
      dataType:   'supply-chain',
      value:      185,
      color:      '#f97316',
      colorHex:   0xf97316,
      thickness:  0.19,
      animationSpeed: 2.12,
      displayPriority: 8,
      lodRules: { visibleAtLevels: [6] },
      visibilityState: 0,
    },
    {
      id: 'co6-hsbc-stan',
      startPoint: [-0.080, 51.515],    // HSBC HQ (London City)
      endPoint:   [-0.091, 51.509],    // Standard Chartered HQ
      dataType:   'capital',
      value:      240,
      color:      '#14b8a6',
      colorHex:   0x14b8a6,
      thickness:  0.21,
      animationSpeed: 2.05,
      displayPriority: 9,
      lodRules: { visibleAtLevels: [6] },
      visibilityState: 0,
    },
    {
      id: 'co6-sam-hai',
      startPoint: [126.978, 37.566],   // Samsung (Seoul)
      endPoint:   [128.681, 35.871],   // Hainil (Changwon)
      dataType:   'supply-chain',
      value:      175,
      color:      '#f97316',
      colorHex:   0xf97316,
      thickness:  0.19,
      animationSpeed: 2.18,
      displayPriority: 8,
      lodRules: { visibleAtLevels: [6] },
      visibilityState: 0,
    },
    {
      id: 'co6-ali-ten',
      startPoint: [120.209, 30.246],   // Alibaba HQ (Hangzhou)
      endPoint:   [113.930, 22.533],   // Tencent HQ (Shenzhen)
      dataType:   'data',
      value:      210,
      color:      '#06b6d4',
      colorHex:   0x06b6d4,
      thickness:  0.20,
      animationSpeed: 2.08,
      displayPriority: 9,
      lodRules: { visibleAtLevels: [6] },
      visibilityState: 0,
    },
  ],
}
