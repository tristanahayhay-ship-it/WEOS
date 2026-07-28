import { useEffect, useRef, useState } from 'react'

interface ElementSize {
  width: number
  height: number
}

function measureElement(element: HTMLElement): ElementSize {
  const { width, height } = element.getBoundingClientRect()
  return { width, height }
}

export function useElementSize<T extends HTMLElement>() {
  const ref = useRef<T | null>(null)
  const [size, setSize] = useState<ElementSize | null>(null)

  useEffect(() => {
    const element = ref.current

    if (!element) {
      return
    }

    const updateSize = () => {
      setSize(measureElement(element))
    }

    updateSize()

    if (typeof ResizeObserver === 'undefined') {
      window.addEventListener('resize', updateSize)

      return () => {
        window.removeEventListener('resize', updateSize)
      }
    }

    const observer = new ResizeObserver(updateSize)
    observer.observe(element)

    return () => {
      observer.disconnect()
    }
  }, [])

  return { ref, size }
}
