import { Navigate, Route, Routes } from 'react-router-dom'
import ProtectedLayout from './components/layout/ProtectedLayout'
import Simulate from './routes/Simulate'
import Review from './routes/Review'
import Analytics from './routes/Analytics'
import Policies from './routes/Policies'
import Login from './routes/Login'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<ProtectedLayout />}>
        <Route path="/simulate" element={<Simulate />} />
        <Route path="/review" element={<Review />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/policies" element={<Policies />} />
        <Route path="/" element={<Navigate to="/simulate" replace />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
