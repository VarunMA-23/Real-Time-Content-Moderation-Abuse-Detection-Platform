function ActionButtons({ messageId, onAction }) {
  return (
    <div className="action-buttons">
      <button type="button" onClick={() => onAction(messageId, 'approve')}>? Approve</button>
      <button type="button" onClick={() => onAction(messageId, 'reject')}>? Reject</button>
      <button type="button" onClick={() => { if (window.confirm('Ban this user?')) onAction(messageId, 'ban') }}>?? Ban User</button>
      <button type="button" onClick={() => onAction(messageId, 'escalate')}>? Escalate</button>
    </div>
  )
}

export default ActionButtons
