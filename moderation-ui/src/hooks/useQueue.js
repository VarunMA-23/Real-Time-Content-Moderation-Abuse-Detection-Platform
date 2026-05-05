import { useCallback, useEffect, useState } from 'react'
import api from '../services/api'
import useModerationStore from '../store/moderationStore'

function useQueue(filters) {
  const queue = useModerationStore((s) => s.queue)
  const setQueue = useModerationStore((s) => s.setQueue)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchQueue = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const result = await api.getQueue({ status: 'pending', ...filters })
      setQueue(result.queue || [])
    } catch (err) {
      setError(err.message || 'Failed to fetch queue')
    } finally {
      setLoading(false)
    }
  }, [filters, setQueue])

  useEffect(() => {
    const initialTimer = setTimeout(() => {
      fetchQueue()
    }, 0)
    const intervalTimer = setInterval(fetchQueue, 30000)
    return () => {
      clearTimeout(initialTimer)
      clearInterval(intervalTimer)
    }
  }, [fetchQueue])

  return { queue, loading, error, refetch: fetchQueue }
}

export default useQueue
