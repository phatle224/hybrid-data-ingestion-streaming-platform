import { useEffect, useState } from 'react'
import { Moon, Sun } from '@phosphor-icons/react'
import UploadForm from './components/UploadForm'
import './App.css'

type ThemeMode = 'light' | 'dark'

function App() {
  const [themeMode, setThemeMode] = useState<ThemeMode>(() => {
    const savedTheme = localStorage.getItem('portal-theme') as ThemeMode | null
    if (savedTheme === 'light' || savedTheme === 'dark') {
      return savedTheme
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', themeMode)
    localStorage.setItem('portal-theme', themeMode)
  }, [themeMode])

  const toggleTheme = () => {
    setThemeMode((prev) => (prev === 'light' ? 'dark' : 'light'))
  }

  return (
    <div className="app-container">
      <div className="app-header">
        <div className="theme-toggle-wrap">
          <button type="button" className="theme-toggle-btn" onClick={toggleTheme}>
            {themeMode === 'light' ? <Moon size={16} weight="fill" /> : <Sun size={16} weight="fill" />}
            <span>{themeMode === 'light' ? 'Dark Mode' : 'Light Mode'}</span>
          </button>
        </div>
        <h1>Insurance Portal</h1>
        <p className="subtitle">High-performance staging parser for CDC streaming pipelines.</p>
      </div>
      <div className="app-content">
        <UploadForm />
      </div>
    </div>
  )
}

export default App


