import type { FlowObject } from './types'
import type { ZoomLevelId } from '../zoom/types'
import { LOD_FLOWS } from './lodFlows'

// ── Types ─────────────────────────────────────────────────────────────────────

/** Runtime state of a single flow during rendering */
interface FlowState {
  flow: FlowObject
  /** Current fade alpha in [0, 1]; driven by tick() during transitions */
  fadeAlpha: number
  /** Direction of the current fade: +1 = fading in, -1 = fading out, 0 = steady */
  fadeDir: 1 | -1 | 0
}

/** Snapshot returned to the renderer each frame */
export interface FlowSnapshot {
  flow: FlowObject
  fadeAlpha: number
}

// ── Constants ─────────────────────────────────────────────────────────────────

/** Duration in seconds for fade-in and fade-out transitions */
const FADE_IN_DURATION  = 0.6
const FADE_OUT_DURATION = 0.5

// ── FlowEngine ────────────────────────────────────────────────────────────────

/**
 * Manages the lifecycle of LOD-aware FlowObjects as the active zoom level changes.
 *
 * Responsibilities:
 *  - Keep track of which flows are active for the current level.
 *  - Animate fade-in / fade-out transitions between levels.
 *  - Expose `getSnapshot()` so the renderer can read per-flow fade alpha each frame.
 *
 * Architecture:
 *  - All flows are stored in a single `Map<id, FlowState>`.
 *  - When `setLevel()` is called, flows not in the new level begin fading out
 *    while the new level's flows begin fading in.
 *  - `tick(delta)` updates all fade alphas; flows that finish fading out are removed.
 *  - `hasChanged()` lets callers know when geometry needs to be rebuilt.
 */
export class FlowEngine {
  private states = new Map<string, FlowState>()
  private currentLevel: ZoomLevelId = 0
  /** Set to true whenever a flow is added or fully removed; cleared after `getSnapshot()`. */
  private _changed = false

  constructor(initialLevel: ZoomLevelId = 0) {
    this.currentLevel = initialLevel
    // Bootstrap: immediately show level-0 flows at full opacity
    for (const flow of LOD_FLOWS[initialLevel]) {
      this.states.set(flow.id, {
        flow: { ...flow, visibilityState: 1 },
        fadeAlpha: 1,
        fadeDir: 0,
      })
    }
    this._changed = true
  }

  // ── Public API ─────────────────────────────────────────────────────────────

  /**
   * Switch to a new zoom level.
   * Flows that belong only to the old level start fading out;
   * flows that belong only to the new level start fading in;
   * flows shared by both levels remain steady.
   */
  setLevel(level: ZoomLevelId): void {
    if (level === this.currentLevel) return
    this.currentLevel = level

    const incoming = LOD_FLOWS[level]
    const incomingIds = new Set(incoming.map((f) => f.id))

    // Mark outgoing flows for fade-out
    for (const [id, state] of this.states) {
      if (!incomingIds.has(id)) {
        state.fadeDir = -1
      }
    }

    // Add incoming flows that aren't already present
    for (const flow of incoming) {
      if (!this.states.has(flow.id)) {
        this.states.set(flow.id, {
          flow: { ...flow, visibilityState: 0 },
          fadeAlpha: 0,
          fadeDir: 1,
        })
        this._changed = true
      } else {
        // Flow is already present (e.g. a flow shared across levels); keep it
        const existing = this.states.get(flow.id)!
        if (existing.fadeDir === -1) {
          // Was fading out — reverse to fade in
          existing.fadeDir = 1
        }
      }
    }
  }

  /**
   * Advance the fade animation for all active flows.
   * Call once per animation frame with the elapsed time in seconds.
   */
  tick(delta: number): void {
    const toRemove: string[] = []

    for (const [id, state] of this.states) {
      if (state.fadeDir === 1) {
        state.fadeAlpha = Math.min(1, state.fadeAlpha + delta / FADE_IN_DURATION)
        state.flow.visibilityState = state.fadeAlpha
        if (state.fadeAlpha >= 1) {
          state.fadeAlpha = 1
          state.fadeDir  = 0
        }
      } else if (state.fadeDir === -1) {
        state.fadeAlpha = Math.max(0, state.fadeAlpha - delta / FADE_OUT_DURATION)
        state.flow.visibilityState = state.fadeAlpha
        if (state.fadeAlpha <= 0) {
          toRemove.push(id)
        }
      }
    }

    if (toRemove.length > 0) {
      for (const id of toRemove) {
        this.states.delete(id)
      }
      this._changed = true
    }
  }

  /**
   * Returns whether the set of active flows has changed since the last call to
   * `getSnapshot()`.  The renderer should rebuild geometry when this is true.
   */
  hasChanged(): boolean {
    return this._changed
  }

  /**
   * Returns the current frame's flow states — one entry per active flow,
   * including those that are mid-transition.
   * Clears the internal `changed` flag.
   */
  getSnapshot(): FlowSnapshot[] {
    this._changed = false
    const result: FlowSnapshot[] = []
    for (const state of this.states.values()) {
      result.push({ flow: state.flow, fadeAlpha: state.fadeAlpha })
    }
    return result
  }

  /** Returns only the FlowObject references (without fade state). */
  getActiveFlows(): FlowObject[] {
    return Array.from(this.states.values()).map((s) => s.flow)
  }

  /** Returns the current active zoom level. */
  getLevel(): ZoomLevelId {
    return this.currentLevel
  }
}
