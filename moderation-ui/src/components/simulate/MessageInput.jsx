function MessageInput({ text, onChange, onSend, disabled }) {
  return (
    <div className="panel">
      <h3>Message Input</h3>
      <textarea rows={8} value={text} onChange={(e) => onChange(e.target.value)} maxLength={500} placeholder="Type a message to test moderation..." />
      <div className="row between"><small>{text.length}/500</small><button type="button" onClick={onSend} disabled={disabled}>Send</button></div>
    </div>
  )
}

export default MessageInput
