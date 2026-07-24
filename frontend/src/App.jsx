import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import CarDetailPage from './pages/CarDetailPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/car/:id" element={<CarDetailPage />} />
    </Routes>
  )
}
