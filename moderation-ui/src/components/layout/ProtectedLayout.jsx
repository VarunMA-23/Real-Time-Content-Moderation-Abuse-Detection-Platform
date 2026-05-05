import { Navigate, Outlet } from 'react-router-dom'
import useModerationStore from '../../store/moderationStore'
import Layout from './Layout'

function ProtectedLayout() {
  const user = useModerationStore((s) => s.user)
  if (!user) return <Navigate to="/login" replace />

  return (
    <Layout>
      <Outlet />
    </Layout>
  )
}

export default ProtectedLayout
