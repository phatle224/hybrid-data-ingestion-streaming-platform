import UploadForm from './components/UploadForm'
import './App.css'

function App() {
  return (
    <div className="app-container">
      <div className="app-header">
        <div className="logo-container">
          <div className="logo-icon-wrapper">
            <span className="logo-icon">🛡️</span>
          </div>
        </div>
        <h1>InsuStream Portal</h1>
        <p className="subtitle">Upload Excel files for CDC processing</p>
      </div>
      <div className="app-content">
        <UploadForm />
      </div>
    </div>
  )
}

export default App

