import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import useModerationStore from '../store/moderationStore'

function Login() {
  const navigate = useNavigate()
  const setUser = useModerationStore((s) => s.setUser)
  const [email, setEmail] = useState('moderator@example.com')
  const [password, setPassword] = useState('secret123')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      const user = await api.login(email, password)
      setUser(user)
      navigate('/simulate')
    } catch (err) {
      setError(err.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <form className="panel login-card" onSubmit={handleSubmit}>
        <h2>Moderator Login</h2>
        <label>Email<input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></label>
        <label>Password<input type="password" required minLength={6} value={password} onChange={(e) => setPassword(e.target.value)} /></label>
        {error ? <p className="status blocked">{error}</p> : null}
        <button type="submit" disabled={loading}>{loading ? 'Signing in...' : 'Sign in'}</button>
      </form>
    </div>
  )
}

export default Login
