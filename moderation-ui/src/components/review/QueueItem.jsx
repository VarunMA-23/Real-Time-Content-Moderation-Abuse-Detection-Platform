import RiskChip from '../shared/RiskChip'
import { formatTime } from '../../utils/formatTime'

function QueueItem({ item, active, onSelect }) {
  const level = (item.scores?.toxicity ?? 0) >= 0.7 ? 'high' : 'medium'
  return (
    <button type="button" className={`queue-item ${active ? 'active' : ''}`} onClick={() => onSelect(item.id)}>
      <div className="row between"><RiskChip level={level} /><small>{formatTime(item.timestamp)}</small></div>
      <p>{item.text.slice(0, 50)}...</p>
      <small>User {item.userId}</small>
    </button>
  )
}

export default QueueItem
