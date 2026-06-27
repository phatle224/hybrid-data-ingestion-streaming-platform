import { Shield } from '@phosphor-icons/react'
import UploadForm from './components/UploadForm'
import './App.css'

function App() {
  return (
    <div className="app-container">
      <div className="app-header">
        <div className="logo-container">
          <div className="logo-icon-wrapper">
            <Shield size={32} weight="duotone" className="logo-icon" />
          </div>
        </div>
        <div className="version-tag mono">INGESTION COCKPIT v2.4</div>
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


