import UploadForm from './components/UploadForm'
import './App.css'

function App() {
  return (
    <div className="app-container">
      <div className="app-header">
        <div className="logo-container">
          <img src="/logo_affina.png" alt="Affina Logo" className="logo" />
        </div>
        <h1>Affina Portal</h1>
        <p className="subtitle">Upload Excel files for CDC processing</p>
      </div>
      <div className="app-content">
        <UploadForm />
      </div>
    </div>
  )
}

export default App

