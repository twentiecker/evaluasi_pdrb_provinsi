// 38 provinsi dikelompokkan per pulau (urutan sama dengan tabel sumber).
export const ISLANDS = [
  { name: 'Sumatra', items: [['Aceh', 'ACE'], ['Sumatera Utara', 'SUT'], ['Sumatera Barat', 'SBR'], ['Riau', 'RIA'], ['Jambi', 'JMB'], ['Sumatera Selatan', 'SSL'], ['Bengkulu', 'BKL'], ['Lampung', 'LPG'], ['Kepulauan Bangka Belitung', 'BBL'], ['Kepulauan Riau', 'KRI']] },
  { name: 'Jawa', items: [['DKI Jakarta', 'JKT'], ['Jawa Barat', 'JBR'], ['Jawa Tengah', 'JTG'], ['DI Yogyakarta', 'DIY'], ['Jawa Timur', 'JTM'], ['Banten', 'BTN']] },
  { name: 'Bali & Nusa Tenggara', items: [['Bali', 'BAL'], ['Nusa Tenggara Barat', 'NTB'], ['Nusa Tenggara Timur', 'NTT']] },
  { name: 'Kalimantan', items: [['Kalimantan Barat', 'KBR'], ['Kalimantan Tengah', 'KTG'], ['Kalimantan Selatan', 'KSL'], ['Kalimantan Timur', 'KTM'], ['Kalimantan Utara', 'KLU']] },
  { name: 'Sulawesi', items: [['Sulawesi Utara', 'SLU'], ['Sulawesi Tengah', 'STG'], ['Sulawesi Selatan', 'SSE'], ['Sulawesi Tenggara', 'STN'], ['Gorontalo', 'GOR'], ['Sulawesi Barat', 'SBA']] },
  { name: 'Maluku & Papua', items: [['Maluku', 'MAL'], ['Maluku Utara', 'MUT'], ['Papua Barat', 'PBR'], ['Papua Barat Daya', 'PBD'], ['Papua', 'PAP'], ['Papua Selatan', 'PSL'], ['Papua Tengah', 'PTG'], ['Papua Pegunungan', 'PPG']] },
]

// Samakan ejaan: huruf kecil, hanya a-z, "Sumatra" = "Sumatera".
export const norm = (s) => String(s).toLowerCase().replace(/[^a-z]/g, '').replace('sumatra', 'sumatera')

/**
 * counts: [{ label, count }] dari backend. Mengembalikan kelompok kotak per pulau.
 * Nama dari data yang tidak cocok dengan daftar di atas masuk kelompok "Lainnya".
 */
export function buildLayout(counts = []) {
  const byNorm = new Map(counts.map((c) => [norm(c.label), c]))
  const used = new Set()
  const max = Math.max(0, ...counts.map((c) => c.count))
  let idx = 0

  const tile = (name, code, hit) => ({
    key: name,
    name: hit ? hit.label : name,
    code,
    count: hit ? hit.count : 0,
    actual: hit ? hit.label : null,
    t: hit && max ? hit.count / max : 0,
    idx: idx++,
  })

  const groups = ISLANDS.map((g) => ({
    name: g.name,
    tiles: g.items.map(([name, code]) => {
      const hit = byNorm.get(norm(name))
      if (hit) used.add(norm(name))
      return tile(name, code, hit)
    }),
  }))

  const extra = counts.filter((c) => !used.has(norm(c.label)))
  if (extra.length) {
    groups.push({ name: 'Lainnya', tiles: extra.map((c) => tile(c.label, c.label.slice(0, 3).toUpperCase(), c)) })
  }
  return { groups, max }
}

// Warna label evaluasi di tabel.
export function tone(text) {
  const t = String(text).toLowerCase()
  if (t.includes('ekstrem')) return 'hot'
  if (t.includes('beda arah')) return 'amber'
  if (t.includes('tertinggi')) return 'teal'
  if (t.includes('terendah')) return 'blue'
  if (t.includes('sog')) return 'violet'
  return 'slate'
}
