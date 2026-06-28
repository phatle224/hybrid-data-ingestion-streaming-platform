export enum InsuranceType {
  TRAVEL = 'TRAVEL',
  VEHICLE = 'VEHICLE',
  MOTO = 'MOTO',
  HEALTH = 'HEALTH',
  MEDICAL_SOCIAL = 'MEDICAL_SOCIAL',  // Combined medical and social in one type
}

export enum UploadStatus {
  IDLE = 'idle',
  UPLOADING = 'uploading',
  SUCCESS = 'success',
  ERROR = 'error',
}

export interface ValidationFieldError {
  field: string
  excel_column: string
  error_type: 'MISSING' | 'EMPTY' | 'INVALID'
  message: string
  current_value?: any
}

export interface ValidationRowError {
  row: number
  excel_row: number
  error_count: number
  field_errors: ValidationFieldError[]
  record_preview: {
    contractId: string
    peopleName: string
    majorName: string
    companyProviderName: string
  }
}

export interface ErrorByField {
  field: string
  display_name: string
  excel_column: string
  count: number
  sample_rows: number[]
}

export interface ValidationSummary {
  total_records: number
  valid_records: number
  invalid_records: number
  success_rate: string
  error_summary_by_field: ErrorByField[]
  first_10_errors: ValidationRowError[]
  insurance_type: string
}

export interface RecordPreview {
  row?: number
  contractId: string
  peopleName: string
  majorName: string
  companyProviderName: string
}

export interface UploadResponse {
  success: boolean
  status: 'success' | 'partial_success' | 'validation_error' | 'error'
  message: string
  filename?: string
  insurance_type?: string
  upload_id?: string
  
  // Success fields
  records_processed?: number
  records_inserted?: number
  duplicates_found?: number
  total_records?: number
  new_records?: number
  duplicate_records?: number
  invalid_rows?: number
  has_duplicates?: boolean
  
  // Record previews for tabs
  valid_records_preview?: RecordPreview[]
  inserted_records_preview?: RecordPreview[]
  duplicate_records_preview?: RecordPreview[]
  
  // Error fields
  validation_summary?: ValidationSummary
  error_details?: {
    total_rows: number
    valid_rows: number
    invalid_rows: number
    success_rate: string
    error_by_field: ErrorByField[]
    sample_errors: ValidationRowError[]
    all_errors?: ValidationRowError[]
    has_more_errors?: boolean
  }
  suggestion?: string
  errors?: string[]
}
