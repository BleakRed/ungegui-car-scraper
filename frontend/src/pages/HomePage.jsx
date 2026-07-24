import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Car, RefreshCw } from 'lucide-react'
import { fetchCars, triggerScrape } from '../api'
import SearchFilters from '../components/SearchFilters'
import CarCard from '../components/CarCard'
import Pagination from '../components/Pagination'

const INITIAL_FILTERS = {
  make: '', model: '', year_from: '', year_to: '',
  price_min: '', price_max: '', fuel: '',
  transmission: '', body_type: '', color: '',
  steering: '', drive_type: '', condition: '',
  doors: '', leasing: '', location: '',
}

function getFiltersFromURL(searchParams) {
  const filters = { ...INITIAL_FILTERS }
  for (const key of Object.keys(filters)) {
    const val = searchParams.get(key)
    if (val !== null && val !== '') {
      filters[key] = val
    }
  }
  return filters
}

export default function HomePage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [filters, setFilters] = useState(() => getFiltersFromURL(searchParams))
  const [page, setPage] = useState(1)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [scraping, setScraping] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = { page, limit: 20 }
      Object.entries(filters).forEach(([k, v]) => {
        if (v !== '' && v != null) params[k] = v
      })
      const result = await fetchCars(params)
      setData(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [page, filters])

  useEffect(() => {
    load()
  }, [load])

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters)
    setPage(1)
    const params = new URLSearchParams()
    Object.entries(newFilters).forEach(([k, v]) => {
      if (v !== '' && v != null) params.set(k, v)
    })
    setSearchParams(params, { replace: true })
  }

  const handleReset = () => {
    setFilters(INITIAL_FILTERS)
    setPage(1)
    setSearchParams({}, { replace: true })
  }

  const handleScrape = async () => {
    setScraping(true)
    try {
      await triggerScrape()
      await load()
    } catch (err) {
      setError(err.message)
    } finally {
      setScraping(false)
    }
  }

  return (
    <>
      <header className="header">
        <div className="header-inner">
          <div>
            <div className="header-title">
              <Car size={24} />
              Unegui Cars
            </div>
            <div className="header-subtitle">unegui.mn machine zarlal</div>
          </div>
          <button className="scrape-btn" onClick={handleScrape} disabled={scraping}>
            <RefreshCw size={14} className={scraping ? 'spinner' : ''} />
            {scraping ? 'Шинэчилж байна...' : 'Мэдээлэл татах'}
          </button>
        </div>
      </header>

      <main className="page-container">
        <div className="main-layout">
          <SearchFilters filters={filters} onChange={handleFilterChange} onReset={handleReset} />

          <section>
            {data && (
              <div className="results-header">
                <div className="results-count">
                  <strong>{data.total.toLocaleString()}</strong> машин олдлоо
                </div>
              </div>
            )}

            {loading && (
              <div className="loading">
                <div className="spinner" />
              </div>
            )}

            {error && (
              <div className="error-message">{error}</div>
            )}

            {!loading && !error && data && data.cars.length === 0 && (
              <div className="empty-state">
                <div className="empty-state-icon"><Car size={48} /></div>
                <div className="empty-state-text">Машин олдсонгүй</div>
                <div className="empty-state-sub">Шүүлтүүрээ өөрчилж үзээрэй</div>
              </div>
            )}

            {!loading && !error && data && data.cars.length > 0 && (
              <>
                <div className="car-grid">
                  {data.cars.map((car) => (
                    <CarCard key={car.id} car={car} />
                  ))}
                </div>
                <Pagination page={data.page} totalPages={data.pages} onChange={setPage} />
              </>
            )}
          </section>
        </div>
      </main>
    </>
  )
}
