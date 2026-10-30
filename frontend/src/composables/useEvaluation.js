import { reactive, computed } from 'vue'
import * as api from '../api'

// State global tunggal (cukup untuk aplikasi satu halaman; tanpa Pinia).
const state = reactive({
  upload: null,        // { upload_id, filename, sheets, missing, periods }
  uploading: false,
  uploadError: '',
  periode: '',
  job: null,           // { id, status, current, total, error, ... }
  runError: '',
  summary: null,
})

let timer = null
const stopPolling = () => { clearTimeout(timer); timer = null }

const running = computed(() => !!state.job && ['queued', 'running'].includes(state.job.status))
const canRun = computed(() =>
  !!state.upload && !state.upload.missing.length && state.upload.periods.length > 0 &&
  !!state.periode && !running.value,
)
const percent = computed(() =>
  state.job && state.job.total ? Math.round((state.job.current / state.job.total) * 100) : 0,
)

async function upload(file) {
  stopPolling()
  Object.assign(state, { upload: null, uploadError: '', job: null, runError: '', summary: null, periode: '', uploading: true })
  try {
    const info = await api.inspectFile(file)
    state.upload = info
    if (info.missing.length) {
      state.uploadError = `Sheet tidak ditemukan: ${info.missing.join(', ')}\nSheet pada file: ${info.sheets.join(', ')}`
    } else if (!info.periods.length) {
      state.uploadError = 'Kolom periode (mis. 2026Q3) tidak terdeteksi pada header tabel.'
    } else {
      state.periode = info.periods[info.periods.length - 1] // default: periode terbaru
    }
  } catch (e) {
    state.uploadError = e.message
  } finally {
    state.uploading = false
  }
}

async function run() {
  state.runError = ''
  state.summary = null
  try {
    state.job = await api.startRun(state.upload.upload_id, state.periode)
    poll()
  } catch (e) {
    state.runError = e.message
  }
}

function poll() {
  stopPolling()
  timer = setTimeout(async () => {
    try {
      const j = await api.getJob(state.job.id)
      state.job = j
      if (j.status === 'done') { state.summary = await api.getSummary(j.id); return }
      if (j.status === 'error') { state.runError = j.error || 'Evaluasi gagal.'; return }
    } catch (e) {
      state.runError = `Koneksi ke server terputus: ${e.message}`
      return
    }
    poll()
  }, 1000)
}

export function useEvaluation() {
  return { state, running, canRun, percent, upload, run, stopPolling }
}
