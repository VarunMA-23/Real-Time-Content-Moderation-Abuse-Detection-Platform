import { useEffect } from 'react'
import { Navigate, Outlet } from 'react-router-dom'
import useModerationStore from '../../store/moderationStore'
import api from '../../services/api'
import Layout from './Layout'

function ProtectedLayout() {
  const user = useModerationStore((s) => s.user)
  const setPolicies = useModerationStore((s) => s.setPolicies)
  const policiesLoaded = useModerationStore((s) => s.policiesLoaded)

  useEffect(() => {
    if (user && !policiesLoaded) {
      api.getPolicies()
        .then((data) => setPolicies(data))
        .catch((err) => console.error('Failed to load policies:', err))
    }
  }, [user, policiesLoaded, setPolicies])

  if (!user) return <Navigate to="/login" replace />

  return (
    <Layout>
      <Outlet />
    </Layout>
  )
}

export default ProtectedLayout
