import { ref, watch, onBeforeUnmount } from 'vue'

// Angka naik halus ke nilai target (ease-out). Tanpa animasi bila reduced-motion.
export function useCountUp(source, duration = 900) {
  const shown = ref(0)
  let raf = 0
  const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches

  watch(source, (to) => {
    cancelAnimationFrame(raf)
    const from = shown.value
    const target = Number(to) || 0
    if (reduce || from === target) { shown.value = target; return }
    const t0 = performance.now()
    const step = (now) => {
      const p = Math.min(1, (now - t0) / duration)
      shown.value = Math.round(from + (target - from) * (1 - Math.pow(1 - p, 3)))
      if (p < 1) raf = requestAnimationFrame(step)
    }
    raf = requestAnimationFrame(step)
  }, { immediate: true })

  onBeforeUnmount(() => cancelAnimationFrame(raf))
  return shown
}
