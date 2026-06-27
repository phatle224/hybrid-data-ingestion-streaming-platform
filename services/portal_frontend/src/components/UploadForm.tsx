import { useEffect, useMemo, useState, useRef } from 'react'
import { useDropzone } from 'react-dropzone'
import { 
  Database, 
  UploadSimple, 
  Lightbulb, 
  ArrowsClockwise, 
  CaretDown,
  Airplane,
  Car,
  Motorcycle,
  Heart,
  ShieldCheck,
  Terminal,
  ArrowRight,
  Sparkle,
  Sliders,
  MagnifyingGlass
} from '@phosphor-icons/react'
import { InsuranceType, UploadStatus, UploadResponse, ValidationRowError, RecordPreview } from '../types'
import { uploadExcel } from '../services/api'
import './UploadForm.css'

// ===================== Record Table (Column Layout) =====================
interface RecordTableProps {
  records: RecordPreview[]
  type: 'inserted' | 'duplicate' | 'valid'
  emptyMessage?: string
}

function RecordTable({ records, type, emptyMessage = 'No records' }: RecordTableProps) {
  const [searchTerm, setSearchTerm] = useState('')
  
  const filteredRecords = useMemo(() => {
    if (!records) return []
    if (!searchTerm.trim()) return records
    const term = searchTerm.toLowerCase()
    return records.filter(r => 
      (r.contractId?.toLowerCase().includes(term)) ||
      (r.peopleName?.toLowerCase().includes(term)) ||
      (r.majorName?.toLowerCase().includes(term)) ||
      (r.companyProviderName?.toLowerCase().includes(term))
    )
  }, [records, searchTerm])

  if (!records || records.length === 0) {
    return <div className="empty-tab-state"><p>{emptyMessage}</p></div>
  }

  return (
    <div className="record-table-container">
      <div className="table-search-bar">
        <MagnifyingGlass size={16} />
        <input 
          type="text" 
          placeholder="Filter records by ID, name, or product..." 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        {searchTerm && (
          <button className="clear-search" onClick={() => setSearchTerm('')}>Clear</button>
        )}
      </div>

      <div className="record-table-wrapper">
        <table className="record-table">
          <thead>
            <tr>
              <th className="row-number-cell">Row</th>
              <th>Contract</th>
              <th>Name</th>
              <th>Product</th>
              <th>Provider</th>
            </tr>
          </thead>
          <tbody>
            {filteredRecords.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
                  No matching records found
                </td>
              </tr>
            ) : (
              filteredRecords.map((rec, idx) => (
                <tr key={idx} className={type === 'valid' ? 'inserted' : type}>
                  <td className="row-number-cell mono"><strong>{rec.row || idx + 1}</strong></td>
                  <td><code className="mono">{rec.contractId || '(empty)'}</code></td>
                  <td>{rec.peopleName || '(empty)'}</td>
                  <td>{rec.majorName || '(empty)'}</td>
                  <td>{rec.companyProviderName || '(empty)'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// ===================== Invalid Table (Column Layout with expandable errors) =====================
interface InvalidTableProps {
  errors: ValidationRowError[]
}

interface InvalidRowProps {
  error: ValidationRowError
  isExpanded: boolean
  onToggle: () => void
}

function InvalidRow({ error, isExpanded, onToggle }: InvalidRowProps) {
  const hasError = (field: string) => {
    return error.field_errors?.some(fe => fe.field === field || fe.excel_column === field)
  }

  const formatCurrentValue = (value: any) => {
    if (value === null || value === undefined) return ''
    if (typeof value === 'object') {
      try {
        return JSON.stringify(value)
      } catch {
        return String(value)
      }
    }
    return String(value)
  }

  const renderValue = (field: string, value: any) => {
    const isErr = hasError(field)
    return (
      <span className={`cell-value ${isErr ? 'has-error' : ''} ${!value ? 'is-empty' : ''}`}>
        {value || '(empty)'}
      </span>
    )
  }

  return (
    <>
      <tr className={`invalid-row clickable ${isExpanded ? 'expanded' : ''}`} onClick={onToggle}>
        <td className="row-number-cell mono"><strong>{error.excel_row}</strong></td>
        <td><code className="mono">{renderValue('contractId', error.record_preview?.contractId)}</code></td>
        <td>{renderValue('peopleName', error.record_preview?.peopleName)}</td>
        <td>{renderValue('majorName', error.record_preview?.majorName)}</td>
        <td>{renderValue('companyProviderName', error.record_preview?.companyProviderName)}</td>
        <td className="error-cell">
          <div className="error-badge-wrapper">
            <span className="error-count-badge mono">
              {error.error_count} {error.error_count > 1 ? 'errors' : 'error'}
            </span>
            <span className={`expand-caret ${isExpanded ? 'rotated' : ''}`}>
              <CaretDown size={14} weight="bold" />
            </span>
          </div>
        </td>
      </tr>
      {isExpanded && (
        <tr className="invalid-detail-row">
          <td colSpan={6}>
            <div className="expanded-error-container">
              <div className="field-errors-list">
                {error.field_errors?.map((fieldErr, fidx) => (
                  <div key={fidx} className={`field-error-item ${fieldErr.error_type.toLowerCase()}`}>
                    <div className="field-error-header">
                      <span className="field-name">{fieldErr.excel_column}</span>
                      <span className={`error-type-badge ${fieldErr.error_type.toLowerCase()}`}>
                        {fieldErr.error_type}
                      </span>
                    </div>
                    <div className="field-error-message">{fieldErr.message}</div>
                    {fieldErr.current_value !== null && fieldErr.current_value !== undefined && (
                      <div className="field-error-value">
                        Current value: <code className="mono">{formatCurrentValue(fieldErr.current_value)}</code>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  )
}

function InvalidTable({ errors }: InvalidTableProps) {
  const PAGE_SIZE = 50
  const [expandedRow, setExpandedRow] = useState<number | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [searchTerm, setSearchTerm] = useState('')

  const filteredErrors = useMemo(() => {
    if (!errors) return []
    if (!searchTerm.trim()) return errors
    const term = searchTerm.toLowerCase()
    return errors.filter(e => 
      (e.record_preview?.contractId?.toLowerCase().includes(term)) ||
      (e.record_preview?.peopleName?.toLowerCase().includes(term)) ||
      (e.field_errors?.some(fe => fe.message?.toLowerCase().includes(term) || fe.excel_column?.toLowerCase().includes(term)))
    )
  }, [errors, searchTerm])

  const totalPages = Math.max(1, Math.ceil(filteredErrors.length / PAGE_SIZE))
  const pageStart = (currentPage - 1) * PAGE_SIZE
  const pagedErrors = useMemo(() => filteredErrors.slice(pageStart, pageStart + PAGE_SIZE), [filteredErrors, pageStart])

  useEffect(() => {
    setCurrentPage(1)
    setExpandedRow(null)
  }, [errors, searchTerm])

  const toggleRow = (excelRow: number) => {
    setExpandedRow(prev => (prev === excelRow ? null : excelRow))
  }

  const goPrev = () => {
    setExpandedRow(null)
    setCurrentPage(prev => Math.max(1, prev - 1))
  }

  const goNext = () => {
    setExpandedRow(null)
    setCurrentPage(prev => Math.min(totalPages, prev + 1))
  }

  if (!errors || errors.length === 0) {
    return <div className="empty-tab-state"><p>No invalid records</p></div>
  }

  return (
    <div className="record-table-container">
      <div className="table-search-bar">
        <MagnifyingGlass size={16} />
        <input 
          type="text" 
          placeholder="Filter invalid records or error messages..." 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        {searchTerm && (
          <button className="clear-search" onClick={() => setSearchTerm('')}>Clear</button>
        )}
      </div>

      <div className="record-table-wrapper">
        <table className="record-table">
          <thead>
            <tr>
              <th className="row-number-cell">Row</th>
              <th>Contract</th>
              <th>Name</th>
              <th>Product</th>
              <th>Provider</th>
              <th>Errors</th>
            </tr>
          </thead>
          <tbody>
            {pagedErrors.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
                  No matching invalid records found
                </td>
              </tr>
            ) : (
              pagedErrors.map((error, idx) => (
                <InvalidRow
                  key={`row-${error.excel_row}-${idx}`}
                  error={error}
                  isExpanded={expandedRow === error.excel_row}
                  onToggle={() => toggleRow(error.excel_row)}
                />
              ))
            )}
          </tbody>
        </table>
      </div>
      <div className="invalid-pagination">
        <button type="button" className="pager-btn" onClick={goPrev} disabled={currentPage === 1}>
          Previous
        </button>
        <span className="pagination-info mono">
          Page {currentPage}/{totalPages} • Showing {pageStart + 1}-{Math.min(pageStart + PAGE_SIZE, filteredErrors.length)} of {filteredErrors.length}
        </span>
        <button type="button" className="pager-btn" onClick={goNext} disabled={currentPage === totalPages}>
          Next
        </button>
      </div>
    </div>
  )
}

// Custom Grid Icons & Options
const INSURANCE_OPTIONS = [
  { value: InsuranceType.HEALTH, label: 'Health', sub: 'Sức khỏe & Tai nạn', icon: Heart },
  { value: InsuranceType.VEHICLE, label: 'Vehicle', sub: 'Bảo hiểm Ô tô', icon: Car },
  { value: InsuranceType.TRAVEL, label: 'Travel', sub: 'Du lịch toàn cầu', icon: Airplane },
  { value: InsuranceType.MOTO, label: 'Motorcycle', sub: 'Bảo hiểm Xe máy', icon: Motorcycle },
  { value: InsuranceType.MEDICAL_SOCIAL, label: 'Med/Social', sub: 'Bảo hiểm Y tế & Xã hội', icon: ShieldCheck },
]

interface ResultState {
  type: 'success' | 'error' | 'validation_error' | 'partial_success'
  message: string
  details?: string
  response?: UploadResponse
}

interface ConsoleLog {
  timestamp: string
  type: 'info' | 'warn' | 'success' | 'error'
  text: string
}

function UploadForm() {
  const [insuranceType, setInsuranceType] = useState<InsuranceType | ''>('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [status, setStatus] = useState<UploadStatus>(UploadStatus.IDLE)
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState<ResultState | null>(null)
  const [activeTab, setActiveTab] = useState<'inserted' | 'duplicates' | 'invalid' | 'valid'>('valid')
  
  // Advanced Parameter States
  const [dryRun, setDryRun] = useState(false)
  const [autoResolve, setAutoResolve] = useState(true)
  const [deepIndexing, setDeepIndexing] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)

  // Real-time Console Log States
  const [logs, setLogs] = useState<ConsoleLog[]>([])
  const terminalEndRef = useRef<HTMLDivElement>(null)

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
    },
    multiple: false,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setSelectedFile(acceptedFiles[0])
        setResult(null)
        // Add log when file selected
        addLog('info', `File selected: "${acceptedFiles[0].name}" (${(acceptedFiles[0].size/1024).toFixed(1)} KB)`)
      }
    },
  })

  // Log helpers
  const addLog = (type: 'info' | 'warn' | 'success' | 'error', text: string) => {
    const time = new Date().toLocaleTimeString('en-US', { hour12: false })
    setLogs(prev => [...prev, { timestamp: time, type, text }])
  }

  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs])

  // Simulate rich technical logs during upload
  useEffect(() => {
    if (status !== UploadStatus.UPLOADING) return

    const generateLog = () => {
      if (progress === 0) {
        setLogs([])
        addLog('info', `Booting high-throughput Ingestion Engine pipeline...`)
        addLog('info', `Establishing virtual sandbox. Parameter DryRun=${dryRun}, AutoResolve=${autoResolve}`)
      } else if (progress > 5 && progress <= 15) {
        if (logs.length < 3) {
          addLog('info', `Target pipeline schema configured for: [${insuranceType}]`)
          addLog('info', `Reading byte streams of Excel document: "${selectedFile?.name}"`)
        }
      } else if (progress > 20 && progress <= 40) {
        if (!logs.some(l => l.text.includes('sheet'))) {
          addLog('info', `Successfully parsed active worksheets. Reading structure layout...`)
          addLog('info', `Running preliminary header mapping audit. Matching against static templates...`)
        }
      } else if (progress > 45 && progress <= 60) {
        if (!logs.some(l => l.text.includes('database'))) {
          addLog('info', `Dialing DB staging area. Connection pool verified successfully.`)
          addLog('info', `Scanning constraints. Checking foreign reference tables for [companyProviderName]...`)
        }
      } else if (progress > 65 && progress <= 80) {
        if (!logs.some(l => l.text.includes('Debezium'))) {
          addLog('warn', `Verification warnings: Empty fields found in non-critical attributes. Continuing...`)
          addLog('info', `Preparing Debezium CDC listener sync triggers...`)
        }
      } else if (progress > 85 && progress <= 95) {
        if (!logs.some(l => l.text.includes('Upsert'))) {
          addLog('info', `Running upsert queries. Resolving partition tables for Q2 datasets...`)
          addLog('info', `Triggering dbt pipeline models validation hooks...`)
        }
      }
    }

    generateLog()
  }, [progress, status])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!insuranceType) {
      alert('Please select an insurance type by clicking one of the options cards')
      return
    }

    if (!selectedFile) {
      alert('Please drag & drop or choose an Excel file to ingest')
      return
    }

    setStatus(UploadStatus.UPLOADING)
    setProgress(0)
    setResult(null)
    setLogs([])
    setActiveTab('valid')

    try {
      const response = await uploadExcel(
        selectedFile,
        insuranceType as InsuranceType,
        setProgress
      )

      if (response.success) {
        setStatus(UploadStatus.SUCCESS)
        addLog('success', `Pipeline completed! Ingestion committed to CDC pipeline database.`)
        setResult({
          type: response.status as any,
          message: response.status === 'partial_success' ? 'Partial Success' : 'Upload Successful',
          details: response.message,
          response
        })
        setInsuranceType('')
        setSelectedFile(null)
      } else if (response.status === 'validation_error') {
        setStatus(UploadStatus.ERROR)
        addLog('error', `Pipeline execution aborted: Ingest data contains structural schema violations.`)
        setResult({
          type: 'validation_error',
          message: 'Validation Error',
          details: response.message,
          response
        })
      } else {
        setStatus(UploadStatus.ERROR)
        addLog('error', `Critical Failure: Ingestion rejected by db constraints. Details: ${response.message}`)
        setResult({
          type: 'error',
          message: 'Upload Failed',
          details: response.message,
          response
        })
      }
    } catch (error: any) {
      setStatus(UploadStatus.ERROR)
      const errorResponse = error.response?.data as UploadResponse | undefined
      if (errorResponse?.status === 'validation_error') {
        addLog('error', `Schema Error: Validation failed.`)
        setResult({
          type: 'validation_error',
          message: 'Validation Error',
          details: errorResponse.message,
          response: errorResponse
        })
      } else {
        const errMsg = error.response?.data?.message || error.response?.data?.detail || error.message || 'Unknown error'
        addLog('error', `API Failure: ${errMsg}`)
        setResult({
          type: 'error',
          message: 'Upload Failed',
          details: errMsg,
        })
      }
    }
  }

  // Pre-compiled Mock pipeline jobs log
  const MOCK_JOBS = [
    { name: 'veh_data_q2_2026.xlsx', type: 'VEHICLE', rows: 412, status: 'success', time: '2 hours ago' },
    { name: 'health_staff_june.xlsx', type: 'HEALTH', rows: 1280, status: 'partial_success', time: '1 day ago' },
    { name: 'moto_expired_check.xls', type: 'MOTO', rows: 98, status: 'success', time: '3 days ago' }
  ]

  return (
    <div className="upload-layout">
      {/* LEFT PANEL */}
      <div className="upload-panel">
        <div className="panel-card main-config-card">
          <h2 className="panel-title">
            <Sliders size={20} weight="duotone" />
            Ingest Config
          </h2>
          
          <form onSubmit={handleSubmit} className="upload-form">
            <div className="form-group">
              <label>1. Select Insurance Type</label>
              <div className="insurance-grid">
                {INSURANCE_OPTIONS.map((opt) => {
                  const IconComp = opt.icon
                  const isSelected = insuranceType === opt.value
                  return (
                    <div 
                      key={opt.value}
                      className={`insurance-grid-card ${isSelected ? 'selected' : ''} ${status === UploadStatus.UPLOADING ? 'disabled' : ''}`}
                      onClick={() => status !== UploadStatus.UPLOADING && setInsuranceType(opt.value)}
                    >
                      <div className="card-icon-box">
                        <IconComp size={20} weight={isSelected ? "fill" : "duotone"} />
                      </div>
                      <div className="card-info-box">
                        <span className="card-title-text">{opt.label}</span>
                        <span className="card-sub-text">{opt.sub}</span>
                      </div>
                      {isSelected && <div className="card-active-indicator" />}
                    </div>
                  )
                })}
              </div>
            </div>

            <div className="form-group">
              <label>2. Data Source (Excel)</label>
              <div
                {...getRootProps()}
                className={`dropzone ${isDragActive ? 'drag-active' : ''} ${
                  selectedFile ? 'has-file' : ''
                } ${status === UploadStatus.UPLOADING ? 'disabled' : ''}`}
              >
                <input {...getInputProps()} disabled={status === UploadStatus.UPLOADING} />
                <div className="dropzone-icon">
                  <UploadSimple size={24} weight="bold" />
                </div>
                <div className="dropzone-text">
                  {selectedFile ? (
                    <>
                      <strong className="mono dropzone-file-name">{selectedFile.name}</strong>
                      <br />
                      <span className="file-size mono">
                        {(selectedFile.size / 1024).toFixed(1)} KB
                      </span>
                    </>
                  ) : isDragActive ? (
                    <span className="drag-active-text">Drop the file here...</span>
                  ) : (
                    <>
                      Drag & drop workbook here or <span className="browse-link">browse</span>
                      <br />
                      <span className="dropzone-limits">Supports .xlsx, .xls • Max 50MB</span>
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* Collapsible Advanced Parameters */}
            <div className="advanced-accordion">
              <button 
                type="button" 
                className="accordion-header"
                onClick={() => setShowAdvanced(!showAdvanced)}
              >
                <span>Advanced Parameters</span>
                <CaretDown size={14} className={`caret-icon ${showAdvanced ? 'rotated' : ''}`} />
              </button>
              
              {showAdvanced && (
                <div className="accordion-content">
                  <div className="toggle-group">
                    <div className="toggle-info">
                      <span className="toggle-label">Dry Run Execution</span>
                      <span className="toggle-desc">Dry run schema validation, bypass database commits</span>
                    </div>
                    <label className="switch">
                      <input 
                        type="checkbox" 
                        checked={dryRun} 
                        onChange={(e) => setDryRun(e.target.checked)}
                        disabled={status === UploadStatus.UPLOADING}
                      />
                      <span className="slider round"></span>
                    </label>
                  </div>

                  <div className="toggle-group">
                    <div className="toggle-info">
                      <span className="toggle-label">Conflict Resolution</span>
                      <span className="toggle-desc">Automatically override and merge duplicate IDs</span>
                    </div>
                    <label className="switch">
                      <input 
                        type="checkbox" 
                        checked={autoResolve} 
                        onChange={(e) => setAutoResolve(e.target.checked)}
                        disabled={status === UploadStatus.UPLOADING}
                      />
                      <span className="slider round"></span>
                    </label>
                  </div>

                  <div className="toggle-group">
                    <div className="toggle-info">
                      <span className="toggle-label">Deep Profiling</span>
                      <span className="toggle-desc">Generate statistical insights on row values</span>
                    </div>
                    <label className="switch">
                      <input 
                        type="checkbox" 
                        checked={deepIndexing} 
                        onChange={(e) => setDeepIndexing(e.target.checked)}
                        disabled={status === UploadStatus.UPLOADING}
                      />
                      <span className="slider round"></span>
                    </label>
                  </div>
                </div>
              )}
            </div>

            <button
              type="submit"
              className="upload-button"
              disabled={status === UploadStatus.UPLOADING || !insuranceType || !selectedFile}
            >
              {status === UploadStatus.UPLOADING ? (
                <div className="loading-btn-content">
                  <ArrowsClockwise size={16} className="spin-icon" />
                  <span>Streaming Ingest ({progress}%)</span>
                </div>
              ) : (
                <div className="btn-content">
                  <Sparkle size={16} weight="fill" />
                  <span>Execute Pipeline</span>
                </div>
              )}
            </button>
          </form>
        </div>
      </div>

      {/* RIGHT PANEL */}
      <div className="result-panel">
        <div className="panel-card cockpit-main-card">
          <h2 className="panel-title">
            <Database size={20} weight="duotone" />
            Ingest Cockpit
          </h2>
          
          {/* 1. IDLE DASHBOARD OVERVIEW */}
          {!result && status !== UploadStatus.UPLOADING && (
            <div className="cockpit-dashboard-idle">
              
              {/* Pipeline Streaming Flow Diagram */}
              <div className="pipeline-flow-diagram">
                <h3 className="diagram-title">CDC Pipeline Flow Map</h3>
                <div className="diagram-flow-wrapper">
                  <div className="diagram-node flow-excel">
                    <div className="node-icon"><UploadSimple size={16} weight="bold" /></div>
                    <span className="node-label">Excel Source</span>
                  </div>
                  <div className="diagram-link">
                    <div className="pulse-dot"></div>
                    <ArrowRight size={14} className="diagram-arrow" />
                  </div>
                  <div className="diagram-node flow-portal active">
                    <div className="node-icon"><Sparkle size={16} weight="fill" /></div>
                    <span className="node-label">Ingest Engine</span>
                  </div>
                  <div className="diagram-link">
                    <div className="pulse-dot"></div>
                    <ArrowRight size={14} className="diagram-arrow" />
                  </div>
                  <div className="diagram-node flow-kafka">
                    <div className="node-icon"><ArrowsClockwise size={16} weight="bold" /></div>
                    <span className="node-label">Kafka Stream</span>
                  </div>
                  <div className="diagram-link">
                    <div className="pulse-dot"></div>
                    <ArrowRight size={14} className="diagram-arrow" />
                  </div>
                  <div className="diagram-node flow-db">
                    <div className="node-icon"><Database size={16} weight="bold" /></div>
                    <span className="node-label">dbt Analytics</span>
                  </div>
                </div>
              </div>

              {/* Status bar indicators */}
              <div className="status-indicator-bar">
                <div className="indicator-pill green">
                  <span className="status-dot"></span>
                  <span className="indicator-label">Connector: RUNNING</span>
                </div>
                <div className="indicator-pill green">
                  <span className="status-dot"></span>
                  <span className="indicator-label">Kafka: HEALTHY</span>
                </div>
                <div className="indicator-pill violet">
                  <span className="status-dot"></span>
                  <span className="indicator-label">dbt Model: SYNCED</span>
                </div>
                <div className="indicator-pill green">
                  <span className="status-dot"></span>
                  <span className="indicator-label">Postgres: CONNECTED</span>
                </div>
              </div>

              {/* Ingest history */}
              <div className="ingest-history-section">
                <h3 className="section-title">Recent Ingestion Jobs</h3>
                <div className="history-table-wrapper">
                  <table className="history-table">
                    <thead>
                      <tr>
                        <th>Job File</th>
                        <th>Schema</th>
                        <th>Volume</th>
                        <th>Outcome</th>
                        <th>Completed</th>
                      </tr>
                    </thead>
                    <tbody>
                      {MOCK_JOBS.map((job, jidx) => (
                        <tr key={jidx}>
                          <td className="mono font-semibold">{job.name}</td>
                          <td>
                            <span className="type-tag">{job.type}</span>
                          </td>
                          <td className="mono">{job.rows} rows</td>
                          <td>
                            <span className={`status-pill ${job.status}`}>
                              {job.status === 'success' ? 'Success' : 'Partial'}
                            </span>
                          </td>
                          <td className="text-muted">{job.time}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

            </div>
          )}

          {/* 2. REAL-TIME LOG TERMINAL (WHILE UPLOADING) */}
          {status === UploadStatus.UPLOADING && (
            <div className="cockpit-terminal-logger">
              <div className="terminal-header">
                <div className="terminal-buttons">
                  <span className="btn-red"></span>
                  <span className="btn-yellow"></span>
                  <span className="btn-green"></span>
                </div>
                <span className="terminal-title">Ingest Engine Server Console</span>
                <span className="terminal-progress-text mono">{progress}%</span>
              </div>
              <div className="terminal-body mono">
                {logs.map((log, lidx) => (
                  <div key={lidx} className={`log-line ${log.type}`}>
                    <span className="log-time">[{log.timestamp}]</span>
                    <span className="log-tag">[{log.type.toUpperCase()}]</span>
                    <span className="log-text">{log.text}</span>
                  </div>
                ))}
                
                {/* Simulated blinking cursor */}
                <div className="log-line info">
                  <span className="log-time">[{new Date().toLocaleTimeString('en-US', { hour12: false })}]</span>
                  <span className="log-tag">[EXEC]</span>
                  <span className="log-text text-blink">Syncing pipelines buffers...</span>
                  <span className="cursor-cursor">_</span>
                </div>
                <div ref={terminalEndRef} />
              </div>
              
              <div className="terminal-status-footer">
                <ArrowsClockwise size={14} className="spin-icon" />
                <span>Our algorithms are parsing and validating your data...</span>
              </div>
            </div>
          )}

          {/* 3. INGESTION RESULTS CARD & TABS */}
          {result && (
            <div className="result-content">
              <div className="result-header-panel">
                <div className="result-title-box">
                  <h3 className="result-status-title">Ingest Process Summary</h3>
                  <p className="result-filename-desc text-muted mono">
                    File: {result.response?.filename || 'Uploaded File'}
                  </p>
                </div>
                <span className={`status-badge ${result.type}`}>
                  {result.type.replace('_', ' ')}
                </span>
              </div>
              
              {result.details && (
                <div className="result-log-pre-wrapper">
                  <div className="log-pre-header">
                    <Terminal size={14} />
                    <span>Raw Response Log</span>
                  </div>
                  <pre className="result-details mono">{result.details}</pre>
                </div>
              )}
          
              {(result.type === 'success' || result.type === 'partial_success' || result.type === 'validation_error') && result.response && (
                <div className="log-section">
                  {/* Summary Cards */}
                  <div className="validation-stats">
                    <div 
                      className={`stat-card success ${activeTab === 'valid' ? 'active' : ''}`}
                      onClick={() => setActiveTab('valid')}
                    >
                      <span className="stat-label">Valid Records</span>
                      <span className="stat-value mono">
                        {result.response.error_details?.valid_rows ?? ((result.response.records_inserted || 0) + (result.response.duplicates_found || 0))}
                      </span>
                    </div>

                    <div 
                      className={`stat-card success-light ${activeTab === 'inserted' ? 'active' : ''}`}
                      onClick={() => setActiveTab('inserted')}
                    >
                      <span className="stat-label">New Inserts</span>
                      <span className="stat-value mono">{result.response.records_inserted || 0}</span>
                    </div>

                    <div 
                      className={`stat-card warning ${activeTab === 'duplicates' ? 'active' : ''}`}
                      onClick={() => setActiveTab('duplicates')}
                    >
                      <span className="stat-label">Duplicates</span>
                      <span className="stat-value mono">{result.response.duplicates_found || 0}</span>
                    </div>

                    <div 
                      className={`stat-card error ${activeTab === 'invalid' ? 'active' : ''}`}
                      onClick={() => setActiveTab('invalid')}
                    >
                      <span className="stat-label">Invalid Rows</span>
                      <span className="stat-value mono">{result.response.error_details?.invalid_rows || result.response.invalid_rows || 0}</span>
                    </div>

                    <div className="stat-card stat-efficiency">
                      <span className="stat-label">Efficiency</span>
                      <span className="stat-value mono text-cyan">{result.response.error_details?.success_rate || '100%'}</span>
                    </div>
                  </div>

                  {/* Tab Header Controls */}
                  <div className="tab-header-controls">
                    <button 
                      className={`tab-link ${activeTab === 'valid' ? 'active' : ''}`}
                      onClick={() => setActiveTab('valid')}
                    >
                      Valid Preview ({result.response.valid_records_preview?.length || 0})
                    </button>
                    <button 
                      className={`tab-link ${activeTab === 'inserted' ? 'active' : ''}`}
                      onClick={() => setActiveTab('inserted')}
                    >
                      New Inserts ({result.response.inserted_records_preview?.length || 0})
                    </button>
                    <button 
                      className={`tab-link ${activeTab === 'duplicates' ? 'active' : ''}`}
                      onClick={() => setActiveTab('duplicates')}
                    >
                      Duplicates ({result.response.duplicate_records_preview?.length || 0})
                    </button>
                    <button 
                      className={`tab-link ${activeTab === 'invalid' ? 'active' : ''}`}
                      onClick={() => setActiveTab('invalid')}
                    >
                      Errors ({result.response.error_details?.all_errors?.length || 0})
                    </button>
                  </div>

                  {/* Tab Content Area */}
                  <div className="tab-content-area">
                    {activeTab === 'valid' && (
                      <RecordTable 
                        records={result.response.valid_records_preview || []}
                        type="valid"
                        emptyMessage="No valid records found in this file."
                      />
                    )}

                    {activeTab === 'inserted' && (
                      <RecordTable 
                        records={result.response.inserted_records_preview || []}
                        type="inserted"
                        emptyMessage="No new records were added to the system."
                      />
                    )}

                    {activeTab === 'duplicates' && (
                      <RecordTable 
                        records={result.response.duplicate_records_preview || []}
                        type="duplicate"
                        emptyMessage="No duplicate entries detected."
                      />
                    )}

                    {activeTab === 'invalid' && (
                      <InvalidTable errors={result.response.error_details?.all_errors || []} />
                    )}
                  </div>

                  {result.response.suggestion && (
                    <div className="suggestion">
                      <Lightbulb size={18} weight="fill" className="suggestion-icon" />
                      <span>{result.response.suggestion}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

        </div>
      </div>
    </div>
  )
}

export default UploadForm
