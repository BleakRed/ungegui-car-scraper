import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, ExternalLink, Gauge, Fuel, Cog, Palette, MapPin } from 'lucide-react'
import { fetchCar, fetchSimilarCars } from '../api'
import CarCard from '../components/CarCard'

export default function CarDetailPage() {
  const { id } = useParams()
  const [car, setCar] = useState(null)
  const [similar, setSimilar] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function load() {
      setLoading(true)
      setError(null)
      try {
        const result = await fetchCar(id)
        setCar(result)

        try {
          const sim = await fetchSimilarCars(id)
          setSimilar(Array.isArray(sim) ? sim : sim.cars || [])
        } catch {
          setSimilar([])
        }
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading"><div className="spinner" /></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-container">
        <Link to="/" className="detail-back"><ArrowLeft size={16} /> Буцах</Link>
        <div className="error-message">{error}</div>
      </div>
    )
  }

  if (!car) return null

  const specs = [
    { label: 'Марк', value: car.make },
    { label: 'Модель', value: car.model },
    { label: 'Он', value: car.year },
    { label: 'Орж ирсэн он', value: car.import_year },
    { label: 'Моторын багтаамж', value: car.engine_volume ? `${car.engine_volume}L` : null },
    { label: 'Хурдны хайрцаг', value: car.transmission },
    { label: 'Хөдөлгүүр', value: car.fuel_type },
    { label: 'Төрөл', value: car.body_type },
    { label: 'Гүйлт', value: car.mileage_km != null ? `${car.mileage_km.toLocaleString()} км` : null },
    { label: 'Өнгө', value: car.color },
    { label: 'Дотор өнгө', value: car.interior_color },
    { label: 'Хүрд', value: car.steering },
    { label: 'Хөтлөгч', value: car.drive_type },
    { label: 'Хаалга', value: car.doors },
    { label: 'Нөхцөл', value: car.condition },
    { label: 'Лизинг', value: car.leasing },
    { label: 'Байршил', value: car.location },
  ].filter((s) => s.value)

  return (
    <>
      <header className="header">
        <div className="header-inner">
          <Link to="/" className="header-title" style={{ textDecoration: 'none' }}>
            <ArrowLeft size={20} style={{ marginRight: 4 }} />
            Unegui Cars
          </Link>
        </div>
      </header>

      <main className="page-container">
        <Link to="/" className="detail-back"><ArrowLeft size={16} /> Бүх машин руу буцах</Link>

        {car.image_urls && car.image_urls.length > 0 && (
          <div className={`detail-gallery${car.image_urls.length === 1 ? ' detail-gallery-single' : ''}`}>
            {car.image_urls.map((url, i) => (
              <img key={i} src={url} alt={`${car.title} ${i + 1}`} />
            ))}
          </div>
        )}

        <div className="detail-info">
          <div className="detail-price">{car.price_display || `${(car.price_mnt / 1000000).toFixed(1)} сая₮`}</div>
          <h1 className="detail-title">{car.title || `${car.make} ${car.model} ${car.year || ''}`}</h1>

          <div className="detail-specs">
            {specs.map((s) => (
              <div key={s.label} className="detail-spec">
                <span className="detail-spec-label">{s.label}</span>
                <span className="detail-spec-value">{s.value}</span>
              </div>
            ))}
          </div>

          {car.description && (
            <div className="detail-description">{car.description}</div>
          )}

          {car.source_url && (
            <a href={car.source_url} target="_blank" rel="noopener noreferrer" className="detail-link">
              <ExternalLink size={16} />
              unegui.mn дээр үзэх
            </a>
          )}
        </div>

        {similar.length > 0 && (
          <div className="similar-section">
            <h2 className="similar-title">Төстэй машинууд</h2>
            <div className="car-grid">
              {similar.map((c) => (
                <CarCard key={c.id} car={c} />
              ))}
            </div>
          </div>
        )}
      </main>
    </>
  )
}
