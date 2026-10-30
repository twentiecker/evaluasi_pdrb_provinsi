<script setup>
import { computed, ref, watch, onBeforeUnmount } from 'vue'
import { useEvaluation } from './composables/useEvaluation'
import { downloadUrl } from './api'
import SidePanel from './components/SidePanel.vue'
import ProvinceMap from './components/ProvinceMap.vue'
import KpiStrip from './components/KpiStrip.vue'
import BarList from './components/BarList.vue'
import ResultTable from './components/ResultTable.vue'

const { state, running, stopPolling } = useEvaluation()
onBeforeUnmount(stopPolling)

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
  <div class="shell">
    <SidePanel />

    <main class="stage">
      <header class="top">
        <div>
          <h1>{{ title }}</h1>
          <p>{{ subtitle }}</p>
        </div>
        <a v-if="done" class="btn" :href="downloadUrl(state.job.id)">Unduh Excel</a>
      </header>

      <KpiStrip v-if="done" :total="state.summary.total" :provinces="state.summary.kabkot_unik" :rules="state.summary.jenis_evaluasi" />

      <section class="mapsec">
        <ProvinceMap
          :counts="done ? state.summary.per_kabkot_all : []" :state="mapState" :selected="fProv[0] ?? ''"
          @pick="pickProv"
        />
      </section>

      <template v-if="done">
        <section class="bars">
          <BarList
            title="Aturan yang paling sering terpicu" hint="Klik untuk melihat baris temuannya."
            :items="state.summary.per_kategori" :active="fKat[0] ?? ''" @pick="pickKat"
          />
          <BarList
            title="Komponen dengan temuan terbanyak" hint="15 komponen teratas."
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
.shell { display: grid; grid-template-columns: 320px minmax(0, 1fr); min-height: 100vh; }
@media (max-width: 900px) { .shell { grid-template-columns: 1fr; } }
.stage { padding: 36px clamp(18px, 4vw, 52px) 70px; display: flex; flex-direction: column; gap: 34px; min-width: 0; max-width: 1180px; }
.top { display: flex; justify-content: space-between; gap: 20px; align-items: flex-start; }
.top h1 { font-size: clamp(28px, 4vw, 40px); line-height: 1.1; }
.top p { margin: 8px 0 0; color: var(--mut); max-width: 62ch; }
.mapsec { background: var(--surface); border-radius: 16px; padding: 22px 22px 20px; box-shadow: 0 0 0 1px var(--line); overflow-x: auto; }
.bars { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 40px; }
</style>
