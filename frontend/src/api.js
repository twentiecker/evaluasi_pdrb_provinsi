// Pembungkus fetch ke backend FastAPI.
async function request(url, options) {
  const res = await fetch(url, options)
  let data = null
  try { data = await res.json() } catch { /* body kosong / bukan JSON */ }
  if (!res.ok) {
    let detail = data?.detail
    if (Array.isArray(detail)) detail = detail.map((d) => d.msg).join('; ') // error validasi 422
    throw new Error(detail || `Permintaan gagal (HTTP ${res.status})`)
  }
  return data
}

export function inspectFile(file) {
  const fd = new FormData()
  fd.append('file', file)
  return request('/api/inspect', { method: 'POST', body: fd })
}

export function startRun(uploadId, periode) {
  return request('/api/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ upload_id: uploadId, periode }),
  })
}

export const getJob = (id) => request(`/api/jobs/${id}`)
export const getSummary = (id) => request(`/api/jobs/${id}/summary`)

export function getResults(id, { kabkot = [], komponen = [], kategori = [], q = '', page = 1, pageSize = 50 }) {
  const p = new URLSearchParams({ page, page_size: pageSize })
  kabkot.forEach((v) => p.append('kabkot', v))
  komponen.forEach((v) => p.append('komponen', v))
  kategori.forEach((v) => p.append('kategori', v))
  if (q) p.set('q', q)
  return request(`/api/jobs/${id}/results?${p}`)
}

export const downloadUrl = (id) => `/api/jobs/${id}/download`
