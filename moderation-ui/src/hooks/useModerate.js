import { useCallback, useState } from 'react'
import api from '../services/api'
import useModerationStore from '../store/moderationStore'

function useModerate() {
  const addMessage = useModerationStore((s) => s.addMessage)
  const updateMessage = useModerationStore((s) => s.updateMessage)
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState('')

  const pollForLLM = useCallback(async (messageId) => {
    for (let attempt = 0; attempt < 5; attempt += 1) {
      await new Promise((resolve) => setTimeout(resolve, 2000))
      try {
        const result = await api.getJob(messageId)
        if (result?.status === 'completed') {
          updateMessage(messageId, {
            llmExplanation: result.llmExplanation || 'LLM analysis completed.',
            policyViolation: result.policyViolation || 'Unspecified policy',
          })
          return
        }
      } catch {
        // ignore transient polling errors
      }
    }
  }, [updateMessage])

  const moderate = useCallback(async (text) => {
    setError('')
    setStatus('loading')
    try {
      const result = await api.moderate(text)
      addMessage({
        id: result.messageId,
        text,
        timestamp: new Date().toISOString(),
        status: result.decision,
        scores: result.scores,
        llmExplanation: null,
        policyViolation: null,
        history: [{ action: 'flagged', actor: 'system', time: new Date().toLocaleTimeString() }],
      })
      setStatus(result.decision === 'blocked' ? 'blocked' : 'sent')
      if (result.decision !== 'allowed') pollForLLM(result.messageId)
    } catch (err) {
      setStatus('idle')
      setError(err.message || 'Moderation request failed')
    }
  }, [addMessage, pollForLLM])

  return { moderate, status, error }
}

export default useModerate
