import axios from 'axios'
import { InsuranceType, UploadResponse } from '../types'

// For browser, always use localhost since it runs on client-side
// Backend service name only works inside Docker network
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for large files
})

export const uploadExcel = async (
  file: File,
  insuranceType: InsuranceType,
  onProgress?: (progress: number) => void
): Promise<UploadResponse> => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('insurance_type', insuranceType)

  const response = await api.post<UploadResponse>('/api/upload/excel', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total && onProgress) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(progress)
      }
    },
  })

  return response.data
}

export const checkHealth = async () => {
  const response = await api.get('/api/health/')
  return response.data
}
