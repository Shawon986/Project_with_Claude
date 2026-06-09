import { reactive, watch } from 'vue'

const state = reactive({
  theme: localStorage.getItem('hz-theme') || 'dark',
  locale: localStorage.getItem('hz-locale') || 'en',
})

watch(() => state.theme, v => {
  document.documentElement.setAttribute('data-theme', v)
  localStorage.setItem('hz-theme', v)
}, { immediate: true })

watch(() => state.locale, v => {
  localStorage.setItem('hz-locale', v)
})

export function useAppStore() {
  function toggleTheme() { state.theme = state.theme === 'dark' ? 'light' : 'dark' }
  function toggleLocale() { state.locale = state.locale === 'en' ? 'zh' : 'en' }
  return { state, toggleTheme, toggleLocale }
}
