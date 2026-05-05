import { NavLink } from 'react-router-dom'

function Sidebar() {
  return (
    <aside className="sidebar">
      <h1 className="sidebar-title">Moderation UI</h1>
      <nav className="sidebar-nav">
        <NavLink to="/simulate">Simulate</NavLink>
        <NavLink to="/review">Review</NavLink>
        <NavLink to="/analytics">Analytics</NavLink>
        <NavLink to="/policies">Policies</NavLink>
      </nav>
    </aside>
  )
}

export default Sidebar
