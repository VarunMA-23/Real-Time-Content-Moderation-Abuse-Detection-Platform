import { useCallback, useEffect, useState } from 'react'
import api from '../services/api'
import useModerationStore from '../store/moderationStore'

function usePolicies() {
  const policies = useModerationStore((s) => s.policies)
  const policiesLoaded = useModerationStore((s) => s.policiesLoaded)
  const setPolicies = useModerationStore((s) => s.setPolicies)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')

  const loadPolicies = useCallback(async (force = false) => {
    if (policiesLoaded && !force) return
    setLoading(true)
    setError('')
    try {
      const result = await api.getPolicies()
      setPolicies(result)
    } catch (err) {
      setError(err.message || 'Failed to load policies')
    } finally {
      setLoading(false)
    }
  }, [setPolicies, policiesLoaded])

  useEffect(() => {
    loadPolicies()
  }, [loadPolicies])

  const savePolicies = useCallback(async () => {
    setSaving(true)
    setSaved(false)
    setError('')
    try {
      await api.savePolicies(policies)
      setSaved(true)
    } catch (err) {
      setError(err.message || 'Failed to save policies')
    } finally {
      setSaving(false)
    }
  }, [policies])

  return { policies, setPolicies, savePolicies, loading, saving, saved, error }
}

export default usePolicies
