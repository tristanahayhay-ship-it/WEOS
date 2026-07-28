/**
 * Lightweight in-memory cache with per-entry TTL.
 * Used by `ProviderManager` to avoid redundant API calls
 * within a single browsing session.
 */

interface CacheEntry<T> {
  value: T
  expiresAt: number
}

export class SimpleCache<T> {
  private readonly store = new Map<string, CacheEntry<T>>()
  private readonly ttlMs: number

  constructor(ttlMs: number) {
    this.ttlMs = ttlMs
  }

  get(key: string): T | undefined {
    const entry = this.store.get(key)
    if (entry === undefined) return undefined
    if (Date.now() > entry.expiresAt) {
      this.store.delete(key)
      return undefined
    }
    return entry.value
  }

  set(key: string, value: T): void {
    this.store.set(key, { value, expiresAt: Date.now() + this.ttlMs })
  }

  has(key: string): boolean {
    return this.get(key) !== undefined
  }

  clear(): void {
    this.store.clear()
  }
}
