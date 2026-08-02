/**
 * adminBoundaryApproximator.ts
 *
 * Derives an approximate GeoJSON polygon ring for an administrative division
 * when no actual boundary source is available.
 *
 * Algorithm:
 *   1. Place a regular n-gon centred on the division's geographic centroid.
 *   2. Scale the radius independently on the longitude axis (÷ cos(lat)) so
 *      the result appears as a circle when projected onto a sphere, not an
 *      oval stretched at high latitudes.
 *   3. Close the ring by repeating the first vertex.
 *
 * Usage:
 *   const rings = buildApproximateBoundaryRings([13.4, 52.5], 1.1)
 *   // → [[number, number][]]  (one outer ring, closed)
 *
 * Note: the polygon is a geometric approximation.  It should be replaced with
 * actual administrative boundary data whenever authoritative sources (e.g.
 * Natural Earth admin-1, GADM) are integrated.
 */

const DEFAULT_SEGMENTS = 16

/**
 * Estimate a sensible default radius (in degrees) from the country's total
 * area (km²) and the expected number of divisions, so that the approximated
 * polygons tile the country without overlapping too much.
 *
 *   cell_area  = country_area / n_divisions
 *   cell_radius_km = sqrt(cell_area / π)
 *   cell_radius_deg ≈ cell_radius_km / 111
 */
export function estimateDivisionRadius(countryAreaKm2: number, nDivisions: number): number {
  const cellArea   = countryAreaKm2 / Math.max(1, nDivisions)
  const radiusKm   = Math.sqrt(cellArea / Math.PI)
  return radiusKm / 111
}

/**
 * Build a single closed polygon ring that approximates the extent of an
 * administrative division centred at `center`.
 *
 * @param center    Geographic centroid as [longitude, latitude].
 * @param radiusDeg Approximate radius in decimal degrees (latitude units).
 * @param segments  Number of polygon vertices (default 16; must be ≥ 3).
 * @returns         A GeoJSON-style ring: an array of [lon, lat] pairs where
 *                  the first and last pair are identical (closed ring).
 */
export function buildApproximateBoundaryRing(
  center: [number, number],
  radiusDeg: number,
  segments: number = DEFAULT_SEGMENTS,
): [number, number][] {
  const [lon, lat] = center
  const n = Math.max(3, segments)

  // Longitude scaling — prevents ellipse distortion at non-equatorial latitudes.
  const cosLat = Math.max(0.01, Math.cos((lat * Math.PI) / 180))

  const ring: [number, number][] = []
  for (let i = 0; i < n; i++) {
    const angle = (i / n) * 2 * Math.PI
    const dLon  = (radiusDeg / cosLat) * Math.cos(angle)
    const dLat  = radiusDeg            * Math.sin(angle)
    ring.push([lon + dLon, lat + dLat])
  }
  // Close the ring
  ring.push(ring[0]!)
  return ring
}

/**
 * Convenience wrapper that returns the ring wrapped in an outer array
 * (`[number, number][][]`) matching the `boundaryRings` field type in
 * `AdministrativeDivision`.
 */
export function buildApproximateBoundaryRings(
  center: [number, number],
  radiusDeg: number,
  segments: number = DEFAULT_SEGMENTS,
): [number, number][][] {
  return [buildApproximateBoundaryRing(center, radiusDeg, segments)]
}
