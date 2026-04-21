import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,
})

export async function analyzeResume(file, onUploadProgress) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress
  })
  return response.data
}

export async function fetchJobs(jobTitle, location) {
  const response = await api.post('/jobs', {
    job_title: jobTitle,
    location:  location || null
  })
  return response.data
}

export async function sendChatMessage(message, analysis, history) {
  const response = await api.post('/chat', { message, analysis, history })
  return response.data
}

export async function checkHealth() {
  const response = await api.get('/health')
  return response.data
}
