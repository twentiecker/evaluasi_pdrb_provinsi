<script setup>
import { ref, computed } from 'vue'
import { useEvaluation } from '../composables/useEvaluation'
import { useTheme } from '../composables/useTheme'

const { state, running, canRun, percent, upload, run } = useEvaluation()
const { theme, toggle } = useTheme()

const input = ref(null)
const over = ref(false)

const uploadOk = computed(() => !!state.upload && !state.uploadError)
const finished = computed(() => !!state.summary)

function onDrop(e) {
  over.value = false
  const f = e.dataTransfer.files?.[0]
  if (f) upload(f)
}
function onPick(e) {
  const f = e.target.files?.[0]
  if (f) upload(f)
  e.target.value = '' // izinkan memilih file yang sama lagi
}
</script>

<template>
  <aside class="side">
    <div class="brand">
      <svg viewBox="0 0 32 32" width="34" height="34" aria-hidden="true">
        <rect x="2" y="2" width="12" height="12" rx="3" fill="#0f8b8d" />
        <rect x="18" y="2" width="12" height="12" rx="3" fill="#f7dda0" />
        <rect x="2" y="18" width="12" height="12" rx="3" fill="#f7dda0" opacity=".55" />
        <rect x="18" y="18" width="12" height="12" rx="3" fill="#d9432b" />
      </svg>
      <div>
        <strong>Evaluasi PDRB</strong>
        <span>Triwulanan, tingkat provinsi</span>
      </div>
    </div>

    <ol class="steps">
      <li class="step" :class="{ done: uploadOk }">
        <span class="mk"><svg v-if="uploadOk" viewBox="0 0 16 16" width="14" height="14"><path d="M3 8.5l3.2 3L13 4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" /></svg><template v-else>1</template></span>
        <div class="body">
          <h2>Unggah file Excel</h2>
          <div
            class="drop" :class="{ over, has: uploadOk }" role="button" tabindex="0"
            @click="input.click()" @keydown.enter="input.click()"
            @dragover.prevent="over = true" @dragenter.prevent="over = true"
            @dragleave.prevent="over = false" @drop.prevent="onDrop"
          >
            <template v-if="state.uploading">Membaca file…</template>
            <template v-else-if="uploadOk">
              <b>{{ state.upload.filename }}</b>
              <small>{{ state.upload.sheets.length }} sheet, {{ state.upload.periods.length }} periode. Klik untuk ganti.</small>
            </template>
            <template v-else>Tarik file .xlsx ke sini atau klik untuk memilih</template>
            <input ref="input" type="file" accept=".xlsx" hidden @change="onPick" />
          </div>
          <p v-if="state.uploadError" class="note err">{{ state.uploadError }}</p>
        </div>
      </li>

      <li class="step" :class="{ done: uploadOk && !!state.periode && (running || finished), locked: !uploadOk }">
        <span class="mk"><svg v-if="uploadOk && !!state.periode && (running || finished)" viewBox="0 0 16 16" width="14" height="14"><path d="M3 8.5l3.2 3L13 4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" /></svg><template v-else>2</template></span>
        <div class="body">
          <h2>Pilih periode</h2>
          <select v-model="state.periode" class="field dark" :disabled="!uploadOk || running" aria-label="Periode evaluasi">
            <option v-if="!uploadOk" value="">Menunggu file</option>
            <option v-for="p in state.upload?.periods ?? []" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>
      </li>

      <li class="step" :class="{ done: finished, locked: !uploadOk }">
        <span class="mk"><svg v-if="finished" viewBox="0 0 16 16" width="14" height="14"><path d="M3 8.5l3.2 3L13 4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" /></svg><template v-else>3</template></span>
        <div class="body">
          <h2>Jalankan evaluasi</h2>
          <button class="btn go" :disabled="!canRun" @click="run">
            {{ running ? 'Memproses…' : finished ? 'Jalankan ulang' : 'Jalankan evaluasi' }}
          </button>
          <div v-if="running" class="prog" role="progressbar" :aria-valuenow="percent" aria-valuemin="0" aria-valuemax="100">
            <div class="bar"><i :style="{ width: percent + '%' }"></i></div>
            <small>{{ state.job.status === 'queued' ? 'Menunggu antrian' : `Sel ${state.job.current} dari ${state.job.total}` }}</small>
          </div>
          <p v-if="state.runError" class="note err">{{ state.runError }}</p>
        </div>
      </li>
    </ol>

    <button class="theme" @click="toggle" :aria-label="theme === 'dark' ? 'Pakai tema terang' : 'Pakai tema gelap'">
      {{ theme === 'dark' ? 'Tema terang' : 'Tema gelap' }}
    </button>
  </aside>
</template>

<style scoped>
.side {
  background: var(--side); color: var(--side-fg); padding: 26px 22px; display: flex; flex-direction: column; gap: 30px;
  position: sticky; top: 0; height: 100vh; overflow-y: auto;
}
.brand { display: flex; gap: 12px; align-items: center; }
.brand strong { display: block; font-family: var(--display); font-size: 18px; letter-spacing: -0.01em; }
.brand span { font-size: 12.5px; color: var(--side-mut); }

.steps { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; }
.step { display: grid; grid-template-columns: 28px 1fr; gap: 14px; padding-bottom: 26px; position: relative; transition: opacity .25s; }
.step:last-child { padding-bottom: 0; }
.step::before { content: ''; position: absolute; left: 13px; top: 30px; bottom: 2px; width: 2px; background: var(--side-line); }
.step:last-child::before { display: none; }
.step.locked { opacity: .45; }
.mk {
  width: 28px; height: 28px; border-radius: 50%; display: grid; place-items: center; font-size: 13px; font-weight: 700;
  background: var(--side-line); color: var(--side-fg); transition: background-color .25s, color .25s;
}
.step.done .mk { background: var(--pri); color: var(--on-pri); }
.body h2 { font-size: 15px; margin: 3px 0 10px; font-weight: 600; }
.body { min-width: 0; display: flex; flex-direction: column; }

.drop {
  border: 1.5px dashed #3a5a69; border-radius: 12px; padding: 16px 12px; text-align: center; font-size: 13.5px;
  color: var(--side-mut); cursor: pointer; transition: border-color .15s, background-color .15s, color .15s;
  display: flex; flex-direction: column; gap: 2px; align-items: center;
}
.drop:hover, .drop.over { border-color: var(--pri); color: var(--side-fg); background: rgba(15, 139, 141, .12); }
.drop.has { border-style: solid; border-color: var(--side-line); color: var(--side-fg); }
.drop b { word-break: break-all; font-weight: 600; }
.drop small { color: var(--side-mut); font-size: 12px; }

.field.dark { background: rgba(255, 255, 255, .06); border-color: var(--side-line); color: var(--side-fg); }
.field.dark option { color: #0e2a38; }
.go { width: 100%; }
.prog { margin-top: 12px; }
.bar { height: 6px; background: var(--side-line); border-radius: 4px; overflow: hidden; }
.bar i { display: block; height: 100%; background: linear-gradient(90deg, var(--pri), #f7dda0); transition: width .35s ease; }
.prog small { color: var(--side-mut); font-size: 12px; }
.note { margin: 10px 0 0; }

.theme { margin-top: auto; background: none; border: 1px solid var(--side-line); color: var(--side-mut); border-radius: 8px; padding: 8px 12px; font-size: 13px; transition: color .15s, border-color .15s; }
.theme:hover { color: var(--side-fg); border-color: var(--side-mut); }

@media (max-width: 900px) {
  .side { position: static; height: auto; }
}
</style>
