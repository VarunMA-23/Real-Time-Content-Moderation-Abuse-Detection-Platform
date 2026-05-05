import EmptyState from '../shared/EmptyState'
import MessageCard from './MessageCard'

function MessageHistory({ messages }) {
  return (
    <div className="panel history">
      <h3>Message History</h3>
      {messages.length === 0 ? <EmptyState title="No messages yet" subtitle="Send a message to see moderation output." /> : messages.map((m) => <MessageCard key={m.id} message={m} />)}
    </div>
  )
}

export default MessageHistory
