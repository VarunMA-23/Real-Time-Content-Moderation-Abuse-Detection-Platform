const BASE_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/v1').replace(/\/$/, '')

async function request(path, options = {}) {
  const token = localStorage.getItem('shieldai_token')
  const headers = { 
    'Content-Type': 'application/json', 
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {}) 
  }
  
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    let message = `Request failed: ${response.status}`
    const text = await response.text()

    try {
      const errorBody = text ? JSON.parse(text) : null
      message = errorBody?.error?.message || errorBody?.message || message
    } catch {
      message = text || message
    }

    throw new Error(message)
  }

  return response.json()
}

function toQuery(params = {}) {
  const query = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') query.set(k, String(v))
  })
  const value = query.toString()
  return value ? `?${value}` : ''
}

const api = {
  login: async (email, password) => {
    const data = await request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })
    if (data.accessToken) {
      localStorage.setItem('shieldai_token', data.accessToken)
    }
    return data.user
  },
  logout: () => {
    localStorage.removeItem('shieldai_token')
  },
  moderate: (text) => request('/moderate', { method: 'POST', body: JSON.stringify({ text }) }),
  getJob: (jobId) => request(`/jobs/${jobId}`),
  getQueue: (filters = {}) => request(`/review${toQuery(filters)}`),
  submitDecision: (messageId, action, moderatorId) => request('/decision', { method: 'POST', body: JSON.stringify({ messageId, action, moderatorId }) }),
  getAnalytics: (from, to) => request(`/analytics${toQuery({ from, to })}`),
  getPolicies: () => request('/policies'),
  savePolicies: (policies) => request('/policies', { method: 'PUT', body: JSON.stringify(policies) }),
}

export default api
