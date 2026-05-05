import ActionButtons from './ActionButtons'
import DecisionHistory from './DecisionHistory'
import ScoreBar from './ScoreBar'

function MessageDetail({ message, onAction }) {
  if (!message) return <div className="panel">Select a queue item to review details.</div>

  return (
    <div className="panel">
      <h3>Message Detail</h3>
      <p>{message.text}</p><small>User {message.userId}</small>
      <div className="section-gap"><h4>Model Scores</h4><ScoreBar label="Toxicity" value={message.scores.toxicity || 0} /><ScoreBar label="Spam" value={message.scores.spam || 0} /><ScoreBar label="Self-harm" value={message.scores.selfHarm || 0} /></div>
      <div className="section-gap"><h4>LLM Explanation</h4><p className="muted">{message.llmExplanation || 'Waiting for enrichment...'}</p><p>Policy Violation: {message.policyViolation || 'Not available'}</p></div>
      <ActionButtons messageId={message.id} onAction={onAction} />
      <DecisionHistory history={message.history} />
    </div>
  )
}

export default MessageDetail
