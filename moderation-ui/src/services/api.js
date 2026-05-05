const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001'

async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `Request failed: ${response.status}`)
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
  login: (email, password) => request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  moderate: (text) => request('/moderate', { method: 'POST', body: JSON.stringify({ text }) }),
  getJob: (jobId) => request(`/jobs/${jobId}`),
  getQueue: (filters = {}) => request(`/review${toQuery(filters)}`),
  submitDecision: (messageId, action, moderatorId) => request('/decision', { method: 'POST', body: JSON.stringify({ messageId, action, moderatorId }) }),
  getAnalytics: (from, to) => request(`/analytics${toQuery({ from, to })}`),
  getPolicies: () => request('/policies'),
  savePolicies: (policies) => request('/policies', { method: 'PUT', body: JSON.stringify(policies) }),
}

export default api
