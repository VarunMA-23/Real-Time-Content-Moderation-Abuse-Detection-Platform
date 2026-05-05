import { useMemo, useState } from 'react'
import MessageDetail from '../components/review/MessageDetail'
import QueueList from '../components/review/QueueList'
import FilterBar from '../components/shared/FilterBar'
import useQueue from '../hooks/useQueue'
import api from '../services/api'
import useModerationStore from '../store/moderationStore'

function Review() {
  const [filters, setFilters] = useState({ risk: 'all', dateRange: 'today', category: 'all' })
  const { queue, loading, error, refetch } = useQueue(filters)
  const selectedMessageId = useModerationStore((s) => s.selectedMessageId)
  const setSelectedMessageId = useModerationStore((s) => s.setSelectedMessageId)
  const resolveMessage = useModerationStore((s) => s.resolveMessage)
  const user = useModerationStore((s) => s.user)

  const selectedMessage = useMemo(() => queue.find((item) => item.id === selectedMessageId) ?? queue[0] ?? null, [queue, selectedMessageId])

  async function handleAction(messageId, action) {
    await api.submitDecision(messageId, action, user?.id || 'mod_1')
    resolveMessage(messageId, action)
    refetch()
  }

  return (
    <div className="review-grid">
      <section className="panel"><h3>Queue</h3><FilterBar filters={filters} onChange={setFilters} />{loading ? <p>Loading queue...</p> : null}{error ? <p className="status blocked">{error}</p> : null}<QueueList queue={queue} selectedMessageId={selectedMessage?.id} onSelect={setSelectedMessageId} onLoadMore={refetch} /></section>
      <MessageDetail message={selectedMessage} onAction={handleAction} />
    </div>
  )
}

export default Review
