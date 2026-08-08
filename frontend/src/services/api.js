import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
})

export async function healthCheck() {
  const { data } = await api.get('/health')
  return data
}

export async function predictReview(review) {
  const { data } = await api.post('/predict', { review })
  return data
}

export async function uploadCsv(file) {
  const form = new FormData()
  form.append('file', file)
  // Do not set Content-Type manually — the browser must include the multipart boundary.
  const { data } = await api.post('/upload', form)
  return data
}

export async function fetchMetrics() {
  const { data } = await api.get('/metrics')
  return data
}

export function getErrorMessage(error) {
  if (error.response?.data?.detail) {
    const detail = error.response.data.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail.map((d) => d.msg || JSON.stringify(d)).join('; ')
    }
  }
  if (error.code === 'ERR_NETWORK' || !error.response) {
    return 'Backend unavailable. Start FastAPI on http://127.0.0.1:8000'
  }
  return error.message || 'Unexpected error'
}

export default api
