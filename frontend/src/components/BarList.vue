<script setup>
import { computed, onMounted, ref } from 'vue'

const props = defineProps({
  title: String,
  hint: String,
  items: { type: Array, default: () => [] }, // [{ label, count }]
  active: { type: String, default: '' },
  maxHeight: { type: String, default: '420px' }, // lebih panjang dari ini -> bisa digulir
})
const emit = defineEmits(['pick'])

// Batang tumbuh dari 0 saat pertama tampil.
const ready = ref(false)
onMounted(() => requestAnimationFrame(() => requestAnimationFrame(() => { ready.value = true })))

const max = computed(() => Math.max(1, ...props.items.map((i) => i.count)))
const fmt = (n) => Number(n).toLocaleString('id-ID')
</script>

<template>
  <section class="bl">
    <h3>{{ title }}</h3>
    <p v-if="hint" class="hint">{{ hint }}</p>
    <div class="scroll" :style="{ maxHeight }">
    <ul>
      <li v-for="(i, idx) in items" :key="i.label">
        <button class="row" :class="{ on: i.label === active }" :aria-pressed="i.label === active" @click="emit('pick', i.label)">
          <span class="lab" :title="i.label">{{ i.label }}</span>
          <span class="num">{{ fmt(i.count) }}</span>
          <span class="track"><i :style="{ width: ready ? (i.count / max) * 100 + '%' : '0%', transitionDelay: idx * 35 + 'ms' }"></i></span>
        </button>
      </li>
    </ul>
    </div>
  </section>
</template>

<style scoped>
.bl h3 { font-size: 17px; }
.hint { margin: 2px 0 10px; color: var(--mut); font-size: 13px; }
/* Padding + margin negatif memberi ruang untuk latar saat hover/aktif agar tidak terpotong. */
.scroll { margin: 10px -8px 0; padding: 0 8px; overflow-y: auto; scrollbar-width: thin; scrollbar-color: var(--line) transparent; overscroll-behavior: contain; }
.scroll::-webkit-scrollbar { width: 8px; }
.scroll::-webkit-scrollbar-thumb { background: var(--line); border-radius: 4px; }
.scroll::-webkit-scrollbar-thumb:hover { background: var(--mut); }
ul { list-style: none; margin: 0; padding: 0; }
.row {
  width: 100%; display: grid; grid-template-columns: 1fr auto; gap: 2px 10px; text-align: left;
  background: none; border: 0; padding: 6px 8px; margin: 0 -8px; border-radius: 8px; transition: background-color .15s;
}
.row:hover { background: color-mix(in oklab, var(--pri) 8%, transparent); }
.row.on { background: color-mix(in oklab, var(--pri) 14%, transparent); }
.lab { font-size: 13.5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.num { font-size: 13px; color: var(--mut); font-variant-numeric: tabular-nums; }
.track { grid-column: 1 / -1; height: 6px; background: var(--line); border-radius: 3px; overflow: hidden; }
.track i { display: block; height: 100%; border-radius: 3px; background: var(--pri); transition: width .7s cubic-bezier(.2, .8, .2, 1); }
.row.on .track i { background: var(--heat-hi); }
</style>
