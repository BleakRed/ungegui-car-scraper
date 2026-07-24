import { Link } from 'react-router-dom'
import { Gauge, Fuel, Cog, MapPin } from 'lucide-react'

export default function CarCard({ car }) {
  const imageUrl = car.image_urls && car.image_urls.length > 0 ? car.image_urls[0] : null

  return (
    <Link to={`/car/${car.id}`} className="car-card">
      <div className="car-card-image-wrap">
        {imageUrl ? (
          <img className="car-card-image" src={imageUrl} alt={car.title} loading="lazy" />
        ) : (
          <div className="car-card-no-image">Зурггүй</div>
        )}
        {car.year && (
          <span className="car-card-badge">{car.year}</span>
        )}
      </div>
      <div className="car-card-body">
        <div className="car-card-price">{car.price_display || `${(car.price_mnt / 1000000).toFixed(1)} сая₮`}</div>
        <div className="car-card-title">{car.title || `${car.make} ${car.model}`}</div>
        <div className="car-card-features">
          {car.mileage_km != null && (
            <span className="car-card-feature">
              <Gauge /> {(car.mileage_km / 1000).toFixed(0)} мян.км
            </span>
          )}
          {car.transmission && (
            <span className="car-card-feature">
              <Cog /> {car.transmission}
            </span>
          )}
          {car.engine_volume && (
            <span className="car-card-feature">
              <Fuel /> {car.engine_volume}L
            </span>
          )}
          {car.fuel_type && (
            <span className="car-card-feature">
              {car.fuel_type}
            </span>
          )}
        </div>
        <div className="car-card-footer">
          <span className="car-card-feature" style={{ background: 'transparent', padding: 0 }}>
            <MapPin /> {car.location || '—'}
          </span>
        </div>
      </div>
    </Link>
  )
}
