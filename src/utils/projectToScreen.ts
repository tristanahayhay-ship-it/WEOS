import { projectLngLatToCartesian, EARTH_RADIUS } from './globe'
import type { GlobeFrameSnapshot } from '../stores/globeViewStore'

/**
 * Project a geographic coordinate (longitude, latitude) to CSS-pixel screen
 * coordinates using the current globe camera frame snapshot.
 *
 * Returns null when the point is on the back-face of the globe (not visible)
 * or falls outside the clip volume.
 *
 * Matrix layout: Three.js `Matrix4.elements` is column-major, so the transform
 * of a column-vector v by matrix M is:
 *   result.x = M[0]*v.x + M[4]*v.y + M[8]*v.z + M[12]
 *   result.y = M[1]*v.x + M[5]*v.y + M[9]*v.z + M[13]
 *   result.z = M[2]*v.x + M[6]*v.y + M[10]*v.z + M[14]
 */
export function projectToScreen(
  lon: number,
  lat: number,
  frame: GlobeFrameSnapshot,
  altitudeOffset = 0.030,
): { x: number; y: number } | null {
  // 1. Lon/lat → cartesian in globe-group local space
  const [lx, ly, lz] = projectLngLatToCartesian(lon, lat, EARTH_RADIUS + altitudeOffset)

  // 2. Apply world matrix to get scene-space position
  const wm = frame.worldMatrix
  const wx = wm[0] * lx + wm[4] * ly + wm[8]  * lz + wm[12]
  const wy = wm[1] * lx + wm[5] * ly + wm[9]  * lz + wm[13]
  const wz = wm[2] * lx + wm[6] * ly + wm[10] * lz + wm[14]

  // 3. Back-face culling: surface normal in scene space ≈ (wx, wy, wz) for a
  //    unit sphere.  If (cam - surface) · normal ≤ 0, the point faces away.
  const [cx, cy, cz] = frame.cameraWorldPosition
  const toCamX = cx - wx
  const toCamY = cy - wy
  const toCamZ = cz - wz
  if (wx * toCamX + wy * toCamY + wz * toCamZ <= 0) return null

  // 4. Apply view matrix (camera.matrixWorldInverse) → camera space
  const vm = frame.viewMatrix
  const vx = vm[0] * wx + vm[4] * wy + vm[8]  * wz + vm[12]
  const vy = vm[1] * wx + vm[5] * wy + vm[9]  * wz + vm[13]
  const vz = vm[2] * wx + vm[6] * wy + vm[10] * wz + vm[14]

  // 5. Apply projection matrix → clip space
  const pm = frame.projectionMatrix
  const clipX = pm[0] * vx + pm[4] * vy + pm[8]  * vz + pm[12]
  const clipY = pm[1] * vx + pm[5] * vy + pm[9]  * vz + pm[13]
  // const clipZ = pm[2] * vx + pm[6] * vy + pm[10] * vz + pm[14]
  const clipW = pm[3] * vx + pm[7] * vy + pm[11] * vz + pm[15]

  if (clipW <= 0) return null

  // 6. Perspective divide → NDC
  const ndcX = clipX / clipW
  const ndcY = clipY / clipW

  // Clip with small margin for cards that straddle the edge
  if (ndcX < -1.15 || ndcX > 1.15 || ndcY < -1.15 || ndcY > 1.15) return null

  // 7. NDC → CSS pixels (NDC Y is up, screen Y is down)
  return {
    x: (ndcX * 0.5 + 0.5) * frame.viewportWidth,
    y: (1 - (ndcY * 0.5 + 0.5)) * frame.viewportHeight,
  }
}
