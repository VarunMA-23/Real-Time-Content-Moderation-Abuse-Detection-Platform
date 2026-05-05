import { useCallback, useEffect, useState } from 'react'
import api from '../services/api'

function useAnalytics(range) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchAnalytics = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const result = await api.getAnalytics(range.from, range.to)
      setData(result)
    } catch (err) {
      setError(err.message || 'Failed to load analytics')
    } finally {
      setLoading(false)
    }
  }, [range.from, range.to])

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchAnalytics()
    }, 0)
    return () => clearTimeout(timer)
  }, [fetchAnalytics])

  return { data, loading, error, refetch: fetchAnalytics }
}

export default useAnalytics
