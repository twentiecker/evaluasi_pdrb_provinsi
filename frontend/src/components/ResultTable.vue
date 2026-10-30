<script setup>
import { computed, ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { getResults } from '../api'
import { tone } from '../data/provinces'

// Dibuat ulang per job (lihat :key di App.vue). Filter dibagi dengan peta dan grafik batang lewat v-model.
const props = defineProps({ jobId: { type: String, required: true }, options: { type: Object, required: true } })
const kabkot = defineModel('kabkot', { type: Array, default: () => [] })
const komponen = defineModel('komponen', { type: Array, default: () => [] })
const kategori = defineModel('kategori', { type: Array, default: () => [] })

const q = ref('')
const page = ref(1)
const rows = ref([])
const total = ref(0)
const pages = ref(1)
const loading = ref(false)
const error = ref('')

// Dropdown satu pilihan <-> array di model.
const one = (m) => computed({ get: () => m.value[0] ?? '', set: (v) => { m.value = v ? [v] : [] } })
const selKab = one(kabkot)
const selKom = one(komponen)
const selKat = one(kategori)
const active = computed(() => kabkot.value.length || komponen.value.length || kategori.value.length || q.value.trim())

let reqId = 0
async function load() {
  const my = ++reqId // abaikan respons usang bila filter berubah cepat
  loading.value = true
  error.value = ''
  try {
    const r = await getResults(props.jobId, {
      kabkot: kabkot.value, komponen: komponen.value, kategori: kategori.value, q: q.value.trim(), page: page.value,
    })
    if (my !== reqId) return
    rows.value = r.rows; total.value = r.total; pages.value = r.pages; page.value = r.page
  } catch (e) {
    if (my === reqId) error.value = e.message
  } finally {
    if (my === reqId) loading.value = false
  }
}

watch([kabkot, komponen, kategori], () => { page.value = 1; load() })
let t
watch(q, () => { clearTimeout(t); t = setTimeout(() => { page.value = 1; load() }, 300) })
onBeforeUnmount(() => clearTimeout(t))

function reset() { kabkot.value = []; komponen.value = []; kategori.value = []; q.value = '' }
function go(d) { page.value += d; load() }
const fmt = (n) => Number(n).toLocaleString('id-ID')
const num = (v) => (v == null ? '' : Number(v).toFixed(2))
onMounted(load)
</script>

<template>
  <section id="detail" class="detail">
    <div class="head">
      <h3>Detail temuan</h3>
      <span class="count">{{ fmt(total) }} baris</span>
    </div>

    <div class="filters">
      <select v-model="selKab" class="field" aria-label="Provinsi">
        <option value="">Semua provinsi</option>
        <option v-for="o in options.kabkot" :key="o" :value="o">{{ o }}</option>
      </select>
      <select v-model="selKom" class="field" aria-label="Komponen">
        <option value="">Semua komponen</option>
        <option v-for="o in options.komponen" :key="o" :value="o">{{ o }}</option>
      </select>
      <select v-model="selKat" class="field" aria-label="Jenis evaluasi">
        <option value="">Semua jenis evaluasi</option>
        <option v-for="o in options.kategori" :key="o" :value="o">{{ o }}</option>
      </select>
      <input v-model="q" class="field" type="search" placeholder="Cari teks evaluasi atau indikator" aria-label="Cari" />
      <button v-if="active" class="btn ghost" @click="reset">Hapus filter</button>
    </div>

    <p v-if="error" class="note err">{{ error }}</p>
    <div class="tw" :class="{ loading }">
      <table>
        <thead>
          <tr><th>No</th><th>Provinsi</th><th>Komponen</th><th>Indikator</th><th class="r">Nilai</th><th>Evaluasi</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in rows" :key="r.no">
            <td class="mut">{{ r.no }}</td>
            <td>{{ r.kabkot }}</td>
            <td>{{ r.komponen }}</td>
            <td class="mut">{{ r.indikator }}</td>
            <td class="r num">{{ num(r.nilai) }}</td>
            <td><span class="chip" :class="tone(r.evaluasi)">{{ r.evaluasi }}</span></td>
          </tr>
          <tr v-if="!rows.length && !loading">
            <td colspan="6" class="empty">Tidak ada temuan untuk filter ini. Hapus filter untuk melihat semua baris.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pager">
      <button class="btn ghost" :disabled="page <= 1 || loading" @click="go(-1)">Sebelumnya</button>
      <span>Halaman {{ page }} dari {{ pages }}</span>
      <button class="btn ghost" :disabled="page >= pages || loading" @click="go(1)">Berikutnya</button>
    </div>
  </section>
</template>

<style scoped>
.head { display: flex; align-items: baseline; gap: 12px; margin-bottom: 12px; }
.head h3 { font-size: 20px; }
.count { color: var(--mut); font-size: 14px; }
.filters { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)) auto; gap: 10px; margin-bottom: 14px; }
@media (max-width: 1000px) { .filters { grid-template-columns: 1fr 1fr; } }
@media (max-width: 560px) { .filters { grid-template-columns: 1fr; } }
.tw { overflow: auto; max-height: 560px; background: var(--surface); border-radius: 14px; box-shadow: 0 0 0 1px var(--line); transition: opacity .15s; }
.tw.loading { opacity: .55; }
table { border-collapse: collapse; width: 100%; font-size: 13.5px; }
th { position: sticky; top: 0; background: var(--surface); text-align: left; font-weight: 600; font-size: 13px; color: var(--mut); padding: 11px 14px; box-shadow: 0 1px 0 var(--line); z-index: 1; }
td { padding: 10px 14px; border-bottom: 1px solid var(--line); vertical-align: top; }
tbody tr { transition: background-color .12s; }
tbody tr:hover { background: color-mix(in oklab, var(--pri) 6%, transparent); }
.r { text-align: right; }
.num { font-variant-numeric: tabular-nums; font-weight: 600; }
.mut { color: var(--mut); }
.empty { text-align: center; color: var(--mut); padding: 36px 14px; }

.chip { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 12.5px; font-weight: 500; line-height: 1.6; }
.chip.hot { background: #fde1db; color: #a1291a; }
.chip.amber { background: #fdf0cc; color: #7c5a05; }
.chip.teal { background: #d4f1ef; color: #0b6466; }
.chip.blue { background: #dbe8fb; color: #1f4f9a; }
.chip.violet { background: #e9e2fb; color: #5a3ba8; }
.chip.slate { background: #e3e9ec; color: #3d5360; }
[data-theme='dark'] .chip.hot { background: #4a201a; color: #ffb3a6; }
[data-theme='dark'] .chip.amber { background: #473a12; color: #f6d77f; }
[data-theme='dark'] .chip.teal { background: #11403f; color: #8fe0dc; }
[data-theme='dark'] .chip.blue { background: #1b3358; color: #a9c8fb; }
[data-theme='dark'] .chip.violet { background: #33285a; color: #cbbdf6; }
[data-theme='dark'] .chip.slate { background: #213744; color: #b4c6cf; }

.pager { display: flex; gap: 14px; align-items: center; justify-content: flex-end; margin-top: 14px; color: var(--mut); font-size: 14px; }
.pager .btn { padding: 8px 14px; }
</style>
