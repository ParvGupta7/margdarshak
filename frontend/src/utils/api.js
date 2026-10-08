import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 180000,
})

async function postWithRetry(url, data, config = {}) {
  try {
    return await api.post(url, data, config)
  } catch (error) {
    const status = error.response?.status
    const shouldRetry = !error.response || status === 502 || status === 503 || status === 504
    if (!shouldRetry) {
      throw error
    }

    await new Promise((resolve) => setTimeout(resolve, 5000))
    return api.post(url, data, config)
  }
}

export async function analyzeResume(file, onUploadProgress) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await postWithRetry('/analyze', formData, {
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

/**
 * Hybrid Teacher & Mentor Recommendation based on skill gaps and target role.
 */
export async function recommendTeachers(analysis, targetRole = null, preferences = null, limit = 6) {
  const payload = {
    analysis,
    target_role: targetRole || null,
    preferences: preferences || null,
    limit: limit || 6
  }
  const response = await api.post('/teachers/recommend', payload)
  return response.data
}

export async function recommendStudentsForTeacher(teacherId, topSkills = []) {
  const params = topSkills.length ? { top_skills: topSkills.join(',') } : undefined
  const response = await api.get(`/teachers/${teacherId}/students`, { params })
  return response.data
}

/**
 * Resume Roaster: Generates a SAVAGE evidence-based roast of the uploaded resume.
 * 
 * NO role selector, NO tone selector.
 * Always generates BRUTAL, WITTY, DARK-HUMORED roast.
 */
export async function roastResume(file, analysisContext = null) {
  const formData = new FormData()
  formData.append('file', file)
  if (analysisContext) {
    formData.append('analysis_context', JSON.stringify(analysisContext))
  }
  const response = await api.post('/resume/roast', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 90000
  })
  return response.data
}

/**
 * Resume Improvement: iterative refinement of specific sections without fabrication.
 */
export async function improveResume(resumeText, targetRole = 'Software Engineer', selectedIssues = null, analysisContext = null) {
  const payload = {
    resume_text: resumeText,
    target_role: targetRole,
    selected_issues: selectedIssues || null,
    analysis_context: analysisContext || null
  }
  const response = await api.post('/resume/improve', payload, {
    timeout: 90000
  })
  return response.data
}
