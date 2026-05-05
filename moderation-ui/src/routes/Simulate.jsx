import { useState } from 'react'
import MessageHistory from '../components/simulate/MessageHistory'
import MessageInput from '../components/simulate/MessageInput'
import StatusFeedback from '../components/simulate/StatusFeedback'
import useModerate from '../hooks/useModerate'
import useModerationStore from '../store/moderationStore'

function Simulate() {
  const [text, setText] = useState('')
  const messages = useModerationStore((s) => s.messages)
  const { moderate, status, error } = useModerate()

  async function handleSend() {
    if (!text.trim()) return
    await moderate(text.trim())
    setText('')
  }

  return (
    <div className="simulate-grid">
      <div><MessageInput text={text} onChange={setText} onSend={handleSend} disabled={!text.trim() || status === 'loading'} /><StatusFeedback status={status} error={error} /></div>
      <MessageHistory messages={messages} />
    </div>
  )
}

export default Simulate
