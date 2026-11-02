<script setup>
import { computed, ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useEvaluation } from './composables/useEvaluation'
import { downloadUrl } from './api'
import SidePanel from './components/SidePanel.vue'
import ProvinceMap from './components/ProvinceMap.vue'
import KpiStrip from './components/KpiStrip.vue'
import BarList from './components/BarList.vue'
import ResultTable from './components/ResultTable.vue'

const { state, running, stopPolling } = useEvaluation()

// Panel kiri: ciutkan/buka (diingat), pintasan Ctrl+B.
const KEY = 'pdrb-side-collapsed'
const readCollapsed = () => { try { return localStorage.getItem(KEY) === '1' } catch { return false } }
const collapsed = ref(readCollapsed())
watch(collapsed, (v) => { try { localStorage.setItem(KEY, v ? '1' : '0') } catch { /* abaikan */ } })
const onKey = (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') { e.preventDefault(); collapsed.value = !collapsed.value }
}

// Mode aplikasi desktop (pywebview): simpan file lewat dialog "Simpan sebagai".
const desktop = ref(!!window.pywebview)
const onReady = () => { desktop.value = true }
const saveMsg = ref('')
onMounted(() => {
  window.addEventListener('keydown', onKey)
  window.addEventListener('pywebviewready', onReady)
})
onBeforeUnmount(() => {
  stopPolling()
  window.removeEventListener('keydown', onKey)
  window.removeEventListener('pywebviewready', onReady)
})

async function onDownload(e) {
  const bridge = window.pywebview?.api
  if (!bridge?.save_excel) return // browser biasa: biarkan tautan mengunduh seperti biasa
  e.preventDefault()
  try {
    const r = await bridge.save_excel(state.job.id)
    saveMsg.value = r.ok ? `Tersimpan di ${r.path}` : r.cancelled ? '' : r.error || 'File gagal disimpan.'
  } catch (err) {
    saveMsg.value = `File gagal disimpan: ${err.message}`
  }
}
const openFolder = () => window.pywebview?.api?.open_output_folder()

const done = computed(() => !!state.summary)
const mapState = computed(() => (running.value ? 'running' : done.value ? 'done' : 'idle'))

const title = computed(() => {
  if (done.value) return `Temuan evaluasi ${state.job.periode}`
  if (running.value) return `Memeriksa data ${state.job.periode}`
  return 'Evaluasi PDRB provinsi'
})
const subtitle = computed(() => {
  if (done.value) return 'Klik kotak provinsi atau batang di bawah untuk menyaring tabel temuan.'
  if (running.value) return 'Notebook sedang menjalankan seluruh aturan. Hasil muncul otomatis setelah selesai.'
  return 'Unggah file sumber, pilih periode, lalu jalankan evaluasi. Temuan per provinsi akan tampil di peta kotak ini.'
})

// Filter bersama: peta, batang, dan tabel.
const fProv = ref([])
const fKom = ref([])
const fKat = ref([])
watch(() => state.job?.id, () => { fProv.value = []; fKom.value = []; fKat.value = [] })

function focusTable() { document.getElementById('detail')?.scrollIntoView({ behavior: 'smooth', block: 'start' }) }
// Klik nilai yang sama lagi = hapus filter. (Ref dipakai langsung di sini; di template ref otomatis di-unwrap.)
function pick(model, v) {
  model.value = model.value[0] === v ? [] : [v]
  if (model.value.length) focusTable()
}
const pickProv = (v) => pick(fProv, v)
const pickKom = (v) => pick(fKom, v)
const pickKat = (v) => pick(fKat, v)
</script>

<template>
  <div class="shell" :style="{ '--side-w': collapsed ? '68px' : '320px' }">
    <SidePanel v-model:collapsed="collapsed" />

    <main class="stage">
      <header class="top">
        <div>
          <h1>{{ title }}</h1>
          <p>{{ subtitle }}</p>
        </div>
        <div v-if="done" class="actions">
          <button v-if="desktop" class="btn ghost" @click="openFolder">Buka folder hasil</button>
          <a class="btn" :href="downloadUrl(state.job.id)" @click="onDownload">Unduh Excel</a>
        </div>
      </header>
      <p v-if="saveMsg" class="note ok">{{ saveMsg }}</p>

      <KpiStrip v-if="done" :total="state.summary.total" :provinces="state.summary.kabkot_unik" :evaluations="state.summary.jenis_evaluasi" :components="state.summary.komponen_unik" />

      <section class="mapsec">
        <ProvinceMap
          :counts="done ? state.summary.per_kabkot_all : []" :state="mapState" :selected="fProv[0] ?? ''"
          @pick="pickProv"
        />
      </section>

      <template v-if="done">
        <section class="bars">
          <BarList
            title="Temuan per jenis evaluasi" hint="Urut abjad. Klik untuk melihat baris temuannya."
            :items="state.summary.per_kategori" :active="fKat[0] ?? ''" @pick="pickKat"
          />
          <BarList
            title="Temuan per komponen" hint="Urut abjad. Klik untuk melihat baris temuannya."
            :items="state.summary.per_komponen" :active="fKom[0] ?? ''" @pick="pickKom"
          />
        </section>

        <ResultTable
          :key="state.job.id" :job-id="state.job.id" :options="state.summary.opsi"
          v-model:kabkot="fProv" v-model:komponen="fKom" v-model:kategori="fKat"
        />
      </template>
    </main>
  </div>
</template>

<style scoped>
.shell {
  --side-w: 320px;
  display: grid; grid-template-columns: var(--side-w) minmax(0, 1fr); min-height: 100vh;
  transition: grid-template-columns .28s ease;
}
@media (max-width: 900px) { .shell { grid-template-columns: 1fr; } }
.stage { padding: 36px clamp(18px, 4vw, 52px) 70px; display: flex; flex-direction: column; gap: 34px; min-width: 0; max-width: 1180px; }
.top { display: flex; justify-content: space-between; gap: 20px; align-items: flex-start; }
.top h1 { font-size: clamp(28px, 4vw, 40px); line-height: 1.1; }
.actions { display: flex; gap: 10px; flex: none; }
.top p { margin: 8px 0 0; color: var(--mut); max-width: 62ch; }
.mapsec { background: var(--surface); border-radius: 16px; padding: 22px 22px 20px; box-shadow: 0 0 0 1px var(--line); overflow-x: auto; }
.bars { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 40px; align-items: start; }
</style>
