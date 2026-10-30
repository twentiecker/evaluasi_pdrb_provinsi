import { ref } from 'vue'

const KEY = 'pdrb-theme'
const read = () => { try { return localStorage.getItem(KEY) } catch { return null } }

const theme = ref(read() || (window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'))
document.documentElement.dataset.theme = theme.value

function toggle() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  document.documentElement.dataset.theme = theme.value
  try { localStorage.setItem(KEY, theme.value) } catch { /* abaikan */ }
}

export function useTheme() {
  return { theme, toggle }
}
