import EmptyState from '../shared/EmptyState'
import QueueItem from './QueueItem'

function QueueList({ queue, selectedMessageId, onSelect, onLoadMore }) {
  if (!queue.length) return <EmptyState title="No messages in queue" subtitle="Incoming flagged messages appear here." />
  return (
    <div className="queue-list">
      {queue.map((item) => <QueueItem key={item.id} item={item} active={selectedMessageId === item.id} onSelect={onSelect} />)}
      <button type="button" onClick={onLoadMore}>Load More</button>
    </div>
  )
}

export default QueueList
