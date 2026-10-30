<script setup>
import { useCountUp } from '../composables/useCountUp'

const props = defineProps({ total: Number, provinces: Number, rules: Number })
const total = useCountUp(() => props.total)
const provinces = useCountUp(() => props.provinces, 700)
const rules = useCountUp(() => props.rules, 700)
const fmt = (n) => n.toLocaleString('id-ID')
</script>

<template>
  <div class="kpis">
    <div class="kpi main"><b>{{ fmt(total) }}</b><span>temuan perlu dicek</span></div>
    <div class="kpi"><b>{{ fmt(provinces) }}</b><span>provinsi terdampak</span></div>
    <div class="kpi"><b>{{ fmt(rules) }}</b><span>jenis aturan terpicu</span></div>
  </div>
</template>

<style scoped>
.kpis { display: flex; flex-wrap: wrap; gap: 8px 0; }
.kpi { padding: 2px 32px 2px 0; margin-right: 32px; border-right: 1px solid var(--line); display: flex; flex-direction: column; }
.kpi:last-child { border-right: 0; margin-right: 0; }
.kpi b { font-family: var(--display); font-size: 34px; line-height: 1.1; font-variant-numeric: tabular-nums; font-weight: 700; }
.kpi.main b { font-size: 52px; color: var(--pri); }
.kpi span { color: var(--mut); font-size: 14px; }
.kpi.main { justify-content: flex-end; }
@media (max-width: 640px) { .kpi { border-right: 0; margin-right: 24px; } .kpi.main b { font-size: 42px; } }
</style>
