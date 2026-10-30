<script setup>
import { computed } from 'vue'
import { buildLayout } from '../data/provinces'

const props = defineProps({
  counts: { type: Array, default: () => [] },   // [{ label, count }]
  state: { type: String, default: 'idle' },      // idle | running | done
  selected: { type: String, default: '' },
})
defineEmits(['pick'])

const layout = computed(() => buildLayout(props.counts))
const label = (t) => (t.count ? `${t.name}: ${t.count.toLocaleString('id-ID')} temuan` : `${t.name}: tidak ada temuan`)
</script>

<template>
  <div class="map" :class="state">
    <div v-for="g in layout.groups" :key="g.name" class="island">
      <div class="iname">{{ g.name }}</div>
      <div class="tiles">
        <button
          v-for="t in g.tiles" :key="t.key" class="tile"
          :class="{ zero: !t.count, hot: t.t > 0.8, sel: t.actual && t.actual === selected }"
          :style="{ '--t': t.t, '--i': t.idx }"
          :disabled="!t.actual" :title="label(t)" :aria-label="label(t)" :aria-pressed="t.actual === selected"
          @click="$emit('pick', t.actual)"
        >
          <span class="code">{{ t.code }}</span>
          <span class="n">{{ t.count || '' }}</span>
        </button>
      </div>
    </div>
    <div v-if="state === 'done'" class="legend" aria-hidden="true">
      <span>Sedikit</span><i></i><span>Banyak</span>
    </div>
  </div>
</template>

<style scoped>
.map { display: flex; flex-direction: column; gap: 10px; }
.island { display: grid; grid-template-columns: 128px 1fr; gap: 12px; align-items: start; }
.iname { font-size: 13px; color: var(--mut); padding-top: 14px; font-weight: 500; }
.tiles { display: flex; flex-wrap: wrap; gap: 6px; }
.tile {
  --c: color-mix(in oklab, var(--heat-hi) calc(var(--t) * 100%), var(--heat-lo));
  width: 62px; height: 50px; border: 0; border-radius: 9px; padding: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center; line-height: 1.15;
  background: var(--c); color: var(--ink);
  transition: background-color .5s ease calc(var(--i) * 16ms), color .3s ease calc(var(--i) * 16ms),
              transform .15s ease, box-shadow .15s ease;
}
.tile .code { font-size: 11.5px; font-weight: 600; opacity: .8; }
.tile .n { font-family: var(--display); font-size: 15px; font-weight: 700; font-variant-numeric: tabular-nums; min-height: 17px; }
.tile.hot { color: #fff; }
.tile.zero { background: var(--tile0); color: var(--tile0-fg); cursor: default; }
.tile:not(:disabled):hover { transform: translateY(-2px); box-shadow: 0 6px 14px -6px rgba(14, 42, 56, .5); }
.tile.sel { box-shadow: 0 0 0 2px var(--surface), 0 0 0 4px var(--pri); }

/* Belum ada hasil: kotak netral. */
.idle .tile { --t: 0; background: var(--tile0); color: var(--tile0-fg); }
.idle .tile .n { visibility: hidden; }
/* Sedang diproses: gelombang pemindaian (hanya opacity, ringan). */
.running .tile { background: var(--tile0); color: var(--tile0-fg); animation: scan 1.5s ease-in-out infinite; animation-delay: calc(var(--i) * 45ms); }
.running .tile .n { visibility: hidden; }
@keyframes scan { 0%, 100% { opacity: .35; } 50% { opacity: 1; } }

.legend { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--mut); margin-left: 140px; margin-top: 4px; }
.legend i { width: 120px; height: 8px; border-radius: 4px; background: linear-gradient(90deg, var(--heat-lo), var(--heat-hi)); }

@media (max-width: 640px) {
  .island { grid-template-columns: 1fr; gap: 4px; }
  .iname { padding-top: 0; }
  .legend { margin-left: 0; }
}
</style>
