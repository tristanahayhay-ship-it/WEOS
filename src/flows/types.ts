/** Category of capital / economic flow */
export type FlowType = 'trade' | 'investment' | 'debt' | 'aid'

/** Direction from the perspective of sourceCountry */
export type FlowDirection = 'outbound' | 'inbound' | 'bilateral'

/** Arbitrary key-value metadata attached to a flow */
export type FlowMetadata = Record<string, string | number | boolean | null>

/**
 * Represents a single capital / economic flow between two countries.
 * Phase 5 uses mock data only; no real API is wired.
 */
export interface FlowModel {
  /** Unique identifier */
  id: string
  /** ISO alpha-2 code of the origin country */
  sourceCountry: string
  /** ISO alpha-2 code of the destination country */
  targetCountry: string
  /** Category of flow */
  flowType: FlowType
  /** Magnitude — USD billions */
  value: number
  /** Direction from sourceCountry perspective */
  direction: FlowDirection
  /** ISO 8601 timestamp */
  timestamp: string
  /** Optional descriptive metadata */
  metadata: FlowMetadata
}
