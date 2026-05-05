function StatusFeedback({ status, error }) {
  if (error) return <p className="status blocked">? {error}</p>
  if (status === 'loading') return <p className="status loading">? Analyzing...</p>
  if (status === 'sent') return <p className="status allowed">? Message sent</p>
  if (status === 'blocked') return <p className="status blocked">? Blocked: Toxic content</p>
  return null
}

export default StatusFeedback
