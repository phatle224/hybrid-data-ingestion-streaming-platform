import { useEffect, useMemo, useState } from 'react'
import { useDropzone } from 'react-dropzone'
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
  if (!records || records.length === 0) {
    return <div className="empty-tab-state"><p>{emptyMessage}</p></div>
  }
  return (
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
          {records.map((rec, idx) => (
            <tr key={idx} className={type === 'valid' ? 'inserted' : type}>
              <td className="row-number-cell"><strong>{rec.row || idx + 1}</strong></td>
              <td><code>{rec.contractId || '(empty)'}</code></td>
              <td>{rec.peopleName || '(empty)'}</td>
              <td>{rec.majorName || '(empty)'}</td>
              <td>{rec.companyProviderName || '(empty)'}</td>
            </tr>
          ))}
        </tbody>
      </table>
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
        <td className="row-number-cell"><strong>{error.excel_row}</strong></td>
        <td><code>{renderValue('contractId', error.record_preview?.contractId)}</code></td>
        <td>{renderValue('peopleName', error.record_preview?.peopleName)}</td>
        <td>{renderValue('majorName', error.record_preview?.majorName)}</td>
        <td>{renderValue('companyProviderName', error.record_preview?.companyProviderName)}</td>
        <td className="error-cell">
          <div className="error-badge-wrapper">
            <span className="error-count-badge">
              {error.error_count} {error.error_count > 1 ? 'errors' : 'error'}
            </span>
            <span className={`expand-caret ${isExpanded ? 'rotated' : ''}`}>
              <svg width="12" height="8" viewBox="0 0 10 6" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M1 1L5 5L9 1" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
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
                        Current value: <code>{formatCurrentValue(fieldErr.current_value)}</code>
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

  if (!errors || errors.length === 0) {
    return <div className="empty-tab-state"><p>No invalid records</p></div>
  }

  const totalPages = Math.max(1, Math.ceil(errors.length / PAGE_SIZE))
  const pageStart = (currentPage - 1) * PAGE_SIZE
  const pagedErrors = useMemo(() => errors.slice(pageStart, pageStart + PAGE_SIZE), [errors, pageStart])

  useEffect(() => {
    setCurrentPage(1)
    setExpandedRow(null)
  }, [errors])

  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages)
    }
  }, [currentPage, totalPages])

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

  return (
    <>
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
          {pagedErrors.map((error, idx) => (
            <InvalidRow
              key={`row-${error.excel_row}-${idx}`}
              error={error}
              isExpanded={expandedRow === error.excel_row}
              onToggle={() => toggleRow(error.excel_row)}
            />
          ))}
        </tbody>
      </table>
      </div>
      <div className="invalid-pagination">
        <button type="button" className="pager-btn" onClick={goPrev} disabled={currentPage === 1}>
          Previous
        </button>
        <span className="pagination-info">
          Page {currentPage}/{totalPages} • Showing {pageStart + 1}-{Math.min(pageStart + PAGE_SIZE, errors.length)} of {errors.length}
        </span>
        <button type="button" className="pager-btn" onClick={goNext} disabled={currentPage === totalPages}>
          Next
        </button>
      </div>
    </>
  )
}

const INSURANCE_OPTIONS = [
  { value: InsuranceType.TRAVEL, label: 'Travel Insurance (Du lịch)' },
  { value: InsuranceType.VEHICLE, label: 'Vehicle Insurance (Ô tô)' },
  { value: InsuranceType.MOTO, label: 'Motorcycle Insurance (Xe máy)' },
  { value: InsuranceType.HEALTH, label: 'Health Insurance (Sức khỏe)' },
  { value: InsuranceType.MEDICAL_SOCIAL, label: 'Medical & Social Insurance (Y tế/Xã hội)' },
]

interface ResultState {
  type: 'success' | 'error' | 'validation_error' | 'partial_success'
  message: string
  details?: string
  response?: UploadResponse
}

function UploadForm() {
  const [insuranceType, setInsuranceType] = useState<InsuranceType | ''>('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [status, setStatus] = useState<UploadStatus>(UploadStatus.IDLE)
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState<ResultState | null>(null)
  const [activeTab, setActiveTab] = useState<'inserted' | 'duplicates' | 'invalid' | 'valid'>('valid')

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
      }
    },
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!insuranceType) {
      alert('Please select insurance type')
      return
    }

    if (!selectedFile) {
      alert('Please select a file')
      return
    }

    setStatus(UploadStatus.UPLOADING)
    setProgress(0)
    setResult(null)
    setActiveTab('inserted')

    try {
      const response = await uploadExcel(
        selectedFile,
        insuranceType as InsuranceType,
        setProgress
      )

      if (response.success) {
        setStatus(UploadStatus.SUCCESS)
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
        setResult({
          type: 'validation_error',
          message: 'Validation Error',
          details: response.message,
          response
        })
      } else {
        setStatus(UploadStatus.ERROR)
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
        setResult({
          type: 'validation_error',
          message: 'Validation Error',
          details: errorResponse.message,
          response: errorResponse
        })
      } else {
        setResult({
          type: 'error',
          message: 'Upload Failed',
          details: error.response?.data?.message || error.response?.data?.detail || error.message || 'Unknown error',
        })
      }
    }
  }

  return (
    <div className="upload-layout">
      {/* LEFT PANEL */}
      <div className="upload-panel">
        <div className="panel-card">
          <h2 className="panel-title">Upload</h2>
          <form onSubmit={handleSubmit} className="upload-form">
            <div className="form-group">
              <label htmlFor="insuranceType">Insurance Type</label>
              <select
                id="insuranceType"
                value={insuranceType}
                onChange={(e) => setInsuranceType(e.target.value as InsuranceType)}
                required
                disabled={status === UploadStatus.UPLOADING}
              >
                <option value="">Select insurance type...</option>
                {INSURANCE_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Data Source (Excel)</label>
              <div
                {...getRootProps()}
                className={`dropzone ${isDragActive ? 'drag-active' : ''} ${
                  selectedFile ? 'has-file' : ''
                }`}
              >
                <input {...getInputProps()} />
                <div className="dropzone-icon"></div>
                <div className="dropzone-text">
                  {selectedFile ? (
                    <>
                      <strong>{selectedFile.name}</strong>
                      <br />
                      <span className="file-size">
                        {(selectedFile.size / 1024).toFixed(1)} KB
                      </span>
                    </>
                  ) : isDragActive ? (
                    'Release to upload'
                  ) : (
                    <>
                      Click or drag to upload Excel file
                      <br />
                      <span style={{fontSize: '11px', color: '#94a3b8'}}>Max 50MB per file</span>
                    </>
                  )}
                </div>
              </div>
            </div>

            <button
              type="submit"
              className="upload-button"
              disabled={status === UploadStatus.UPLOADING}
            >
              {status === UploadStatus.UPLOADING ? (
                <div className="loading">
                  <div className="spinner"></div>
                  <span>Processing {progress}%</span>
                </div>
              ) : (
                'Process Records'
              )}
            </button>
          </form>
        </div>
      </div>

      {/* RIGHT PANEL */}
      <div className="result-panel">
        <div className="panel-card">
          <h2 className="panel-title">Processing</h2>
          
          {!result && status !== UploadStatus.UPLOADING && (
            <div className="empty-state">
              <div className="empty-icon" style={{fontSize: '48px', marginBottom: '16px'}}>📊</div>
              <p>Selection an insurance type and upload a file to start analysis</p>
            </div>
          )}

          {status === UploadStatus.UPLOADING && (
             <div className="empty-state">
               <div className="spinner" style={{borderColor: '#e2e8f0', borderTopColor: '#6366f1', width: '40px', height: '40px', marginBottom: '20px'}}></div>
               <p>Our algorithms are parsing and validating your data...</p>
             </div>
          )}

          {result && (
            <div className={`result-content`}>
              <div className="result-header">
                <span className={`status-badge ${result.type}`}>
                  {result.type.replace('_', ' ')}
                </span>
              </div>
              
              {result.details && (
                <pre className="result-details">{result.details}</pre>
              )}
          
              {(result.type === 'success' || result.type === 'partial_success' || result.type === 'validation_error') && result.response && (
                <div className="log-section">
                  {/* Summary Cards */}
                  <div className="validation-stats">
                    <h4>Overview (Click cards to filter)</h4>
                    <div 
                      className={`stat-card success ${activeTab === 'inserted' ? 'active' : ''}`}
                      onClick={() => setActiveTab('inserted')}
                    >
                      <span className="stat-label">Inserted</span>
                      <span className="stat-value">{result.response.records_inserted || 0}</span>
                    </div>
                    <div 
                      className={`stat-card warning ${activeTab === 'duplicates' ? 'active' : ''}`}
                      onClick={() => setActiveTab('duplicates')}
                    >
                      <span className="stat-label">Duplicates</span>
                      <span className="stat-value">{result.response.duplicates_found || 0}</span>
                    </div>
                    <div 
                      className={`stat-card info ${activeTab === 'valid' ? 'active' : ''}`}
                      onClick={() => setActiveTab('valid')}
                    >
                      <span className="stat-label">Valid Records</span>
                      <span className="stat-value">
                        {result.response.error_details?.valid_rows ?? ((result.response.records_inserted || 0) + (result.response.duplicates_found || 0))}
                      </span>
                    </div>
                    <div 
                      className={`stat-card error ${activeTab === 'invalid' ? 'active' : ''}`}
                      onClick={() => setActiveTab('invalid')}
                    >
                      <span className="stat-label">Invalid</span>
                      <span className="stat-value">{result.response.error_details?.invalid_rows || result.response.invalid_rows || 0}</span>
                    </div>
                    <div className="stat-card">
                      <span className="stat-label">Efficiency</span>
                      <span className="stat-value">{result.response.error_details?.success_rate || '100%'}</span>
                    </div>
                  </div>

                  {/* Tab Content Area (Managed by clicking cards above) */}
                  <div className="tab-content-area" style={{ marginTop: '24px' }}>
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
                      {result.response.suggestion}
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
