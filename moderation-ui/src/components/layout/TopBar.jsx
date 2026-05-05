import useModerationStore from '../../store/moderationStore'

function TopBar() {
  const user = useModerationStore((s) => s.user)

  return (
    <header className="topbar">
      <div>
        <h2>Real-Time Content Moderation</h2>
        <p>Operational dashboard for live abuse detection workflows.</p>
      </div>
      <div className="topbar-user">{user?.email || 'Anonymous'}</div>
    </header>
  )
}

export default TopBar
