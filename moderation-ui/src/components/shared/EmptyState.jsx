function EmptyState({ icon = '??', title, subtitle }) {
  return (
    <div className="empty-state">
      <div>{icon}</div><h3>{title}</h3><p>{subtitle}</p>
    </div>
  )
}

export default EmptyState
