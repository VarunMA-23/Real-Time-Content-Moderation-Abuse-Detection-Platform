import StatusBadge from '../shared/StatusBadge'
import { formatTime } from '../../utils/formatTime'

function MessageCard({ message }) {
  const preview = message.text.length > 80 ? `${message.text.slice(0, 80)}...` : message.text
  return (
    <article className="message-card">
      <div className="row between"><strong>{formatTime(message.timestamp)}</strong><StatusBadge decision={message.status} /></div>
      <p>{preview}</p>
      <small>Score: {(message.scores?.toxicity ?? 0).toFixed(2)}</small>
      <p className="muted">{message.llmExplanation || 'LLM reasoning pending...'}</p>
    </article>
  )
}

export default MessageCard
