import { useEffect, useRef } from 'react'
import type { RefObject } from 'react'
import { Group, Mesh, PerspectiveCamera, Raycaster, Vector2, Vector3 } from 'three'
import { cartesianToLngLat, EARTH_RADIUS } from '../utils/globe'
import {
  findCountryAtPoint,
  createHoverMesh,
  createSelectedMesh,
  hoverMaterial,
  selectedMaterial,
} from '../utils/countryGeometry'
import { useCountryStore } from '../stores/countryStore'

/**
 * Intersect a ray (origin + normalised direction) with a unit sphere centred at the origin.
 * Returns the closest intersection point, or null when the ray misses.
 */
function sphereRayIntersect(
  origin: Vector3,
  dir: Vector3,
  radius: number,
): Vector3 | null {
  const b = 2 * origin.dot(dir)
  const c = origin.dot(origin) - radius * radius
  const discriminant = b * b - 4 * c
  if (discriminant < 0) return null

  const t = (-b - Math.sqrt(discriminant)) / 2
  if (t < 0) return null

  return new Vector3(
    origin.x + t * dir.x,
    origin.y + t * dir.y,
    origin.z + t * dir.z,
  )
}

/**
 * Wires country hover and click interactions to the Three.js globe.
 *
 * Minimal contract:
 *  – containerRef  the div that wraps the WebGL canvas
 *  – cameraRef     the PerspectiveCamera used to render the scene
 *  – worldRef      the Group that represents the globe (carries the axial tilt)
 *
 * The hook adds/removes country highlight meshes directly on the world Group
 * and writes hover/select state to useCountryStore.
 */
export function useCountryInteraction(
  containerRef: RefObject<HTMLDivElement | null>,
  cameraRef: RefObject<PerspectiveCamera | null>,
  worldRef: RefObject<Group | null>,
): void {
  const setHoveredCountry = useCountryStore((s) => s.setHoveredCountry)
  const selectCountry = useCountryStore((s) => s.selectCountry)
  const selectedCountry = useCountryStore((s) => s.selectedCountry)

  // Three.js objects managed without React re-renders
  const hoverMeshRef = useRef<Mesh | null>(null)
  const selectedMeshRef = useRef<Mesh | null>(null)
  const raycaster = useRef(new Raycaster())
  const ndcMouse = useRef(new Vector2())
  // Maps each hover Mesh to its country numeric code — avoids mutating Three.js objects
  const hoverMeshCode = useRef(new WeakMap<Mesh, number>())

  // ── Sync selected-country mesh whenever the store value changes ────────────
  useEffect(() => {
    const world = worldRef.current

    // Remove old selected mesh
    if (selectedMeshRef.current && world) {
      world.remove(selectedMeshRef.current)
      selectedMeshRef.current = null
    }

    if (selectedCountry && world) {
      const mesh = createSelectedMesh(selectedCountry, selectedMaterial)
      if (mesh) {
        world.add(mesh)
        selectedMeshRef.current = mesh
      }
    }
  }, [selectedCountry, worldRef])

  // ── Mouse event listeners ─────────────────────────────────────────────────
  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const getLngLat = (event: MouseEvent): [number, number] | null => {
      const camera = cameraRef.current
      const world = worldRef.current
      if (!camera || !world) return null

      const rect = container.getBoundingClientRect()
      ndcMouse.current.set(
        ((event.clientX - rect.left) / rect.width) * 2 - 1,
        -((event.clientY - rect.top) / rect.height) * 2 + 1,
      )

      raycaster.current.setFromCamera(ndcMouse.current, camera)

      // Transform ray into world-Group local space (accounts for axial tilt)
      const worldInverse = world.matrixWorld.clone().invert()
      const localOrigin = raycaster.current.ray.origin
        .clone()
        .applyMatrix4(worldInverse)
      const localDir = raycaster.current.ray.direction
        .clone()
        .transformDirection(worldInverse)
        .normalize()

      const hit = sphereRayIntersect(localOrigin, localDir, EARTH_RADIUS)
      if (!hit) return null

      return cartesianToLngLat(hit.x, hit.y, hit.z)
    }

    const onMouseMove = (event: MouseEvent) => {
      const world = worldRef.current
      const coords = getLngLat(event)

      if (!coords) {
        // Remove hover mesh
        if (hoverMeshRef.current && world) {
          world.remove(hoverMeshRef.current)
          hoverMeshRef.current = null
        }
        setHoveredCountry(null)
        return
      }

      const [lng, lat] = coords
      const country = findCountryAtPoint(lng, lat)

      // Update hover mesh only when the country changes
      const currentHover = hoverMeshRef.current
      const currentCode = currentHover ? hoverMeshCode.current.get(currentHover) : undefined

      if (country?.numericCode !== currentCode) {
        if (currentHover && world) {
          world.remove(currentHover)
          hoverMeshRef.current = null
        }

        if (country && world) {
          const mesh = createHoverMesh(country, hoverMaterial)
          if (mesh) {
            hoverMeshCode.current.set(mesh, country.numericCode)
            world.add(mesh)
            hoverMeshRef.current = mesh
          }
        }
      }

      setHoveredCountry(country, { x: event.clientX, y: event.clientY })
    }

    const onClick = (event: MouseEvent) => {
      const coords = getLngLat(event)
      if (!coords) {
        selectCountry(null)
        return
      }

      const [lng, lat] = coords
      const country = findCountryAtPoint(lng, lat)
      selectCountry(country)
    }

    container.addEventListener('mousemove', onMouseMove)
    container.addEventListener('click', onClick)

    return () => {
      container.removeEventListener('mousemove', onMouseMove)
      container.removeEventListener('click', onClick)

      // Clean up Three.js scene objects
      const world = worldRef.current
      if (world) {
        if (hoverMeshRef.current) world.remove(hoverMeshRef.current)
        if (selectedMeshRef.current) world.remove(selectedMeshRef.current)
      }
      hoverMeshRef.current = null
      selectedMeshRef.current = null

      setHoveredCountry(null)
    }
  }, [containerRef, cameraRef, worldRef, setHoveredCountry, selectCountry])
}
